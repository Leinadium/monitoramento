from flask import Flask, jsonify
from shutil import disk_usage
from random import uniform

app = Flask(__name__)


@app.route("/teste")
def teste():
    total, used, _ = disk_usage("/")
    porcentagem = used / total

    return jsonify({'porcentagem': uniform(0, 1)})  # testando valor aleatorio
    # return jsonify({'porcentagem': 0.91})         # testando valor fixo
    # return jsonify({'porcentagem': porcentagem})  # testando valor verdadeiro


if __name__ == "__main__":
    from os import environ
    # environ['FLASK_ENV'] = 'development'
    app.run(host='0.0.0.0', port=5000, debug=False)
