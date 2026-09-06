# Morrowind CP949 Korean Support

Classic **The Elder Scrolls III: Morrowind 1.6.0.1820**에서 한국어를 표시하고, OpenMW용 한국어 재번역 데이터를 Classic 엔진에서 사용할 수 있도록 변환하는 프로젝트입니다.

현재 권장 배포본은 **v1.0.7-rc7 Classic CP949**입니다.

## 현재 릴리스

태그:

```text
v1.0.7-rc7-classic-cp949
```

일반 사용자는 Release에서 다음 **합본 ZIP 하나만** 받으면 됩니다.

```text
Morrowind_Classic_CP949_Korean_v1.0.7-rc7_Full.zip
```

현재 합본에는 다음이 모두 들어 있습니다.

- `Data Files/Morrowind_Korean_ReTranslation.esp`
- `Data Files/Morrowind_Korean_ReTranslation.top`
- `Data Files/Morrowind_Korean_ReTranslation.mrk`
- `Data Files/Morrowind_Korean_ReTranslation.cel` — OpenMW KR1 지역/셀 이름 1,439행을 Classic CP949용으로 변환
- RC6에서 실제 사용하던 Classic CP949 FNT/TEX 폰트 8개
- `Morrowind_Korean_INI.ini` — OpenMW KR1의 Classic 대응 INI 표시 문자열 63개
- `Apply_CP949_Patch.bat` — Python 없이 실행 파일 패치와 INI 표시 문자열 병합
- 설치 안내문

Bethesda의 `Morrowind.exe` 자체는 포함하지 않습니다.

## RC7 핵심 변경

### 대화 토픽 링크

RC6 Classic CP949를 기준으로 OpenMW KR1의 대화 링크 수정만 안전하게 이식합니다.

- 명시적 `@topic#` 링크가 추가된 INFO **7,692개** 반영
- OpenMW KR1 최종 TOP **5,843행** CP949 변환
- OpenMW KR1 최종 MRK **376행** CP949 변환
- 일반 번역 내용이 달라진 INFO **177개는 제외**
- Classic CP949 RC6의 compiled SCPT **236개 바이트 그대로 보존**
- Classic 전용 Voice `ANAM="Wilderness"` 보정 유지
- CP949 변환 fallback **0**
- 미해결 토픽 마커 **0**

이 방식으로 하스팟 안타볼리스, 라니스 아트리스, 아지라/갈베디르 등 기존에 보고되었던 대화 토픽 누락 계열을 OpenMW KR1 기준 링크 데이터에 맞춰 처리합니다.

### 지역/셀 이름

OpenMW KR1의 지역 이름은 ESP만으로 처리되지 않고 `Morrowind_Korean_ReTranslation.cel`에도 들어 있습니다.

기존 Classic RC7 합본에서 이 파일이 빠져 있어 `Seyda Neen`, `Balmora`, `Bitter Coast Region` 등의 이름이 영어로 표시되는 문제가 있었습니다. 현재 합본은 KR1 `.cel` **1,439행**을 CP949로 변환해 포함합니다.

예:

```text
Seyda Neen -> 세이다 닌
Balmora -> 발모라
Ascadian Isles Region -> 아스카디안 제도 지역
Bitter Coast Region -> 쓰라린 해안 지역
Grazelands Region -> 그래즐랜드 지역
```

### Classic Morrowind.ini 표시 문자열 63개

OpenMW KR1은 Classic에서 `Morrowind.ini`가 담당하던 여러 표시 문자열을 `openmw.cfg` fallback으로 제공합니다. 기존 Classic RC7에서는 직업 질문만 이식했지만, 현재는 Classic에 대응되는 표시 문자열을 모두 한 번에 변환합니다.

구성:

- `[Question 1]`~`[Question 10]`: 질문/답변 **40개**
- `[Level Up]`: `Level2`~`Level20` + `Default` **20개**
- `[Blood]`: `Texture Name 0`~`Texture Name 2` **3개**
- 합계 **63개**

생성 파일:

```text
Morrowind_Korean_INI.ini
```

중요하게, BAT는 섹션 전체를 덮어쓰지 않습니다. **63개 표시 키의 값만 갱신**합니다.

따라서 다음과 같은 기술 설정은 기존 `Morrowind.ini` 값을 그대로 보존합니다.

- 직업 질문의 `Sound=`
- `[Blood]`의 모델/텍스처 파일 경로
- `[Fonts]` 설정
- 그 밖의 사용자/MCP 설정

## 설치

### 1. 게임과 MCP 준비

1. Morrowind GOTY 1.6.0.1820 준비
2. Morrowind Code Patch(MCP) 적용
3. MCP에서 **Japanese localization compatibility** 옵션 활성화

### 2. 합본 ZIP 설치

`Morrowind_Classic_CP949_Korean_v1.0.7-rc7_Full.zip`을 Morrowind 게임 폴더에 풀어 기존 `Data Files`와 병합합니다.

별도 번역 ZIP이나 폰트 ZIP을 받을 필요가 없습니다.

### 3. BAT 실행

게임 폴더의 `Apply_CP949_Patch.bat`을 더블클릭합니다.

**Python 설치는 필요 없습니다.** BAT가 Windows 기본 PowerShell을 내부적으로 사용합니다.

BAT는 다음을 처리합니다.

1. `Morrowind.exe`의 CP949 패치 상태 확인
2. 아직 패치되지 않았다면 지원되는 MCP 실행 파일 SHA-256인지 검사
3. `Morrowind.exe.cp949-backup` 백업 생성 후 CP949 DBCS 루틴 적용
4. 이미 동일한 CP949 루틴이 적용되어 있으면 실행 파일 패치는 건너뜀
5. `Morrowind.ini`를 `Morrowind.ini.cp949-backup`으로 백업
6. `Morrowind_Korean_INI.ini`의 **63개 표시 키만** 기존 INI에 병합
7. 병합된 63개 값을 다시 읽어 검증

현재 지원 실행 파일 입력 SHA-256:

```text
8fe33fb11b6a682721e7456af78eefd228e8b60dc7c9f4253f89a361f8a4dfc5  MCP default
c3585b91741689057c18ff86a1c3381d47278cd1d81443d38ed3b179c2fa1cd8  MCP Japanese localization enabled
a87ee7f9239023469d4c031e6dab87648a316ab8c1354e96c2478aca3376167c  MCP Japanese localization + current project option set
```

현재 프로젝트 기준 입력:

```text
a87ee7f9239023469d4c031e6dab87648a316ab8c1354e96c2478aca3376167c
```

위 입력의 CP949 패치 출력 SHA-256:

```text
bff9c8381d59657e5dfbfc66058745996327b20f4516f63e54ce9c7f726b45fc
```

참고로 RC6에 실제 포함되어 있던 CP949 `Morrowind.exe`의 `0x3457C0` 루틴과 현재 BAT가 적용하는 루틴은 바이트 단위로 동일합니다.

`tools/patch_morrowind_cp949.py`는 저장소의 개발/검증용 도구로만 남기며 일반 사용자 배포본에는 포함하지 않습니다.

### 4. 번역 활성화

- `Morrowind_Korean_ReTranslation.esp` 활성화
- 이전 한국어 번역 ESP가 있다면 비활성화

## RC6 폰트 재사용

RC7은 폰트 엔진이나 CP949 DBCS atlas 형식을 변경하지 않았습니다. 따라서 **RC6 배포 ZIP에 들어 있던 실제 Classic CP949 폰트 파일 8개를 바이트 그대로 재사용**합니다.

포함 파일:

```text
Data Files/Fonts/Magic_Cards_Regular.fnt
Data Files/Fonts/Magic_Cards_Regular_0_Lod_A.tex
Data Files/Fonts/century_gothic_big.fnt
Data Files/Fonts/century_gothic_big_0_Lod_A.tex
Data Files/Fonts/century_gothic_font_regular.fnt
Data Files/Fonts/century_gothic_font_regular_0_Lod_A.tex
Data Files/Fonts/daedric_font.fnt
Data Files/Fonts/daedric_font_0_Lod_A.tex
```

RC7 릴리스 빌드는 이 8개 파일의 SHA-256을 RC6 원본과 직접 대조해 하나라도 달라지면 실패합니다.

재현·개발·커스텀 글꼴용 빌더:

```text
tools/build_classic_cp949_fonts.py
```

자세한 내용: [`CLASSIC_FONT_SETUP.md`](CLASSIC_FONT_SETUP.md)

## 검증 상태

RC7 빌드는 고정된 OpenMW KR1 및 Classic RC6 입력 해시를 기준으로 재현하며 다음 검증을 통과해야 Release를 갱신합니다.

- DIAL 수/구조 보존: **PASS**
- INFO 키 구조 보존: **PASS**
- marker-only INFO 변경 7,692: **PASS**
- 일반 번역 변경 177개 제외: **PASS**
- TOP 5,843행: **PASS**
- MRK 376행: **PASS**
- 미해결 `@topic#` 마커: **0**
- CP949 변환 fallback: **0**
- compiled SCPT byte-identical: **PASS**
- 예상한 INFO `NAME` 외 변경 없음: **PASS**
- Classic Voice `Wilderness` 보정 유지: **PASS**
- KR1 CEL: **1,439행 / CP949 변환 PASS**
- KR1 Question 표시 문자열: **40개 / PASS**
- KR1 Level Up 표시 문자열: **20개 / PASS**
- KR1 Blood 표시 이름: **3개 / PASS**
- Classic INI 표시 문자열 합계: **63개 / PASS**
- INI overlay에 `Sound`/모델/텍스처/폰트 기술 키 없음: **PASS**
- Windows `cmd.exe` BAT 실행 및 63개 키 병합: **PASS**
- Windows BAT 테스트에서 기존 `Sound`/Blood 모델·텍스처/일반 INI 설정 보존: **PASS**
- RC6 FNT/TEX 8개 byte-identical: **PASS**
- Full ZIP 무결성 검사: **PASS**

## 런타임 확인 상태

정적 검증과 사용자 제보를 통해 다음 누락 원인은 확인하여 보정했습니다.

- 지역/셀 이름 영어 표시 → KR1 `.cel` 누락
- 직업 자동 생성 10문항 영어 표시 → Classic INI 변환 누락
- 레벨업 문구/혈액 표시 이름 → 같은 KR1 fallback 계열을 추가로 Classic INI에 이식

사용자가 보고한 **직업 질문 완료 후 재선택/No 경로의 크래시**는 이 보정본으로 실제 Classic Morrowind 재테스트가 필요합니다. 현재 단계에서는 크래시 해결을 확정하지 않습니다.

자막의 한글만 흐릿하게 보이는 문제 역시 별도 런타임 렌더링 이슈로 추적 중이며, 다른 UI 한글이 정상인 점을 고려하면 전체 CP949 폰트 데이터 손상으로 판단하지 않습니다.

## Classic CP949 스크립트 처리

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

## 포팅 도구

대화 토픽 링크:

```text
tools/port_openmw_kr1_topic_links.py
```

Classic sidecar/INI 표시 문자열:

```text
tools/port_openmw_kr1_classic_sidecars.py
```

## RC7 SHA-256

현재 Full ZIP:

```text
1ac160bc7c147aafed3c6a6ac1e4e3ab945e2af7a8e09f1c0fec4c2859aa8a2b  Morrowind_Classic_CP949_Korean_v1.0.7-rc7_Full.zip
```

핵심 데이터:

```text
bd277b2a2d2b343badd74f26a1ac3190466e6149914f7342135bf1112145dda5  ESP
a5831b89d8dd7e5e4a30177d3b2df3d775eade2ce030cbb889bd226266d1c0f8  TOP
9e4a426add4bb006365be358b125ee88714819aba3612a6eaa1ea2da54f4bc55  MRK
ba68eeeef7047cd0253acf87288398e358ee458248b6d1cff8a5e14d0eba5747  CEL
41f706ff4073a39abc9e55e09c82d37299a8d0f5ce21b594dca3cb42d03fc3ae  Classic INI overlay
```

## 저장소에 포함하지 않는 것

- Bethesda의 `Morrowind.exe` 원본/수정본
- 게임 원본 ESM

## Status

**v1.0.7-rc7 / Release / Full ZIP / no-Python BAT / KR1 TOP+MRK+CEL / 63 Classic INI strings / Windows BAT validated / RC6 fonts reused**
