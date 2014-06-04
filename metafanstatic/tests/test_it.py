# -*- coding:utf-8 -*-
from korpokkur.testing import file_structure_from_dict
import os.path
import shutil
here = os.path.dirname(os.path.abspath(__name__))
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

candidates = ["js", "package"]

for c in candidates:
    if os.path.exists(os.path.join(here, c)):
        shutil.rmtree(os.path.join(here, c))

bower_json = """{
  "name": "sample",
  "version": "0.0.1",
  "description": "sample-package",
  "main": ["dist/sample.js"]
}
"""

file_structure = {
    "package": {},
    "js": {
        "bootstrap-datepicker": {
            "main.js": "/*main*/",
        },
        "bootstrap": {
            "dist": {
                "bootstrap.js": "/*bootstrap.js*/",
                "bootstrap.min.js": "/*bootstrap.min.js*/",
                "bootstrap.css": "/* css */"
            },
        },
        "jquery": {
            "dist": {
                "jquery.js": "/*jquery.js*/",
                "jquery.min.js": "/*jquery.min.js*/"
            }
        },
        "underscore": {
            "dist": {
                "underscore.js": "/*underscore.js*/",
                "underscore.min.js": "/*underscore.min.js*/"
            }
        }
    }
}


file_structure_from_dict(here, file_structure)


from metafanstatic.complement import TotalComplement
from configless import Configurator
from metafanstatic.generating import Generating

params = {
    "jquery": {
        "name": "jquery",
        "version": "0.0.1",
        "description": "jquery-package",
        "bower_directory": os.path.join(here, "js", "jquery"),
        "main": ["dist/jquery.js"]
    },
    "underscore": {
        "name": "underscore",
        "version": "0.0.1",
        "description": "underscore-package",
        "bower_directory": os.path.join(here, "js", "underscore"),
        "main": "dist/underscore.js"
    },
    "bootstrap": {
        "name": "bootstrap",
        "version": "0.0.1",
        "description": "bootstrap-package",
        "main": ["dist/bootstrap.js", "dist/bootstrap.css"],
        "bower_directory": os.path.join(here, "js", "bootstrap"),
        "dependencies": {"jquery": "0.0.1"}
    },
    "bootstrap-datepicker": {
        "name": "bootstrap-datepicker",
        "version": "0.0.1",
        "description": "bootstrap-datepicker-package",
        "main": ["main.js"],
        "bower_directory": os.path.join(here, "js", "bootstrap-datepicker"),
        "dependencies": {"bootstrap": "0.0.1", "underscore": "0.0.1"}
    }
}

bowerpath = os.path.join(here, "js")
complement = TotalComplement()
complement.complement(params)

config = Configurator({
    "entry_points_name": "korpokkur.scaffold",
    "input.prompt": "{word}?"
})

generating = Generating(config)
for c in params["total"]["pro"]:
    generating.generate(params[c], os.path.join(here, "package"))

