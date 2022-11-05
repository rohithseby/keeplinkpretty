from flask import Flask
from threading import Thread
from datetime import datetime

app = Flask("")


@app.route("/")
def home():
    return "server up and running" + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


def run():
    app.run(host="0.0.0.0", port=8080)


def keepalive():
    t = Thread(target=run)
    t.start()
