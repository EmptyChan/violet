# -*- coding: utf-8 -*- 
"""
 Created with IntelliJ IDEA.
 Description:
 User: jinhuichen
 Date: 3/20/2018 11:12 AM 
 Description: 
"""
from fetchman.pipeline.console_pipeline import ConsolePipeline
from fetchman.pipeline.pic_pipeline import PicPipeline
from fetchman.pipeline.test_pipeline import TestPipeline

POSTGRESQL_PIPELINE = 'postgresql'
MONGODB_PIPELINE = 'mongodb'
MYSQL_PIPELINE = 'mysql'
SQL_SERVER_PIPELINE = 'sql_server'
SQLITE_PIPELINE = 'sqlite'
CONSOLE_PIPELINE = 'console'


PIPEINE_MAP = {
    CONSOLE_PIPELINE: ConsolePipeline,
    MONGODB_PIPELINE: None,
    MYSQL_PIPELINE: None,
    SQL_SERVER_PIPELINE: None,
    SQLITE_PIPELINE: None,
    POSTGRESQL_PIPELINE: None
}

