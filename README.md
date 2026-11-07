# moai-upq5 PR 그림

buzzni/moai 의 PR "moai daemon — Linux, macOS 사용자 서비스 등록 (moai-upq5)" 본문이 쓰는 그림이다.
PR 가지와 이력을 나누지 않는 별도 가지라서, PR 의 변경과 병합 대상에는 들지 않는다. 본문은 이 가지의 커밋으로 그림을 가리킨다.

| 파일 | 내용 |
|---|---|
| `media/01-overview.png` | 변경 개요: 결정 3가지, 등록 경로, 바뀌지 않는 것 |
| `media/02-first-install.png` | 첫 설치: install.sh 의 다섯 조건과 moai daemon install 의 동작 |
| `media/03-update.png` | 업데이트: 서비스를 재시작하는 조건과 결과 |

## 다시 그리기

    python3 make/plot.py ko      make/ko/ 에 PNG 3개를 만든다

matplotlib 과 ARGUS 스타일 모듈(`argus_style.py`)이 필요하다. `plot.py` 머리의 `sys.path` 가 그 모듈의 경로를 가리킨다. 한글 글꼴은 Noto Serif CJK 를 쓴다.
