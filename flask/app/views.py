from datetime import timedelta

from quart import request, render_template, send_from_directory, make_response
from quart_rate_limiter import RateLimiter, rate_limit

from . import app
from .giffe import giffer
from .utils import sanitize_html


rate_limiter = RateLimiter()

@app.route('/')
@rate_limit(1, timedelta(seconds=3))
async def index():
    # response = await render_template('index.html')

    content = await render_template('index.html')
    response = await make_response(content)
    response.headers['Content-Security-Policy'] = "default-src 'self' https://giffe.s3.amazonaws.com/gifs/ https://giffe.s3.ap-south-1.amazonaws.com/share_buttons/ style-src 'self' 'unsafe-inline';"

    return response


@app.route('/generate_gif')
@rate_limit(1, timedelta(seconds=3))
async def generate_gif():
    url = request.args.get('url')

    sanitized_url = sanitize_html(url)

    result = await giffer(sanitized_url)
    return result


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'assets/favicon.ico')


