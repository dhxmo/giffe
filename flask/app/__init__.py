from quart import Quart
from quart_rate_limiter import RateLimiter


app = Quart(__name__, template_folder="templates")
RateLimiter(app)

from . import views


if __name__ == '__main__':
    app.run(debug=True)
