from quart import Quart

app = Quart(__name__)

from . import views

if __name__ == '__main__':
    app.run()
