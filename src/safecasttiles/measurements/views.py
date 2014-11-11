from collections import OrderedDict

from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.cache import cache_page


from tmstiler.django import DjangoRasterTileLayerManager

from .models import Measurement

class Legend:

    def get_hsl_color(self, value):
        pass

class SafecastMeasurementsTileView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # create per month layers
        months = Measurement.objects.order_by("date").values_list('date', flat=True).distinct()
        layers = OrderedDict()
        legend = Legend()
        for m in months:
            qs = Measurement.objects.filter(date=m)
            layers[m] = {
                        "pixel_size": 250, # currently hard-coded in load_safecast_csv
                        "point_position": "upperleft",
                        "model_queryset": qs,
                        "model_point_fieldname": "location",
                        "model_value_fieldname": "value",
                        "legend_instance": legend,
                        }
        self.tilemgr = DjangoRasterTileLayerManager(layers)

    @cache_page(60 * 120) # go ahead and cache for 2 hrs
    def get(self, request):
        layername, zoom, x, y, image_format = self.tilemgr.parse_url(request.path)
        mimetype, tile_pil_img_object = self.tilemgr.get_tile(layername, zoom, x, y)
        image_encoding = image_format.replace(".", "")
        return HttpResponse(tile_pil_img_object.tobytes(encoder_name=image_encoding), content_type=mimetype)

