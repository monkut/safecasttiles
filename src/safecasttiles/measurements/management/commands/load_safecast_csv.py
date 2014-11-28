"""
Load & process the safecast CSV file
"""
import csv
import gzip
import io
import datetime
from collections import Counter, defaultdict

from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.gdal.error import OGRException
from django.core.management.base import BaseCommand, CommandError
from ...models import Measurement

SPHERICAL_MERCATOR_SRID = 3857 # google maps projection




class Command(BaseCommand):
    help = 'Load & aggregate Safecast CSV data'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--filepath',
                            dest="filepath",
                            required=True,
                            help="Filepath to Safcast CSV file")
        parser.add_argument("-p", "--pixelsize",
                            dest="pixelsize",
                            default=250,
                            type=int,
                            help="Size of pixels/bins in meters [DEFAULT=250]")

    def handle(self, *args, **options):
        filepath = options["filepath"]
        pixelsize = options["pixelsize"]

        day_sum_data = defaultdict(Counter)
        day_counts_data = defaultdict(Counter)

        read_mode = "r"
        open_method = open
        if filepath.endswith(".csv.gz"):
            open_method = gzip.open
            read_mode = "rb"
        start = datetime.datetime.now()
        self.stdout.write(str(start))
        with open_method(filepath, read_mode) as in_csv:
            self.stdout.write("Measurements CSV: {}".format(filepath))
            dreader = csv.DictReader(io.TextIOWrapper(in_csv))
            self.stdout.write("Aggregating CSV values...")
            for row in dreader:
                if row and row["Longitude"] and row["Latitude"]:
                    lng = float(row["Longitude"])
                    lat = float(row["Latitude"])
                    if not (-90 <= lat <= 90):
                        # values added incorrectly, invert
                        p = Point(lat, lng, srid=4326)
                    else:
                        p = Point(lng, lat, srid=4326)
                    try:
                        p.transform(SPHERICAL_MERCATOR_SRID)
                    except OGRException as e:
                        # bin to upper-left
                        self.stderr.write("Unable to transform: {}".format(p.ewkt))
                        continue
                    binned_x = p.x - (p.x % pixelsize)  # shift left
                    binned_y = p.y + (pixelsize - (p.y % pixelsize))  # shift up
                    binned_p = Point(binned_x, binned_y, srid=SPHERICAL_MERCATOR_SRID)
                    dt =  datetime.datetime.strptime(row["Captured Time"], "%Y-%m-%d %H:%M:%S")
                    # skip values defined in the future
                    if dt.year > start.year:
                        self.stderr.write("Invalid date({}), skipping!".format(row["Captured Time"]))
                        continue
                    date_key = dt.strftime("%Y-%m")
                    if row["Unit"] == "cpm":
                        if row["Value"]:
                            day_sum_data[date_key][binned_p.ewkt] += int(float(row["Value"]))
                            day_counts_data[date_key][binned_p.ewkt] += 1
                    else:
                        self.stderr.write("Warning -- Unknown units: {}".format(row["Unit"]))

        # once counts are aggregated per bin create & commit Measurement instances
        self.stdout.write("Committing values...")
        for date_key in day_sum_data:
            measurements = []
            try:
                d = datetime.datetime.strptime(date_key, "%Y-%m").date()
            except ValueError:
                self.stderr.write("Unable to parse date_key('{}'), skipping".format(date_key))
                continue
            for ewkt_key in day_sum_data[date_key]:
                counts = day_counts_data[date_key][ewkt_key]
                result = day_sum_data[date_key][ewkt_key]/counts
                m = Measurement(location=GEOSGeometry(ewkt_key),
                                date=d,
                                counts=counts,
                                value=result,
                                )
                measurements.append(m)
            self.stdout.write("Committing values for ({})...".format(date_key))
            Measurement.objects.bulk_create(measurements)
        end = datetime.datetime.now()
        elapsed = end - start
        self.stdout.write("Elapsed Time: {}".format(elapsed))


