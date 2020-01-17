from dataclasses import dataclass
import json

@dataclass(frozen=True)
class MySQLConf:
    host: str
    port: str
    user: str
    pwd: str
    db_name: str

    @property
    def connection_uri(self):
        return f"jdbc:mysql://{self.host}:{self.port}/{self.db_name}?user={self.user}&password={self.pwd}"

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