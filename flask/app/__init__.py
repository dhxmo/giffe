from quart import Quart

from .views import rate_limiter

app = Quart(__name__, template_folder="templates")
rate_limiter.init_app(app)

from . import views

if __name__ == '__main__':
    app.run(debug=True)
