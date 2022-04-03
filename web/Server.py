from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('Home.html')

@app.route('/client', methods=['GET', 'POST'])
def client():
    if request.method == 'POST':
        req_data_client = request.files.get("csvfile")
        result_client = pd.read_csv(req_data_client)
        return render_template('data.html', data=result_client)

# @app.route('/driver', methods=['GET', 'POST'])
# def client():
#     if request.method == 'POST':
#         req_data = request.files.get("csvfile")
#         result = pd.read_csv(req_data)
#         return render_template('data.html', data=result)

if __name__ == '__main__':
    app.run(debug=True)