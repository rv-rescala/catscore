from dataclasses import dataclass
import json
from pyspark import SparkContext, SQLContext
from pyspark.sql import SparkSession, DataFrame

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
                host=j["host"],
                port=j["port"],
                user=j["user"],
                pwd=j["pwd"],
                db_name=j["db_name"])
        return m
    
class MySQLSpark:
    @classmethod
    def read(cls, spark:SparkSession, mysql_conf:MySQLConf, table_name:str) -> DataFrame:
        sql_context = SQLContext(spark.sparkContext)
        return sql_context.read.format("jdbc").options(url=mysql_conf.connection_uri("jdbc"), dbtable=table_name).load()
    
    @classmethod
    def overwrite(cls, spark:SparkSession, table_name: str, df:DataFrame, mysql_conf:MySQLConf):
        df.write.jdbc(mysql_conf.connection_uri("jdbc"), table=table_name, mode='overwrite')
    