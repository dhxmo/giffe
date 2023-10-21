from quart import request, render_template, send_from_directory

from . import app
from .giffe import giffer


@app.route('/')
async def index():
    return await render_template('index.html')


@app.route('/generate_gif')
async def generate_gif():
    url = request.args.get('url')
    result = await giffer(url)
    return result


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'assets/favicon.ico')
