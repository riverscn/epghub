from apiflask import APIFlask, Schema
from apiflask.fields import String, Date
from flask import send_file
from flask_compress import Compress
import json
import os

app = APIFlask(__name__)
Compress(app)


class ChannelIn(Schema):
    ch = String(required=True)
    date = Date("%Y-%m-%d", required=True)


@app.get("/diyp")
@app.input(ChannelIn, "query")
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
def index():
    return send_file(os.path.join(os.getcwd(), "web", "index.html"))


@app.route("/epg.xml")
def epg_xml():
    return send_file(os.path.join(os.getcwd(), "web", "epg.xml"))


@app.route("/robots.txt")
def robots_txt():
    return send_file(os.path.join(os.getcwd(), "web", "robots.txt"))
