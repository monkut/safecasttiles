"""
Create ghosting values.
Create Measurement objects for locations where measurements currently do NOT exist.
Currently just hold the latest value and fade via the alpha
"""
from django.contrib.gis.geos import Polygon
from django.core.management.base import BaseCommand, CommandError
from ...models import MeasurementLayer, Measurement

__author__ = 'q16127'

SPHERICAL_MERCATOR_SRID = 3857 # google maps projection

DEFAULT_DEPTH = 6

class Command(BaseCommand):
    help = 'Load & aggregate Safecast CSV data'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--depth',
                            dest="depth",
                            required=True,
                            type=int,
                            default=DEFAULT_DEPTH,
                            help="How many past months to allow as 'ghost' values [DEFAULT={}]".format(DEFAULT_DEPTH))
        parser.add_argument("-b", "--bbox",
                            dest="bbox",
                            nargs=4,
                            type=float,
                            default=None,
                            help="(OPTIONAL) If given ghost value creation is limited to given bounding-box area. format: 'minx miny maxx maxy'")
        parser.add_argument("-s", "--srid",
                            dest="srid",
                            type=int,
                            default=4326,
                            help="(OPTIONAL) SRID for optional bbox [DEFAULT=4326]")

    def handle(self, *args, **options):
        depth = options["depth"]
        bbox = options["bbox"]
        srid = options["srid"]
        bbox_poly = None
        if bbox:
            bbox_poly = Polygon.from_bbox(bbox)
            bbox_poly.srid = srid
            if srid != SPHERICAL_MERCATOR_SRID:
                bbox_poly.transform(SPHERICAL_MERCATOR_SRID)

        # get measurements by month
        months = Measurement.objects.order_by("date").values_list('date', flat=True).distinct()

        prevous_month_measurements = {}
        for m in months:
            monthly_measurements = Measurement.objects.filter(date=m)
            if bbox_poly:
                # apply bbox filter
                kwargs = {"location__within": bbox_poly, }
                monthly_measurements.filter(**kwargs)
            if not prevous_month_measurements:
                for measurement in monthly_measurements:
                    location_key = measurement.location.ewkt
                    prevous_month_measurements[location_key] = measurement
            else:
                ghost_measurements_created = 0
                # get values from previous month which are not in current
                current_measurements = { m.location.ewkt: m for m in monthly_measurements}
                for previous_measurement_location in prevous_month_measurements:
                    if previous_measurement_location not in current_measurements:
                        # check depth, update date, increment months_to_actual
                        previous_measurement = prevous_month_measurements[previous_measurement_location]
                        if previous_measurement.months_to_actual <= depth:
                            previous_measurement.date = m
                            previous_measurement.months_to_actual += 1
                            previous_measurement.save(force_insert=True)
                            # add to current measurements
                            current_measurements[previous_measurement_location] = previous_measurement
                            ghost_measurements_created += 1
                self.stdout.write("{} created: {}".format(m,
                                                          ghost_measurements_created))
                prevous_month_measurements = current_measurements.copy()




