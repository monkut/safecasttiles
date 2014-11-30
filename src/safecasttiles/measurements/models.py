from django.contrib.gis.db import models

SPHERICAL_MERCATOR_SRID = 3857 # google maps projection

class MeasurementLayer(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True)
    source_filepath = models.FilePathField()
    pixel_size_meters = models.PositiveIntegerField()


class Measurement(models.Model):
    layer = models.ForeignKey(MeasurementLayer)
    location = models.PointField(srid=SPHERICAL_MERCATOR_SRID)
    date = models.DateField()
    counts = models.IntegerField()
    value = models.FloatField()
    objects = models.GeoManager()
