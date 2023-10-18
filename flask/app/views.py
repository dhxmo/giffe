from quart import request, render_template

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
