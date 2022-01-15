from threading import Thread

import requests

from flask import Flask
from flask import request

from utils.coding import pack_k

app = Flask(__name__)
# PORTS = [8000, 9000, 10000]
PORTS = []
# mixers = [f"http://127.0.0.1:{port}" for port in PORTS]
mixers = set()  # TODO перевести на List и убедиться что повторений нет. TODO 2: энергонезависимый кэш


@app.route("/get-mixers", methods=['GET'])
def get_mixers():
    print("Get mixers")
    print(mixers)
    return {"servers": list(mixers)}, 200


@app.route("/register", methods=['GET'])
def register():
    a = request.environ['REMOTE_ADDR']
    p = request.environ['REMOTE_PORT']
    # print(a, p)
    # print("DATA", request.json)
    http = "http://"
    addr = http + request.remote_addr
    mixer_port = request.json["port"]
    mixers.add(f"{addr}:{mixer_port}")
    print("ADDED MIXER ------------------------")
    t = Thread(target=notify_all_nodes, daemon=True)
    t.start()
    # notify_all_nodes()



    print("MIXERS:", mixers)
    return "OK", 200


def notify_all_nodes():
    for mixer in mixers:
        print(f"SEND DATA TO {mixer}")
        requests.get(f"{mixer}/new-node-notification")


if __name__ == '__main__':
    app.run(debug=True)
