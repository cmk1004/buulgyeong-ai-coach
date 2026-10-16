"""부울경 생활비 절감·복지혜택 AI 코치 — STEP 5 MVP (+ 디자인 개선)

실행: streamlit run app.py
"""

import plotly.express as px
import streamlit as st

from src import ui
from src.data_loader import load_expense_benchmarks, load_glossary, load_policies, load_saving_tips
from src.easy_explain import find_terms, original_text
from src.local_policies import count_by_region_and_category, filter_local_policies
from src.recommender import count_good_matches, income_percent, recommend_policies
from src.saving_coach import CATEGORIES, check_expenses

st.set_page_config(page_title="부울경 생활비·복지 AI 코치", page_icon="💰", layout="centered")
ui.apply_style()

TITLE = "부울경 생활비 절감·복지혜택 AI 코치"
SLOGAN = "내가 아낄 수 있는 생활비와 받을 수 있는 지원금, AI가 한 번에 찾아드립니다."

REGIONS = {
    "부산": ["해운대구", "부산진구", "사하구", "동래구", "남구", "북구", "기타"],
    "울산": ["남구", "중구", "동구", "북구", "울주군"],
    "경남": ["창원시", "김해시", "진주시", "양산시", "거제시", "통영시", "창녕군", "기타"],
}
HOUSEHOLD_TYPES = ["1인가구", "부부가구", "자녀가구", "한부모가구", "기타"]
HOUSING_TYPES = ["자가", "전세", "월세", "공공임대", "기타"]
INTERESTS = ["고령층", "1인가구", "생활비", "의료", "주거", "청년", "출산·육아", "일자리"]

MOCK_NOTICE = "✅ 표시는 출처를 확인한 실제 정책, 🧪 표시는 테스트용 가상 데이터(is_mock=True)입니다. 실제 신청 전에는 원문을 꼭 확인하세요."
SCORE_NOTICE = "AI 적합도는 추천 우선순위이며 실제 지원 대상 여부를 확정하지 않습니다."


# 데이터는 한 번만 읽고 재사용합니다.
@st.cache_data
def get_policies():
    return load_policies()


@st.cache_data
def get_saving_tips():
    return load_saving_tips()


@st.cache_data
def get_benchmarks():
    return load_expense_benchmarks()


def data_badge(row):
    """정책이 실제인지 테스트용인지 표시합니다."""
    if row["is_mock"]:
        st.caption("🧪 테스트용 가상 데이터")
    else:
        if row["status_note"]:
            st.write(f"**참고**: {row['status_note']}")
        st.caption(f"✅ 실제 정책 · 2026-10-16 확인 · [원문 보기]({row['source_url']})")


@st.cache_data
def get_glossary():
    return load_glossary()


def easy_explanation(row):
    """공고 내용(왼쪽)과 쉬운 설명(오른쪽)을 나란히 보여줍니다."""
    original = original_text(row)
    left, right = st.columns(2)
    with left:
        st.markdown("**📄 공고 내용**")
        st.markdown("\n".join(f"- {line}" for line in original.split("\n")))
    with right:
        st.markdown("**🗣️ 쉬운 설명**")
        st.info(row["easy_text"])

    terms = find_terms(original + row["easy_text"], get_glossary())
    if terms:
        st.markdown("**📖 어려운 말 풀이**")
        for term, meaning in terms:
            st.write(f"- **{term}**: {meaning}")


def easy_button(row):
    """추천 카드 안에서 '쉽게 설명 보기'를 펼쳐 볼 수 있게 합니다."""
    if row["easy_text"]:
        with st.expander("🗣️ 쉽게 설명 보기"):
            easy_explanation(row)


def real_only_toggle(key: str) -> bool:
    return st.toggle("실제 정책만 보기", value=False, key=key, help="켜면 테스트용 가상 데이터를 빼고 보여 줍니다.")


def expense_inputs() -> dict:
    """통신비·공공요금·보험료 입력칸(선택)을 보여주고, 원 단위로 돌려줍니다."""
    st.write("**현재 월 지출(선택 입력, 만원)** — 0이면 비교하지 않습니다.")
    cols = st.columns(3)
    labels = {"통신비": "통신비(휴대폰·인터넷)", "공공요금": "공공요금(전기·가스·수도)", "보험료": "보험료(민간보험)"}
    expenses = {}
    for col, category in zip(cols, CATEGORIES):
        value = col.number_input(labels[category], min_value=0.0, max_value=500.0, value=0.0, step=0.5, format="%.1f")
        expenses[category] = int(value * 10_000)
    return expenses


def show_saving_results(results: list[dict]):
    """생활비 절감 카드(항목별 확인 필요/양호)를 보여줍니다."""
    if not results:
        st.write("입력한 지출이 없어 생활비 비교는 건너뛰었습니다.")
        return

    for item in results:
        with st.container(border=True):
            if item["status"] == "확인 필요":
                badge = ui.chips([("🔶 확인 필요", "warn")])
            else:
                badge = ui.chips([("✅ 양호", "real")])
            st.markdown(f"{badge}<h4 style='margin:2px 0 8px 0;padding:0'>{item['category']}</h4>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("내 지출", f"{item['amount']:,}원")
            col2.metric("비슷한 가구 평균", f"{item['average']:,}원")
            col3.metric("저렴한 대안 기준", f"{item['low']:,}원")
            if item["status"] == "확인 필요":
                st.write(f"평균보다 **{item['amount'] - item['average']:,}원** 더 쓰고 있습니다. "
                         f"저렴한 대안으로 바꾸면 월 최대 **{item['saving']:,}원**을 아낄 수 있습니다(참고용).")
                st.write("**이렇게 해 보세요**")
                for tip in item["tips"]:
                    st.write(f"- {tip}")
            else:
                st.write("비슷한 가구 평균 이하로 잘 관리하고 있습니다.")

    if get_benchmarks()["is_mock"].any():
        st.caption("🧪 비교 기준값은 테스트용 가상 데이터입니다. 절감액은 참고용입니다.")
    else:
        st.caption(
            "📊 평균: 통계청 2025년 가계동향조사 가구원수별 월평균 지출"
            "([KOSIS](https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1L9U105)). "
            "통신비=통신서비스, 공공요금=연료비+상하수도, 보험료=민간보험(미가입 가구 포함 평균). "
            "저렴한 대안 기준은 소득 1분위/전체 평균 비율을 곱한 앱 자체 가정이며, 절감액은 참고용입니다."
        )


# 지금 어떤 화면을 보여줄지 기억합니다.
if "page" not in st.session_state:
    st.session_state.page = "main"


def go(page: str):
    st.session_state.page = page


def back_button():
    st.button("← 처음으로", on_click=go, args=("main",))


# ---------------- 메인 화면 ----------------
def go_category(category: str):
    """'자주 찾는 분야'를 누르면 그 분야로 걸러진 우리동네 화면으로 갑니다."""
    st.session_state["local_categories"] = [category]
    st.session_state.page = "local"


CATEGORY_ICONS = {
    "고령층": "👵", "1인가구": "🏠", "생활비": "💳", "의료": "🏥",
    "주거": "🔑", "청년": "🎓", "출산·육아": "👶", "일자리": "💼",
}


def main_page():
    ui.hero(TITLE, SLOGAN)

    services = [
        ("🎯", "AI 맞춤 지원금 찾기", "나이·소득·가구형태를 입력하면 받을 수 있는 지원제도를 적합도 순으로 추천합니다.", "input"),
        ("✂️", "AI 생활비 절감 코치", "통신비·공공요금·보험료를 비슷한 가구 평균과 비교해 아낄 곳을 찾습니다.", "saving"),
        ("📍", "우리동네 지원사업", "부산·울산·경남 지역을 고르면 우리 동네 지원사업만 모아 봅니다.", "local"),
    ]
    for col, (icon, title, desc, page) in zip(st.columns(3), services):
        with col:
            ui.service_card(icon, title, desc)
            st.button("바로가기 →", key=f"go_{page}", on_click=go, args=(page,),
                      use_container_width=True, type="primary" if page == "input" else "secondary")

    ui.section_title("자주 찾는 분야")
    for i, col in enumerate(st.columns(4) + st.columns(4)):
        category = INTERESTS[i]
        col.button(f"{CATEGORY_ICONS[category]} {category}", key=f"cat_{category}",
                   on_click=go_category, args=(category,), use_container_width=True)

    st.markdown(f'<p class="notice">{MOCK_NOTICE}</p>', unsafe_allow_html=True)


# ---------------- 입력 화면 + 추천 결과 ----------------
def input_page():
    back_button()
    ui.page_head("🎯 AI 맞춤 지원금 찾기", "기본 정보를 입력하면 적합도가 높은 지원제도 5개를 추천해 드립니다.")

    # 지역을 바꾸면 세부지역 목록이 바로 바뀌도록 form 밖에 둡니다.
    col1, col2 = st.columns(2)
    region = col1.selectbox("거주 지역", list(REGIONS.keys()))
    city = col2.selectbox("세부 지역", REGIONS[region])

    with st.form("user_form"):
        col1, col2 = st.columns(2)
        age = col1.number_input("나이(만)", min_value=0, max_value=120, value=40, step=1)
        household_type = col2.selectbox("가구형태", HOUSEHOLD_TYPES)

        col1, col2 = st.columns(2)
        household_size = col1.number_input(
            "가구원 수(본인 포함)", min_value=1, max_value=10, value=1, step=1,
            help="1인가구를 선택하면 1명으로 계산합니다.",
        )
        monthly_income = col2.number_input("가구 월소득(만원)", min_value=0, max_value=5000, value=200, step=10)

        housing_type = st.selectbox("주거형태", HOUSING_TYPES)
        interests = st.multiselect("관심분야(여러 개 선택 가능)", INTERESTS)

        expenses = expense_inputs()

        real_only = real_only_toggle("input_real_only")
        submitted = st.form_submit_button("추천 받기", type="primary")

    if not submitted:
        return

    if household_type == "1인가구":
        household_size = 1
    percent = income_percent(monthly_income * 10_000, household_size)

    user = {
        "region": region,
        "city": city,
        "age": int(age),
        "household_type": household_type,
        "income_percent": percent,
        "housing_type": housing_type,
        "interests": interests,
    }

    ui.section_title("📋 추천 결과")
    st.caption(f"입력하신 소득은 2026년 기준중위소득의 약 {percent:.0f}% 입니다(참고용 계산).")

    policies = get_policies()
    if real_only:
        policies = policies[~policies["is_mock"]]
    results = recommend_policies(policies, user, top_n=5)
    good_count = count_good_matches(policies, user, min_score=70)
    saving_results = check_expenses(expenses, household_size, get_benchmarks(), get_saving_tips())
    check_count = sum(item["status"] == "확인 필요" for item in saving_results)
    total_saving = sum(item["saving"] for item in saving_results)

    # 결과 요약 — "내가 놓치고 있는 혜택"
    st.success(f"확인해볼 만한 지원제도 **{good_count}건** + 절감 가능 항목 **{check_count}건**")
    col1, col2, col3 = st.columns(3)
    col1.metric("확인해볼 지원제도", f"{good_count}건", help="AI 적합도 70점 이상인 지원제도 수")
    col2.metric("절감 가능 항목", f"{check_count}건")
    col3.metric("월 최대 절감 여지", f"{total_saving:,}원", help="저렴한 대안 기준 참고용 금액")

    ui.section_title("💰 추천 지원제도 TOP 5")
    if results.empty:
        st.warning("조건에 맞는 지원제도를 찾지 못했습니다.")
    for _, row in results.iterrows():
        with st.container(border=True):
            ui.policy_head(row, score=row["score"])
            st.progress(row["score"] / 100, text=f"AI 적합도 {row['score']}점 / 100점")
            st.write(f"**지원 내용**: {row['support_content']}")
            st.write("**추천 이유**")
            for reason in row["reasons"]:
                st.write(f"- {reason}")
            st.write(f"**신청 방법**: {row['application_method']} · {row['organization']}")
            easy_button(row)
            data_badge(row)

    ui.section_title("✂️ 생활비 절감 진단")
    show_saving_results(saving_results)

    st.info(SCORE_NOTICE)
    st.markdown(f'<p class="notice">{MOCK_NOTICE}</p>', unsafe_allow_html=True)


# ---------------- 생활비 절감 코치 / 우리동네 지원사업 ----------------
def saving_page():
    back_button()
    ui.page_head("✂️ AI 생활비 절감 코치", "매달 내는 통신비·공공요금·보험료를 입력하면, 비슷한 가구와 비교해 아낄 곳을 찾아 드립니다.")

    with st.form("saving_form"):
        household_size = st.number_input("가구원 수(본인 포함)", min_value=1, max_value=10, value=1, step=1)
        expenses = expense_inputs()
        submitted = st.form_submit_button("진단하기", type="primary")

    if submitted:
        saving_results = check_expenses(expenses, int(household_size), get_benchmarks(), get_saving_tips())
        check_count = sum(item["status"] == "확인 필요" for item in saving_results)
        total_saving = sum(item["saving"] for item in saving_results)
        if saving_results:
            st.success(f"절감 가능 항목 **{check_count}건** · 월 최대 **{total_saving:,}원** 절감 여지(참고용)")
        show_saving_results(saving_results)

    tips = get_saving_tips()
    ui.section_title("💡 전체 절감 팁")
    st.dataframe(
        tips[["category", "description", "estimated_saving"]].rename(
            columns={"category": "분야", "description": "절감 방법", "estimated_saving": "예상 절감액(월, 원)"}
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.caption("🧪 테스트용 가상 데이터입니다. 예상 절감액은 참고용입니다.")


def local_page():
    back_button()
    ui.page_head("📍 우리동네 지원사업", "지역을 고르면 그 지역에서 받을 수 있는 지원사업만 모아 보여 드립니다.")

    policies = get_policies()
    if real_only_toggle("local_real_only"):
        policies = policies[~policies["is_mock"]]

    col1, col2 = st.columns(2)
    region = col1.selectbox("지역", list(REGIONS.keys()), key="local_region")
    city = col2.selectbox("세부 지역", ["전체"] + REGIONS[region], key="local_city")
    categories = st.multiselect("분야(선택하지 않으면 전체)", INTERESTS, key="local_categories")

    local = filter_local_policies(policies, region, city, categories)
    area = region if city == "전체" else f"{region} {city}"
    st.success(f"{area} 지원사업 **{len(local)}건**")

    for _, row in local.iterrows():
        target = row["region"] + " 전체" if row["city"] == "전체" else row["city"]
        mark = "🧪" if row["is_mock"] else "✅"
        with st.expander(f"{mark} [{row['category']}] {row['policy_name']} · {target}"):
            ui.policy_head(row)
            st.write(f"**지원 내용**: {row['support_content']}")
            st.write(f"**대상 연령**: {row['target_age']}세 · **가구형태**: {row['household_type'].replace('|', ', ')}")
            st.write(f"**소득 조건**: {row['income_condition']} · **주거형태**: {row['housing_type'].replace('|', ', ')}")
            st.write(f"**신청 방법**: {row['application_method']} · {row['organization']}")
            if row["easy_text"]:
                st.divider()
                easy_explanation(row)
            data_badge(row)

    ui.section_title("📊 부울경 분야별 지원사업 수")
    counts = count_by_region_and_category(policies)
    fig = px.bar(
        counts, x="category", y="count", color="region", barmode="group",
        labels={"category": "분야", "count": "정책 수", "region": "지역"},
        category_orders={"region": list(REGIONS.keys()), "category": INTERESTS},
        color_discrete_map={"부산": "#1F5BD8", "울산": "#4FA3F7", "경남": "#17A673"},
    )
    fig.update_layout(
        height=360, margin=dict(l=10, r=10, t=10, b=10), yaxis=dict(dtick=1, gridcolor="#E6EBF2"),
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font=dict(family="Pretendard, sans-serif"),
        legend=dict(orientation="h", y=1.08, x=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f'<p class="notice">{MOCK_NOTICE}</p>', unsafe_allow_html=True)


PAGES = {"main": main_page, "input": input_page, "saving": saving_page, "local": local_page}
PAGES[st.session_state.page]()
