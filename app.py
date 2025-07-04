from flask import Flask, request, redirect

from lego_crypt import Crypt
import mln

app = Flask(__name__)

def generate_body(session_id, username): return f"""
<root>
    <username>{'' if username is None else username}</username>
    <token>Test</token>
    <data>
        <mylegobadge>1</mylegobadge>
        <level levelnumber="1">
            <score>0</score>
            <medals>0</medals>
        </level>
        <totalscore>0</totalscore>
        <currentrank>1</currentrank>
        <levelsunlocked>0</levelsunlocked>
        <loginurl>{mln.get_login_url(session_id)}</loginurl>
        <legowebsiteurl></legowebsiteurl>
        <getbadgeurl>{mln.MLN_MAILBOX_URL}</getbadgeurl>
    </data>
</root>
"""

def encrypt_body(body):
    return Crypt.f_encrypt(body, Crypt.S_ENCRYPTION_KEY1)

@app.route("/InfoRequest.xml", methods=["POST"])
def info_request():
    session_id = request.cookies.get("sessionid")
    username = mln.SESSION_TO_USERNAME.get(session_id)
    body = generate_body(session_id, username)
    encrypted_body = encrypt_body(body)
    return (f'''
<?xml version="1.0" encoding="utf-8"?>
<string xmlns="http://www.lego.com/Services.HiScore/service">{encrypted_body}</string>
''')

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

@app.route("/api/login")
def on_mln_login():
    mln.on_login(**request.args)
    return redirect("/")
