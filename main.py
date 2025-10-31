import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# 1. 기본 설정
# -------------------------------
st.set_page_config(page_title="OTT 서비스 이용 비율 시각화", layout="wide")

st.title("🎬 성별·연령별 OTT 서비스 이용 비율 시각화")
st.markdown("한국방송광고진흥공사 데이터 기반 시각화 (2025-08-25)")

# -------------------------------
# 2. 데이터 불러오기
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("한국방송광고진흥공사_성별 연령별 OTT 서비스 이용 비율_20250825.csv")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ CSV 파일을 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

st.subheader("📁 원본 데이터 미리보기")
st.dataframe(df.head())

# -------------------------------
# 3. 데이터 구조 파악
# -------------------------------
st.markdown("#### 데이터 기본 정보")
st.write(df.describe(include="all"))

# -------------------------------
# 4. 필터 설정
# -------------------------------
st.sidebar.header("🔍 필터 선택")

# 자동으로 컬럼명 탐색
columns = df.columns.tolist()

# 성별 및 연령 관련 컬럼 자동 추출
gender_col = next((col for col in columns if "성별" in col), None)
age_col = next((col for col in columns if "연령" in col), None)
ott_col = next((col for col in columns if "OTT" in col or "서비스" in col), None)

# 유효성 확인
if not gender_col or not age_col:
    st.error("⚠️ '성별' 또는 '연령' 관련 컬럼을 찾을 수 없습니다. CSV 파일의 헤더를 확인해주세요.")
    st.stop()

# 필터 위젯
selected_gender = st.sidebar.multiselect(
    "성별 선택",
    options=df[gender_col].unique().tolist(),
    default=df[gender_col].unique().tolist()
)

selected_ages = st.sidebar.multiselect(
    "연령대 선택",
    options=df[age_col].unique().tolist(),
    default=df[age_col].unique().tolist()
)

# 필터 적용
filtered_df = df[df[gender_col].isin(selected_gender) & df[age_col].isin(selected_ages)]

# -------------------------------
# 5. Plotly 시각화
# -------------------------------
st.subheader("📊 OTT 서비스 이용 비율 시각화")

numeric_cols = df.select_dtypes(include=["float", "int"]).columns.tolist()

if not numeric_cols:
    st.warning("⚠️ 시각화할 수 있는 수치형 컬럼이 없습니다.")
else:
    y_col = st.selectbox("시각화할 지표 선택", numeric_cols)
    
    fig = px.bar(
        filtered_df,
        x=age_col,
        y=y_col,
        color=gender_col,
        barmode="group",
        text_auto=".1f",
        title=f"{y_col} - 성별·연령별 비교",
        labels={age_col: "연령대", y_col: y_col, gender_col: "성별"}
    )
    fig.update_layout(
        xaxis_title="연령대",
        yaxis_title=y_col,
        legend_title="성별",
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 6. 추가 분석 (선택 기능)
# -------------------------------
with st.expander("📈 추가 분석 보기"):
    avg_df = df.groupby(gender_col)[numeric_cols].mean().reset_index()
    fig2 = px.bar(
        avg_df,
        x=gender_col,
        y=numeric_cols[0],
        text_auto=".2f",
        title="성별 평균 이용률 비교"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("✅ **완료:** OTT 이용률 데이터를 시각화했습니다!")
