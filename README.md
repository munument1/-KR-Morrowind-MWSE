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
3ef8bdc548e18be5b318d354b6753758040a1f818c9e522fd4cf0ac7b1b90f43
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
Fonts/
```

현재 Nested MO2 ZIP SHA-256:

```text
acafb9518d93b477186e9f9d53b372394545fc68ba068e3fafffbf2a2d070b5a
```

## 설치

1. Morrowind GOTY 1.6.0.1820 준비
2. Morrowind Code Patch(MCP) 적용
3. MCP에서 **Japanese localization compatibility** 활성화
4. Better typography, UI display quality fix 등 원하는 MCP 옵션도 이 단계에서 먼저 적용
5. Full ZIP의 `Apply_CP949_Patch.bat`과 `Morrowind_Korean_INI.ini`를 게임 폴더에 배치
6. `Apply_CP949_Patch.bat` 실행
7. MO2에서 안쪽 `Morrowind_Korean_ReTranslation_v1.0.7-rc7_MO2.zip` 설치
8. `Morrowind_Korean_ReTranslation.esp` 활성화, 이전 한국어 ESP 비활성화

Python 설치는 필요 없습니다.

## CP949 Code Patch

우리 패치도 `Morrowind.exe`를 수정하는 **CP949 Code Patch**입니다.

현재 BAT는 전체 EXE SHA-256만으로 허용/거부하지 않습니다.

- 이미 CP949 루틴이 있으면 건너뜀
- 아니면 `0x3457C0`의 **MCP Japanese localization 코드 패턴을 직접 검증**
- Better typography/UI fix 등 다른 MCP 옵션으로 전체 EXE 해시가 달라도 대상 코드 패턴이 정확하면 패치
- 코드 패턴이 다르면 중단
- 기존 `Morrowind.exe.cp949-backup`이 있으면 `.1`, `.2` 식으로 새 백업을 생성
- 패치 후 CP949 코드 바이트를 재검증

Windows `cmd.exe` CI에서 알 수 없는 전체 SHA + 올바른 Japanese-localization 코드 패턴과 기존 백업이 있는 경우까지 검증합니다.

## Classic Morrowind.ini 한국어

OpenMW KR1의 `openmw.cfg` fallback 중 Classic `Morrowind.ini`에 대응하는 표시 문자열 **63개**를 CP949로 변환합니다.

- `[Question 1]`~`[Question 10]`: 직업 질문/답변 40개
- `[Level Up]`: Level2~Level20 + Default 20개
- `[Blood]`: Texture Name 0~2 3개

BAT는 해당 63개 키의 값만 바꾸며 `Sound=`, Blood 모델/텍스처 경로, `[Fonts]`, 기타 사용자/MCP 설정은 보존합니다.

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

## 폰트 크기 조정

기존 RC6/초기 RC7 폰트는 CP949 DBCS 템플릿을 네 폰트 모두 사실상 동일한 **8x11 표시 크기**로 사용해, 한글이 영문보다 작게 보이고 특히 자막에서 작고 흐리게 느껴질 수 있었습니다.

현재 RC7은 RC6의 검증된 8개 FNT/TEX 파일을 **매 빌드마다 원본으로 다시 복원한 뒤**, 한국어 부분만 다음처럼 조정합니다.

- CP949 저장 셀과 UV 계산은 기존 **8x11** 그대로 유지
- 영문/ASCII 글리프는 변경하지 않음
- CP949 셀 내부 글리프를 nearest-neighbour 방식으로 확대해 셀을 더 크게 사용
- `Magic_Cards_Regular`: DBCS 표시 geometry **9x12**
- `century_gothic_font_regular`: **9x12**
- `century_gothic_big`: **10x14**
- `daedric_font`: **9x12**

따라서 기존 CP949 코드 패치의 셀/UV 계산을 바꾸지 않으면서 한글 표시 크기만 키웁니다.

튜닝 도구:

```text
tools/tune_classic_cp949_fonts.py
```

검증 결과는 Release의 다음 파일에도 기록됩니다.

```text
classic_cp949_font_tuning.json
```

기존 RC7 릴리스 빌드가 다시 실행되더라도 `Tune RC7 Classic Korean fonts` 워크플로가 성공 후 자동으로 RC6 폰트 원본에서 다시 튜닝하므로 **중복 확대되지 않습니다.**

## 현재 검증 상태

- RC7 번역 payload 정적 검증: **PASS**
- TOP/MRK marker resolution: **PASS / unresolved 0**
- CEL CP949 변환: **PASS / 1,439행**
- INI 63개 생성 및 병합: **PASS**
- Windows BAT 실행: **PASS**
- 기존 Sound/Model/Texture/일반 INI 설정 보존: **PASS**
- 알 수 없는 MCP 전체 SHA + Japanese-localization 코드 패턴 패치: **PASS**
- 기존 EXE 백업이 있는 상태의 backup rollover: **PASS**
- RC6 폰트 원본 해시 검증 후 Korean font tuning: **PASS**
- DBCS FNT UV 보존: **PASS**
- Nested MO2 ZIP 구조 검증: **PASS**
- Full ZIP 무결성: **PASS**

폰트 조정은 정적 검증을 통과했지만 실제 Classic 화면에서의 최종 크기와 자막 선명도는 런타임 테스트가 필요합니다.

사용자가 보고한 **직업 질문 완료 후 No/재선택 경로 크래시**도 실제 Classic 런타임 재테스트 전에는 해결됐다고 확정하지 않습니다.

## 핵심 SHA-256

```text
3ef8bdc548e18be5b318d354b6753758040a1f818c9e522fd4cf0ac7b1b90f43  Full ZIP
acafb9518d93b477186e9f9d53b372394545fc68ba068e3fafffbf2a2d070b5a  Nested MO2 ZIP
bd277b2a2d2b343badd74f26a1ac3190466e6149914f7342135bf1112145dda5  ESP
ba68eeeef7047cd0253acf87288398e358ee458248b6d1cff8a5e14d0eba5747  CEL
41f706ff4073a39abc9e55e09c82d37299a8d0f5ce21b594dca3cb42d03fc3ae  Classic INI overlay
d37de9f79628f4fc8eeca6b5ab1dab757f59b0656564a40704d5080659cc9cf8  Font tuning validation JSON
```

## 저장소에 포함하지 않는 것

- Bethesda의 `Morrowind.exe` 원본/수정본
- 게임 원본 ESM

## Status

**v1.0.7-rc7 / Release / CP949 Code Patch / nested MO2 archive / KR1 TOP+MRK+CEL / 63 Classic INI strings / tuned Classic Korean fonts**
