from flask import Flask, flash, render_template, redirect, request
from Process import *
import time, os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
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

@app.route("/laporan-kemanfaatan", methods=['GET', 'POST'])
def page_laporan_kemanfaatan():
    data_requests = dict(request.args)
    if data_requests == {}:
        home = {}
    else:
        home = get_laporan_kemanfaatan(data_requests)
    print(home)
    return render_template("Laporan Kemanfaatan - Start.html", home = home)

@app.route("/input-gangguan")
def page_input_gangguan():
    data_requests = dict(request.args)
    if data_requests == {}:
        ret = {}
        tipe_gangguan = get_tipe_gangguan()
    else:
        ret = post_input_gangguan(data_requests)
        flash(ret['message'])
        return redirect("/input-gangguan")
    return render_template("Input Gangguan.html", tipe_gangguan = tipe_gangguan, data = ret)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)