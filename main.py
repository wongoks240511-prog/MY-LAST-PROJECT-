import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------
# 1️⃣ 앱 기본 설정
# -----------------------------------
st.set_page_config(
    page_title="OTT 서비스 이용 비율 시각화",
    page_icon="📺",
    layout="wide"
)

st.title("📊 한국방송광고진흥공사 - 성별·연령별 OTT 서비스 이용 비율")
st.markdown("#### 데이터 기반으로 OTT 이용 비율을 시각화합니다.")

# -----------------------------------
# 2️⃣ 데이터 불러오기
# -----------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("한국방송광고진흥공사_성별 연령별 OTT 서비스 이용 비율_20250825.csv")
    return df

df = load_data()

st.write("### 데이터 미리보기")
st.dataframe(df.head())

# -----------------------------------
# 3️⃣ 컬럼 자동 인식 및 정리
# -----------------------------------
# 예시: 성별, 연령대, 서비스명, 이용비율 등의 컬럼이 있다고 가정
# (파일 컬럼명이 다르다면 실제 컬럼명을 출력해서 수정 가능)
st.write("### 데이터 컬럼 확인")
st.write(df.columns.tolist())

# -----------------------------------
# 4️⃣ 사용자 입력 위젯
# -----------------------------------
if '성별' in df.columns:
    genders = df['성별'].unique().tolist()
    selected_gender = st.sidebar.selectbox("성별 선택", genders)
else:
    selected_gender = None

if '연령대' in df.columns:
    ages = df['연령대'].unique().tolist()
    selected_age = st.sidebar.selectbox("연령대 선택", ages)
else:
    selected_age = None

if '서비스명' in df.columns:
    services = df['서비스명'].unique().tolist()
    selected_services = st.sidebar.multiselect("OTT 서비스 선택", services, default=services)
else:
    selected_services = None

# -----------------------------------
# 5️⃣ 필터 적용
# -----------------------------------
filtered_df = df.copy()

if selected_gender:
    filtered_df = filtered_df[filtered_df['성별'] == selected_gender]

if selected_age:
    filtered_df = filtered_df[filtered_df['연령대'] == selected_age]

if selected_services:
    filtered_df = filtered_df[filtered_df['서비스명'].isin(selected_services)]

# -----------------------------------
# 6️⃣ 시각화
# -----------------------------------
if '이용비율' in df.columns and '서비스명' in df.columns:
    fig = px.bar(
        filtered_df,
        x='서비스명',
        y='이용비율',
        color='서비스명',
        text='이용비율',
        title=f"{selected_gender or '전체'} / {selected_age or '전체'} 이용비율",
        labels={'이용비율': '이용 비율(%)', '서비스명': 'OTT 서비스'},
    )
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(xaxis_title="OTT 서비스", yaxis_title="이용비율(%)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ '서비스명' 또는 '이용비율' 컬럼이 데이터에 없습니다. CSV 컬럼명을 확인해주세요.")

# -----------------------------------
# 7️⃣ 추가 시각화: 연령대별 비교 (선택)
# -----------------------------------
if '연령대' in df.columns and '이용비율' in df.columns and '서비스명' in df.columns:
    st.write("### 연령대별 이용비율 비교")
    fig2 = px.line(
        df[df['서비스명'].isin(selected_services)],
        x='연령대',
        y='이용비율',
        color='서비스명',
        markers=True,
        title="연령대별 OTT 서비스 이용 추세"
    )
    st.plotly_chart(fig2, use_container_width=True)
