from quart import Quart

from .views import rate_limiter

app = Quart(__name__, template_folder="templates")

from . import views

rate_limiter.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
