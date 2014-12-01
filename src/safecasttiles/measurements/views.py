import json
import logging
from collections import OrderedDict
from urllib.parse import urljoin
from io import BytesIO

from django.http import HttpResponse
from django.views.generic import View

from tmstiler.django import DjangoRasterTileLayerManager

from .models import MeasurementLayer, Measurement

SAFECAST_TILELAYER_PREFIX = "/tiles/"  # needs to match urls.py

# Get an instance of a logger
logger = logging.getLogger(__name__)


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
        max_value = 3.99
        min_value = 0.03
        full_range = max_value - min_value
        max_h = 61
        min_h = 246
        color_range = min_h - max_h

        if value > max_value:
            value = max_value
        elif value < min_value:
            value = min_value

        value_percentage = (value - min_value)/full_range
        h = int(color_range - (value_percentage * color_range))
        return "hsl({}, 100%, 50%)".format(h)


class SafecastMeasurementsTileView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # get layer.. should only be one
        mlayer = MeasurementLayer.objects.get(pk=1)

        # create per month layers
        months = Measurement.objects.order_by("date").values_list('date', flat=True).distinct()
        layers = OrderedDict()
        legend = Legend()
        for m in months:
            qs = Measurement.objects.filter(date=m)
            month_layername = m.strftime("%Y%m")
            layers[month_layername] = {
                        "pixel_size": mlayer.pixel_size_meters,  # currently hard-coded in measurements.management.commands.load_safecast_csv
                        "point_position": "upperleft",
                        "model_queryset": qs,
                        "model_point_fieldname": "location",
                        "model_value_fieldname": "value",
                        "legend_instance": legend,  # object with '.get_color_str()' method that returns an rgb() or hsl() color string.
                        }
        self.tilemgr = DjangoRasterTileLayerManager(layers)

    def get(self, request):
        layername, zoom, x, y, image_format = self.tilemgr.parse_url(request.path)
        logger.info("layername({}) zoom({}) x({}) y({}) image_format({})".format(layername, zoom, x, y, image_format))
        mimetype, tile_pil_img_object = self.tilemgr.get_tile(layername, zoom, x, y)
        image_encoding = image_format.replace(".", "")

        # pillow tile_pil_img_object.tobytes() doesn't seem to work, workaround to serve raw bytes via BytesIO()
        image_fileio = BytesIO()
        tile_pil_img_object.save(image_fileio, image_encoding)
        image_fileio.seek(0)
        return HttpResponse(image_fileio, content_type=mimetype)


def get_month_layers(request):
    months = Measurement.objects.order_by("date").values_list('date', flat=True).distinct()
    layers = []
    for m in months:
        month_layername = m.strftime("%Y%m")
        layer_url = urljoin(SAFECAST_TILELAYER_PREFIX, month_layername)
        layer_data = {"url": layer_url, "layername": month_layername, "mapurl": "/index.html"}
        layers.append(layer_data)
    return HttpResponse(json.dumps(layers), content_type="application/json")



