"""화면 꾸미기(디자인) — 공공 복지 서비스 느낌의 파란색 톤 스타일입니다.

색상·글꼴·카드 모양을 한곳에 모아 두어, app.py는 기능 코드만 보이게 합니다.
"""

import base64
import html
from pathlib import Path

import streamlit as st

PRIMARY = "#1F5BD8"
PRIMARY_DARK = "#163F9E"
BORDER = "#DDE3EC"
MUTED = "#5B6575"

CSS = f"""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

html, body, .stApp, .stMarkdown, button, input, textarea, select {{
    font-family: 'Pretendard', -apple-system, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif !important;
}}
.block-container {{ max-width: 980px; padding-top: 2rem; }}
p, li, h1, h2, h3, h4, span, label, button {{ word-break: keep-all; }}
h1, h2, h3, h4 {{ letter-spacing: -0.02em; color: #1E2530; }}

/* 버튼 */
.stButton > button, .stFormSubmitButton > button {{
    border-radius: 10px; font-weight: 600; padding: 0.6rem 1rem;
}}

/* 테두리 있는 카드(st.container(border=True)) */
[data-testid="stVerticalBlockBorderWrapper"] {{
    background: #FFFFFF; border-radius: 14px !important; border-color: {BORDER} !important;
}}
[data-testid="stExpander"] details {{
    background: #FFFFFF; border-radius: 12px; border-color: {BORDER};
}}
[data-testid="stForm"] {{ background: #FFFFFF; border-radius: 14px; border-color: {BORDER}; }}
[data-testid="stMetric"] {{
    background: #FFFFFF; border: 1px solid {BORDER}; border-radius: 12px; padding: 14px 16px;
}}

/* 메인 상단 큰 안내 상자 */
.hero {{
    background: linear-gradient(135deg, {PRIMARY} 0%, #3D7EF2 100%);
    color: #FFFFFF; border-radius: 18px; padding: 36px 32px; margin-bottom: 24px;
}}
.hero .badge {{
    display: inline-block; background: rgba(255,255,255,0.18); border-radius: 999px;
    padding: 4px 12px; font-size: 13px; font-weight: 600; margin-bottom: 14px;
}}
.hero h1 {{ color: #FFFFFF; font-size: 32px; line-height: 1.3; margin: 0 0 10px 0; padding: 0; }}
.hero p {{ color: rgba(255,255,255,0.92); font-size: 17px; margin: 0; }}
.hero-row {{ display: flex; align-items: center; justify-content: space-between; gap: 24px; }}
.hero-logo {{ width: 112px; height: 112px; flex-shrink: 0; border-radius: 28px;
    border: 4px solid rgba(255, 255, 255, 0.9); background: #FFFFFF;
    box-shadow: 0 6px 18px rgba(10, 30, 80, 0.25); }}
@media (max-width: 640px) {{ .hero-logo {{ display: none; }} }}

/* 하위 화면 제목 띠 */
.page-head {{
    background: #FFFFFF; border: 1px solid {BORDER}; border-left: 6px solid {PRIMARY};
    border-radius: 14px; padding: 18px 22px; margin: 8px 0 18px 0;
}}
.page-head h2 {{ margin: 0 0 4px 0; padding: 0; font-size: 24px; }}
.page-head p {{ margin: 0; color: {MUTED}; font-size: 15px; }}

/* 서비스 메뉴 카드 */
.svc {{
    background: #FFFFFF; border: 1px solid {BORDER}; border-radius: 16px;
    padding: 22px 20px; min-height: 190px; margin-bottom: 10px;
}}
.svc .icon {{ font-size: 30px; }}
.svc h3 {{ font-size: 18px; margin: 8px 0 6px 0; padding: 0; }}
.svc p {{ color: {MUTED}; font-size: 14px; margin: 0; line-height: 1.5; }}

/* 작은 꼬리표(칩) */
.chip {{
    display: inline-block; border-radius: 999px; padding: 3px 10px; margin: 0 6px 6px 0;
    font-size: 12.5px; font-weight: 600; background: #EAF1FF; color: {PRIMARY_DARK};
}}
.chip.real {{ background: #E5F6EE; color: #0B7A52; }}
.chip.mock {{ background: #F0F2F5; color: #6B7280; }}
.chip.warn {{ background: #FFF1E3; color: #B45309; }}

/* 정책 카드 제목줄 */
.policy-head {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }}
.policy-head h4 {{ margin: 4px 0 0 0; padding: 0; font-size: 19px; }}
.score {{
    flex-shrink: 0; text-align: center; background: #EAF1FF; color: {PRIMARY_DARK};
    border-radius: 12px; padding: 8px 12px; font-weight: 700; font-size: 20px; line-height: 1.1;
}}
.score small {{ display: block; font-size: 11px; font-weight: 600; color: {MUTED}; }}

.section-title {{ font-size: 21px; font-weight: 700; margin: 28px 0 12px 0; }}
.notice {{ color: {MUTED}; font-size: 13px; }}
</style>
"""


def apply_style():
    """모든 화면에 공통 스타일을 적용합니다."""
    st.markdown(CSS, unsafe_allow_html=True)


def _e(text) -> str:
    """HTML에 넣을 글자를 안전하게 바꿉니다."""
    return html.escape(str(text))


def hero(title: str, slogan: str, logo_path=None):
    """메인 상단 안내 상자. logo_path가 있으면 오른쪽에 로고를 함께 보여줍니다."""
    logo_html = ""
    if logo_path and Path(logo_path).exists():
        data = base64.b64encode(Path(logo_path).read_bytes()).decode()
        logo_html = f'<img class="hero-logo" src="data:image/png;base64,{data}" alt="서비스 로고">'
    st.markdown(
        f'<div class="hero"><div class="hero-row"><div><span class="badge">부산 · 울산 · 경남</span>'
        f"<h1>{_e(title)}</h1><p>{_e(slogan)}</p></div>{logo_html}</div></div>",
        unsafe_allow_html=True,
    )


def page_head(title: str, description: str):
    st.markdown(
        f'<div class="page-head"><h2>{_e(title)}</h2><p>{_e(description)}</p></div>',
        unsafe_allow_html=True,
    )


def service_card(icon: str, title: str, description: str):
    st.markdown(
        f'<div class="svc"><div class="icon">{icon}</div><h3>{_e(title)}</h3><p>{_e(description)}</p></div>',
        unsafe_allow_html=True,
    )


def section_title(text: str):
    st.markdown(f'<div class="section-title">{_e(text)}</div>', unsafe_allow_html=True)


def chips(items: list[tuple[str, str]]) -> str:
    """[(글자, 종류)] 목록을 칩 HTML로 만듭니다. 종류: "", "real", "mock", "warn" """
    return "".join(f'<span class="chip {kind}">{_e(text)}</span>' for text, kind in items)


def policy_chips(row) -> str:
    area = f"{row['region']} 전체" if row["city"] == "전체" else f"{row['region']} {row['city']}"
    kind = ("🧪 테스트 데이터", "mock") if row["is_mock"] else ("✅ 실제 정책", "real")
    items = [(area, ""), (row["category"], ""), kind]
    if "마감" in str(row.get("status_note", "")) and "신청 가능" not in str(row.get("status_note", "")):
        items.append(("올해 접수 마감", "warn"))
    return chips(items)


def policy_head(row, score: int | None = None):
    """정책 카드 맨 위(칩 + 정책명 + 적합도 점수)를 그립니다."""
    score_html = f'<div class="score">{score}<small>적합도</small></div>' if score is not None else ""
    st.markdown(
        f'<div class="policy-head"><div>{policy_chips(row)}<h4>{_e(row["policy_name"])}</h4></div>{score_html}</div>',
        unsafe_allow_html=True,
    )
