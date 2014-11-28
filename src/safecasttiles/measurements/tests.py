import datetime

from PIL import Image, ImageDraw

from django.test import TestCase
from django.contrib.gis.geos import Polygon, Point

from safecasttiles.measurements.models import Measurement
from tmstiler.rtm import RasterTileManager


SPHERICAL_MERCATOR_SRID = 3857 # google maps projection


class Legend:

    def get_color_str(self, value):
        """
        :param value:
        :return:  rgb or hsl color string in the format:

        rgb(255,0,0)
        rgb(100%,0%,0%)

        hsl(hue, saturation%, lightness%)
        where:
            hue is the color given as an angle between 0 and 360 (red=0, green=120, blue=240)
            saturation is a value between 0% and 100% (gray=0%, full color=100%)
            lightness is a value between 0% and 100% (black=0%, normal=50%, white=100%).

        For example, hsl(0,100%,50%) is pure red.
        """
        return "hsl(0,100%,50%)"  # pure red for now...


class TestDjangoRasterTileLayerManager(TestCase):

    def test_get_tile(self):
        pixel_size_meters = 250
        tile_pixel_size = 256
        zoom = 10
        tilex = 911
        tiley = 626


        rtmgr = RasterTileManager()

        tile_extent = rtmgr.tile_sphericalmercator_extent(zoom, tilex, tiley)
        bbox = Polygon.from_bbox(tile_extent)
        buffered_bbox = bbox.buffer(pixel_size_meters/2, quadsegs=2)

        # create dummy data in extent
        upperright_x = tile_extent[0]  # minx
        upperright_y = tile_extent[3]  # maxy

        # create measurement instances for the left half of the tile
        # --> get the x halfway point
        xmin = tile_extent[0]  # minx
        xmax = tile_extent[2]  # maxx
        ymin = tile_extent[1]  # miny
        tile_width = xmax - xmin
        half_tile_width = tile_width/2
        halfx = xmin + half_tile_width

        # create Measurement() objects for half of the tile
        d = datetime.date(2014, 11, 28)
        x = upperright_x
        y = upperright_y
        created_measurement_count = 0
        while x <= halfx:
            while y >= ymin:
                point = Point(x, y, srid=SPHERICAL_MERCATOR_SRID)
                m = Measurement(location=point,
                                date=d,
                                counts=50,
                                value=1)
                m.save()
                created_measurement_count += 1
                y -= pixel_size_meters
            x += pixel_size_meters
        print("Created Measurement Count: {}".format(created_measurement_count))

        # pull created data
        temp_measurements = Measurement.objects.filter(location__within=buffered_bbox)
        query_result_count = temp_measurements.count()
        self.assertTrue(query_result_count == created_measurement_count, "Retrieved Meaurement Count({}) != created count({})".format(query_result_count,
                                                                                                                                      created_measurement_count))

        # create tile image from pulled data
        tile_image = Image.new("RGBA", (tile_pixel_size, tile_pixel_size), (255,255,255, 0))
        draw = ImageDraw.Draw(tile_image)
        legend = Legend()
        processed_pixel_count = 0
        for pixel in temp_measurements:
            color_str = legend.get_color_str(pixel.value)
            self.assertTrue(color_str == "hsl(0,100%,50%)")

            # pixel x, y expected to be in spherical-mercator
            # attempt to transform, note if srid is not defined this will generate an error
            if pixel.location.srid != SPHERICAL_MERCATOR_SRID:
                pixel.location.transform(SPHERICAL_MERCATOR_SRID)

            # adjust to upper-left/nw
            upperleft_point = pixel.location
            # (xmin, ymin, xmax, ymax)
            sphericalmercator_bbox = (upperleft_point.x ,
                                      upperleft_point.y - pixel_size_meters,
                                      upperleft_point.x + pixel_size_meters,
                                      upperleft_point.y)
            # transform pixel spherical-mercator coords to image pixel coords
            # --> min values
            xmin, ymin = sphericalmercator_bbox[:2]
            pxmin, pymin = rtmgr.sphericalmercator_to_pixel(zoom, tilex, tiley, xmin, ymin)
            #debug
            print("Minpixel sm({}, {}) pixel({}, {})".format(xmin, ymin,
                                                             pxmin, pymin))

            # --> max values
            xmax, ymax = sphericalmercator_bbox[2:]
            pxmax, pymax = rtmgr.sphericalmercator_to_pixel(zoom, tilex, tiley, xmax, ymax )
            #debug
            print("Maxpixel sm({}, {}) pixel({}, {})".format(xmax, ymax,
                                                             pxmax, pymax))

            pixel_poly_bbox = Polygon.from_bbox((pxmin, pymin, pxmax, pymax))

            # draw pixel on tile
            draw.polygon(pixel_poly_bbox.coords[0], fill=color_str)
            processed_pixel_count += 1
        print("Processed Pixels: {}".format(processed_pixel_count))

        # confirm that half of image is red
        # --> get percentage of image that is red.
        color_counts = tile_image.getcolors()  #
        print(color_counts)