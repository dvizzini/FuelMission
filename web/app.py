import os
from flask import Flask, jsonify, render_template, request
from fuellookup import multi_prices
app = Flask(__name__)


@app.route('/_get_stations')
def get_stations():
    zips = map(int,request.args.getlist('zips[]'))
    return jsonify({'stations':multi_prices(zips)})


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
