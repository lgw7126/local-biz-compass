import os
import streamlit as st
from dotenv import load_dotenv
from stores import load_stores, get_districts, count_stores
from weather import get_tomorrow_forecast
from insight import get_insight

load_dotenv()

STORES_PATH = "mapo_stores.csv"
API_KEY = os.getenv("WEATHER_API_KEY", "")

st.set_page_config(page_title="동네상권 나침반", page_icon="🧭", layout="wide")

@st.cache_data
def load_data():
    return load_stores(STORES_PATH)

@st.cache_data(ttl=3600)
def fetch_weather():
    return get_tomorrow_forecast(API_KEY)

df = load_data()

with st.sidebar:
    st.title("🧭 내 가게 설정")
    districts = get_districts(df)
    district = st.selectbox("법정동", districts)
    categories = sorted(
        df[(df["법정동명"] == district) & (df["상권업종대분류명"] == "음식")]["상권업종소분류명"].dropna().unique().tolist()
    )
    category = st.selectbox("업종", categories)

st.title(f"동네상권 나침반 — 마포구 {district}")
st.caption("오늘의 장사, 데이터로 확인하세요.")

weather = fetch_weather()

col1, col2, col3 = st.columns(3)

store_count = count_stores(df, district, category)
with col1:
    st.metric(label=f"{category} 수", value=f"{store_count}개")

if weather:
    with col2:
        st.metric(label="내일 강수확률", value=f"{weather['pop']}%")
    with col3:
        st.metric(label="내일 기온", value=f"{weather['tmp_max']}°C",
                  delta=f"최저 {weather['tmp_min']}°C")
    insight = get_insight(weather["pop"])
else:
    with col2:
        st.metric(label="내일 강수확률", value="—")
    with col3:
        st.metric(label="내일 기온", value="—")
    insight = {
        "color": "orange",
        "message": "날씨 정보를 불러올 수 없습니다. 잠시 후 다시 시도해주세요.",
    }

COLOR_MAP = {
    "green": "#1e8449",
    "orange": "#d35400",
    "red": "#c0392b",
}
bg_color = COLOR_MAP[insight["color"]]

st.markdown(
    f"""
    <div style="background-color:{bg_color};padding:20px 24px;border-radius:10px;margin-top:16px">
        <p style="color:white;font-size:11px;margin:0 0 6px;opacity:0.8">오늘의 조언</p>
        <p style="color:white;font-size:16px;font-weight:600;margin:0;line-height:1.6">{insight['message']}</p>
    </div>
    """,
    unsafe_allow_html=True,
)
