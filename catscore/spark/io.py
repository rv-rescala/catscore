from pyspark.sql import SparkSession, DataFrame

class SparkIO: 
    @classmethod
    def write_to_json(cls, df: DataFrame, fullpath: str, orient='records'):
        df.toPandas().to_json(fullpath, force_ascii=False, orient=orient)