from dataclasses import dataclass
import json
from pyspark import SparkContext, SQLContext
from pyspark.sql import SparkSession, DataFrame
from catscore.lib.logger import logging
import logging
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *
import sys
from sqlalchemy_utils import database_exists, create_database, drop_database
from cats_food.libs.config import DBConfig
from peeping_cats.pclib.pc_config import PCConfig
from threading import Lock
import csv
import socket
from cats_food.libs.logger import Logging

@dataclass(frozen=True)
class MySQLConf:
    host: str
    port: str
    user: str
    pwd: str
    db_name: str

    def connection_uri(self, inteface:str):
        if inteface == "jdbc":
            uri = f"jdbc:mysql://{self.host}:{self.port}/{self.db_name}?user={self.user}&password={self.pwd}"
        elif inteface == "pymysql":
            uri =  'mysql+pymysql://%s:%s@%s/%s?charset=utf8' % (self.user, self.pwd, self.host + ":" + self.port, self.db_name)
        print(uri)
        return uri

    @classmethod
    def from_json(cls, path):
        with open(path, "r") as f:
            j = json.load(f)
            m = MySQLConf(
                host=j["mysql"]["host"],
                port=j["mysql"]["port"],
                user=j["mysql"]["user"],
                pwd=j["mysql"]["pwd"],
                db_name=j["mysql"]["db_name"])
        return m

class MySQLSpark:
    @classmethod
    def read(cls, spark:SparkSession, mysql_conf:MySQLConf, table_name:str) -> DataFrame:
        sql_context = SQLContext(spark.sparkContext)
        return sql_context.read.format("jdbc").options(url=mysql_conf.connection_uri("jdbc"), dbtable=table_name).load()
    
    @classmethod
    def overwrite(cls, spark:SparkSession, table_name: str, df:DataFrame, mysql_conf:MySQLConf):
        df.write.jdbc(mysql_conf.connection_uri("jdbc"), table=table_name, mode='overwrite')


class MySQLAlchemySingleton:
    Base = declarative_base()
    DB_NAME = "peeping_cats"
    """
    
    """
    _unique_instance = None
    _lock = Lock()  # Class Lock
    session = None

    def __new__(cls):
        raise NotImplementedError('Cannot initialize via Constructor')

    @classmethod
    def __internal_new__(cls):
        return super().__new__(cls)

    @classmethod
    def initialize(cls, mysql_conf: MySQLConf):
        """

        :param config:
        :return:
        """
        logging.info(f"db config {mysql_conf}")
        db_setting = mysql_conf.connection_uri(inteface="pymysql")
        logging.info("db_setting : {}".format(db_setting))
        print("db_setting : {}".format(db_setting))

        cls.engine = create_engine(
            db_setting,
            encoding="utf-8",
            echo=False  # Trueだと実行のたびにSQLが出力される
        )
        # Sessionの作成
        cls.session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=cls.engine
            )
        )
        cls.query = cls.session.query_property()

        if not cls._unique_instance:
            with cls._lock:
                if not cls._unique_instance:
                    cls._unique_instance = cls.__internal_new__()
                    logging.info("PCSQLAlchemySingleton instance created.")
        else:
            message = "PCSQLAlchemySingleton instance has already created."
            logging.error(message)
            raise RuntimeError(message)

    @classmethod
    def close(cls):
        logging.info("PCSQLAlchemySingleton close")
        cls.session.close()
        cls._unique_instance = None

    @classmethod
    def get_instance(cls):
        """
        Get instance of PCSQLAlchemySingleton
        :return:
        """
        logging.info(f"get_instance : {cls._unique_instance}")
        return cls._unique_instance

    @classmethod
    def create_db(cls):
        """
        create database
        Attention!! create_dbを呼ぶファイルに対象modelがimportされていないと、tableが作成されない
        :return:
        """
        if not database_exists(cls.engine.url):
            logging.info("create database")
            create_database(cls.engine.url)

        cls.Base.metadata.create_all(bind=cls.engine)

        logging.info("db created.")

    @classmethod
    def drop_db(cls):
        if database_exists(cls.engine.url):
            logging.info(f"drop database {cls.engine.url}")
            #drop_database(cls.engine.url)
            cls.Base.metadata.drop_all(bind=cls.engine)
        else:
            logging.info("db not found")

    @classmethod
    def insert(cls, il, allow_duplicate = False):
        """

        :param il:
        :return:
        """
        # add list, with remove None
        if allow_duplicate:
            for item in il:
                try:
                    cls.session.add(item)
                    cls.session.commit()
                except:
                    logging.info(f"{sys.exc_info()}")
                    logging.info(f"key is duplicate]: {item}")
                    cls.session.rollback()
        else:
            try:
                cls.session.add_all(filter(None, il))
                cls.session.commit()
            except:
                Logging.error("sys.exc_info : {}".format(sys.exc_info()))
                Logging.error("session rollback")
                cls.session.rollback()
                raise RuntimeError("sys.exc_info : {}".format(sys.exc_info()))
    @classmethod
    def tables_to_csv(cls, tables):
        for table in tables:
            filename = f'{PCConfig.dump_path}/{table.__tablename__}_{socket.gethostname()}.csv'
            logging.info(f"{table} output to {filename}")
            with open(filename, 'w') as outfile:
                outcsv = csv.writer(outfile)
                cursor = MySQLAlchemySingleton.get_instance().session.query(table)
                header = table.__table__.columns.keys()
                logging.info(f"tables_to_csv header: {header}")
                # dump column titles (optional)
                outcsv.writerow(header)
                for cur in cursor.yield_per(10):
                    r = [getattr(cur, c) for c in header]
                    remove_n = list(map(lambda x: str(x).replace("\n",""), r))
                    outcsv.writerow(remove_n)
                # dump rows => fetchallだとmemoryが足りない
                #outcsv.writerows(cursor.fetchall())
                #print(filename)