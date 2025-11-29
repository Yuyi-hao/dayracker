import core
from flask import render_template
app = core.create_app()

@app.route("/")
def hello():
    return render_template("index.html")