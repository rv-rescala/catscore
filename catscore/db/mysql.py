from dataclasses import dataclass

@dataclass(frozen=True)
class MysqlConf:
    host: str
    port: str
    usr: str
    pwd: str
    db_name: str

    @property
    def sql_connection(self):
        return f"jdbc:mysql://{self.host}:{self.port}/{self.db_name}?user={self.usr}&password={self.pwd}"