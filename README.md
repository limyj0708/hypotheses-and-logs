# 가설과 로그

데이터와 가설, 그리고 삶에 관한 관찰 기록입니다.

첫 번째 글은 미국 대통령 선거주기에서 `2년차 10월~3년차 4월`이 유난히 강했다는 GMO의 공개 가설을, 공개 S&P 500 가격지수 데이터로 다시 확인한 기록입니다.

## 읽기

- 공개 글: `https://limyj0708.github.io/hypotheses-and-logs/`
- 편집·재현용 노트북: [`notebooks/gmo_election_cycle_hypothesis_test.ipynb`](notebooks/gmo_election_cycle_hypothesis_test.ipynb)

## 재현 방법

```powershell
python -m pip install -r requirements.txt
python scripts/fetch_index_price_history.py
python scripts/build_pages_site.py
```

그 뒤 `docs/index.html`을 브라우저에서 열면 공개 글과 같은 결과를 볼 수 있습니다.

## 데이터와 해석의 범위

- 데이터는 Yahoo Finance chart API에서 받은 일별 **가격지수**입니다. 배당을 포함한 총수익률이나 물가 조정 수익률이 아닙니다.
- GMO의 원문은 Global Financial Data의 실질 총수익률을 사용했습니다. 이 저장소는 공개 데이터로 방향과 통계적 차이를 독립적으로 재현한 것입니다.
- 이 글은 투자 권유가 아닙니다. 과거의 패턴은 미래 수익을 보장하지 않습니다.

원시 가격 CSV는 저장소에 넣지 않습니다. 위 수집 스크립트를 실행하면 로컬 `data/`에 생성됩니다.
