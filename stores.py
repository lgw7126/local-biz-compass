import pandas as pd

def load_stores(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)

def get_districts(df: pd.DataFrame) -> list:
    return sorted(df["법정동명"].dropna().unique().tolist())

def count_stores(df: pd.DataFrame, district: str, category: str) -> int:
    mask = (df["법정동명"] == district) & (df["상권업종소분류명"] == category)
    return int(mask.sum())

def get_store_list(df: pd.DataFrame, district: str, category: str) -> pd.DataFrame:
    mask = (df["법정동명"] == district) & (df["상권업종소분류명"] == category)
    return df[mask][["상호명", "도로명주소"]].dropna(subset=["상호명"]).reset_index(drop=True)
