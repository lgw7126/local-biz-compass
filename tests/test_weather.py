from weather import parse_forecast, get_base_time

def test_parse_forecast_extracts_max_pop():
    items = [
        {"category": "POP", "fcstValue": "30", "fcstDate": "20260623"},
        {"category": "POP", "fcstValue": "70", "fcstDate": "20260623"},
        {"category": "TMP", "fcstValue": "18", "fcstDate": "20260623"},
        {"category": "TMP", "fcstValue": "15", "fcstDate": "20260623"},
    ]
    result = parse_forecast(items, "20260623")
    assert result["pop"] == 70
    assert result["tmp_max"] == 18
    assert result["tmp_min"] == 15

def test_parse_forecast_returns_none_when_no_data():
    result = parse_forecast([], "20260623")
    assert result is None

def test_get_base_time_returns_tuple():
    base_date, base_time = get_base_time()
    assert len(base_date) == 8
    assert base_time in ["0200","0500","0800","1100","1400","1700","2000","2300"]
