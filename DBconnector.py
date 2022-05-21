import pandas as pd
import numpy as np
from helpers import Config
import os, time

class Database(object):
    def __init__(self, engine) -> None:
        self.engine = engine
        self.set_tag()

    def set_tag(self) -> None:
        self.copt_enable_tag = self.get_tag_from_description(Config.TagsDescription['COPT Enable'])
        self.sopt_enable_tag = self.get_tag_from_description(Config.TagsDescription['SOPT Enable'])
        self.gross_load_tag = self.get_tag_from_description(Config.TagsDescription['Gross Load'])
        self.watchdog_tag = Config.TagsDescription['Watchdog']
        self.copt_safeguard_tag = Config.TagsDescription['COPT Safeguard']
        self.sopt_safeguard_tag = Config.TagsDescription['SOPT Safeguard']
        self.efficiency_tag = Config.TagsDescription['Efficiency']
        
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
    
    def read_gangguan(self, timestart=None, timeend=None, category=None):
        if not timeend: timeend = 'NOW()'
        if not timestart: timestart = 'NOW() - INTERVAL 1 DAY'
        
        # Where script
        wherescript  =  f"""(ga.f_date_start BETWEEN {timestart} AND {timeend}
                            OR ga.f_date_end BETWEEN {timestart} AND {timeend}) """
        if category:
            if type(category) == str:
                wherescript += f"""AND ga.f_tipe_id = {category}"""
            elif type(category) == tuple or type(category) == list:
                wherescript += f"""AND ga.f_tipe_id IN {tuple(category)}"""
        q = f"""SELECT ga.f_id, ga.f_date_start, ga.f_date_end,
                cat.f_tipe_gangguan, ga.f_desc_gangguan, ga.f_remarks FROM tb_rp_gangguan ga
                LEFT JOIN tb_rp_category cat
                ON ga.f_tipe_id = cat.f_id 
                WHERE {wherescript}
                """
        df = pd.read_sql(q, self.engine)

        timestart_pd = pd.to_datetime(timestart.replace('"',''))
        timeend_pd = pd.to_datetime(timeend.replace('"',''))

        df['f_date_start'] = df['f_date_start'].clip(lower=pd.to_datetime(timestart_pd), upper=pd.to_datetime(timeend_pd))
        df['f_date_end'] = df['f_date_end'].clip(lower=pd.to_datetime(timestart_pd), upper=pd.to_datetime(timeend_pd))
        df['f_duration'] = df['f_date_end'] - df['f_date_start']
        df = df.set_index('f_id')
        return df