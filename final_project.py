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

# =========================
# 대시보드 소개 섹션
# =========================
st.markdown(
    f"""
    <div style="
        background-color:#F5F9FF;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 30px;
    ">
        <h2 style="text-align:center; color:#005BAC; margin-bottom:10px;">
            🧠 서울시 정신건강 데이터 대시보드
        </h2>
        <p style="text-align:center; font-size:17px; color:#333333; margin-bottom:20px;">
            서울시 공공데이터와 보건 통계를 기반으로, <b>정신건강 현황</b>을 한눈에 확인하고<br>
            <b>지역별 서비스 격차</b> 및 <b>질환별 진료 트렌드</b>를 분석하여
            데이터 기반 정책 의사결정을 지원합니다.
        </p>
        <hr style="border:1px solid #E5E5E5; margin:15px 0;">
        <div style="display:flex; justify-content:space-around; text-align:center; margin-top:20px;">
            <div style="flex:1; padding:10px;">
                <h4 style="color:#005BAC;">📊 종합 현황</h4>
                <p style="font-size:15px; color:#555;">서울시 및 전국의 진료 현황, 예산, 주요 질환 분석</p>
            </div>
            <div style="flex:1; padding:10px;">
                <h4 style="color:#78BE20;">📍 지역별 격차</h4>
                <p style="font-size:15px; color:#555;">자치구별 서비스 등록률 및 기관 현황 비교</p>
            </div>
            <div style="flex:1; padding:10px;">
                <h4 style="color:#F58220;">🩺 질환 트렌드</h4>
                <p style="font-size:15px; color:#555;">질환별 진료 인원 및 진료비 변화 분석</p>
            </div>
        </div>
    </div>
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
# [TAB 1] 개요 탭 (개선 버전)
# =====================================================
with tabs[0]:
    st.header("📌 국내 정신건강 현황 개요")

    # -----------------------------
    # 1. 데이터 로드
    # -----------------------------
    예산 = load_csv(files["예산"])
    진료정보 = load_csv(files["진료정보"])
    상병그룹 = load_csv(files["상병그룹"])
    등록관리율 = load_csv(files["등록관리율"])

    # -----------------------------
    # 2. 핵심 지표 계산
    # -----------------------------
    try:
        # 진료년도 전처리 (문자 → 숫자)
        상병그룹['진료년도'] = (
            상병그룹['진료년도']
            .astype(str)
            .str.replace("년", "", regex=False)
            .astype(int)
        )

        # 기간 범위 산출
        min_year = 상병그룹['진료년도'].min()
        max_year = 상병그룹['진료년도'].max()

        total_patients = 진료정보['진료인원(명)'].sum()
        top_disease = 진료정보.groupby('주상병명')['진료인원(명)'].sum().idxmax()
        avg_reg_rate = 등록관리율['추계중증정신질환자수 대비 정신건강복지센터 등록 중증정신질환자'].mean()
        mental_budget_ratio = 예산['보건 예산 대비 정신건강증진 예산 비중'].iloc[-1]
    except KeyError:
        st.error("⚠️ '개요' 탭에 필요한 컬럼명이 일치하지 않습니다.")
        st.stop()


    # ========================
    # KPI 카드 커스텀 스타일
    # ========================
    def kpi_card(title, value, description, color="#FFFFFF"):
        card_html = f"""
        <div style="background-color:#1E1E1E; padding:18px; border-radius:12px; text-align:center; 
                    box-shadow:0px 2px 8px rgba(0,0,0,0.3);">
            <h3 style="color:{color}; font-size:22px; font-weight:700; margin-bottom:6px;">{title}</h3>
            <p style="color:#A0A0A0; font-size:14px; margin:0 0 10px 0;">{description}</p>
            <h2 style="color:{color}; font-size:36px; font-weight:900; margin:0;">{value}</h2>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    # ========================
    # 3. KPI 카드 구성
    # ========================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card(
            title=f"👥 누적 진료 환자 수",
            value=f"{total_patients:,.0f} 명",
            description=f"정신질환으로 진료받은 전체 환자 수 ({min_year}~{max_year})"
        )
    with col2:
        kpi_card(
            title="🧩 가장 많은 정신 질환",
            value=top_disease,
            description="가장 많이 진료받은 정신 질환명"
        )
    with col3:
        kpi_card(
            title="📈 평균 등록률",
            value=f"{avg_reg_rate:.1f}%",
            description="중증정신질환자의 센터 등록률 평균"
        )
    with col4:
        kpi_card(
            title="💰 서울시 예산 비중",
            value=f"{mental_budget_ratio:.1f}%",
            description="보건 예산 대비 정신건강 예산 비중"
        )
    st.markdown("---")

    # -----------------------------
    # 4. 연도별 전체 진료 환자 수 추이
    # -----------------------------
    group_trend = 상병그룹.groupby(['진료년도'])['진료실인원(명)'].sum().reset_index()

    fig_trend = px.line(
        group_trend,
        x='진료년도',
        y='진료실인원(명)',
        title='연도별 전체 정신질환 진료 환자 수 추이',
        markers=True,
        color_discrete_sequence=["#005BAC"]
    )

    # 데이터 레이블 및 스타일 강화
    fig_trend.update_traces(
        line=dict(width=3),
        text=group_trend['진료실인원(명)'],
        textposition="top center"
    )
    fig_trend.update_layout(
        title={
            'text': '연도별 전체 정신질환 진료 환자 수 추이',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=22)
        },
        yaxis_title="진료 환자 수",
        xaxis_title="연도",
        template="plotly_white"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # -----------------------------
    # 5. 자동 인사이트 추가
    # -----------------------------
    recent_years = group_trend.tail(5)
    growth_rate = (
        (recent_years['진료실인원(명)'].iloc[-1] - recent_years['진료실인원(명)'].iloc[0])
        / recent_years['진료실인원(명)'].iloc[0]
    ) * 100

    st.info(
        f"최근 5년간 전체 정신질환 진료 환자 수는 약 **{growth_rate:.1f}%** 증가했습니다. "
        f"이는 정신건강 관리 및 예방 정책의 중요성을 시사합니다."
    )

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
