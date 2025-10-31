# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# 앱 설정
# -----------------------
st.set_page_config(page_title="OTT 이용 비율 (성별·연령별)", page_icon="📺", layout="wide")
st.title("📊 한국방송광고진흥공사 — 성별 / 연령대별 OTT 서비스 이용 비율")

# -----------------------
# 데이터 불러오기
# -----------------------
@st.cache_data
def load_data(path="한국방송광고진흥공사_성별 연령별 OTT 서비스 이용 비율_20250825.csv"):
    df = pd.read_csv(path)
    return df

df = load_data()

st.write("### 데이터 미리보기")
st.dataframe(df.head())

# -----------------------
# 컬럼명 및 서비스 컬럼 자동 감지
# -----------------------
# 데이터 구조:
# - '구분1' : "성별" 또는 "연령별" (그룹 종류)
# - '구분2' : 실제 그룹값 (예: '남성','여성','13-19세','20대', ...)
# - 나머지 컬럼들 : 각 OTT 서비스의 이용 비율
group_col = '구분1'
group_value_col = '구분2'

# 서비스(비율) 컬럼들 추출 (연/구분 컬럼 제외)
service_cols = [c for c in df.columns if c not in ['연도', group_col, group_value_col, '사례수']]

# -----------------------
# 사이드바: 성별 / 연령대 선택 (각각 올바른 값만 노출)
# -----------------------
st.sidebar.header("필터 옵션 (정확히 분리됨)")

# 성별 옵션: df에서 구분1 == '성별' 인 행의 구분2 값들 (예: '남성', '여성')
sex_values = df[df[group_col] == '성별'][group_value_col].dropna().unique().tolist()
sex_values_sorted = sorted(sex_values)  # 정렬 (보통 ['남성','여성'])
sex_options = ['전체'] + sex_values_sorted
selected_sex = st.sidebar.selectbox("성별 선택", sex_options, index=0)

# 연령대 옵션: df에서 구분1 == '연령별' 인 행의 구분2 값들 (예: '13-19세','20대',...)
age_values = df[df[group_col] == '연령별'][group_value_col].dropna().unique().tolist()
# 연령 문자열 정렬을 보기 좋게 (숫자 기반 정렬 시도)
def age_sort_key(x):
    # '13-19세' -> 13, '20대' -> 20, '60대 ' -> 60
    import re
    m = re.search(r'\d{2,}', str(x))
    return int(m.group()) if m else 999
age_values_sorted = sorted(age_values, key=age_sort_key)
age_options = ['전체'] + age_values_sorted
selected_age = st.sidebar.selectbox("연령대 선택", age_options, index=0)

# 서비스 선택 (그래프에 표시할 서비스)
st.sidebar.markdown("---")
default_services = service_cols[:4] if len(service_cols) >= 4 else service_cols
selected_services = st.sidebar.multiselect("표시할 OTT 서비스 (최대 10개 권장)", service_cols, default=default_services)

# -----------------------
# 데이터 변형: wide -> long
# -----------------------
df_long = df.melt(
    id_vars=['연도', group_col, group_value_col],
    value_vars=service_cols,
    var_name='OTT 서비스',
    value_name='이용비율'
)

# 숫자형으로 변환 시도 (오류 대비)
df_long['이용비율'] = pd.to_numeric(df_long['이용비율'], errors='coerce')

# -----------------------
# 시각화: 성별 선택 결과 (막대그래프)
# -----------------------
st.subheader("성별 기준 OTT 이용 비율")
if selected_sex == '전체':
    st.info("성별별 전체 보기를 원하시면 아래 '성별 비교 (막대)'를 확인하세요.")
else:
    # 성별 필터 적용
    sex_df = df_long[(df_long[group_col] == '성별') & (df_long[group_value_col] == selected_sex)]
    if selected_services:
        sex_df = sex_df[sex_df['OTT 서비스'].isin(selected_services)]

    if sex_df.empty:
        st.warning("선택한 성별에 해당하는 데이터가 없습니다. (CSV의 값 확인 필요)")
    else:
        fig_sex = px.bar(
            sex_df,
            x='OTT 서비스',
            y='이용비율',
            color='OTT 서비스',
            text='이용비율',
            title=f"{selected_sex}의 OTT 서비스 이용 비율",
            labels={'이용비율': '이용 비율(%)'}
        )
        fig_sex.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_sex.update_layout(showlegend=False, yaxis_title="이용 비율(%)", xaxis_title="OTT 서비스")
        st.plotly_chart(fig_sex, use_container_width=True)

# -----------------------
# 시각화: 연령대 선택 결과 (막대그래프)
# -----------------------
st.subheader("연령대 기준 OTT 이용 비율")
if selected_age == '전체':
    st.info("연령대별 전체 보기를 원하시면 아래 '연령대 비교 (선)'을 확인하세요.")
else:
    age_df = df_long[(df_long[group_col] == '연령별') & (df_long[group_value_col] == selected_age)]
    if selected_services:
        age_df = age_df[age_df['OTT 서비스'].isin(selected_services)]

    if age_df.empty:
        st.warning("선택한 연령대에 해당하는 데이터가 없습니다. (CSV의 값 확인 필요)")
    else:
        fig_age = px.bar(
            age_df,
            x='OTT 서비스',
            y='이용비율',
            color='OTT 서비스',
            text='이용비율',
            title=f"{selected_age}의 OTT 서비스 이용 비율",
            labels={'이용비율': '이용 비율(%)'}
        )
        fig_age.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_age.update_layout(showlegend=False, yaxis_title="이용 비율(%)", xaxis_title="OTT 서비스")
        st.plotly_chart(fig_age, use_container_width=True)

# -----------------------
# 비교 시각화: 성별 비교(막대) & 연령대별 추세(선)
# -----------------------
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("성별 비교 (막대)")
    # 모든 '성별' 그룹(남성/여성)을 비교
    comp_sex_df = df_long[df_long[group_col] == '성별']
    if selected_services:
        comp_sex_df = comp_sex_df[comp_sex_df['OTT 서비스'].isin(selected_services)]
    if comp_sex_df.empty:
        st.warning("성별 비교용 데이터가 없습니다.")
    else:
        fig_comp_sex = px.bar(
            comp_sex_df,
            x=group_value_col,   # 남성/여성
            y='이용비율',
            color='OTT 서비스',
            barmode='group',
            title="성별별 OTT 이용비율 비교",
            labels={group_value_col: "성별", '이용비율': '이용 비율(%)'}
        )
        st.plotly_chart(fig_comp_sex, use_container_width=True)

with col2:
    st.subheader("연령대별 추세 (선)")
    comp_age_df = df_long[df_long[group_col] == '연령별']
    if selected_services:
        comp_age_df = comp_age_df[comp_age_df['OTT 서비스'].isin(selected_services)]
    if comp_age_df.empty:
        st.warning("연령대 비교용 데이터가 없습니다.")
    else:
        # 연령대 순서 보장: use categorical ordering from age_options (제대로 정렬됨)
        comp_age_df['구분2'] = pd.Categorical(comp_age_df[group_value_col], categories=age_values_sorted, ordered=True)
        fig_comp_age = px.line(
            comp_age_df,
            x=group_value_col,
            y='이용비율',
            color='OTT 서비스',
            markers=True,
            title="연령대별 OTT 서비스 이용 추세",
            labels={group_value_col: "연령대", '이용비율': '이용 비율(%)'}
        )
        fig_comp_age.update_layout(xaxis={'categoryorder':'array', 'categoryarray': age_values_sorted})
        st.plotly_chart(fig_comp_age, use_container_width=True)

# -----------------------
# 하단 안내
# -----------------------
st.markdown("---")
st.caption("데이터 출처: 한국방송광고진흥공사 (파일명: 한국방송광고진흥공사_성별 연령별 OTT 서비스 이용 비율_20250825.csv)")
