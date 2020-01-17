from dataclasses import dataclass

@dataclass(frozen=True)
class MySQLConf:
    host: str
    port: str
    usr: str
    pwd: str
    db_name: str

    @property
    def connection_uri(self):
        return f"jdbc:mysql://{self.host}:{self.port}/{self.db_name}?user={self.usr}&password={self.pwd}"