"""생활비 절감 코치 — 내 지출을 기준값과 비교하는 파일입니다.

비교 방법(단순 비교):
- 내 지출 > 평균      → "확인 필요" (저렴한 대안 기준으로 아낄 수 있는 금액 표시)
- 내 지출 <= 평균     → "양호"
- 입력하지 않은 항목  → 비교하지 않음
"""

import pandas as pd

CATEGORIES = ["통신비", "공공요금", "보험료"]


def check_expenses(expenses: dict, household_size: int, benchmarks: pd.DataFrame, tips: pd.DataFrame) -> list[dict]:
    """항목별 비교 결과 목록을 돌려줍니다.

    expenses 예시: {"통신비": 90000, "공공요금": 0, "보험료": 200000}  (월, 원 / 0은 미입력)
    """
    size = min(max(household_size, 1), 4)  # 기준값은 1~4인(4인 이상)까지 있습니다.
    results = []

    for category in CATEGORIES:
        amount = expenses.get(category, 0)
        if not amount:
            continue

        row = benchmarks[(benchmarks["category"] == category) & (benchmarks["household_size"] == size)].iloc[0]
        average = int(row["average_monthly"])
        low = int(row["low_monthly"])

        if amount > average:
            status = "확인 필요"
            saving = amount - low
        else:
            status = "양호"
            saving = 0

        category_tips = tips[tips["category"] == category]["description"].tolist()

        results.append({
            "category": category,
            "amount": amount,
            "average": average,
            "low": low,
            "status": status,
            "saving": saving,
            "tips": category_tips if status == "확인 필요" else [],
        })

    return results
