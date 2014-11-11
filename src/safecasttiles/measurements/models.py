from django.contrib.gis.db import models

SPHERICAL_MERCATOR_SRID = 3857 # google maps projection

class Measurement(models.Model):
    location = models.PointField(srid=SPHERICAL_MERCATOR_SRID)
    date = models.DateField()
    counts = models.IntegerField()
    value = models.FloatField()
    objects = models.GeoManager()
