import requests
from datetime import datetime, timedelta

BASE_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
BASE_TIMES = ["0200", "0500", "0800", "1100", "1400", "1700", "2000", "2300"]

def get_base_time() -> tuple:
    now = datetime.now()
    selected = "0200"
    for t in BASE_TIMES:
        if now.hour >= int(t[:2]):
            selected = t
        else:
            break
    if selected == "0200" and now.hour < 2:
        yesterday = (now - timedelta(days=1)).strftime("%Y%m%d")
        return yesterday, "2300"
    return now.strftime("%Y%m%d"), selected

def parse_forecast(items: list, tomorrow: str) -> dict | None:
    pops, tmps = [], []
    for item in items:
        if item.get("fcstDate") != tomorrow:
            continue
        if item["category"] == "POP":
            pops.append(int(item["fcstValue"]))
        elif item["category"] == "TMP":
            tmps.append(int(item["fcstValue"]))
    if not pops and not tmps:
        return None
    return {
        "pop": max(pops) if pops else 0,
        "tmp_max": max(tmps) if tmps else 0,
        "tmp_min": min(tmps) if tmps else 0,
    }

def get_tomorrow_forecast(api_key: str, nx: int = 59, ny: int = 126) -> dict | None:
    base_date, base_time = get_base_time()
    tomorrow = (datetime.strptime(base_date, "%Y%m%d") + timedelta(days=1)).strftime("%Y%m%d")
    params = {
        "serviceKey": api_key,
        "pageNo": 1,
        "numOfRows": 1000,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny,
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json()["response"]["body"]["items"]["item"]
        return parse_forecast(items, tomorrow)
    except Exception:
        return None
