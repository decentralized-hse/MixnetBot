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
    h = "http://"
    address = request.remote_addr
    if h not in address:
        address = h + address
    p = request.environ['REMOTE_PORT']
    # print(a, p)
    # print("DATA", request.json)
    mixer_port = request.json["port"]
    notify_all_nodes()
    mixers.add(f"{address}:{mixer_port}")
    # [requests.get(f"{mixer}/new-node-notification") for mixer in mixers]
    print("MIXERS:", mixers)
    return "OK", 200


def notify_all_nodes():
    for mixer in mixers:
        print(mixers)
        url = f"{mixer}/new-node-notification"
        print(f"SENDING {url} ALL DATA")
        # requests.post(url=url,
        data = {"servers": list(mixers)}
        requests.post(url=url)
    # requests.post(url=first_node, data=data)


if __name__ == '__main__':
    app.run(debug=True)
