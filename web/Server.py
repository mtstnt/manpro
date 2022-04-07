from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
import pandas as pd

import goalprog as gp

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    data = {
        "title": "Project Goal Programming"
    }

    return render_template('index.html', **data)

@app.route('/upload', methods=['POST'])
def upload():
    req_data_client = request.files.get("client_data")
    req_data_driver = request.files.get("driver_data")

    clients_data = pd.read_csv(req_data_client)
    drivers_data = pd.read_csv(req_data_driver)

    result = gp.match(clients_data, drivers_data)

    data = {
        "clients_data": clients_data,
        "drivers_data": drivers_data,
        "result": result
    }

    return render_template('result.html', **data)

if __name__ == '__main__':
    load_dotenv(override=True)
    app.run(debug=True)