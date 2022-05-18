import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os, time
from plotly.subplots import make_subplots
from DBconnector import Database
from helpers import Config, Dummy

DB1 = Database(Config.EngineUnit['tja1'])
DB2 = Database(Config.EngineUnit['tja2'])

def update_home(unit = 'tja1'):
    if unit == 'tja1': DB = DB1
    elif unit == 'tja2': DB = DB2
    else: return

    tags = [DB.efficiency_tag, DB.copt_enable_tag, DB.sopt_enable_tag]
    DF = DB.read_tag(tags, timestart='NOW() - INTERVAL 36 HOUR', timeend='NOW()')
    DF = DF.rename(columns={
        DB.efficiency_tag: 'Efficiency',
        DB.copt_enable_tag: 'COPT Enabled',
        DB.sopt_enable_tag: 'SOPT Enabled'
    })

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x = DF.index, y = DF['Efficiency'], name='Efficiency'),
        secondary_y = False
    )
    fig.add_trace(
        go.Scatter(x = DF.index, y = DF['SOPT Enabled'], name='SOPT Enabled'),
        secondary_y = True
    )
    fig.add_trace(
        go.Scatter(x = DF.index, y = DF['COPT Enabled'], name='COPT Enabled'),
        secondary_y = True
    )
    fig.update_yaxes(range=[-0.1, 1.1], secondary_y=True)
    fig.update_layout(
        xaxis_title = "Time",
        yaxis_title = "Efficiency",
        yaxis = dict(showgrid=False),
        margin = go.layout.Margin(l=0, r=0, t=0, b=0),
        hovermode = 'x'
    )

    fig.write_html(f'static/figure/home-{unit}.html')
    return

def get_home():
    update_figure_tja1, update_figure_tja2 = (True, True)
    path_figure_tja1 = 'static/figure/home-tja1.html' 
    path_figure_tja2 = 'static/figure/home-tja2.html'

    if os.path.isfile(path_figure_tja1):
        if time.time() - os.path.getmtime(path_figure_tja1) < Config.UpdateRate:
            update_figure_tja1 = False

    if os.path.isfile(path_figure_tja2):
        if time.time() - os.path.getmtime(path_figure_tja2) < Config.UpdateRate:
            update_figure_tja2 = False
    
    if update_figure_tja1:
        update_home('tja1')
    if update_figure_tja2:
        update_home('tja2')
    return

def get_bat_status():
    return

def get_server_status(server, debug_mode=True):
    ret = {}

    # Disk check
    ssh_command = "df"
    ssh_template_bat = f"""ssh -t root@10.7.1.116 -p 24012 "ssh -t {server} '{ssh_command}'" """

    if debug_mode:
        result = Dummy.SSH[ssh_command]
    else:
        stream = os.popen(ssh_template_bat)
        result = stream.read()
    DFresult = __text_to_dataframe__(result)
    DFresult = DFresult.rename(columns={'1K-blocks': 'Size'})

    ret['Disk Usage'] = {
        'Total': DFresult[DFresult['Filesystem'] != 'overlay'].sum()['Size'],
        'Used': DFresult[DFresult['Filesystem'] != 'overlay'].sum()['Used'],
        'Percent': round(DFresult[DFresult['Filesystem'] != 'overlay'].sum()['Used'] / DFresult[DFresult['Filesystem'] != 'overlay'].sum()['Size'],3) * 100,
    }

    # Memory
    ssh_command = "free -m"
    ssh_template_bat = f"""ssh -t root@10.7.1.116 -p 24012 "ssh -t {server} '{ssh_command}'" """

    if debug_mode:
        result = Dummy.SSH[ssh_command]
    else:
        stream = os.popen(ssh_template_bat)
        result = stream.read()
    while "  " in result:
        result = result.replace("  "," ")
    result = result.split('\n')
    result = [f.strip().split(" ") for f in result]

    ret = {
        'Disk Usage': {
            'Total': DFresult[DFresult['Filesystem'] != 'overlay'].sum()['Size'],
            'Used': round(DFresult[DFresult['Filesystem'] != 'overlay'].sum()['Used'] / DFresult[DFresult['Filesystem'] != 'overlay'].sum()['Size'],3)
        },
        'Memory': {                                                                                               
            'Total': 4,
            'Used': 0.9
        }
    }
    return ret

def __text_to_dataframe__(text):
    # Text to table
    results = [r for r in text.split('\n')]
    maxlength = max([len(f) for f in results])
    space_cols = np.zeros(maxlength)
    for i in range(len(results)):
        for j in range(maxlength):
            if j < len(results[i]):
                if results[i][j] == ' ': space_cols[j] += 1
            else:
                space_cols[j] += 1
    maxspace = max(space_cols)
    separators = [0]
    for i in range(len(space_cols) - 1):
        if space_cols[i] == maxspace and space_cols[i + 1] != maxspace:
            separators.append(i)
    separators.append(maxlength)

    results_table = []
    for i in range(len(results)):
        results_line = []
        for j in range(len(separators)-1):
            val = results[i][separators[j]:separators[j+1]].strip()
            if val.isnumeric(): val = float(val)
            results_line.append(val)
        results_table.append(results_line)

    results_df = pd.DataFrame(results_table[1:], columns=results_table[0])
    return results_df

if __name__ == "__main__":
    data = get_home()
    print(data)