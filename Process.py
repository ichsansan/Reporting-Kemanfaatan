import pandas as pd
import numpy as np
from pexpect import ExceptionPexpect
import plotly.graph_objects as go
import os, time, re
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

def get_svg(name):
    type, unit = name.split('-')
    if type != 'copt': return ''
    if unit == 'tja1': DB = DB1
    elif unit == 'tja2': DB = DB2
    SVG_PATH = "static/figure/Drawing TAW White v1.0.txt"
    f = open(SVG_PATH)
    svg_raw = f.readlines()
    f.close()

    svg = ''
    for i in range(len(svg_raw)):
        for j in range(len(svg_raw[i])):
            if svg_raw[i][j].isascii():
                svg += svg_raw[i][j].encode('utf-8').decode('utf-8')
    sensor_values = DB.read_display()

    for sensor_name in sensor_values.keys():
        svg = svg.replace("{" + sensor_name + "}", str(sensor_values[sensor_name]))
    svg = re.sub('\{[0-9A-z_]+\}', '-', svg)
    return svg

def get_daftar_gangguan():
    df1 = DB1.read_gangguan()
    df1.insert(0, "Unit", "Tanjung Awar-Awar 1")
    df2 = DB2.read_gangguan()
    df2.insert(0, "Unit", "Tanjung Awar-Awar 2")
    df = df1.append(df2, ignore_index=True)
    df = df.reset_index()
    
    return df.to_dict()

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

def get_laporan_kemanfaatan(data, unit='tja'):
    datestart = 'now'
    dateend = 'now'
    ret = {}

    if 'datestart' in data.keys():
        datestart = data['datestart']
    if 'dateend' in data.keys():
        dateend = data['dateend']

    datestart = pd.to_datetime(datestart)
    dateend = pd.to_datetime(dateend)
    datestart, dateend = (min(datestart, dateend), max(datestart, dateend) + pd.to_timedelta('1d') - pd.to_timedelta('1min')) 
    ret['datestart'] = datestart
    ret['dateend'] = dateend

    try:
        # Unit 1
        tags = [DB1.copt_enable_tag, DB1.sopt_enable_tag, DB1.watchdog_tag, 
                DB1.copt_safeguard_tag, DB1.sopt_safeguard_tag, DB1.gross_load_tag]
        df = DB1.read_tag(tags, timestart=f'"{datestart}"', timeend=f'"{dateend}"')
        df_gangguan = DB1.read_gangguan(timestart=f'"{datestart}"', timeend=f'"{dateend}"', category=None)
        dfg_timeseries = pd.DataFrame(columns=df_gangguan.index, index=df.index)
        for i in df_gangguan.index:
            f_date_start = df_gangguan.loc[i, 'f_date_start']
            f_date_end = df_gangguan.loc[i, 'f_date_end']
            dfg_timeseries.loc[f_date_start, i] = 1
            dfg_timeseries.loc[f_date_end, i] = 0
        dfg_timeseries = dfg_timeseries.ffill()
        dfg_timeseries = dfg_timeseries.fillna(0)
        dfg_timeseries['total'] = dfg_timeseries.max(axis=1)
        
        df_gangguan_unit = dfg_timeseries[['total']].rename(columns={'total': 'Perbaikan'})
        df_gangguan_unit['Safeguard'] = 1 - df[['SAFEGUARD:COMBUSTION','SAFEGUARD:SOOTBLOW','WatchdogStatus']].max(axis=1)
        df_gangguan_unit['Load'] = (df[DB1.gross_load_tag] < 0.7*350).astype(int)

        ret['l11'] = df[[DB1.copt_enable_tag, DB1.sopt_enable_tag]].max(axis=1).sum()
        ret['l13'] = (dateend - datestart).seconds / 60
        ret['l15'] = df_gangguan_unit.max(axis=1).sum()
        ret['l17'] = df_gangguan_unit['Perbaikan'].sum()
        ret['l18'] = df_gangguan_unit['Safeguard'].sum()
        ret['l19'] = df_gangguan_unit['Load'].sum()
        ret['l25'] = len(df_gangguan_unit) - ret['l15']

        # Unit 2
        tags = [DB2.copt_enable_tag, DB2.sopt_enable_tag, DB2.watchdog_tag, 
                DB2.copt_safeguard_tag, DB2.sopt_safeguard_tag, DB2.gross_load_tag]
        df = DB2.read_tag(tags, timestart=f'"{datestart}"', timeend=f'"{dateend}"')
        df_gangguan = DB2.read_gangguan(timestart=f'"{datestart}"', timeend=f'"{dateend}"', category=None)
        dfg_timeseries = pd.DataFrame(columns=df_gangguan.index, index=df.index)
        for i in df_gangguan.index:
            f_date_start = df_gangguan.loc[i, 'f_date_start']
            f_date_end = df_gangguan.loc[i, 'f_date_end']
            dfg_timeseries.loc[f_date_start, i] = 1
            dfg_timeseries.loc[f_date_end, i] = 0
        dfg_timeseries = dfg_timeseries.ffill()
        dfg_timeseries = dfg_timeseries.fillna(0)
        dfg_timeseries['total'] = dfg_timeseries.max(axis=1)
        
        df_gangguan_unit = dfg_timeseries[['total']].rename(columns={'total': 'Perbaikan'})
        df_gangguan_unit['Safeguard'] = 1 - df[['SAFEGUARD:COMBUSTION','SAFEGUARD:SOOTBLOW','WatchdogStatus']].max(axis=1)
        df_gangguan_unit['Load'] = (df[DB2.gross_load_tag] < 0.7*350).astype(int)

        ret['y11'] = df[[DB2.copt_enable_tag, DB2.sopt_enable_tag]].max(axis=1).sum()
        ret['y13'] = (dateend - datestart).seconds / 60
        ret['y15'] = df_gangguan_unit.max(axis=1).sum()
        ret['y17'] = df_gangguan_unit['Perbaikan'].sum()
        ret['y18'] = df_gangguan_unit['Safeguard'].sum()
        ret['y19'] = df_gangguan_unit['Load'].sum()
        ret['y25'] = len(df_gangguan_unit) - ret['y15']
        
        for k in ret.keys():
            if k.startswith('l') or k.startswith('y'):
                try: ret[k] = round(ret[k] / 60, 2)
                except: pass
        
        ret['jumlahenablehours'] = ret['l11'] + ret['y11']
        ret['jumlahavailablehours'] = ret['l25'] + ret['y25']

        ret['efektivitaspersen'] = round(100 * ret['jumlahenablehours'] / ret['jumlahavailablehours'], 2)
    except:
        pass

    return ret

def get_tipe_gangguan():
    tipe_gangguan = DB1.mapping_tipe_gangguan
    tipe_gangguan_2 = DB2.mapping_tipe_gangguan
    for k in tipe_gangguan_2.keys():
        if k not in tipe_gangguan.keys():
            tipe_gangguan[k] = tipe_gangguan_2[k]
    return tipe_gangguan

def post_input_gangguan(data):
    ret = {'message': 'Gagal menginput data'}
    try:
        if data['unitname'] == 'tja1':
            ret['message'] = DB1.post_gangguan(data)
        elif data['unitname'] == 'tja2':
            ret['message'] = DB2.post_gangguan(data)
    except Exception as E: 
        print(E)
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
    results_df = results_df.replace({"":None}).dropna()
    return results_df


# Data Processing
def process_safeguard():
    q = f"""SELECT tsrd.f_sequence AS "Sequence", tsrd.f_tag_sensor as Tag, tsrd.f_bracket_open AS "Bracket Open", ttrc.f_description AS Description, 
        tsrd.f_bracket_close AS "Bracket Close", tsr.f_value AS SampleValue FROM tb_combustion_rules_dtl tsrd 
        LEFT JOIN tb_bat_raw tsr 
        ON tsrd.f_tag_sensor = tsr.f_address_no
        LEFT JOIN tb_combustion_rules_hdr tsrh 
        ON tsrd.f_rule_hdr_id = tsrh.f_rule_hdr_id 
        LEFT JOIN tb_tags_read_conf ttrc 
        ON tsrd.f_tag_sensor = ttrc.f_tag_name 
        WHERE tsrd.f_is_active = 1
        AND tsrh.f_rule_descr = "SAFEGUARD"
        ORDER BY tsrd.f_rule_hdr_id ASC, tsrd.f_sequence ASC;"""
    return

if __name__ == "__main__":
    data = get_home()
    print(data)
