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

## 패키지 구조

바깥 Full ZIP을 풀면 다음이 있습니다.

```text
Apply_CP949_Patch.bat
Morrowind_Korean_INI.ini
Morrowind_Korean_ReTranslation_v1.0.7-rc7_MO2.zip
README_RC7.txt
```

번역 데이터와 폰트는 바깥 ZIP의 `Data Files` 폴더에 직접 넣지 않습니다.

안쪽의 다음 ZIP을 **Mod Organizer 2에서 바로 설치**합니다.

```text
Morrowind_Korean_ReTranslation_v1.0.7-rc7_MO2.zip
```

MO2 ZIP의 데이터 루트 구조:

```text
Morrowind_Korean_ReTranslation.esp
Morrowind_Korean_ReTranslation.top
Morrowind_Korean_ReTranslation.mrk
Morrowind_Korean_ReTranslation.cel
Fonts/
```

`Fonts/`에는 RC6에서 실제 사용하던 Classic CP949 FNT/TEX 8개를 바이트 그대로 재사용합니다.

## 설치

1. Morrowind GOTY 1.6.0.1820을 준비합니다.
2. Morrowind Code Patch(MCP)를 적용합니다.
3. MCP에서 **Japanese localization compatibility**를 활성화합니다.
4. Better typography, UI display quality fix 등 원하는 다른 MCP 옵션도 이 단계에서 먼저 적용합니다.
5. Full ZIP의 `Apply_CP949_Patch.bat`과 `Morrowind_Korean_INI.ini`를 Morrowind 게임 폴더에 둡니다.
6. `Apply_CP949_Patch.bat`을 실행합니다.
7. MO2에서 `Morrowind_Korean_ReTranslation_v1.0.7-rc7_MO2.zip`을 설치합니다.
8. `Morrowind_Korean_ReTranslation.esp`를 활성화하고 이전 한국어 ESP는 비활성화합니다.

Python 설치는 필요 없습니다.

## CP949 Code Patch

우리 패치도 엄밀히 말하면 `Morrowind.exe`를 수정하는 **CP949 Code Patch**입니다.

기존 BAT는 `Morrowind.exe` 전체 SHA-256 화이트리스트를 사용했기 때문에 MCP에서 Better typography 등 다른 옵션을 추가하면 실행 파일 전체 해시가 달라져 패치를 거부할 수 있었습니다.

현재 BAT는 다음 방식으로 동작합니다.

- 이미 CP949 루틴이 있으면 건너뜀
- 그렇지 않으면 `0x3457C0`의 **MCP Japanese localization 코드 패턴을 직접 검증**
- 전체 EXE SHA-256이 알려지지 않은 MCP 옵션 조합이어도 해당 코드 패턴이 정확하면 CP949 패치 적용
- 코드 패턴이 다르면 안전을 위해 중단
- 패치 후 해당 위치의 CP949 바이트를 다시 검증
- 수정 전 `Morrowind.exe.cp949-backup` 생성

따라서 Better typography, UI display quality fix 등 **다른 MCP 옵션 때문에 전체 EXE 해시가 달라지는 것만으로 실패하지 않습니다.**

알 수 없는 전체 SHA이지만 올바른 Japanese-localization 코드 패턴을 가진 더미 실행 파일을 Windows `cmd.exe`에서 실제 BAT로 패치하는 CI도 통과합니다.

## Classic Morrowind.ini 한국어

OpenMW KR1의 `openmw.cfg` fallback 중 Classic `Morrowind.ini`에 대응하는 표시 문자열 **63개**를 CP949로 변환해 포함합니다.

- `[Question 1]`~`[Question 10]`: 직업 질문/답변 40개
- `[Level Up]`: Level2~Level20 + Default 20개
- `[Blood]`: Texture Name 0~2 3개

BAT는 섹션 전체를 덮지 않고 **위 63개 키의 값만 변경**합니다.

다음 설정은 보존합니다.

- Question의 `Sound=`
- Blood의 모델/텍스처 경로
- `[Fonts]`
- 기타 사용자/MCP INI 설정

`Morrowind.ini.cp949-backup`도 자동 생성합니다.

## OpenMW KR1 → Classic 변환 내용

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

RC7은 RC6 Classic CP949 폰트를 그대로 사용합니다.

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

릴리스 빌드에서 8개 파일의 SHA-256을 RC6 원본과 직접 대조합니다.

## 현재 검증 상태

- RC7 번역 payload 정적 검증: **PASS**
- TOP/MRK marker resolution: **PASS / unresolved 0**
- CEL CP949 변환: **PASS / 1,439행**
- INI 63개 생성 및 병합: **PASS**
- Windows `cmd.exe` BAT 실행: **PASS**
- 기존 Sound/Model/Texture/일반 INI 설정 보존: **PASS**
- 알 수 없는 MCP 전체 SHA + 올바른 Japanese-localization 코드 패턴 패치 경로: **PASS**
- RC6 폰트 8개 byte-identical: **PASS**
- Nested MO2 ZIP 구조 검증: **PASS**
- Full ZIP 무결성: **PASS**

사용자가 보고한 **직업 질문 완료 후 No/재선택 경로 크래시**는 실제 Classic 런타임 재테스트가 필요합니다. 해결됐다고 아직 확정하지 않습니다.

## 현재 Release SHA-256

```text
f1bc125f0b4cdcf41f4374cb4401e40a9c7faa3e0c7bdd15cff4027a59c1bf39  Morrowind_Classic_CP949_Korean_v1.0.7-rc7_Full.zip
628188d673a64a38d5f5d09ac753e055dd3fec1d8b2257bbd724d821dacf446b  Morrowind_Korean_ReTranslation_v1.0.7-rc7_MO2.zip
bd277b2a2d2b343badd74f26a1ac3190466e6149914f7342135bf1112145dda5  ESP
ba68eeeef7047cd0253acf87288398e358ee458248b6d1cff8a5e14d0eba5747  CEL
41f706ff4073a39abc9e55e09c82d37299a8d0f5ce21b594dca3cb42d03fc3ae  Classic INI overlay
```

## 저장소에 포함하지 않는 것

- Bethesda의 `Morrowind.exe` 원본/수정본
- 게임 원본 ESM

## Status

**v1.0.7-rc7 / Release / CP949 Code Patch / nested MO2 archive / KR1 TOP+MRK+CEL / 63 Classic INI strings / RC6 fonts reused**
