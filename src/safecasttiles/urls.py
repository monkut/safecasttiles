from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from .measurements.views import SafecastMeasurementsTileView, get_month_layers
urlpatterns = [
    url(r'^layers/$', get_month_layers),
    url(r'^tiles/', SafecastMeasurementsTileView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
