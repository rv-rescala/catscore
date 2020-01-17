from dataclasses import dataclass

@dataclass(frozen=True)
class MysqlConf:
    host: str
    port: str
    usr: str
    pwd: str
    db_name: str