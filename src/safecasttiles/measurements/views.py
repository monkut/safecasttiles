import json
from collections import OrderedDict
from urllib.parse import urljoin

from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.cache import cache_page


from tmstiler.django import DjangoRasterTileLayerManager

from .models import Measurement

SAFECAST_TILELAYER_PREFIX = "/tiles/"  # needs to match urls.py

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


class SafecastMeasurementsTileView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # create per month layers
        months = Measurement.objects.order_by("date").values_list('date', flat=True).distinct()
        layers = OrderedDict()
        legend = Legend()
        for m in months:
            qs = Measurement.objects.filter(date=m)
            month_layername = m.strftime("%Y%m")
            layers[month_layername] = {
                        "pixel_size": 250,  # currently hard-coded in measurements.management.commands.load_safecast_csv
                        "point_position": "upperleft",
                        "model_queryset": qs,
                        "model_point_fieldname": "location",
                        "model_value_fieldname": "value",
                        "legend_instance": legend,  # returns a hslcolor_str
                        }
        self.tilemgr = DjangoRasterTileLayerManager(layers)

    def get(self, request):
        layername, zoom, x, y, image_format = self.tilemgr.parse_url(request.path)
        mimetype, tile_pil_img_object = self.tilemgr.get_tile(layername, zoom, x, y)
        image_encoding = image_format.replace(".", "")
        return HttpResponse(tile_pil_img_object.tobytes(encoder_name=image_encoding), content_type=mimetype)


def get_month_layers(request):
    months = Measurement.objects.order_by("date").values_list('date', flat=True).distinct()
    layers = []
    for m in months:
        month_layername = m.strftime("%Y%m")
        layer_url = urljoin(SAFECAST_TILELAYER_PREFIX, month_layername)
        layers.append(layer_url)
    return HttpResponse(json.dumps(layers), content_type="application/json")



