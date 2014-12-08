safecasttiles
=============

A python3 django 1.8 project for generating & serving map tiles from safecast CSV data (http://blog.safecast.org/data/).

Sample timelapse created with tiles rendered with this project:

https://plus.google.com/u/0/114056874915345387620/posts/YkUsdcvejXY?pid=6088998041645036706&oid=114056874915345387620


Libraries/Tools
-------------------

Required
.............

- tmstiler (https://github.com/monkut/tmstiles)

- django (geodjango) >= 1.8

- postgres/postgis

- leafletjs (include)d

Optional
..............

- phantomjs (http://phantomjs.org/)
  For image capture

- avconv
  For timelapse video creation

Loading & Creating Data
-------------------------------

The following django management commands are used to load and aggregate the safecast CSV data.

- 'load_safecast_csv'

  - Load & aggregate the safecast CSV data to monthly averages stored in Measurement model objects.

- 'create_ghost_values'

  - Create Measurement objects for locations where measurements currently do NOT exist. (Currently just hold the latest value and fade via the color staturation)


