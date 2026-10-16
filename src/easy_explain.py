"""정책 쉽게 설명하기 — 공고 문구 속 어려운 용어를 찾는 파일입니다.

MVP에서는 LLM 없이, 미리 써 둔 쉬운 설명(policy_easy.csv)과
용어 사전(glossary.csv)으로 원문과 쉬운 말을 나란히 보여줍니다.
"""

import pandas as pd


def original_text(policy: pd.Series) -> str:
    """화면 왼쪽에 보여줄 공고 내용(원문 요지)을 만듭니다."""
    lines = [
        f"지원내용: {policy['support_content']}",
        f"대상연령: {policy['target_age']}세",
        f"소득기준: {policy['income_condition']}",
        f"신청방법: {policy['application_method']}",
    ]
    if policy.get("status_note"):
        lines.append(f"비고: {policy['status_note']}")
    return "\n".join(lines)


def find_terms(text: str, glossary: pd.DataFrame) -> list[tuple[str, str]]:
    """글 속에 들어 있는 어려운 용어와 그 뜻을 찾아 돌려줍니다."""
    return [(row["term"], row["meaning"]) for _, row in glossary.iterrows() if row["term"] in text]
