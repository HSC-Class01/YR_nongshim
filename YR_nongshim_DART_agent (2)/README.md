# 농심 DART Financial Analysis Agent

> OpenDART → 재무수치 추출 → 재무비율 분석 → GitHub Actions 월 1일 자동 업데이트 → GitHub Pages Dashboard

## 🔗 대시보드 바로가기

[![Dashboard](https://img.shields.io/badge/%F0%9F%94%97%20Dashboard-%EB%86%8D%EC%8B%AC%20Financial%20Dashboard-174d3b?style=for-the-badge)](https://HSC-Class01.github.io/YR_nongshim/)

> 실제 Pages URL은 GitHub Pages가 활성화된 후 `https://HSC-Class01.github.io/YR_nongshim/` 형태입니다.

## 1. 구성

- `src/collect_dart.py` — OpenDART 정기보고서 재무 API 수집
- `src/analyze.py` — 주요 재무비율 계산
- `dashboard/index.html` — 정적 GitHub Pages dashboard
- `data/financials.json`, `data/financials.csv` — 수집 원자료
- `data/analysis.json` — 분석 결과
- `github_workflows/` — ZIP에서 숨김 폴더를 피하기 위한 workflow 원본
- `scripts/install_workflow.ps1` — `.github/workflows`로 workflow를 설치하는 스크립트
- `config/config.json` — 농심 및 peer 설정

## 2. 핵심 재무수치

재무상태표: 총자산, 현금및현금성자산, 매출채권, 재고자산, 유형자산, 총부채, 차입금, 자본총계

손익계산서: 매출액, 매출총이익, 영업이익, 세전이익, 당기순이익, 지배주주순이익, 이자비용, 감가상각비

현금흐름: 영업활동현금흐름(CFO), 투자활동현금흐름(CFI), 재무활동현금흐름(CFF), FCF

재무비율: 매출총이익률, 영업이익률, 순이익률, 부채비율, 자기자본비율, 차입금의존도, 이자보상배율, 순차입금, CFO/순이익, 매출증가율 등

## 3. 기간

요청 범위는 2010년부터입니다.

중요: OpenDART의 현재 `단일회사 전체 재무제표` API는 공식적으로 2015년 이후 정보를 제공합니다. 따라서 2010~2014는 자동으로 허위 수치를 만들지 않고 `legacy_not_available_via_current_fnltt_api` 상태로 남깁니다. 해당 구간을 완전하게 채우려면 DART 원문/legacy 자료를 별도 매핑하는 추가 단계가 필요합니다.

## 4. API Key 입력

### 로컬 실행

Windows PowerShell:

```powershell
$env:DART_API_KEY="발급받은_40자리_OpenDART_API_KEY"
python -m pip install -r requirements.txt
python src/collect_dart.py
python src/analyze.py
```

### GitHub Actions

Repository → **Settings → Secrets and variables → Actions → New repository secret**

- Name: `DART_API_KEY`
- Secret: OpenDART에서 발급받은 40자리 인증키

API Key는 코드나 README에 직접 입력하지 마세요.

OpenDART API: https://opendart.fss.or.kr/

## 5. GitHub Actions 설치

ZIP에서는 `.github`가 숨김 폴더로 취급될 수 있어 업로드 편의를 위해 workflow를 `github_workflows/`에 넣었습니다.

PowerShell에서 저장소 루트에서:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_workflow.ps1
```

그러면 다음 workflow가 생성됩니다.

- `.github/workflows/dart_update_and_pages.yml` — 매월 1일 09:10 KST(UTC 00:10) 데이터 수집 → 분석 → commit → GitHub Pages 배포

데이터 업데이트와 Pages 배포를 하나의 workflow에서 처리하므로, `GITHUB_TOKEN`으로 데이터 commit을 만든 뒤 별도 workflow가 다시 트리거되지 않는 문제를 피합니다.

두 workflow 모두 `workflow_dispatch`로 수동 실행할 수 있습니다.

## 6. GitHub Pages 설정

Repository → Settings → Pages → Build and deployment → Source를 **GitHub Actions**로 선택하세요.

GitHub 공식 문서의 Pages artifact/deploy 방식에 맞춰 구성되어 있습니다.

## 7. About 섹션

Repository → About → 톱니바퀴(Edit repository details)에서 Website에:

`https://HSC-Class01.github.io/YR_nongshim/`

를 입력하세요.

## 8. Peer firms

초기 peer set:

| 기업 | KRX |
|---|---:|
| 오뚜기 | 007310 |
| 삼양식품 | 003230 |
| 동원F&B | 049770 |
| 대상 | 001680 |
| CJ제일제당 | 097950 |

Peer set은 국내 식품 제조/가공업에서 농심과 사업구조가 겹치는 비교군을 위한 것입니다.

## 9. 주의

- GitHub Pages는 공개 웹사이트이므로 API key를 repository에 저장하지 않습니다.
- 데이터가 없는 기간은 `N/A`로 표시합니다.
- 연결/별도 기준을 혼합하지 않도록 기본 수집은 연결재무제표(CFS)입니다.
- 공시 계정명이 바뀌는 경우 `src/collect_dart.py`의 `ALIASES`를 추가하면 됩니다.
