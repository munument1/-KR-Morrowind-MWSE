# Morrowind CP949 Korean Support

Classic **The Elder Scrolls III: Morrowind 1.6.0.1820**에서 한국어를 표시하고, OpenMW용 한국어 재번역 데이터를 Classic 엔진에서 사용할 수 있도록 변환하는 프로젝트입니다.

현재 권장 배포본은 **v1.0.7-rc7 Classic CP949**입니다.

## 현재 릴리스

태그:

```text
v1.0.7-rc7-classic-cp949
```

번역 패키지:

```text
Morrowind_Korean_ReTranslation_v1.0.7-rc7_Classic_CP949.zip
```

RC7은 기존 Classic CP949 RC6을 기반으로, 최신 OpenMW KR1에서 검증된 **대화 토픽/키워드 링크 수정만** Classic용으로 이식한 버전입니다.

OpenMW KR1의 일반 번역 문장 변경까지 다시 가져오지는 않고, Classic에서 실제 대화 연결 문제를 일으키는 토픽 마커와 TOP/MRK 데이터를 중심으로 동기화했습니다.

## RC7 핵심 변경

- 명시적 `@topic#` 링크가 추가된 INFO **7,692개** 반영
- OpenMW KR1 최종 TOP **5,843행** CP949 변환
- OpenMW KR1 최종 MRK **376행** CP949 변환
- 일반 번역 내용이 달라진 INFO **177개는 제외**
- Classic CP949 RC6의 compiled SCPT **236개 바이트 그대로 보존**
- Classic 전용 Voice `ANAM="Wilderness"` 보정 유지
- CP949 변환 fallback **0**
- 미해결 토픽 마커 **0**

이 방식으로 하스팟 안타볼리스, 라니스 아트리스, 아지라/갈베디르 등 기존에 보고되었던 **대화 토픽이 나타나지 않거나 후속 선택지가 연결되지 않는 계열의 문제**를 OpenMW KR1 기준 데이터에 맞춰 처리합니다.

## 검증 상태

RC7 빌드는 고정된 OpenMW KR1 및 Classic RC6 입력 해시를 기준으로 재현하며, 다음 검증을 통과해야만 릴리스가 생성됩니다.

- DIAL 수/구조 보존: **PASS**
- INFO 키 구조 보존: **PASS**
- marker-only INFO 변경 수 7,692: **PASS**
- 일반 번역 변경 177개 제외: **PASS**
- TOP 5,843행: **PASS**
- MRK 376행: **PASS**
- 미해결 `@topic#` 마커: **0**
- CP949 변환 fallback: **0**
- compiled SCPT byte-identical: **PASS**
- 예상한 INFO `NAME` 외 변경 없음: **PASS**
- Classic Voice `Wilderness` 보정 유지: **PASS**
- ZIP 무결성 검사: **PASS**

OpenMW KR1에서 정리된 토픽/키워드 연결 데이터를 기준으로 포팅했기 때문에 RC7을 현재 권장 배포본으로 사용합니다. 다만 Classic 엔진 전체 플레이를 끝까지 통과하는 장기 회귀 테스트는 별도로 계속할 수 있습니다.

## Classic 사용자 설치 정책

Classic에서 한글을 표시하려면 다음 세 요소가 모두 필요합니다.

1. **CP949 대응 실행 파일** — `tools/patch_morrowind_cp949.py`
2. **CP949 bitmap font** — 사전 생성된 FNT/TEX 폰트팩
3. **CP949 번역 ESP/TOP/MRK** — RC7 번역 패키지

실행 파일 패치는 CP949 바이트를 올바른 DBCS 글리프 위치로 해석하게 만들고, 실제 한글 모양은 FNT/TEX bitmap font가 제공합니다.

프로젝트 정책은 **일반 사용자에게 폰트 생성 스크립트 실행을 요구하지 않는 것**입니다. 사용자용 배포에서는 사전 생성한 Classic CP949 폰트팩을 사용하는 것을 기본 경로로 둡니다.

권장 폰트팩 asset 이름:

```text
Morrowind_CP949_Classic_Fonts.zip
```

`tools/build_classic_cp949_fonts.py`는 재현·개발·커스텀 글꼴용 선택 도구로 유지합니다.

자세한 내용: [`CLASSIC_FONT_SETUP.md`](CLASSIC_FONT_SETUP.md)

## Classic CP949 스크립트 처리

Classic 변환에서는 일반 표시 문자열을 CP949로 바꾸고, 번역 `SCTX` 때문에 게임 시작 시 스크립트가 재컴파일되지 않도록 공식 마스터의 compiled `SCDT`를 기준으로 스크립트를 재구성합니다.

기존 RC6 Classic 빌드에서 검증된 다음 항목은 RC7에서도 그대로 유지됩니다.

- compiled SCPT: **236개**
- compiled `MessageBox` 본문: **413개**
- `MessageBox` 버튼: **359개**
- compiled `AddTopic`: **105개**
- scripted `Say`: **128개**
- `FNAM` 32바이트 초과 처리: **33건**
- Voice INFO `ANAM="Wilderness"` 문제 조건 제거
- 프로케수스 INFO: **1개 유지**
- 프로케수스 기술 필터: `ANAM = Seyda Neen, Census and Excise Office`
- 출력 SCPT: `SCDT` 포함, `SCTX` 없음

공식 스크립트 기준은 실제 로드 순서와 같은

```text
Morrowind.esm -> Tribunal.esm -> Bloodmoon.esm
```

순서에서 마지막 정의를 사용합니다.

## OpenMW KR1 토픽 링크 포팅

도구:

```text
tools/port_openmw_kr1_topic_links.py
```

이 포터는 Classic RC6 ESP를 기준본으로 유지하면서 OpenMW KR1과 INFO 응답을 비교합니다.

OpenMW 쪽 응답에서 `@topic#` 마커만 제거했을 때 Classic RC6 응답과 문장이 동일한 경우에만 링크 수정으로 판정해 이식합니다. 따라서 단순 번역 문장 개정은 자동으로 제외됩니다.

최종 출력에는 OpenMW KR1의 `.top`과 `.mrk`도 CP949로 변환해 포함하며, 모든 명시 토픽 마커가 TOP 또는 실제 DIAL로 해석되는지 다시 검사합니다.

## CP949 실행 파일 패치

패처:

```text
tools/patch_morrowind_cp949.py
```

지원 입력 SHA-256:

```text
8fe33fb11b6a682721e7456af78eefd228e8b60dc7c9f4253f89a361f8a4dfc5  MCP default
c3585b91741689057c18ff86a1c3381d47278cd1d81443d38ed3b179c2fa1cd8  MCP Japanese localization enabled
```

기존 런타임 확인 Korean Pilot 출력 SHA-256:

```text
710196b98d1a4efa174aebb5539e14b36cff20d008dc1f0c0610ce099d06cf72
```

사용 예:

```bash
python tools/patch_morrowind_cp949.py Morrowind.exe Morrowind.MCP-Korean-Pilot.exe
```

## 설치 순서

1. Morrowind GOTY 1.6.0.1820 준비
2. 지원되는 MCP 상태의 자신의 `Morrowind.exe`에 CP949 패치 적용
3. 사전 생성 Classic CP949 폰트팩 설치
4. RC7 번역 ZIP 설치
5. `Morrowind_Korean_ReTranslation.esp` 활성화
6. 이전 한국어 번역 ESP 시험판 비활성화

Classic에서는 기존 `Morrowind.ini` 폰트 이름을 바꾸지 않는 것을 기준으로 합니다.

## RC7 SHA-256

```text
f15f2c4dd16da9cb5e7707fe85a25925f39039310525fbb559184673017e54e2  RC7 ZIP
bd277b2a2d2b343badd74f26a1ac3190466e6149914f7342135bf1112145dda5  RC7 ESP
a5831b89d8dd7e5e4a30177d3b2df3d775eade2ce030cbb889bd226266d1c0f8  RC7 TOP
9e4a426add4bb006365be358b125ee88714819aba3612a6eaa1ea2da54f4bc55  RC7 MRK
```

Release에는 검증 JSON과 `SHA256SUMS.txt`도 함께 제공합니다.

## 회귀 테스트 우선 항목

정적 검증에서 링크 구조는 통과했으며, 실제 Classic 환경에서 추가 확인할 경우 다음 경로를 우선 권장합니다.

- 하스팟 안타볼리스 / 정보 제공 경로
- 라니스 아트리스 / 마법사 길드 가입 및 업무
- 아지라 / 갈베디르 내기
- 전사 길드 직접 토픽 연결
- Tribunal scripted dialogue / topic links
- Bloodmoon scripted dialogue / topic links
- 게임 시작 시 `Script in file ... compiled.` 경고 여부
- 시작부 `Say`, `MessageBox`, 버튼

## OpenMW 폰트 파일명 호환성

OpenMW 쪽은 글로벌 기본 `MysticCards / DemonicLetters`와 Import Wizard 계승 `magic_cards_regular / daedric_font` 두 정상 경로가 있으므로 별도 alias 정책을 사용합니다.

자세한 내용: [`OPENMW_FONT_COMPAT.md`](OPENMW_FONT_COMPAT.md)

## 저장소에 포함하지 않는 것

- Bethesda의 `Morrowind.exe` 원본/수정본
- 게임 원본 ESM

## Status

**v1.0.7-rc7 / Release / OpenMW KR1 topic-link sync**
