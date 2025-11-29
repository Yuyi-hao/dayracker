import core

app = core.create_app()

@app.route("/")
def hello():
    return "<h1>Hey jean 😍</h1>"