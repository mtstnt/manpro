from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
import pandas as pd

import goalprog as gp

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

def upload():
    req_data_client = request.files.get("client_data")
    req_data_driver = request.files.get("driver_data")
    clients_data = pd.read_csv(req_data_client)
    drivers_data = pd.read_csv(req_data_driver)
    print(gp.match(clients_data, drivers_data))
    return redirect('/')

# @app.route('/driver', methods=['GET', 'POST'])
# def client():
#     if request.method == 'POST':
#         req_data = request.files.get("csvfile")
#         result = pd.read_csv(req_data)
#         return render_template('data.html', data=result)

if __name__ == '__main__':
    load_dotenv(override=True)
    app.run(debug=True)