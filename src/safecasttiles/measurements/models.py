from colorsys import rgb_to_hls, hls_to_rgb
from django.contrib.gis.db import models

SPHERICAL_MERCATOR_SRID = 3857 # google maps projection

class MeasurementLayer(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True)
    source_filepath = models.FilePathField()
    pixel_size_meters = models.PositiveIntegerField()


class Measurement(models.Model):
    layer = models.ForeignKey(MeasurementLayer,
                              null=True,
                              default=None,)  # new migrations doesn't seem to like foreign key fields without a default value
    location = models.PointField(srid=SPHERICAL_MERCATOR_SRID)
    date = models.DateField()
    counts = models.IntegerField()
    months_to_actual = models.PositiveIntegerField(default=0,
                                                   help_text="Number of months since an actual value was here (0 if actual")
    value = models.FloatField()
    objects = models.GeoManager()


class ScaledFloatLegend(models.Model):
    """
    Intended to provide a scaled legend for pciopt and kpi bin maps
    """
    name = models.CharField(max_length=150,
                            unique=True,
                            help_text="kpi name that the legend represents")
    hex_min_color = models.CharField(max_length=6,
                                     default="66b219", # yellow
                                     help_text=u"Color in HEX RGB (e.g. AABBCC) for the color to apply to the min value")
    hex_max_color = models.CharField(max_length=6,
                                     default="1900FF", # blue
                                     help_text=u"Color in HEX RGB (e.g. AABBCC) for the color to apply to the max value")
    display_band_count = models.SmallIntegerField(default=6,
                                                  help_text=u"Number of color bands to display in HTML legend",)
    minimum_value = models.FloatField()
    maximum_value = models.FloatField()


    def get_rgb_tuple(self, color):
        """
        :param color: hex string of RGB color, ex: 'FFFFFF'
        :returns: tuple of RGB color as integers between 0-255, ex: (255, 255, 255)

        Convert hex string value to tuple of ints
        'FFFFFF' --> (255, 255, 255)
        """
        assert len(self.hex_min_color) == 6
        assert len(self.hex_max_color) == 6
        color_tuple = []
        for idx in range(0, 6, 2):
            #color_tuple.append(self.hex_min_color[idx: idx+2])
            color_tuple.append(int(color[idx: idx+2], 16))
        return tuple(color_tuple)

    def get_color_str(self, model_instance, value):
        return self.value_to_hsl(value, as_str=True)

    def value_to_hsl(self, value, as_str=False):
        """
        :param value: float value to convert to HSL color
        :param as_str: Toggle to force resulting HSL color as a string in the form  'hsl({}, {}%, {}%)'
        :type as_str: bool
        :returns: HSL color as tuple or string

        Convert the given value to the appropriate color
        resulting color is represented in HSL (not rgb)
        """
        if value < self.minimum_value:
            value = self.minimum_value
        elif value > self.maximum_value:
            value = self.maximum_value

        if self.minimum_value < 0:
            offset = abs(self.minimum_value)
            minimum_value = self.minimum_value + offset
            maximum_value = self.maximum_value + offset
            value = value + offset
        else:
            minimum_value = self.minimum_value
            maximum_value = self.maximum_value

        scale = float(value - minimum_value) / float(maximum_value - minimum_value)

        # scale all channels linearly between START_COLOR and END_COLOR
        start_rgb = self.get_rgb_tuple(self.hex_min_color)
        end_rgb = self.get_rgb_tuple(self.hex_max_color)

        # convert rgb to hsl
        # --> put rgb values on scale between 0, and 1 for usage with colorsys conversion functions
        # results in values 0-1 for all (h,l,s)
        start_hls = rgb_to_hls(*[v/255.0 for v in start_rgb])
        end_hls = rgb_to_hls(*[v/255.0 for v in end_rgb])

        h, l, s = [float(scale * (end-start) + start) for start, end in zip(start_hls, end_hls)]

        # adjust to expected scales 0-360, 0-100, 0-100
        h *= 360
        l *= 100
        s *= 100

        assert 0 <= h <= 360
        assert 0 <= l <= 100
        assert 0 <= s <= 100
        hsl_color = (int(h), int(s), int(l))
        if as_str:
            hsl_color = "hsl({}, {}%, {}%)".format(*hsl_color)
        return hsl_color

    def value_to_rgb(self, value, htmlhex=False, max_rgb_value=255):
        """
        :param value: float value to convert to RGB color
        :param htmlhex: toggle to return value as html formatted hex, ex: '#FFFFFF'
        :returns: RGB color as tuple or string

        convert the given float value to rgb color
        """
        # flooring value to the limits of the legend
        if value < self.minimum_value:
            value = self.minimum_value
        elif value > self.maximum_value:
            value = self.maximum_value

        # hsl is used because it is easier to 'rotate' evenly to another color on the spectrum
        h, s, l = self.value_to_hsl(value)
        # adjust range to be from 0 to 1 change to hls for use with hls_to_rgb()
        hls = (h/360.0, l/100.0, s/100.0)

        # covert to rgb
        if max_rgb_value == 255:
            # --> adjust values from 0 to 1, to 0 to 255
            rgb = [int(i * 255) for i in hls_to_rgb(*hls)]
        else:
            rgb= hls_to_rgb(*hls)

        if htmlhex:
            rgb = "#" + "".join("{:02x}".format(i) for i in rgb)
        return rgb

    def html(self, invert=True):
        """
        :param invert: toggle to invert, so that larger values are on top
        :type invert: bool
        :returns: html legend snippet for leaflet map display

        Create the html needed for leaflet.js legend display
        reference:
        http://leafletjs.com/examples/choropleth.html
        """
        div_innerHTML = []
        band_count = self.display_band_count - 1  # adjust to n-1 (last MAX value added automatically

        full_range = self.maximum_value - self.minimum_value
        step = full_range / band_count
        for i in range(int(band_count)):
            current_value = self.minimum_value + (i * step)
            next_value = current_value + step
            color_str = self.value_to_rgb(current_value, htmlhex=True)
            # dash, "-": &ndash;
            # tilde, "~": &#126;
            grade_html = '''<i style="background:{rgb}"></i>{value} &#126; {next}<br>'''.format(rgb=color_str,
                                                                                                value=round(current_value, 2),
                                                                                                next=round(next_value, 2))
            div_innerHTML.append(grade_html)
        # add the last maximum value
        color_str = self.value_to_rgb(self.maximum_value, htmlhex=True)
        grade_html = '''<i style="background:{rgb}"></i>{value} +<br>'''.format(rgb=color_str,
                                                                                value=round(self.maximum_value, 2))
        div_innerHTML.append(grade_html)
        if invert:
            div_innerHTML = list(reversed(div_innerHTML))
        return "".join(div_innerHTML)