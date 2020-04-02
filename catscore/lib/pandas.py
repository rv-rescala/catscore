import pandas as pd
from dataclasses import asdict

class PandasConverter:
    @classmethod
    def dataclass_to_dataframe(cls, dc) -> pd.DataFrame:
        print(type(dc))
        return pd.DataFrame([asdict(x) for x in dc])