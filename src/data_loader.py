"""CSV 데이터를 읽어오는 파일입니다."""

from pathlib import Path

import pandas as pd

# 프로젝트 최상위 폴더 기준으로 data/mock, data/real 경로를 찾습니다.
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "mock"
REAL_DIR = Path(__file__).resolve().parent.parent / "data" / "real"


def load_policies() -> pd.DataFrame:
    """복지·지원제도 데이터를 불러옵니다(실제 정책 + 테스트 데이터)."""
    mock = pd.read_csv(DATA_DIR / "policies_mock.csv", dtype=str)
    real = pd.read_csv(REAL_DIR / "policies_real.csv", dtype=str)
    df = pd.concat([real, mock], ignore_index=True)
    df["is_mock"] = df["is_mock"].str.lower() == "true"
    df["status_note"] = df["status_note"].fillna("")

    # 쉬운 설명(정책 쉽게 설명하기)을 policy_id 기준으로 붙입니다.
    easy = pd.read_csv(REAL_DIR / "policy_easy.csv", dtype=str)
    df = df.merge(easy, on="policy_id", how="left")
    df["easy_text"] = df["easy_text"].fillna("")
    return df


def load_glossary() -> pd.DataFrame:
    """어려운 행정용어와 쉬운 뜻을 불러옵니다."""
    return pd.read_csv(REAL_DIR / "glossary.csv", dtype=str)


def load_saving_tips() -> pd.DataFrame:
    """생활비 절감 정보 테스트 데이터를 불러옵니다."""
    df = pd.read_csv(DATA_DIR / "saving_tips_mock.csv")
    df["is_mock"] = df["is_mock"].astype(str).str.lower() == "true"
    return df


def load_expense_benchmarks() -> pd.DataFrame:
    """가구원 수별 지출 기준값(평균·저렴한 대안)을 불러옵니다.

    통계청 실제 기준값(data/real)이 있으면 그것을, 없으면 테스트 데이터를 씁니다.
    """
    real_path = REAL_DIR / "expense_benchmarks_real.csv"
    path = real_path if real_path.exists() else DATA_DIR / "expense_benchmarks_mock.csv"
    df = pd.read_csv(path)
    df["is_mock"] = df["is_mock"].astype(str).str.lower() == "true"
    return df
