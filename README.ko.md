# prfaq-smoke-test

[English](README.md) · 한국어

제품 코드를 쓰기 전에, 이 제품을 만들 가치가 있는지와 어떤 메시지가 먹히는지를 알려 주는 에이전트 스킬입니다.

**PR/FAQ → 각도 3개 → 랜딩페이지 3개 → 같은 금액의 소액 광고 → 비교 → 이긴 각도로 개발(또는 접기)**

- **워킹 백워드(Working Backwards)부터 합니다.** 에이전트가 제품이 출시됐다고 가정하고 아마존식 보도자료와 FAQ를 씁니다. 보도자료가 고객을 끌지 못하면 거기서 멈춥니다. 돈이 들지 않습니다.
- **각도 3개, 페이지 3개.** PR/FAQ에서 서로 다른 구매 이유 3개를 뽑고, 각도마다 페이크 도어 랜딩페이지를 하나씩 만듭니다. 세 페이지는 메시지만 다르고 나머지는 바이트 단위로 같습니다. 그래서 차이는 메시지 하나에서만 나옵니다.
- **정직한 페이크 도어.** 버튼을 누르면 "아직 준비 중"이라고 밝히고 대기 명단을 받는 창이 뜹니다. 결제를 받지 않고, 가짜 후기를 쓰지 않으며, 이메일은 분석 도구로 보내지 않습니다.
- **믿을 수 있는 판정.** 작은 스크립트가 광고비를 쓰기 전에 필요한 방문자 수를 계산하고, 끝난 뒤 결과를 `WINNER`·`TIE`·`BELOW_BAR`·`UNDECIDED` 중 하나로 읽습니다.

## 만들어지는 파일

| 파일 | 내용 |
| --- | --- |
| `prfaq.md` | 보도자료, 외부·내부 FAQ, 에이전트의 판정, 테스트 뒤의 결정과 근거 숫자 |
| `angles.md` | 각도 3개. 각각 PR/FAQ의 어느 줄에서 왔는지, 어떤 가정을 시험하는지 |
| `a.html`, `b.html`, `c.html` | 페이크 도어와 이벤트 기록이 들어간 단일 파일 랜딩페이지 3개 |
| `test-plan.md` | 지표, 예산, 최소 방문자 수, 통과 기준, 종료일. 출시 전에 고정합니다 |

결과는 이렇게 읽습니다.

```
$ python3 scripts/compare.py results.csv --min-visitors 400 --min-rate 0.04
metric: signups per visitor, 95% Wilson interval
variant    visitors     signups    rate   interval          cost/conv
a               520          31   5.96%    4.23% – 8.34%         6.45
b               505          12   2.38%    1.36% – 4.11%        16.67
c               498          14   2.81%    1.68% – 4.66%        14.29
...
verdict: WINNER: a at 5.96% beats every other variant
```

<sub>예시 숫자입니다. 실제 테스트 결과가 아닙니다.</sub>

## 설치

Claude Code:

```
/plugin marketplace add robfold/prfaq-smoke-test
/plugin install prfaq-smoke-test@prfaq-smoke-test
```

다른 에이전트는 [skills CLI](https://skills.sh)로 설치합니다.

```
npx skills add robfold/prfaq-smoke-test
```

또는 [`skills/prfaq-smoke-test/`](skills/prfaq-smoke-test/) 폴더를 에이전트의 스킬 폴더에 복사합니다. Claude Code는 `~/.claude/skills/`입니다.

## 쓰는 법

에이전트에게 "이 아이템으로 PR/FAQ랑 랜딩 3개 만들어", "만들기 전에 스모크 테스트부터 해"라고 하거나 스킬 이름으로 부릅니다. 고객, 문제, 아이디어를 주면 나머지는 에이전트가 찾아보고, 찾을 수 없는 것만 묻습니다.

에이전트는 모든 것을 내 컴퓨터 안에서 쓰고 만듭니다. 페이지 공개, 이메일 수집, 광고비 집행은 각각 내가 명시적으로 허락해야 진행합니다.

비교 스크립트는 Python 3만 있으면 됩니다. 랜딩페이지는 빌드 단계와 의존성이 없습니다.

## 다른 방법이 맞을 때

이미 출시해서 트래픽이 있는 제품이면, 제품 분석 도구의 A/B 테스트를 쓰세요. PR/FAQ 문서만 필요하면 2단계에서 멈추면 됩니다.

## 출처

PR/FAQ는 콜린 브라이어와 빌 카의 『Working Backwards』(2021, 국내판 『순서 파괴』, 다산북스)와 [아마존의 발췌문](https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes)에서 왔습니다. 제품보다 랜딩페이지를 먼저 띄우는 방식은 Buffer의 [Idea to Paying Customers in 7 Weeks](https://buffer.com/resources/idea-to-paying-customers-in-7-weeks-how-we-did-it)를 따랐습니다. 문장은 새로 썼습니다. 각도 3개로 잇는 흐름, 메시지만 다른 페이지 규칙, 비교 스크립트는 이 스킬이 직접 조합한 것입니다. 더 읽을 책은 [SKILL.md](skills/prfaq-smoke-test/SKILL.md) 끝에 있습니다.

## 라이선스

[MIT](LICENSE)
