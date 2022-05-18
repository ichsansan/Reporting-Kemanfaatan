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
        self.watchdog_tag = Config.TagsDescription['Watchdog']
        self.copt_safeguard_tag = Config.TagsDescription['COPT Safeguard']
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

        return df 