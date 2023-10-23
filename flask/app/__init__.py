from quart import Quart

app = Quart(__name__, template_folder="templates")

from . import views

if __name__ == '__main__':
    app.run(debug=True)
