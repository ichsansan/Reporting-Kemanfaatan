from venv import create
import pandas as pd
import numpy as np
from helpers import Config
from sqlalchemy import create_engine
import os, time

class Database(object):
    def __init__(self, engine) -> None:
        if type(engine) == str: self.engine = create_engine(engine)
        else: self.engine = engine

        self.set_tag()
        self.set_mapping_gangguan()

    def set_tag(self) -> None:
        self.copt_enable_tag = self.get_tag_from_description(Config.TagsDescription['COPT Enable'])
        self.sopt_enable_tag = self.get_tag_from_description(Config.TagsDescription['SOPT Enable'])
        self.gross_load_tag = self.get_tag_from_description(Config.TagsDescription['Gross Load'])
        self.watchdog_tag = Config.TagsDescription['Watchdog']
        self.copt_safeguard_tag = Config.TagsDescription['COPT Safeguard']
        self.sopt_safeguard_tag = Config.TagsDescription['SOPT Safeguard']
        self.efficiency_tag = Config.TagsDescription['Efficiency']
        
        return 
    
    def set_mapping_gangguan(self) -> None:
        q = f"""SELECT f_id, f_tipe_gangguan FROM tb_rp_category """
        df = pd.read_sql(q, self.engine).astype(str)
        self.mapping_tipe_gangguan = df.set_index('f_id')['f_tipe_gangguan'].to_dict()
        self.mapping_tipe_gangguan_r = df.set_index('f_tipe_gangguan')['f_id'].to_dict()
        return 

    def get_tag_from_description(self, description):
        q = f"""SELECT f_tag_name FROM tb_tags_read_conf WHERE f_description = "{description}"
                UNION
                SELECT f_tag_name FROM tb_sootblow_conf_tags WHERE f_description = "{description}" """
        df = pd.read_sql(q, self.engine)
        if len(df) > 0:
            tag = df.iloc[0][0]
        else: tag = None
        return tag
    
    def read_tag(self, tagname, timestart=None, timeend=None):
        tagscript = ""
        if type(tagname) == str: tagscript = f'= "{tagname}"'
        else: tagscript = f"IN {tuple(tagname)}"

        if not timeend: timeend = 'NOW()'
        if not timestart: timestart = 'NOW() - INTERVAL 1 DAY'
        q = f"""SELECT f_address_no, f_date_rec, f_value FROM tb_bat_history
                WHERE f_address_no {tagscript}
                AND f_date_rec BETWEEN {timestart} AND {timeend}"""
        df = pd.read_sql(q, self.engine)
        df['f_value'] = df['f_value'].astype(float)
        df = df.pivot_table(index='f_date_rec', columns='f_address_no', values='f_value')
        df = df.resample('1min').mean().ffill()

        # Filling unavailable tags
        for tag in tuple(tagname):
            if tag not in df.columns:
                df[tag] = None

        return df 
    
    def read_gangguan(self, timestart=None, timeend=None, category=None, clip=True):
        if not timeend: timeend = (pd.to_datetime(time.ctime())).strftime('"%Y-%m-%d %H:%M"')
        if not timestart: timestart = (pd.to_datetime(time.ctime()) - pd.to_timedelta('1day')).strftime('"%Y-%m-%d %H:%M"')
        
        # Where script
        wherescript  =  f"""(ga.f_date_start BETWEEN {timestart} AND {timeend}
                            OR ga.f_date_end BETWEEN {timestart} AND {timeend}) """
        if category:
            if type(category) == str:
                wherescript += f"""AND ga.f_tipe_id = {category}"""
            elif type(category) == tuple or type(category) == list:
                wherescript += f"""AND ga.f_tipe_id IN {tuple(category)}"""
        q = f"""SELECT ga.f_id AS ID, ga.f_date_start AS DateStart, ga.f_date_end AS DateEnd,
                cat.f_tipe_gangguan AS TipeGangguan, ga.f_desc_gangguan AS Deskripsi, ga.f_remarks AS Remarks FROM tb_rp_gangguan ga
                LEFT JOIN tb_rp_category cat
                ON ga.f_tipe_id = cat.f_id 
                
                """
        df = pd.read_sql(q, self.engine)

        timestart_pd = pd.to_datetime(timestart.replace('"',''))
        timeend_pd = pd.to_datetime(timeend.replace('"',''))

        if clip:
            df['DateStart'] = df['DateStart'].clip(lower=pd.to_datetime(timestart_pd), upper=pd.to_datetime(timeend_pd))
            df['DateEnd'] = df['DateEnd'].clip(lower=pd.to_datetime(timestart_pd), upper=pd.to_datetime(timeend_pd))
        df = df.set_index('ID')
        return df

    def read_display(self):
        q = f"""SELECT d.f_desc, r.f_date_rec, r.f_value, d.f_units FROM cb_display d
                LEFT JOIN tb_bat_raw r
                ON d.f_tags = r.f_address_no """
        df = pd.read_sql(q, self.engine)
        df['f_value'] = df['f_value'].round(2).astype(str) + " " + df['f_units']
        sensor_values = df.set_index('f_desc')['f_value'].to_dict()
        return sensor_values

    def post_gangguan(self, data):
        f_date_start = pd.to_datetime(data['datestart'])
        f_date_end = pd.to_datetime(data['dateend'])
        f_tipe_id = str(data['tipegangguan'])
        f_desc_gangguan = data['deskripsi']
        f_remarks = data['remarks']
        
        q = f"""INSERT INTO tb_rp_gangguan (f_date_start, f_date_end, f_tipe_id, f_desc_gangguan, f_remarks)
                VALUES ("{f_date_start}","{f_date_end}","{f_tipe_id}","{f_desc_gangguan}","{f_remarks}") """
        with self.engine.connect() as conn:
            response = conn.execute(q)
            ret = f"Success importing {response.rowcount} line(s)."
        return ret