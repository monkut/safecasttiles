# safecasttiles


A python3 django 1.8 project for generating & serving map tiles from safecast CSV data (http://blog.safecast.org/data/).

Sample image created with tiles rendered with this project:

![Safecast Data 2014-10](https://lh5.googleusercontent.com/8Uj8wENmgpN0s59mmbKqwced4z2WaxcFGK-fRp3kXas=s259-p-no)





## Libraries/Tools


### Required

- tmstiler (https://github.com/monkut/tmstiler)

- django (geodjango) >= 1.8

- postgres/postgis

- leafletjs (include)d

### Optional

- phantomjs (http://phantomjs.org/)
  For image capture

- avconv
  For timelapse video creation

## Loading & Creating Data


The following django management commands are used to load and aggregate the safecast CSV data.

- 'load_safecast_csv'

  - Load & aggregate the safecast CSV data to monthly averages stored in Measurement model objects.

- 'create_ghost_values'

  - Create Measurement objects for locations where measurements currently do NOT exist. (Currently just hold the latest value and fade via the color staturation)


