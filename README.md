# Morrowind CP949 Korean Support

Classic **The Elder Scrolls III: Morrowind 1.6.0.1820**에서 OpenMW KR1 한국어 데이터를 사용할 수 있도록 CP949용으로 변환하는 프로젝트입니다.

현재 권장 배포본은 **v1.0.7-rc7 Classic CP949**입니다.

## 다운로드

태그:

```text
v1.0.7-rc7-classic-cp949
```

일반 사용자는 Release에서 다음 합본 하나만 받으면 됩니다.

```text
Morrowind_Classic_CP949_Korean_v1.0.7-rc7_Full.zip
```

현재 Full ZIP SHA-256:

```text
68e463f0b9adb82c4f54d695e49b3bca236d0446e0566b5c1b2c3e8583253a67
```

## 패키지 구조

바깥 Full ZIP:

```text
Apply_CP949_Patch.bat
Morrowind_Korean_INI.ini
Morrowind_Korean_ReTranslation_v1.0.7-rc7_MO2.zip
README_RC7.txt
```

안쪽 `Morrowind_Korean_ReTranslation_v1.0.7-rc7_MO2.zip`은 **Mod Organizer 2에서 바로 설치**합니다.

MO2 ZIP 데이터 루트:

```text
Morrowind_Korean_ReTranslation.esp
Morrowind_Korean_ReTranslation.top
Morrowind_Korean_ReTranslation.mrk
Morrowind_Korean_ReTranslation.cel
Morrowind.cel
Tribunal.cel
Bloodmoon.cel
Fonts/
```

현재 Nested MO2 ZIP SHA-256:

```text
9d44c2d7558c364aa3b3bafa69547e9d0b5157012d7d021908df54321ca23ef9
```

## 설치

1. Morrowind GOTY 1.6.0.1820 준비
2. Morrowind Code Patch(MCP) 적용
3. MCP에서 **Japanese localization compatibility** 활성화
4. **UI display quality fix**와 Better typography 등 원하는 MCP 옵션도 이 단계에서 먼저 적용
5. Full ZIP의 `Apply_CP949_Patch.bat`과 `Morrowind_Korean_INI.ini`를 게임 폴더에 배치
6. `Apply_CP949_Patch.bat` 실행
7. MO2에서 안쪽 `Morrowind_Korean_ReTranslation_v1.0.7-rc7_MO2.zip` 설치
8. `Morrowind_Korean_ReTranslation.esp` 활성화. Classic의 ESP 순서에서 다른 일반 ESP 뒤에 두고 이전 한국어 ESP는 비활성화

Python 설치는 필요 없습니다.

## CP949 Code Patch

우리 패치도 `Morrowind.exe`를 수정하는 **CP949 Code Patch**입니다.

현재 BAT는 전체 EXE SHA-256만으로 허용/거부하지 않습니다.

- 이미 CP949 루틴이 있으면 건너뜀
- 아니면 `0x3457C0`의 **MCP Japanese localization 코드 패턴을 직접 검증**
- Better typography/UI fix 등 다른 MCP 옵션으로 전체 EXE 해시가 달라도 대상 코드 패턴이 정확하면 패치
- 코드 패턴이 다르면 중단
- 기존 `Morrowind.exe.cp949-backup`이 있으면 `.1`, `.2` 식으로 새 백업 생성
- 패치 후 CP949 코드 바이트 재검증

Windows `cmd.exe` CI에서 알 수 없는 전체 SHA + 올바른 Japanese-localization 코드 패턴과 기존 백업이 있는 경우까지 검증합니다.

## Classic Morrowind.ini 한국어

OpenMW KR1의 `openmw.cfg` fallback 중 Classic `Morrowind.ini`에 대응하는 표시 문자열 **63개**를 CP949로 변환합니다.

- `[Question 1]`~`[Question 10]`: 직업 질문/답변 40개
- `[Level Up]`: Level2~Level20 + Default 20개
- `[Blood]`: Texture Name 0~2 3개

BAT는 해당 63개 키의 값만 바꾸며 `Sound=`, Blood 모델/텍스처 경로, `[Fonts]`, 기타 사용자/MCP 설정은 보존합니다.

이전 시험판 BAT를 여러 번 적용한 환경에서 남을 수 있는 중복 `[Question 1]`~`[Question 10]` 섹션도 정리합니다. 각 Question 섹션은 첫 번째 것만 유지하고 두 번째 이후 중복 섹션을 제거하며, 첫 섹션의 `Sound=`는 그대로 보존합니다. 설치 후 Question 1~10이 정확히 하나씩 존재하는지 다시 검증합니다.

## Classic CEL 현지화

OpenMW KR1의 CELL 표시명 번역 1,439행을 CP949로 변환합니다.

Classic은 로드한 마스터/플러그인과 같은 basename의 CEL sidecar를 사용할 수 있으므로 다음 네 파일을 함께 제공합니다.

- `Morrowind.cel`
- `Tribunal.cel`
- `Bloodmoon.cel`
- `Morrowind_Korean_ReTranslation.cel`

네 CEL은 같은 번역 테이블을 사용합니다. CELL 레코드의 실제 기술 ID/NAME은 영어 그대로 두므로 `PositionCell` 같은 스크립트 참조를 변경하지 않습니다. 이 보강은 문/출입구에 커서를 올렸을 때 표시되는 목적지명 같은 Classic UI 경로를 대상으로 합니다.

## Classic ESP 로드 순서

RC7 번역 ESP의 실제 한국어 GMST는 직업 결과창 관련 항목까지 정상적으로 들어 있습니다. 다만 Classic Morrowind는 ESP 순서의 영향을 받으므로, 뒤에서 로드되는 다른 ESP가 영어 GMST를 다시 덮을 수 있습니다.

MO2 ZIP 안의 `Morrowind_Korean_ReTranslation.esp`는 추출 시 너무 이른 플러그인이 되지 않도록 고정된 늦은 수정일을 사용합니다. 수동 정렬 환경에서도 번역 ESP를 다른 일반 ESP 뒤에 두는 것을 권장합니다.

확인된 한국어 GMST 예:

- `sMessageQuestionAnswer1` — 직업 결과 설명
- `sMessageQuestionAnswer2` / `3` — 이 직업 선택 / 다른 직업 선택
- `sChooseClassMenu1`~`4` — 전문화 / 선호 능력치 / 주요 기술 / 보조 기술
- `sCreateClassMenuWarning` — 직업 재선택 확인
- `sYes` / `sNo`

## OpenMW KR1 → Classic 변환

- 명시적 `@topic#` 링크 INFO: **7,692개**
- TOP: **5,843행**
- MRK: **376행**
- CEL 지역/셀 이름: **1,439행**
- Classic INI 표시 문자열: **63개**
- compiled SCPT: **236개 byte-identical 유지**
- 일반 번역 내용 변경 INFO 177개는 기존 RC7 방침대로 제외
- 미해결 토픽 마커: **0**
- CP949 변환 fallback: **0**

Classic 전용 Voice `ANAM="Wilderness"` 보정 등 RC6의 Classic 호환 수정도 유지합니다.

## 폰트

현재 RC7은 검증된 **RC6 Classic CP949 폰트 8개를 바이트 그대로 사용**합니다.

```text
Fonts/Magic_Cards_Regular.fnt
Fonts/Magic_Cards_Regular_0_Lod_A.tex
Fonts/century_gothic_big.fnt
Fonts/century_gothic_big_0_Lod_A.tex
Fonts/century_gothic_font_regular.fnt
Fonts/century_gothic_font_regular_0_Lod_A.tex
Fonts/daedric_font.fnt
Fonts/daedric_font_0_Lod_A.tex
```

한글 DBCS 템플릿은 원래 검증된 **8x11 geometry**를 유지합니다. 9x12/10x14로 확대했던 시험판은 Classic에서 전체 한글이 깨지는 것이 확인되어 완전히 철회했습니다.

특정 자막과 직업 질문의 프롬프트만 흐리고 같은 화면의 선택지는 선명한 현상은 폰트 파일 자체보다는 UI 위치/texel alignment 경로로 조사 중입니다. MCP의 **UI display quality fix**는 반드시 MCP 단계에서 먼저 적용하는 것을 권장합니다.

## 현재 검증 상태

- RC7 번역 payload 정적 검증: **PASS**
- TOP/MRK marker resolution: **PASS / unresolved 0**
- CEL CP949 변환: **PASS / 1,439행**
- Classic master CEL alias 4종 생성: **PASS**
- INI 63개 생성 및 병합: **PASS**
- 중복 Question 섹션 정리 Windows 테스트: **PASS**
- 기존 Sound/Model/Texture/일반 INI 설정 보존: **PASS**
- Windows BAT 실행: **PASS**
- 알 수 없는 MCP 전체 SHA + Japanese-localization 코드 패턴 패치: **PASS**
- 기존 EXE 백업이 있는 상태의 backup rollover: **PASS**
- RC6 폰트 8개 byte-identical: **PASS**
- Nested MO2 ZIP 구조 및 CEL alias 검증: **PASS**
- 번역 ESP 늦은 고정 timestamp 검증: **PASS**
- Full ZIP 무결성: **PASS**

사용자가 보고한 **직업 질문 완료 후 재선택 확인창의 No 경로 크래시**는 중복 Question 섹션 정리와 로드 순서 보강 후 실제 Classic 런타임 재테스트가 필요합니다. 해결됐다고 아직 확정하지 않습니다.

참고로 `직업을 다시 선택하시겠습니까?`라는 확인창에서 **Yes가 질문 단계로 돌아가는 것은 질문 의미상 정상 동작**입니다. 문제는 No가 확인창을 닫고 결과창으로 돌아가지 않고 크래시하는 현상입니다.

## 핵심 SHA-256

```text
68e463f0b9adb82c4f54d695e49b3bca236d0446e0566b5c1b2c3e8583253a67  Full ZIP
9d44c2d7558c364aa3b3bafa69547e9d0b5157012d7d021908df54321ca23ef9  Nested MO2 ZIP
bd277b2a2d2b343badd74f26a1ac3190466e6149914f7342135bf1112145dda5  ESP
ba68eeeef7047cd0253acf87288398e358ee458248b6d1cff8a5e14d0eba5747  CEL table
41f706ff4073a39abc9e55e09c82d37299a8d0f5ce21b594dca3cb42d03fc3ae  Classic INI overlay
```

## 저장소에 포함하지 않는 것

- Bethesda의 `Morrowind.exe` 원본/수정본
- 게임 원본 ESM

## Status

**v1.0.7-rc7 / Release / CP949 Code Patch / nested MO2 archive / KR1 TOP+MRK+master CEL aliases / 63 Classic INI strings / original RC6 Classic fonts**
