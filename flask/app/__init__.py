from flask import Flask
from quart import Quart

# app = Flask(__name__)
app = Quart(__name__)

from . import views
