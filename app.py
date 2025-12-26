import core
from core.utils import min_to_time
from flask import render_template
app = core.create_app()

@app.template_filter('min_to_time')
def min_to_time_filter(min: int|float) -> str:
    return min_to_time(min)
                         
@app.route("/")
def hello():
    return render_template("index.html")