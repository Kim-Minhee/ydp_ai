import os
import pandas as pd
import streamlit as st
import plotly.express as px

# =========================
# 1. 데이터 경로 설정
# =========================
DATA_PATH = os.path.join(os.path.dirname(__file__), "cleaned")

files = {
    "등록관리율": os.path.join(DATA_PATH, "등록관리율.csv"),
    "기관현황": os.path.join(DATA_PATH, "기관현황.csv"),
    "예산": os.path.join(DATA_PATH, "예산.csv"),
    "진료정보": os.path.join(DATA_PATH, "진료정보.csv"),
    "상병그룹": os.path.join(DATA_PATH, "상병그룹.csv"),
    "주관적건강": os.path.join(DATA_PATH, "주관적건강.csv"),
    "알코올사망": os.path.join(DATA_PATH, "알코올사망.csv")
}

# =========================
# 2. 캐시 적용된 데이터 로드 함수
# =========================
@st.cache_data
def load_csv(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.warning(f"⚠️ {os.path.basename(path)} 로드 실패: {e}")
        return pd.DataFrame()

# =========================
# 3. Streamlit 페이지 설정
# =========================
st.set_page_config(
    page_title="서울시 정신건강 데이터 대시보드",
    page_icon="🧠",
    layout="wide"
)

st.markdown(
    """
    <h1 style='text-align: center; color: #005BAC;'>🧠 서울시 정신건강 데이터 대시보드</h1>
    <p style='text-align: center; color: #6E6E6E; font-size:16px'>
    서울시 공공데이터 기반으로 정신건강 현황과 정책 방향을 시각화합니다.
    </p>
    """,
    unsafe_allow_html=True
)

# =========================
# 4. 탭 구성
# =========================
tabs = st.tabs([
    "개요",
    "지역별 서비스 격차",
    "질환별 진료 트렌드",
    "위험 요인 및 인식"
])

# =====================================================
# [TAB 1] 개요 탭
# =====================================================
with tabs[0]:
    st.header("📌 국내 정신건강 현황 개요")
    st.markdown("서울시 및 전국 정신건강 데이터를 기반으로 핵심 지표를 요약하고, 주요 트렌드를 시각화합니다.")

    예산 = load_csv(files["예산"])
    진료정보 = load_csv(files["진료정보"])
    상병그룹 = load_csv(files["상병그룹"])
    등록관리율 = load_csv(files["등록관리율"])

    try:
        total_patients = 진료정보['진료인원(명)'].sum()
        top_disease = 진료정보.groupby('주상병명')['진료인원(명)'].sum().idxmax()
        avg_reg_rate = 등록관리율['추계중증정신질환자수 대비 정신건강복지센터 등록 중증정신질환자'].mean()
        mental_budget_ratio = 예산['보건 예산 대비 정신건강증진 예산 비중'].iloc[-1]
    except KeyError:
        st.error("⚠️ '개요' 탭에 필요한 컬럼명이 일치하지 않습니다.")
        st.stop()

    # KPI 카드
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("전체 진료환자 수", f"{total_patients:,.0f} 명")
    kpi2.metric("가장 많은 진료 질환", top_disease)
    kpi3.metric("평균 등록률", f"{avg_reg_rate:.1f}%")
    kpi4.metric("서울시 정신건강 예산 비중", f"{mental_budget_ratio:.1f}%")

    st.markdown("---")

    # 연도별 전체 진료 환자 수 추이
    group_trend = 상병그룹.groupby(['진료년도'])['진료실인원(명)'].sum().reset_index()
    fig_trend = px.line(
        group_trend,
        x='진료년도',
        y='진료실인원(명)',
        title='연도별 전체 정신질환 진료 환자 수 추이',
        markers=True
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# =====================================================
# [TAB 2] 지역별 서비스 격차 분석
# =====================================================
with tabs[1]:
    st.header("📍 지역별 서비스 격차 분석")
    등록관리율 = load_csv(files["등록관리율"])
    기관현황 = load_csv(files["기관현황"])

    # 등록률 상위 5개 및 하위 5개 지역 비교
    reg_rate = 등록관리율[['지역명', '추계중증정신질환자수 대비 정신건강복지센터 등록 중증정신질환자']]
    top_bottom = pd.concat([
        reg_rate.sort_values(by=reg_rate.columns[1], ascending=False).head(5),
        reg_rate.sort_values(by=reg_rate.columns[1], ascending=True).head(5)
    ])
    fig_reg = px.bar(
        top_bottom,
        x='지역명',
        y=reg_rate.columns[1],
        color=reg_rate.columns[1],
        color_continuous_scale='Blues',
        title="중증정신질환자 등록률 상위·하위 5개 지역"
    )
    st.plotly_chart(fig_reg, use_container_width=True)

    # 자치구별 기관 수 비교
    org_count = 기관현황[['지역명', '합계']].sort_values(by='합계', ascending=False)
    fig_org = px.bar(
        org_count,
        x='지역명',
        y='합계',
        title='자치구별 정신건강증진기관 수',
        color='합계',
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig_org, use_container_width=True)

# =====================================================
# [TAB 3] 질환별 진료 트렌드 분석
# =====================================================
with tabs[2]:
    st.header("🩺 질환별 진료 트렌드")
    진료정보 = load_csv(files["진료정보"])

    top_diseases = (
        진료정보
        .groupby('주상병명')['진료인원(명)']
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .index.tolist()
    )
    trend_df = 진료정보[진료정보['주상병명'].isin(top_diseases)]
    fig_disease_trend = px.line(
        trend_df,
        x='진료년월',
        y='진료인원(명)',
        color='주상병명',
        title="주요 질환별 진료인원 추이"
    )
    st.plotly_chart(fig_disease_trend, use_container_width=True)

# =====================================================
# [TAB 4] 위험 요인 및 정신건강 인식
# =====================================================
with tabs[3]:
    st.header("⚠️ 위험 요인 및 정신건강 인식")
    알코올사망 = load_csv(files["알코올사망"])
    주관적건강 = load_csv(files["주관적건강"])

    col1, col2 = st.columns(2)
    fig_alcohol = px.line(
        알코올사망[알코올사망['구분'] == '사망자수'],
        x='연도',
        y='계',
        title='연도별 알코올 관련 사망자수'
    )
    col1.plotly_chart(fig_alcohol, use_container_width=True)

    fig_health = px.line(
        주관적건강,
        x='연도',
        y=['좋은편', '보통', '좋지않은편'],
        title='서울시민 주관적 정신건강 수준 변화'
    )
    col2.plotly_chart(fig_health, use_container_width=True)

