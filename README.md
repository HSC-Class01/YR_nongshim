# 농심 DART Financial Analysis Agent

> OpenDART → 재무수치 추출 → 재무비율 분석 → GitHub Actions 월 1일 자동 업데이트 → GitHub Pages Dashboard

## 🔗 대시보드 바로가기

[![Dashboard](https://img.shields.io/badge/%F0%9F%94%97%20Dashboard-%EB%86%8D%EC%8B%AC%20Financial%20Dashboard-174d3b?style=for-the-badge)](https://HSC-Class01.github.io/YR_nongshim/)

## 1. 구성

- `src/collect_dart.py` — OpenDART 정기보고서 재무 API 수집
- `src/analyze.py` — 주요 재무비율 계산
- `src/validate.py` — 수집 결과 검증
- `dashboard/index.html` — GitHub Pages 정적 dashboard
- `data/financials.json`, `data/financials.csv` — 수집 데이터
- `data/analysis.json` — 분석 결과
- `.github/workflows/dart_update_and_pages.yml` — 월 1일 자동 수집·분석·Pages 배포
- `config/config.json` — 농심 및 국내 peer 설정

## 2. 분석 항목

**재무상태표:** 총자산, 현금및현금성자산, 매출채권, 재고자산, 유형자산, 총부채, 차입금, 자본총계

**손익계산서:** 매출액, 매출총이익, 영업이익, 세전이익, 당기순이익, 지배주주순이익, 이자비용, 감가상각비

**현금흐름:** 영업활동현금흐름(CFO), 투자활동현금흐름(CFI), 재무활동현금흐름(CFF), FCF

**재무비율:** 매출총이익률, 영업이익률, 순이익률, 부채비율, 자기자본비율, 차입금의존도, 이자보상배율, 순차입금, CFO/순이익, 매출증가율

## 3. 기간과 데이터 범위

요청 범위는 2010년부터입니다.

OpenDART의 현재 `fnlttSinglAcntAll` API는 공식적으로 2015년 이후 사업연도 정보를 제공합니다. 따라서 2010~2014는 허위 수치를 생성하지 않고 `legacy_not_available_via_current_fnltt_api`로 표시합니다. 2015년 이후 데이터는 DART API Key가 등록되면 자동 수집됩니다.

## 4. API Key

Repository → **Settings → Secrets and variables → Actions → New repository secret**

- Name: `DART_API_KEY`
- Value: OpenDART에서 발급받은 40자리 인증키

API Key는 코드, README, dashboard에 저장하지 않습니다.

## 5. 자동 업데이트

GitHub Actions가 매월 1일 **09:10 KST (00:10 UTC)**에 실행됩니다.

1. OpenDART에서 사업보고서·반기보고서·1분기보고서·3분기보고서 수집
2. 재무비율 계산
3. 데이터 검증
4. `data/` 자동 commit
5. GitHub Pages dashboard 재배포

또한 Actions 화면에서 `workflow_dispatch`로 수동 실행할 수 있습니다.

## 6. GitHub Pages

이 저장소는 `gh-pages` 브랜치를 GitHub Pages publishing source로 사용합니다.
GitHub Actions의 DART 수집·분석이 완료되면 dashboard와 최신 `data/`가 `gh-pages` 브랜치에 자동 배포됩니다.

최초 1회만 Repository → **Settings → Pages → Build and deployment**에서:

- **Source:** Deploy from a branch
- **Branch:** `gh-pages`
- **Folder:** `/ (root)`
- **Save**

현재 GitHub Actions의 기본 `GITHUB_TOKEN`으로 Pages 사이트 자체를 생성하는 단계에서 권한 오류가 발생하여, Pages 설정은 관리자 계정에서 위와 같이 한 번 활성화해야 합니다. 이후에는 매월 자동 배포됩니다.

배포 주소:

https://HSC-Class01.github.io/YR_nongshim/

## 7. About 섹션

Repository의 **About → Edit repository details → Website**에 다음 주소를 입력하세요.

https://HSC-Class01.github.io/YR_nongshim/

## 8. 국내 Peer Firms

농심과 비교 가능한 국내 식품 제조·가공 상장사를 다음과 같이 설정했습니다.

| 기업 | KRX | 비교 목적 |
|---|---:|---|
| CJ제일제당 | 097950 | 종합식품·가공식품 |
| 동원F&B | 049770 | 식품 제조·가공 |
| 대상 | 001680 | 식품·소재·가공 |
| 오뚜기 | 007310 | 가공식품·면류·소스 |
| 삼양식품 | 003230 | 면류·가공식품 |

Peer set은 재무구조와 사업구조 비교를 위한 분석용 비교군이며 투자 판단을 위한 순위가 아닙니다.

## 9. Dashboard

상단에는 핵심 KPI와 매출·영업이익 및 수익성 추이를 시각화하고, 하단에는 다음 3개 표를 제공합니다.

- **Annual:** 사업보고서
- **Half-year:** 반기보고서
- **Quarterly:** 1분기·3분기보고서

Dashboard 최하단에는 국내 peer firms table을 제공합니다.

## 10. 데이터 원칙

- 기본 재무제표 기준은 연결재무제표(CFS)
- 값이 없는 기간은 0으로 대체하지 않고 N/A 처리
- 공시 계정명 변경에 대응할 수 있도록 alias 기반 추출
- OpenDART 제공 범위 밖의 2010~2014는 별도 legacy 보정 대상으로 표시
- 원자료와 분석자료를 구분하여 저장

Source: OpenDART / 금융감독원
