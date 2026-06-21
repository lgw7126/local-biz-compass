import os
import pandas as pd
import altair as alt
import streamlit as st
from dotenv import load_dotenv
from stores import load_stores, get_districts, count_stores
from weather import get_tomorrow_forecast, get_weekly_forecast
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

@st.cache_data(ttl=3600)
def fetch_weekly():
    return get_weekly_forecast(API_KEY)

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
    icon = weather.get("icon", "🌤️")
    with col2:
        st.metric(label="내일 강수확률", value=f"{weather['pop']}%")
    with col3:
        st.metric(
            label=f"내일 기온 {icon}",
            value=f"{weather['tmp_max']}°C",
            delta=f"최저 {weather['tmp_min']}°C",
        )
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

COLOR_MAP = {"green": "#1e8449", "orange": "#d35400", "red": "#c0392b"}
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

# 주간 날씨 그래프
st.markdown("<div style='margin-top:32px'></div>", unsafe_allow_html=True)
st.subheader("📅 1주일 날씨 예보")

weekly = fetch_weekly()
if weekly:
    wdf = pd.DataFrame(weekly)

    # 아이콘 행
    icon_cols = st.columns(len(wdf))
    for i, row in wdf.iterrows():
        with icon_cols[i]:
            st.markdown(
                f"<div style='text-align:center'>"
                f"<div style='font-size:22px'>{row['icon']}</div>"
                f"<div style='font-size:11px;color:#8892a4;margin-top:2px'>{row['date']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # 기온 범위 차트
    temp_area = alt.Chart(wdf).mark_area(
        opacity=0.25, color="#74b9ff",
        line={"color": "#74b9ff", "strokeWidth": 2}
    ).encode(
        x=alt.X("date:O", title="", axis=alt.Axis(labelColor="#8892a4", grid=False, domainColor="#2a3040", tickColor="#2a3040")),
        y=alt.Y("tmp_max:Q", title="기온 (°C)", scale=alt.Scale(zero=False),
                axis=alt.Axis(labelColor="#8892a4", gridColor="#2a3040", domainColor="#2a3040", titleColor="#8892a4")),
        y2="tmp_min:Q",
        tooltip=[
            alt.Tooltip("date:O", title="날짜"),
            alt.Tooltip("icon:N", title="날씨"),
            alt.Tooltip("tmp_max:Q", title="최고기온"),
            alt.Tooltip("tmp_min:Q", title="최저기온"),
            alt.Tooltip("pop:Q", title="강수확률(%)"),
        ]
    )

    pop_bars = alt.Chart(wdf).mark_bar(
        opacity=0.45, color="#e74c3c", cornerRadiusTopLeft=3, cornerRadiusTopRight=3
    ).encode(
        x=alt.X("date:O", title=""),
        y=alt.Y("pop:Q", title="강수확률 (%)", scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(labelColor="#8892a4", gridColor="#2a3040", domainColor="#2a3040", titleColor="#8892a4")),
        tooltip=[alt.Tooltip("pop:Q", title="강수확률(%)")]
    )

    chart = alt.layer(pop_bars, temp_area).resolve_scale(y="independent").properties(
        height=180,
        background="#12151f",
    ).configure_view(strokeWidth=0)

    st.altair_chart(chart, use_container_width=True)
else:
    st.caption("주간 날씨 정보를 불러올 수 없습니다.")
