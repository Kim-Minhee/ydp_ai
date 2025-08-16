import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(page_title="시각화 대시보드 (엑셀 업로드)", layout="wide")

st.title("📊 시각화 대시보드")
st.caption("엑셀 파일(.xlsx/.xls)을 업로드하면 5개의 차트를 자동 생성합니다. 다크 모드에 최적화된 팔레트를 사용합니다.")

# --- Sidebar ---
st.sidebar.header("설정")
theme_template = st.sidebar.selectbox("Plotly 테마", ["plotly_dark", "plotly", "ggplot2", "seaborn"], index=0)
color_yellow = "#FFCE56"  # 노란색
color_green  = "#4BC0C0"  # 민트/그린
color_lime   = "#99FF33"  # 라임
color_orange = "#FF9F40"  # 오렌지
color_blue   = "#36A2EB"  # 파랑

uploaded = st.file_uploader("엑셀 파일 업로드", type=["xlsx", "xls"], help="시트명: 바차트_히스토그램, 시계열차트, 파이차트, 산점도, 파레토차트")

@st.cache_data(show_spinner=False)
def load_excel(file: BytesIO):
    xls = pd.ExcelFile(file)
    sheets = {name: xls.parse(name) for name in xls.sheet_names}
    return sheets, xls.sheet_names

if not uploaded:
    st.info("좌측 또는 위의 업로더에서 파일을 선택하세요. 샘플 시트명은 `바차트_히스토그램`, `시계열차트`, `파이차트`, `산점도`, `파레토차트` 입니다.")
    st.stop()

sheets, sheet_names = load_excel(uploaded)
required = ["바차트_히스토그램", "시계열차트", "파이차트", "산점도", "파레토차트"]
missing = [s for s in required if s not in sheet_names]
if missing:
    st.warning(f"다음 시트가 누락되었습니다: {', '.join(missing)}. 있는 시트만 표시합니다.")

# --- Helper functions ---
def to_datetime_safe(series):
    try:
        s = pd.to_datetime(series)
        return s
    except Exception:
        return series

# --- 1) 바차트_히스토그램: 월별 총 매출 ---
if "바차트_히스토그램" in sheets:
    df_bar = sheets["바차트_히스토그램"].copy()
    # 기대 컬럼: 월, 총 매출
    if "월" in df_bar.columns and "총 매출" in df_bar.columns:
        df_bar["월"] = to_datetime_safe(df_bar["월"]).dt.strftime("%Y-%m")
        fig_bar = px.bar(
            df_bar, x="월", y="총 매출", title="월별 총 매출",
            template=theme_template, color_discrete_sequence=[color_yellow]
        )
        fig_bar.update_traces(hovertemplate="%{x}<br>총 매출: %{y:,}")
        fig_bar.update_layout(margin=dict(l=10,r=10,t=60,b=10))
    else:
        fig_bar = go.Figure().add_annotation(text="'월' 또는 '총 매출' 컬럼이 없습니다.", showarrow=False)
        fig_bar.update_layout(template=theme_template)
else:
    fig_bar = go.Figure().add_annotation(text="바차트_히스토그램 시트 없음", showarrow=False)
    fig_bar.update_layout(template=theme_template)

# --- 2) 시계열차트: 첫 두 열 사용 ---
if "시계열차트" in sheets:
    df_line = sheets["시계열차트"].copy()
    if df_line.shape[1] >= 2:
        xcol, ycol = df_line.columns[:2]
        df_line[xcol] = to_datetime_safe(df_line[xcol]).dt.strftime("%Y-%m")
        fig_line = px.line(
            df_line, x=xcol, y=ycol, markers=True, title="시계열 추세",
            template=theme_template, color_discrete_sequence=[color_green]
        )
        fig_line.update_traces(hovertemplate=f"%{{x}}<br>{ycol}: %{{y:,}}")
        fig_line.update_layout(margin=dict(l=10,r=10,t=60,b=10))
    else:
        fig_line = go.Figure().add_annotation(text="시계열차트 시트에 최소 2개 열이 필요합니다.", showarrow=False)
        fig_line.update_layout(template=theme_template)
else:
    fig_line = go.Figure().add_annotation(text="시계열차트 시트 없음", showarrow=False)
    fig_line.update_layout(template=theme_template)

# --- 3) 파이차트: 첫 열=라벨, 둘째=값 ---
if "파이차트" in sheets:
    df_pie = sheets["파이차트"].copy()
    if df_pie.shape[1] >= 2:
        lcol, vcol = df_pie.columns[:2]
        fig_pie = px.pie(
            df_pie, names=lcol, values=vcol, title="비율 분석",
            template=theme_template, color_discrete_sequence=[color_yellow, color_green, color_orange, color_blue, color_lime]
        )
        fig_pie.update_traces(textposition="inside", insidetextorientation="auto", textinfo="percent+label")
        fig_pie.update_layout(margin=dict(l=10,r=10,t=60,b=10))
    else:
        fig_pie = go.Figure().add_annotation(text="파이차트 시트에 최소 2개 열이 필요합니다.", showarrow=False)
        fig_pie.update_layout(template=theme_template)
else:
    fig_pie = go.Figure().add_annotation(text="파이차트 시트 없음", showarrow=False)
    fig_pie.update_layout(template=theme_template)

# --- 4) 산점도: 첫 두 열 사용, 마커 강조 ---
if "산점도" in sheets:
    df_sc = sheets["산점도"].copy()
    if df_sc.shape[1] >= 2:
        xsc, ysc = df_sc.columns[:2]
        fig_scatter = px.scatter(
            df_sc, x=xsc, y=ysc, title="산점도 분석",
            template=theme_template, color_discrete_sequence=[color_lime]
        )
        fig_scatter.update_traces(marker=dict(size=10, line=dict(width=1.5, color="#FFFFFF")))
        fig_scatter.update_layout(margin=dict(l=10,r=10,t=60,b=10))
    else:
        fig_scatter = go.Figure().add_annotation(text="산점도 시트에 최소 2개 열이 필요합니다.", showarrow=False)
        fig_scatter.update_layout(template=theme_template)
else:
    fig_scatter = go.Figure().add_annotation(text="산점도 시트 없음", showarrow=False)
    fig_scatter.update_layout(template=theme_template)

# --- 5) 파레토: 첫 열=라벨, 둘째=값 + 누적비율 라인 ---
if "파레토차트" in sheets:
    df_pa = sheets["파레토차트"].copy()
    if df_pa.shape[1] >= 2:
        lcol, vcol = df_pa.columns[:2]
        dfp = df_pa[[lcol, vcol]].dropna().copy()
        dfp = dfp.sort_values(vcol, ascending=False)
        dfp["누적비율(%)"] = (dfp[vcol].cumsum() / dfp[vcol].sum() * 100).round(2)

        fig_pareto = go.Figure()
        fig_pareto.add_bar(x=dfp[lcol], y=dfp[vcol], name="값", marker_color=color_orange, yaxis="y")
        fig_pareto.add_trace(go.Scatter(x=dfp[lcol], y=dfp["누적비율(%)"], name="누적 비율(%)",
                                        mode="lines+markers", line=dict(color=color_green, width=2), yaxis="y2"))
        fig_pareto.update_layout(
            template=theme_template, title="파레토 차트",
            yaxis=dict(title="값"),
            yaxis2=dict(title="누적 비율(%)", overlaying="y", side="right", range=[0, 100]),
            margin=dict(l=10,r=10,t=60,b=10)
        )
    else:
        fig_pareto = go.Figure().add_annotation(text="파레토차트 시트에 최소 2개 열이 필요합니다.", showarrow=False)
        fig_pareto.update_layout(template=theme_template)
else:
    fig_pareto = go.Figure().add_annotation(text="파레토차트 시트 없음", showarrow=False)
    fig_pareto.update_layout(template=theme_template)

# --- Layout: 2 x 2 + 1 ---
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_bar, use_container_width=True)
with col2:
    st.plotly_chart(fig_line, use_container_width=True)
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig_pie, use_container_width=True)
with col4:
    st.plotly_chart(fig_scatter, use_container_width=True)

st.plotly_chart(fig_pareto, use_container_width=True)

# --- Optional: 데이터 미리보기 ---
with st.expander("원시 데이터 미리보기", expanded=False):
    for name in sheet_names:
        st.subheader(name)
        st.dataframe(sheets[name], use_container_width=True)

# --- (선택) 이미지 저장 기능: kaleido 필요 ---
# def fig_to_png_bytes(fig):
#     return fig.to_image(format="png", scale=2)
# if st.sidebar.button("모든 차트 PNG로 저장"):
#     try:
#         for n, fg in {"bar": fig_bar, "line": fig_line, "pie": fig_pie, "scatter": fig_scatter, "pareto": fig_pareto}.items():
#             png = fig_to_png_bytes(fg)
#             st.sidebar.download_button(label=f"다운로드 {n}.png", data=png, file_name=f"{n}.png", mime="image/png")
#     except Exception as e:
#         st.sidebar.warning("PNG 내보내기에는 kaleido 패키지가 필요합니다: pip install -U kaleido")
