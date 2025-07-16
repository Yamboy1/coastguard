import uuid

from flask import Flask, g, make_response, redirect, request
from lxml import etree
from lxml.builder import E
from lxml.etree import Element

import db
import mln
import api
from lego_crypt import Crypt

app = Flask(__name__)
db.init_app(app)


def encrypt_body(body):
    return Crypt.f_encrypt(body, Crypt.S_ENCRYPTION_KEY1)


def encrypted_response(xml_string: str):
    encrypted_string = Crypt.f_encrypt(xml_string, Crypt.S_ENCRYPTION_KEY1)

    element = Element(
        "string",
        nsmap={None: "http://www.lego.com/Services.HiScore/service"},
    )
    element.text = encrypted_string

    return etree.tostring(element, encoding="utf-8", xml_declaration=True).decode()


@app.route("/InfoRequest.xml", methods=["POST"])
def info_request():
    # All requests must have the session_id cookie
    session_id = request.cookies.get("session_id")
    if session_id is None:
        res = make_response()
        res.set_cookie("session_id", value=str(uuid.uuid4()))
        return res

    username = mln.SESSION_TO_USERNAME.get(session_id)

    if "_GameName" not in request.form or "_Body" not in request.form:
        return "Missing required form fields", 401

    if request.form["_GameName"] != "CityCoastGuard":
        return "Invalid _GameName field", 402

    decrypted_body = Crypt.f_decrypt(request.form["_Body"])
    print(decrypted_body)
    root = etree.fromstring(decrypted_body)

    if root.tag != "root" or root.get("gamename") != "CityCoastGuard":
        return "Invalid root element", 400

    if not (method := root.get("method")):
        return "Missing method attribute", 400

    match method:
        case "gettoken":
            elements = api.gettoken(session_id, username)
        case "getlinkurls":
            elements = api.getlinkurls(session_id)
        case "getscore":
            elements = api.getscore(username)
        case "savescore":
            elements = api.savescore(session_id, username, root)
        case _:
            return "Invalid method attribute", 400

    root = E.root(gamename="CityCoastGuard", method=method, *elements)
    xml_string = etree.tostring(root, encoding="utf-8", xml_declaration=False).decode()
    print(xml_string)

    return encrypted_response(xml_string)


@app.route("/config.xml")
def config():
    return app.send_static_file("config.xml")


@app.route("/strings.xml")
def strings():
    return app.send_static_file("strings.xml")


@app.route("/index.html")
@app.route("/")
@app.route("/Launcher.html")
def launcher():
    return app.send_static_file("Launcher.html")


@app.route("/LegoCoastGuards.swf")
def legocoastguards():
    return app.send_static_file("LegoCoastGuards.swf")


@app.route("/loader.swf")
def loader():
    return app.send_static_file("loader.swf")


@app.route("/icon")
def icon():
    return app.send_static_file("icon.png")


@app.route("/api/login")
def on_mln_login():
    mln.on_login(**request.args)
    return redirect("/")


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
