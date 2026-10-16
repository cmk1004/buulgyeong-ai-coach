"""AI 추천 적합도 점수를 계산하는 파일입니다.

가중치(총 100점): 지역 30 + 연령 20 + 소득 20 + 가구형태 15 + 관심분야 10 + 기타(주거형태) 5
이 점수는 서비스 자체의 추천 우선순위이며, 실제 지원 대상 여부를 확정하지 않습니다.
"""

import re

import pandas as pd

WEIGHTS = {
    "region": 30,
    "age": 20,
    "income": 20,
    "household": 15,
    "interest": 10,
    "etc": 5,
}

# 2026년 기준중위소득(월, 원) — 참고용. 7인 이상은 6인 값을 사용합니다.
MEDIAN_INCOME_2026 = {
    1: 2_564_238,
    2: 4_199_292,
    3: 5_359_036,
    4: 6_494_738,
    5: 7_556_719,
    6: 8_555_952,
}


def income_percent(monthly_income_won: int, household_size: int) -> float:
    """월소득이 기준중위소득의 몇 %인지 계산합니다."""
    size = min(max(household_size, 1), 6)
    return monthly_income_won / MEDIAN_INCOME_2026[size] * 100


def _split(value: str) -> list[str]:
    """'1인가구|부부가구' 같은 값을 목록으로 바꿉니다."""
    return [v.strip() for v in str(value).split("|")]


def _age_ok(target_age: str, age: int) -> bool:
    """'19~39' 형식의 연령 조건에 맞는지 확인합니다."""
    low, high = target_age.split("~")
    return int(low) <= age <= int(high)


def _income_ok(income_condition: str, user_percent: float) -> bool:
    """'중위소득 100% 이하' 형식의 소득 조건에 맞는지 확인합니다."""
    if income_condition == "제한없음":
        return True
    match = re.search(r"(\d+)%", income_condition)
    return match is not None and user_percent <= int(match.group(1))


def score_policy(policy: pd.Series, user: dict) -> tuple[int, list[str]]:
    """정책 하나의 적합도 점수와 추천 이유를 계산합니다.

    지역이 맞지 않으면 0점을 돌려주고 추천에서 제외합니다.
    """
    reasons = []

    # 1) 지역 (30점) — 같은 광역 지역이고, 세부지역이 '전체'이거나 같아야 합니다.
    if policy["region"] != user["region"]:
        return 0, []
    if policy["city"] not in ("전체", user["city"]):
        return 0, []
    score = WEIGHTS["region"]
    area = user["region"] if policy["city"] == "전체" else policy["city"]
    reasons.append(f"✅ {area} 거주자 대상")

    # 2) 연령 (20점)
    if _age_ok(policy["target_age"], user["age"]):
        score += WEIGHTS["age"]
        reasons.append(f"✅ 연령 조건({policy['target_age']}세) 충족")
    else:
        reasons.append(f"⚠️ 연령 조건({policy['target_age']}세) 확인 필요")

    # 3) 소득 (20점)
    if _income_ok(policy["income_condition"], user["income_percent"]):
        score += WEIGHTS["income"]
        reasons.append(f"✅ 소득 조건({policy['income_condition']}) 충족 예상")
    else:
        reasons.append(f"⚠️ 소득 조건({policy['income_condition']}) 확인 필요")

    # 4) 가구형태 (15점)
    households = _split(policy["household_type"])
    if "전체" in households or user["household_type"] in households:
        score += WEIGHTS["household"]
        reasons.append("✅ 가구형태 일치")
    else:
        reasons.append(f"⚠️ 대상 가구형태: {policy['household_type'].replace('|', ', ')}")

    # 5) 관심분야 (10점)
    if policy["category"] in user["interests"]:
        score += WEIGHTS["interest"]
        reasons.append(f"✅ 관심분야({policy['category']}) 일치")

    # 6) 기타 조건 — 주거형태 (5점)
    housings = _split(policy["housing_type"])
    if "전체" in housings or user["housing_type"] in housings:
        score += WEIGHTS["etc"]
    else:
        reasons.append(f"⚠️ 대상 주거형태: {policy['housing_type'].replace('|', ', ')}")

    return score, reasons


def recommend_policies(policies: pd.DataFrame, user: dict, top_n: int = 5) -> pd.DataFrame:
    """적합도가 높은 순서로 상위 top_n개 정책을 돌려줍니다.

    user 예시:
        {"region": "부산", "city": "해운대구", "age": 68, "household_type": "1인가구",
         "income_percent": 80.0, "housing_type": "월세", "interests": ["고령층", "의료"]}
    """
    rows = []
    for _, policy in policies.iterrows():
        score, reasons = score_policy(policy, user)
        if score > 0:
            row = policy.to_dict()
            row["score"] = score
            row["reasons"] = reasons
            rows.append(row)

    if not rows:
        return pd.DataFrame()

    result = pd.DataFrame(rows)
    # 점수가 같으면 실제 정책(is_mock=False)을 먼저 보여줍니다.
    result = result.sort_values(["score", "is_mock", "policy_id"], ascending=[False, True, True])
    return result.head(top_n).reset_index(drop=True)


def count_good_matches(policies: pd.DataFrame, user: dict, min_score: int = 70) -> int:
    """적합도가 min_score점 이상인 정책 수를 셉니다(결과 요약용)."""
    return sum(score_policy(policy, user)[0] >= min_score for _, policy in policies.iterrows())
