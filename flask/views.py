from . import app
from .main import giffer
from flask import request


@app.route('/giffe', methods=['GET'])
def generate_gif():
    url = request.args.get('url')
    
    giffer(url)

    return "GIF generated successfully"  # Replace with the actual response