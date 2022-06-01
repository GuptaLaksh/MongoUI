from os import getenv
from .base import *
# you need to set "myproject = 'prod'" as an environment variable
# in your OS (on which your website is hosted)
if getenv('myproject') == 'prod':
    from .prod import *
else:
    from .dev import *
