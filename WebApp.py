from distutils.log import debug
from flask import Flask, render_template, redirect
from Process import *
import time, os

app = Flask(__name__)
debug_mode = True

@app.route("/")
def page_home():
    data = get_home()
    return render_template('Home.html')

@app.route("/bat-status")
def page_bat_status():
    return render_template('BAT Status.html')

@app.route("/server-status")
def page_server_status():
    bat1 = get_server_status('bat1', debug_mode=debug_mode)
    bat2 = get_server_status('bat2', debug_mode=debug_mode)
    data = {
        'Tanjung Awar-Awar Unit 1': bat1,
        'Tanjung Awar-Awar Unit 2': bat2
    }
    return render_template('Server Status.html', data = data)

@app.route("/laporan-kemanfaatan")
def page_laporan_kemanfaatan():
    return render_template("Laporan Kemanfaatan - Start.html")

if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)