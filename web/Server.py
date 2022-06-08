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

    print(req_data_banned)

    clients_data = pd.read_csv(req_data_client)
    drivers_data = pd.read_csv(req_data_driver)

    clients_data = clients_data[0:20]
    drivers_data = drivers_data[0:20]

    if request.files['banned_data'].filename == '':
        banned_data = None
    else: 
        banned_data = pd.read_csv(req_data_banned)

    raw, result = gp.match(clients_data, drivers_data, banned_data)

    drivers = drivers_data['id'].to_list()
    clients = clients_data['id'].to_list()

    # Ambilnya table[driver_id][client_id]
    table = result.to_dict('index')

    print(table)

    data = []
    for d in drivers:
        for c in clients:
            if result.loc[d][c] == 1.0:
                data.append({"client": c, "driver": d, **raw[d][c]})

    # Dump to csv file, assuming run dengan runweb.sh
    result.to_excel('./static/results.xlsx')
            
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