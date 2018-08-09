# encoding: utf-8

TYR_DIR = "/srv/tyr"

DATA_DIR = "/srv/artemis_data"

CITIES_INPUT_FILE = DATA_DIR + "/france_boundaries.osm.pbf"

DATASET_PATH_LAYOUT = DATA_DIR + "/{dataset}/"

NAV_FILE_PATH_LAYOUT = "/srv/ed/{dataset}/data.nav.lz4"

NEW_FUSIO_FILE_PATH_LAYOUT = "/srv/fusio/source/{dataset}/NAVITIART/databases.zip"

RESPONSE_FILE_PATH = 'output'

REFERENCE_FILE_PATH = 'reference'

API_POINT_PREFIX = ''

KIRIN_API = 'http://localhost:9090'

JORMUNGANDR_DB = 'dbname=jormungandr user=jormungandr host=localhost password=jormungandr'

KIRIN_DB = 'dbname=kirin user=kirin host=localhost password=kirin'

CITIES_DB = 'dbname=cities user=navitia host=localhost password=password'

# Beginning of the URL : we want the request to go to our own Jormun on our own machine
URL_JORMUN = 'http://localhost:9191'

CONTAINER_DATA_INPUT_PATH ='/srv/ed/input'

CONTAINER_DATA_OUTPUT_PATH ='/srv/ed/output'

ARTEMIS_PATH = '/home/louis_gaillet/Projets/Artemis'

TYR_PORT = "9898"
URL_TYR = 'http://localhost'

LOGGER = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters':{
        'default': {
            'format': '[%(asctime)s] [%(levelname)5s] [%(name)25s] %(message)s',
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
        'requests': {
            'handlers': ['default'],
            'level': 'WARN',
            'propagate': True
        },
    }
}
