from flask import Flask, request
from lego_crypt import Crypt

app = Flask(__name__)

body = """
<root>
    <username>Blah Blah Blah</username>
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
        <loginurl></loginurl>
        <legowebsiteurl></legowebsiteurl>
        <getbadgeurl></getbadgeurl>
    </data>
</root>
"""

encrypted_body = Crypt.f_encrypt(body, Crypt.S_ENCRYPTION_KEY1)

@app.route("/InfoRequest.xml", methods=["POST"])
def info_request():
    print(Crypt.f_decrypt(request.form["_Body"]))
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

@app.route("/Launcher.html")
def launcher():
    return app.send_static_file("Launcher.html")

@app.route("/LegoCoastGuards.swf")
def legocoastguards():
    return app.send_static_file("LegoCoastGuards.swf")

@app.route("/loader.swf")
def loader():
    return app.send_static_file("loader.swf")
