import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------
# 1️⃣ 기본 설정
# -----------------------------------
st.set_page_config(
    page_title="OTT 서비스 이용 비율 시각화",
    page_icon="📺",
    layout="wide"
)

st.title("📊 성별·연령별 OTT 서비스 이용 비율")
st.markdown("한국방송광고진흥공사 데이터 기반 시각화")

# -----------------------------------
# 2️⃣ 데이터 불러오기
# -----------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("한국방송광고진흥공사_성별 연령별 OTT 서비스 이용 비율_20250825.csv")
    return df

df = load_data()

# -----------------------------------
# 3️⃣ 컬럼 설명
# -----------------------------------
# 구분1 = 성별, 구분2 = 연령대
st.write("### 데이터 미리보기")
st.dataframe(df.head())

# -----------------------------------
# 4️⃣ 사용자 선택
# -----------------------------------
sexes = df['구분1'].unique().tolist()
ages = df['구분2'].unique().tolist()

selected_sex = st.sidebar.selectbox("성별 선택", sexes)
selected_age = st.sidebar.selectbox("연령대 선택", ages)

# -----------------------------------
# 5️⃣ 데이터 변환 (wide → long 형태)
# -----------------------------------
value_cols = [
    '유튜브', '넷플릭스', '티빙', '웨이브', 'SOOP(구 아프리카TV)',
    '카카오TV', '왓챠', '쿠팡플레이', 'NAVER TV(구 NOW)',
    '디즈니플러스', 'U플러스모바일TV', '애플TV플러스', '기타', 'OTT 비이용'
]

df_long = df.melt(
    id_vars=['연도', '구분1', '구분2'],
    value_vars=value_cols,
    var_name='OTT 서비스',
    value_name='이용비율'
)

# 선택된 필터 적용
filtered = df_long[(df_long['구분1'] == selected_sex) & (df_long['구분2'] == selected_age)]

# -----------------------------------
# 6️⃣ 막대 그래프 시각화
# -----------------------------------
st.subheader(f"📈 {selected_sex} / {selected_age} 의 OTT 서비스 이용 비율")

fig = px.bar(
    filtered,
    x='OTT 서비스',
    y='이용비율',
    color='OTT 서비스',
    text='이용비율',
    title=f"{selected_sex} / {selected_age} OTT 이용비율",
    labels={'이용비율': '이용 비율(%)'}
)
fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig.update_layout(showlegend=False, yaxis_title="이용 비율(%)", xaxis_title="OTT 서비스")
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# 7️⃣ 연령대별 추세선 (선 그래프)
# -----------------------------------
st.subheader("📊 연령대별 OTT 서비스 이용 추세 비교")

selected_services = st.multiselect("OTT 서비스 선택", value_cols, default=['유튜브', '넷플릭스', '티빙'])

filtered_age = df_long[
    (df_long['구분1'] == selected_sex) & 
    (df_long['OTT 서비스'].isin(selected_services))
]

fig2 = px.line(
    filtered_age,
    x='구분2',
    y='이용비율',
    color='OTT 서비스',
    markers=True,
    title=f"{selected_sex} 기준 연령대별 OTT 서비스 이용 추세"
)
fig2.update_layout(xaxis_title="연령대", yaxis_title="이용비율(%)")
st.plotly_chart(fig2, use_container_width=True)
