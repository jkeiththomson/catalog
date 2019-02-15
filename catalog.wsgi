#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/catalog/")

from catalog import catalog
application = catalog.app
application.secret_key = 'this_is_my_super_secret_key'
