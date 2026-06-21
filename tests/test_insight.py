from insight import get_insight

def test_green_when_pop_below_30():
    result = get_insight(20)
    assert result["color"] == "green"
    assert "평소대로" in result["message"]

def test_orange_when_pop_between_30_and_59():
    result = get_insight(45)
    assert result["color"] == "orange"
    assert "90%" in result["message"]

def test_red_when_pop_60_or_above():
    result = get_insight(60)
    assert result["color"] == "red"
    assert "줄이" in result["message"]

def test_boundary_30_is_orange():
    assert get_insight(30)["color"] == "orange"

def test_boundary_59_is_orange():
    assert get_insight(59)["color"] == "orange"

def test_boundary_0_is_green():
    assert get_insight(0)["color"] == "green"

def test_boundary_100_is_red():
    assert get_insight(100)["color"] == "red"
