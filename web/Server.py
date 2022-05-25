from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
import pandas as pd

import goalprog as gp

app = Flask(__name__)
app.static_folder = 'static'

@app.route('/', methods=['GET'])
def home():
    data = {
        "title": "Project Goal Programming"
    }

    return render_template('index.html', **data)

@app.route('/testing', methods=['GET'])
def result():
    return render_template('result.html', title="hellow orld")

@app.route('/upload', methods=['POST'])
def upload():
    req_data_client = request.files.get("client_data")
    req_data_driver = request.files.get("driver_data")
    req_data_banned = request.files.get("banned_data")

    clients_data = pd.read_csv(req_data_client)
    drivers_data = pd.read_csv(req_data_driver)

    banned_data = None

    if req_data_banned is not None:
        banned_data = pd.read_csv(req_data_banned)

    raw, result = gp.match(clients_data, drivers_data, banned_data)

    drivers = drivers_data[0:20]['id'].to_list()
    clients = clients_data[0:20]['id'].to_list()

    # Ambilnya table[driver_id][client_id]
    table = result.to_dict('index')

    data = []
    for d in drivers:
        for c in clients:
            if result.loc[d][c] == 1.0:
                data.append({"client": c, "driver": d, **raw[d][c]})
            
    data = {
        "result": table,
        "data": data,

        "drivers": drivers,
        "clients": clients,

        "title": "Result",
    }

    return render_template('result.html', **data)

if __name__ == '__main__':
    load_dotenv(override=True)
    app.run(debug=True)