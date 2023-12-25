from apiflask import APIFlask, Schema, EmptySchema
from apiflask.fields import String, Date, List, Nested
from flask import send_file
from flask_compress import Compress
import json
import os

app = APIFlask(__name__)
Compress(app)


class ChannelIn(Schema):
    ch = String(required=True)
    date = Date("%Y-%m-%d", required=True)

class ChannelOut(Schema):
    class EpgData(Schema):
        start = String()
        end = String()
        title = String()
        desc = String()
    channel_name = String()
    date = String()
    epg_data = List(Nested(EpgData))

@app.get("/diyp")
@app.input(ChannelIn, "query")
@app.output(ChannelOut)
def diyp(query_data):
    # Read file web/diyp_files/{ch}/{date}.json and return json content
    ch = query_data["ch"]
    date = query_data["date"]
    try:
        with open(
            os.path.join(
                os.getcwd(),
                "web",
                "diyp_files",
                ch,
                date.strftime("%Y-%m-%d") + ".json",
            ),
            "r",
        ) as f:
            return json.load(f)
    # If file not found, return templates/404.json (replace channel_name and date)
    except FileNotFoundError:
        with open(os.path.join(os.getcwd(), "templates", "404.json"), "r") as f:
            json_404 = json.load(f)
        json_404["channel_name"] = ch
        json_404["date"] = date.strftime("%Y-%m-%d")
        return json_404


@app.route("/")
@app.output(EmptySchema, content_type="text/html")
@app.doc(hide=True)
def index():
    return send_file(os.path.join(os.getcwd(), "web", "index.html"))


@app.route("/epg.xml")
@app.output(EmptySchema, content_type="application/xml")
@app.doc(hide=True)
def epg_xml():
    return send_file(os.path.join(os.getcwd(), "web", "epg.xml"))


@app.route("/robots.txt")
@app.output(EmptySchema, content_type="text/plain")
@app.doc(hide=True)
def robots_txt():
    return send_file(os.path.join(os.getcwd(), "web", "robots.txt"))
