# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# 🔧 기본 설정
# -----------------------
st.set_page_config(
    page_title="Netflix 감성 OTT 이용 비율 시각화",
    page_icon="🎬",
    layout="wide",
)

# -----------------------
# 🎨 넷플릭스 감성 스타일 적용 (CSS)
# -----------------------
st.markdown("""
    <style>
    /* 전체 배경 & 글자 */
    .main {
        background-color: #141414;
        color: #FFFFFF;
        font-family: 'Pretendard', sans-serif;
    }
    /* 제목 스타일 */
    .stTitle {
        color: #E50914;
        font-weight: 800;
        font-size: 2.3rem !important;
    }
    h2, h3, h4 {
        color: #E50914;
    }
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #1f1f1f;
        color: white;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: #E5E5E5 !important;
        font-weight: 600;
    }
    /* 구분선 */
    hr {
        border: 1px solid #E50914;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------
# 🎬 타이틀 & 소개
# -----------------------
st.title("🎬 성별·연령별 OTT 서비스 이용 비율 대시보드")
st.markdown("##### 넷플릭스 감성으로 보는 대한민국 OTT 소비 패턴 분석 📊")
st.markdown("---")

# -----------------------
# 📂 데이터 불러오기
# -----------------------
@st.cache_data
def load_data(path="한국방송광고진흥공사_성별 연령별 OTT 서비스 이용 비율_20250825.csv"):
    df = pd.read_csv(path)
    return df

df = load_data()

# -----------------------
# 📊 데이터 컬럼 확인
# -----------------------
group_col = '구분1'
group_value_col = '구분2'
service_cols = [c for c in df.columns if c not in ['연도', group_col, group_value_col, '사례수']]

# -----------------------
# 🧩 사이드바 설정
# -----------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", use_container_width=True)
st.sidebar.header("🎯 필터 선택")

sex_values = sorted(df[df[group_col] == '성별'][group_value_col].dropna().unique().tolist())
age_values = df[df[group_col] == '연령별'][group_value_col].dropna().unique().tolist()

# 연령대 정렬 함수
import re
def age_sort_key(x):
    m = re.search(r'\d{2,}', str(x))
    return int(m.group()) if m else 999

age_values_sorted = sorted(age_values, key=age_sort_key)

selected_sex = st.sidebar.selectbox("성별 선택", ['전체'] + sex_values)
selected_age = st.sidebar.selectbox("연령대 선택", ['전체'] + age_values_sorted)

default_services = service_cols[:4] if len(service_cols) >= 4 else service_cols
selected_services = st.sidebar.multiselect("OTT 서비스 선택", service_cols, default=default_services)

# -----------------------
# 🔄 데이터 변형
# -----------------------
df_long = df.melt(
    id_vars=['연도', group_col, group_value_col],
    value_vars=service_cols,
    var_name='OTT 서비스',
    value_name='이용비율'
)
df_long['이용비율'] = pd.to_numeric(df_long['이용비율'], errors='coerce')

# -----------------------
# 🎥 Plotly 테마 공통 설정
# -----------------------
plotly_dark_template = dict(
    plot_bgcolor="#141414",
    paper_bgcolor="#141414",
    font=dict(family="Pretendard", color="white"),
    title_font=dict(size=20, color="#E50914", family="Pretendard"),
)

# -----------------------
# 🎯 성별 시각화
# -----------------------
st.subheader("👫 성별 기준 OTT 이용 비율")
if selected_sex != '전체':
    sex_df = df_long[(df_long[group_col] == '성별') & (df_long[group_value_col] == selected_sex)]
    if selected_services:
        sex_df = sex_df[sex_df['OTT 서비스'].isin(selected_services)]

    fig_sex = px.bar(
        sex_df,
        x='OTT 서비스',
        y='이용비율',
        color='OTT 서비스',
        text='이용비율',
        title=f"🎬 {selected_sex}의 OTT 이용 비율",
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    fig_sex.update_layout(**plotly_dark_template)
    fig_sex.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_sex, use_container_width=True)
else:
    st.info("성별을 선택하면 해당 그룹의 그래프가 표시됩니다.")

# -----------------------
# 🎯 연령대 시각화
# -----------------------
st.subheader("👶 연령대 기준 OTT 이용 비율")
if selected_age != '전체':
    age_df = df_long[(df_long[group_col] == '연령별') & (df_long[group_value_col] == selected_age)]
    if selected_services:

