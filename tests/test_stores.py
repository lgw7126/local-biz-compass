import pandas as pd
import pytest
from stores import load_stores, get_districts, count_stores

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "시군구명": ["마포구", "마포구", "마포구", "마포구"],
        "법정동명": ["서교동", "서교동", "합정동", "합정동"],
        "상권업종소분류명": ["커피전문점/카페/다방", "커피전문점/카페/다방", "커피전문점/카페/다방", "한식음식점"],
    })

def test_get_districts_returns_sorted_unique(sample_df):
    result = get_districts(sample_df)
    assert result == ["서교동", "합정동"]

def test_count_stores_filters_by_district_and_category(sample_df):
    assert count_stores(sample_df, "서교동", "커피전문점/카페/다방") == 2

def test_count_stores_different_district(sample_df):
    assert count_stores(sample_df, "합정동", "커피전문점/카페/다방") == 1

def test_count_stores_no_match(sample_df):
    assert count_stores(sample_df, "서교동", "한식음식점") == 0
