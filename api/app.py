from apiflask import APIFlask, Schema
from apiflask.fields import String, Date
from flask import send_file
from flask_compress import Compress
import os

app = APIFlask(__name__, docs_path=None)
Compress(app)


class ChannelIn(Schema):
    ch = String(required=True)
    date = Date("%Y-%m-%d", required=True)


@app.route("/diyp")
@app.input(ChannelIn, "query")
def diyp(query_data):
    ch = query_data["ch"]
    date = query_data["date"]
    try:
        return send_file(
            os.path.join(
                os.getcwd(),
                "web",
                "diyp_files",
                ch,
                date.strftime("%Y-%m-%d") + ".json",
            )
        )
    except FileNotFoundError:
        return send_file(os.path.join(os.getcwd(), "templates", "404.json"))


@app.route("/")
def index():
    return send_file(os.path.join(os.getcwd(), "web", "index.html"))


@app.route("/epg.xml")
def epg_xml():
    return send_file(os.path.join(os.getcwd(), "web", "epg.xml"))


@app.route("/robots.txt")
def robots_txt():
    return send_file(os.path.join(os.getcwd(), "web", "robots.txt"))
