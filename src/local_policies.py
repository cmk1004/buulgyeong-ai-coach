"""우리동네 지원사업 — 지역별로 정책을 골라내는 파일입니다."""

import pandas as pd


def filter_local_policies(policies: pd.DataFrame, region: str, city: str = "전체", categories: list[str] | None = None) -> pd.DataFrame:
    """선택한 지역의 정책만 돌려줍니다.

    - city가 "전체"이면 그 광역 지역의 모든 정책을 보여줍니다.
    - city를 고르면 광역 전체 대상 정책(city="전체")과 그 세부지역 정책을 함께 보여줍니다.
    - categories를 고르면 그 분야만 남깁니다(비어 있으면 전체).
    """
    result = policies[policies["region"] == region]

    if city != "전체":
        result = result[result["city"].isin(["전체", city])]

    if categories:
        result = result[result["category"].isin(categories)]

    # 실제 정책을 먼저, 그 안에서 광역 전체 대상 → 세부지역 순서로 보여줍니다.
    result = result.assign(_order=(result["city"] != "전체").astype(int))
    return result.sort_values(["is_mock", "_order", "city", "policy_id"]).drop(columns="_order").reset_index(drop=True)


def count_by_region_and_category(policies: pd.DataFrame) -> pd.DataFrame:
    """지역·분야별 정책 수를 셉니다(차트용)."""
    return policies.groupby(["region", "category"]).size().reset_index(name="count")
