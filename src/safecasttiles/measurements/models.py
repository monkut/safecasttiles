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
