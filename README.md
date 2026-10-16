# 부울경 생활비 절감·복지혜택 AI 코치

> 내가 아낄 수 있는 생활비와 받을 수 있는 지원금, AI가 한 번에 찾아드립니다.

부산·울산·경남 주민이 거주지역·연령·가구형태·소득을 입력하면 **받을 수 있는 복지·지원제도**와 **줄일 수 있는 생활비 항목**을 한 화면에서 진단·추천하는 Streamlit 서비스입니다.
NEXT:AI DEVELOPER 온라인 부트캠프 최종 프로젝트(2026).

- 배포 주소: https://buulgyeong-coach.streamlit.app/

## 주요 기능

| 기능 | 설명 |
| --- | --- |
| AI 맞춤 지원금 찾기 | 지역30·연령20·소득20·가구형태15·관심분야10·기타5 = 100점 적합도로 상위 5개 추천 |
| AI 생활비 절감 코치 | 통신비·공공요금·보험료를 통계청 가구원수별 평균과 비교해 「확인 필요/양호」 표시 |
| 내가 놓치고 있는 혜택 | "확인해볼 만한 지원제도 n건 + 절감 가능 항목 n건" 요약 |
| 우리동네 지원사업 | 지역·세부지역·분야 필터와 지역별 정책 수 차트 |
| 정책 쉽게 설명하기 | 공고 내용과 쉬운 설명을 나란히 보여주고 어려운 행정용어 풀이 |

AI 적합도는 서비스 자체의 추천 우선순위이며 실제 지원 대상 여부를 확정하지 않습니다.

## 실행 방법

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 폴더 구조

```
app.py                  화면(메인·입력·결과·절감 코치·우리동네)
src/
  data_loader.py        CSV 읽기
  recommender.py        적합도 점수 계산
  saving_coach.py       생활비 비교
  local_policies.py     지역 필터
  easy_explain.py       쉬운 설명·용어 찾기
  ui.py                 디자인(색상·카드·칩)
data/
  real/                 실제 정책 12건·통계청 기준값·쉬운 설명·용어 사전
  mock/                 테스트용 가상 데이터(is_mock=True)
```

## 데이터 출처

- 실제 정책 12건(부산·울산·경남 각 4건): 각 지자체·정부24·복지로 공식 페이지, 2026-10-16 확인. 정책별 `source_url` 참고
- 생활비 기준값: 통계청 2025년 가계동향조사 「가구원수별 가구당 월평균 가계수지」(KOSIS DT_1L9U105)
- 테스트 데이터는 `is_mock=True`로 표시하고 화면에서 🧪로 구분합니다

## 기술 스택

Python · Streamlit · Pandas · Plotly · Streamlit Community Cloud
