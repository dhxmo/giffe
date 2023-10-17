from flask import request

from . import app
from .giffe import giffer


@app.route('/giffe', methods=['GET'])
def generate_gif():
    url = request.args.get('url')

    response = giffer(url)

    return response
