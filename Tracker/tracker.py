import requests
from flask import Flask
from flask import request

from utils.coding import pack_k

app = Flask(__name__)
PORTS = [8000, 9000, 10000]
default_mixers = [f"http://127.0.0.1:{port}" for port in PORTS]
mixers = set()  # TODO перевести на List и убедиться что повторений нет. TODO 2: энергонезависимый кэш


@app.route("/get-mixers", methods=['GET'])
def get_mixers():
    print("Get mixers")
    print(mixers)
    return {"servers": list(mixers)}, 200
    # return {"servers": list(mixers)}, 200


@app.route("/register", methods=['GET'])
def register():
    h = "http://"
    address = request.remote_addr
    if h not in address:
        address = h + address
    mixer_port = request.json["port"]
    new_mixer = f"{address}:{mixer_port}"
    notify_all_nodes(existing_mixers=mixers, new_mixer=new_mixer)
    mixers.add(new_mixer)
    print("MIXERS:", mixers)
    return "OK", 200


def notify_all_nodes(existing_mixers, new_mixer):
    union = list(set(list(existing_mixers) + [new_mixer]))
    for mixer in existing_mixers:
        url = f"{mixer}/new-node-notification"
        print(f"SENDING {url} ALL DATA")
        try:
            requests.post(url=url, json={"servers": union})
        except ConnectionError:
            pass


if __name__ == '__main__':
    app.run(debug=True)
