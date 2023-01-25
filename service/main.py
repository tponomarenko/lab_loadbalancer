import os
import sys

from flask import Flask

ALLOWED_COLOURS = {"RED", 'GREEN', "BLUE", "ORANGE", "PINK", "FUCHSIA", "AMBER", "CORAL", "MAROON"}

if "COLOUR" not in os.environ:
    print("Fatal error: environment variable COLOUR is not set.")
    sys.exit(1)

if os.getenv("COLOUR").upper() not in ALLOWED_COLOURS:
    print(f"Fatal error: configured color may be one of {', '.join(ALLOWED_COLOURS)}.")
    sys.exit(1)


app = Flask(__name__)


@app.get("/colour")
def get_colour():
    colour = os.getenv("COLOUR")
    return colour.upper()


app.run("0.0.0.0", 80, debug=False)
