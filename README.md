# 의정부 주유소 가격 지도

Opinet 스냅샷을 GitHub Actions에서 생성하고 GitHub Pages의 지도·가격순 표로 표시하는 정적 SPA입니다.

- 공개 페이지: https://zasfe.github.io/gas/
- 소스코드: https://github.com/zasfe/gas
- 제작자: zasfe
- 라이선스: MIT

브라우저는 Opinet API를 호출하지 않고 저장소의 `public/data.json`만 읽습니다. 데이터 갱신은 GitHub Actions의 `workflow_dispatch`로 실행하며, API 키는 `OPINET_API_KEY` Secret으로만 사용합니다. 의정부시 행정구역 bounding box를 5km 반경 격자로 조회하고 Opinet 주유소 ID를 중복 제거합니다.

## 로컬 검증

```bash
uv run --with pytest python -m pytest -q
python scripts/validate_data.py public/data.json
```

## 데이터 갱신

GitHub 저장소의 Actions → Refresh Opinet snapshot → Run workflow에서 실행합니다. 기본 조회 범위는 기준점 반경 5km입니다. 상세 조회 실패가 있는 경우 기본적으로 배포를 중단하며, 의도적인 부분 결과가 필요할 때만 `allow_partial`을 선택합니다.
