import requests
from datetime import datetime, timedelta

BASE_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
MID_TEMP_URL = "https://apis.data.go.kr/1360000/MidFcstInfoService/getMidTa"
MID_LAND_URL = "https://apis.data.go.kr/1360000/MidFcstInfoService/getMidLandFcst"
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

def get_mid_base_time() -> str:
    now = datetime.now()
    if now.hour >= 18:
        return now.strftime("%Y%m%d") + "1800"
    elif now.hour >= 6:
        return now.strftime("%Y%m%d") + "0600"
    else:
        return (now - timedelta(days=1)).strftime("%Y%m%d") + "1800"

def get_weather_icon(pty: int, pop: int) -> str:
    if pty == 1: return "🌧️"
    if pty == 2: return "🌨️"
    if pty == 3: return "❄️"
    if pty == 4: return "🌦️"
    if pop >= 60: return "☁️"
    if pop >= 30: return "⛅"
    return "☀️"

def wf_to_icon(wf: str) -> str:
    if "비/눈" in wf or "눈/비" in wf: return "🌨️"
    if "눈" in wf: return "❄️"
    if "소나기" in wf: return "🌦️"
    if "비" in wf: return "🌧️"
    if "흐림" in wf: return "🌥️"
    if "구름많음" in wf: return "⛅"
    if "맑음" in wf: return "☀️"
    return "🌤️"

def parse_forecast(items: list, tomorrow: str) -> dict | None:
    pops, tmps, ptys = [], [], []
    for item in items:
        if item.get("fcstDate") != tomorrow:
            continue
        if item["category"] == "POP":
            pops.append(int(item["fcstValue"]))
        elif item["category"] == "TMP":
            tmps.append(int(item["fcstValue"]))
        elif item["category"] == "PTY":
            ptys.append(int(item["fcstValue"]))
    if not pops and not tmps:
        return None
    pop = max(pops) if pops else 0
    pty = max(set(ptys), key=ptys.count) if ptys else 0
    return {
        "pop": pop,
        "tmp_max": max(tmps) if tmps else 0,
        "tmp_min": min(tmps) if tmps else 0,
        "pty": pty,
        "icon": get_weather_icon(pty, pop),
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

def get_weekly_forecast(api_key: str, nx: int = 59, ny: int = 126) -> list:
    base_date, base_time = get_base_time()
    today = datetime.strptime(base_date, "%Y%m%d")
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

    daily = {}
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        items = resp.json()["response"]["body"]["items"]["item"]
        for item in items:
            d = item["fcstDate"]
            if d not in daily:
                daily[d] = {"pops": [], "tmps": [], "ptys": []}
            cat = item["category"]
            val = item["fcstValue"]
            if cat == "POP": daily[d]["pops"].append(int(val))
            elif cat == "TMP": daily[d]["tmps"].append(int(val))
            elif cat == "PTY": daily[d]["ptys"].append(int(val))
    except Exception:
        pass

    result = []
    for d in sorted(daily.keys()):
        dt = datetime.strptime(d, "%Y%m%d")
        if dt <= today:
            continue
        data = daily[d]
        pop = max(data["pops"]) if data["pops"] else 0
        pty = max(set(data["ptys"]), key=data["ptys"].count) if data["ptys"] else 0
        result.append({
            "date": dt.strftime("%m/%d"),
            "label": dt.strftime("%m/%d\n(%a)"),
            "pop": pop,
            "tmp_max": max(data["tmps"]) if data["tmps"] else 0,
            "tmp_min": min(data["tmps"]) if data["tmps"] else 0,
            "icon": get_weather_icon(pty, pop),
        })

    # 중기예보로 4~7일 보완
    if len(result) < 7:
        tmFc = get_mid_base_time()
        try:
            temp_resp = requests.get(MID_TEMP_URL, params={
                "serviceKey": api_key, "pageNo": 1, "numOfRows": 10,
                "dataType": "JSON", "regId": "11B10101", "tmFc": tmFc,
            }, timeout=10)
            temp_item = temp_resp.json()["response"]["body"]["items"]["item"][0]

            land_resp = requests.get(MID_LAND_URL, params={
                "serviceKey": api_key, "pageNo": 1, "numOfRows": 10,
                "dataType": "JSON", "regId": "11B00000", "tmFc": tmFc,
            }, timeout=10)
            land_item = land_resp.json()["response"]["body"]["items"]["item"][0]

            covered_days = len(result)
            for n in range(max(4, covered_days + 1), 8):
                dt = today + timedelta(days=n)
                wf = str(land_item.get(f"wf{n}Am", "") or land_item.get(f"wf{n}", "") or "")
                pop = int(land_item.get(f"rnSt{n}Am", 0) or 0)
                result.append({
                    "date": dt.strftime("%m/%d"),
                    "label": dt.strftime("%m/%d"),
                    "pop": pop,
                    "tmp_max": int(temp_item.get(f"taMax{n}", 0) or 0),
                    "tmp_min": int(temp_item.get(f"taMin{n}", 0) or 0),
                    "icon": wf_to_icon(wf),
                })
        except Exception:
            pass

    return result
