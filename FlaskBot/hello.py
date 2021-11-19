from flask import Flask, request

from Protocol.field_type import MessageType, Field

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# bytes_to_b64(PUBLIC_KEY.encode()
@app.route("/public-key", methods=['POST'])
def get_public_key():
    body = request.get_json(force=True, silent=False, cache=True)
    sender_pub_k = body[Field.sender_public_key]
    response = {"public_key": 1,
                "encoding": "base64"}
    return response


@app.route("/message", methods=['POST'])
def post_message():
    body = request.get_json(force=True, silent=False, cache=True)
    print(body)
    return body["hi"]


if __name__ == "__main__":
    app.run()