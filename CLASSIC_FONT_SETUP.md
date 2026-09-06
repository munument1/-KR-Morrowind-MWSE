# Classic Morrowind CP949 폰트 설치

Classic Morrowind에서 CP949 한국어를 실제로 표시하려면 **CP949 글리프가 들어 있는 bitmap font**가 필요합니다. 실행 파일 패치는 CP949 바이트를 해석할 뿐이고 실제 글자 모양은 FNT/TEX가 제공합니다.

## 일반 사용자 권장 방식

RC7 Release에는 사전 생성된 폰트팩이 포함되어 있습니다.

```text
Morrowind_CP949_Classic_Fonts.zip
```

이 폰트팩은 새로 생성한 변형이 아니라 **RC6 배포 ZIP에서 실제 사용하던 Classic CP949 FNT/TEX 8개를 내용 수정 없이 그대로 재사용**한 것입니다. RC7은 폰트 엔진이나 CP949 DBCS atlas 형식을 바꾸지 않았으므로 RC6 폰트를 그대로 사용합니다.

권장 구조:

```text
Data Files/
  Fonts/
    Magic_Cards_Regular.fnt
    Magic_Cards_Regular_0_Lod_A.tex
    century_gothic_big.fnt
    century_gothic_big_0_Lod_A.tex
    century_gothic_font_regular.fnt
    century_gothic_font_regular_0_Lod_A.tex
    daedric_font.fnt
    daedric_font_0_Lod_A.tex
```

Classic 쪽에서는 기존 `Morrowind.ini`의 폰트 이름을 바꾸지 않는 것을 기준으로 합니다. 폰트팩이 원래 경로에 호환 FNT/TEX를 제공합니다.

## RC6 폰트 재사용 검증

RC7 릴리스 워크플로는 RC6 릴리스 패키지에서 폰트 8개를 직접 꺼내고 각 파일의 SHA-256을 고정값과 비교합니다. 하나라도 RC6 원본과 다르면 릴리스 작업이 실패합니다.

현재 RC7 폰트 ZIP SHA-256:

```text
3f55fc91f4f27182906baef64b1747d6a3931c2fdd0bc36f7e60fa3ae6b11b8c
```

ZIP 컨테이너는 재현 가능하도록 다시 포장했지만 내부 FNT/TEX 바이트는 RC6과 동일합니다.

## clean install에 필요한 것

1. Morrowind GOTY 1.6.0.1820
2. MCP Japanese localization compatibility가 적용된 자신의 `Morrowind.exe`
3. RC7 Release의 `Morrowind_CP949_Executable_Patcher_v1.0.7-rc7.zip`
4. RC7 Release의 `Morrowind_CP949_Classic_Fonts.zip`
5. RC7 Release의 `Morrowind_Korean_ReTranslation_v1.0.7-rc7_Classic_CP949.zip`

실행 파일, 폰트, 번역 중 하나라도 빠지면 정상적인 Classic CP949 환경이 완성되지 않습니다.

## 설치

MO2 사용 시 `Morrowind_CP949_Classic_Fonts.zip`을 별도 모드로 설치하고 번역 모드와 함께 활성화합니다.

직접 설치한다면 `Data Files/Fonts`의 동명 파일을 먼저 백업한 뒤 폰트팩의 `Data Files/Fonts` 내용을 게임 폴더에 병합합니다.

## 재현·개발·커스텀 글꼴용 선택 도구

일반 사용자는 폰트 생성 스크립트를 실행할 필요가 없습니다. `tools/build_classic_cp949_fonts.py`는 다음 용도로만 유지합니다.

- 배포 폰트 구조 재현
- 개발 검증
- 다른 TTF로 커스텀 폰트 제작
- FNT/TEX 구조 실험

필요한 Python 패키지:

```bash
python -m pip install -r tools/requirements-fonts.txt
```

예시:

```bat
python tools\build_classic_cp949_fonts.py ^
  --vanilla-fonts "C:\Games\Morrowind\Data Files\Fonts" ^
  --ttf "C:\Fonts\KoreanFont.ttf" ^
  --output "build\Classic_CP949_Fonts"
```

빌더는 다음을 처리합니다.

- 원본 single-byte 글리프 atlas 보존
- TEX를 `2048 x 2048 RGBA`로 확장
- CP949 DBCS grid를 `y=512`부터 생성
- lead `0x81..0xFD`
- trail `0x41..0x5A`, `0x61..0x7A`, `0x81..0xFE`
- 셀 크기 `8 x 11`
- 원본 FNT UV를 2048 atlas에 맞게 재계산
- FNT glyph slot `0xFF`를 CP949 DBCS template으로 설정
- 현대 한글 11,172자 coverage 검증
- 생성 파일 SHA-256 manifest 작성

일반 사용자 경로는 **Release의 RC6 재사용 사전 생성 폰트팩 설치**이고, 이 빌더는 선택적인 개발 도구입니다.
