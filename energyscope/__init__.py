import logging.config
import logging
import os
import importlib

from .common import commons

# Remove old log file:
for filename in (f for f in os.listdir('.') if f.endswith('.energyscope.log')):
    try:
        os.remove(filename)
    except OSError:
        print('Could not erase previous log file ' + filename)

# Logging: #
_LOGCONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)-8s] (%(funcName)s): %(message)s',
            'datefmt': '%y/%m/%d %H:%M:%S'
        },
        'notime': {
            'format': '[%(levelname)-8s] (%(funcName)s): %(message)s',
            'datefmt': '%y/%m/%d %H:%M:%S'
        },
    },
    "handlers": {
        "console": {
            "class": "energyscope.misc.colorstreamhandler.ColorStreamHandler",
            "stream": "ext://sys.stderr",
            # "stream": "sys.stdout",
            "level": "INFO",
            'formatter': 'notime',
        },

        "error_file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            'formatter': 'standard',
            'filename': commons['logfile'],
            'encoding': 'utf8'

        }
    },

    "root": {
        "level": "INFO",
        "handlers": ["console", "error_file"],
    }
}

# Setting logging configuration:
try:
    logging.config.dictConfig(_LOGCONFIG)
except Exception:
    # if it didn't work, it might be due to ipython messing with the output
    # typical error: Unable to configure handler 'console': IOStream has no fileno
    # try without console output:
    logging.warning('The colored console output is failing (possibly because of ipython). '
                    'Switching to monochromatic output')
    _LOGCONFIG['handlers']['console']['class'] = "logging.StreamHandler"
    logging.config.dictConfig(_LOGCONFIG)


from .energyscope import run_energyscope
from .misc.utils import make_dir
from .preprocessing.print_data import import_data, print_param, newline, print_df, print_set, ampl_syntax, \
    print_estd, print_12td
from .preprocessing.print_run import print_run
from .postprocessing.utils import get_total_cost, get_total_gwp, get_total_einv, get_asset_value
from .postprocessing.draw_sankey.ESSankey import drawSankey
