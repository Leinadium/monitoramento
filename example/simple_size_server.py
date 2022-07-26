from flask import Flask, jsonify
from shutil import disk_usage

app = Flask(__name__)


@app.route("/teste")
def teste():
    total, used, _ = disk_usage("/")
    porcentagem = used / total

    return jsonify({'porcentagem': porcentagem})


if __name__ == "__main__":
    app.run(port=5000)
