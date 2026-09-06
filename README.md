# Morrowind CP949 Korean Support

Classic **The Elder Scrolls III: Morrowind 1.6.0.1820**에서 한국어를 표시하고, OpenMW용 한국어 재번역 데이터를 Classic 엔진에서 사용할 수 있도록 변환하는 프로젝트입니다.

현재 권장 배포본은 **v1.0.7-rc7 Classic CP949**입니다.

## 현재 릴리스

태그:

```text
v1.0.7-rc7-classic-cp949
```

Release에서 다음 세 파일을 받으면 됩니다.

```text
Morrowind_Korean_ReTranslation_v1.0.7-rc7_Classic_CP949.zip
Morrowind_CP949_Executable_Patcher_v1.0.7-rc7.zip
Morrowind_CP949_Classic_Fonts.zip
```

- **번역 ZIP** — RC7 ESP/TOP/MRK
- **실행 파일 패처** — MCP Japanese localization 적용본을 CP949 대응으로 변경
- **폰트 ZIP** — RC6에서 실제 사용하던 Classic CP949 FNT/TEX 8개를 그대로 재사용

Bethesda의 `Morrowind.exe` 전체 파일은 Release에 포함하지 않습니다.

RC7은 기존 Classic CP949 RC6을 기반으로, 최신 OpenMW KR1에서 검증된 **대화 토픽/키워드 링크 수정만** Classic용으로 이식한 버전입니다.

## RC7 핵심 변경

- 명시적 `@topic#` 링크가 추가된 INFO **7,692개** 반영
- OpenMW KR1 최종 TOP **5,843행** CP949 변환
- OpenMW KR1 최종 MRK **376행** CP949 변환
- 일반 번역 내용이 달라진 INFO **177개는 제외**
- Classic CP949 RC6의 compiled SCPT **236개 바이트 그대로 보존**
- Classic 전용 Voice `ANAM="Wilderness"` 보정 유지
- CP949 변환 fallback **0**
- 미해결 토픽 마커 **0**

이 방식으로 하스팟 안타볼리스, 라니스 아트리스, 아지라/갈베디르 등 기존에 보고되었던 대화 토픽 누락 계열을 OpenMW KR1 기준 데이터에 맞춰 처리합니다.

## Classic에서 필요한 구성

Classic에서 한글을 표시하려면 다음 세 요소가 모두 필요합니다.

1. **CP949 대응 실행 파일**
2. **CP949 bitmap font (FNT/TEX)**
3. **RC7 CP949 번역 ESP/TOP/MRK**

### 실행 파일

권장 경로는 다음과 같습니다.

1. Morrowind GOTY 1.6.0.1820 준비
2. Morrowind Code Patch(MCP) 적용
3. MCP에서 **Japanese localization compatibility** 옵션 활성화
4. 자신의 `Morrowind.exe`에 RC7 실행 파일 패처 적용

패처:

```text
tools/patch_morrowind_cp949.py
```

현재 지원 입력 SHA-256:

```text
8fe33fb11b6a682721e7456af78eefd228e8b60dc7c9f4253f89a361f8a4dfc5  MCP default
c3585b91741689057c18ff86a1c3381d47278cd1d81443d38ed3b179c2fa1cd8  MCP Japanese localization enabled
a87ee7f9239023469d4c031e6dab87648a316ab8c1354e96c2478aca3376167c  MCP Japanese localization + current project option set
```

현재 프로젝트에서 검증한 MCP Japanese localization 입력:

```text
a87ee7f9239023469d4c031e6dab87648a316ab8c1354e96c2478aca3376167c
```

위 입력을 CP949 패치한 출력 SHA-256:

```text
bff9c8381d59657e5dfbfc66058745996327b20f4516f63e54ce9c7f726b45fc
```

사용 예:

```bash
py -3 patch_morrowind_cp949.py Morrowind.exe Morrowind.MCP-Korean.exe
```

### 폰트 — RC6 폰트팩 그대로 재사용

RC7은 폰트 엔진이나 CP949 DBCS atlas 형식을 변경하지 않았습니다. 따라서 새 폰트를 만들지 않고 **RC6 배포 ZIP에 들어 있던 실제 Classic CP949 폰트 파일 8개를 바이트 그대로 재사용**합니다.

Release asset:

```text
Morrowind_CP949_Classic_Fonts.zip
```

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

RC7 릴리스 빌드는 이 8개 파일의 SHA-256을 RC6 원본과 직접 대조해 하나라도 달라지면 실패합니다. ZIP 포장만 별도로 재현 가능하게 만들었고 **FNT/TEX 내용은 RC6과 동일**합니다.

재현·개발·커스텀 글꼴용 빌더는 계속 제공합니다.

```text
tools/build_classic_cp949_fonts.py
```

자세한 내용: [`CLASSIC_FONT_SETUP.md`](CLASSIC_FONT_SETUP.md)

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
- RC6 FNT/TEX 8개 byte-identical: **PASS**
- ZIP 무결성 검사: **PASS**

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

## OpenMW KR1 토픽 링크 포팅

도구:

```text
tools/port_openmw_kr1_topic_links.py
```

Classic RC6 ESP를 기준본으로 유지하면서 OpenMW KR1과 INFO 응답을 비교하고, `@topic#` 마커만 제거했을 때 문장이 동일한 경우에만 링크 수정으로 이식합니다.

## 설치 순서

1. Morrowind GOTY 1.6.0.1820 준비
2. MCP 적용 및 Japanese localization compatibility 활성화
3. `Morrowind_CP949_Executable_Patcher_v1.0.7-rc7.zip`의 패처로 자신의 `Morrowind.exe` CP949 패치
4. `Morrowind_CP949_Classic_Fonts.zip` 설치
5. `Morrowind_Korean_ReTranslation_v1.0.7-rc7_Classic_CP949.zip` 설치
6. `Morrowind_Korean_ReTranslation.esp` 활성화
7. 이전 한국어 번역 ESP 비활성화

Classic에서는 기존 `Morrowind.ini` 폰트 이름을 바꾸지 않는 것을 기준으로 합니다.

## RC7 SHA-256

```text
f15f2c4dd16da9cb5e7707fe85a25925f39039310525fbb559184673017e54e2  RC7 translation ZIP
67bb6f9923742044a8c1b254ba81fc20218c4b9504a57c74b38bdaa4516378e5  RC7 executable patcher ZIP
3f55fc91f4f27182906baef64b1747d6a3931c2fdd0bc36f7e60fa3ae6b11b8c  RC6 font payload repackaged for RC7
bd277b2a2d2b343badd74f26a1ac3190466e6149914f7342135bf1112145dda5  RC7 ESP
a5831b89d8dd7e5e4a30177d3b2df3d775eade2ce030cbb889bd226266d1c0f8  RC7 TOP
9e4a426add4bb006365be358b125ee88714819aba3612a6eaa1ea2da54f4bc55  RC7 MRK
```

Release의 `SHA256SUMS.txt`에도 번역 ZIP, 실행 파일 패처, 폰트 ZIP 및 핵심 출력 파일 해시를 함께 제공합니다.

## 저장소에 포함하지 않는 것

- Bethesda의 `Morrowind.exe` 원본/수정본
- 게임 원본 ESM

## Status

**v1.0.7-rc7 / Release / OpenMW KR1 topic-link sync / RC6 fonts reused / MCP Japanese-localization CP949 patch supported**
