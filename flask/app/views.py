from quart import request

from . import app
from .giffe import giffer


@app.route('/generate_gif')
async def generate_gif():
    url = request.args.get('url')
    result = await giffer(url)
    return result

