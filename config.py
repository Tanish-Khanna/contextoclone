import os

WINNING_TOLERANCE = .0001

# Determines if Flask should run in debug mode. Defaults to False if the
# environment variable is not set.
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true", "yes")
