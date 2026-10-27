# Hermes AI 연구실 — 새 컴퓨터 설치 매뉴얼

이 문서만 보고 **처음 보는 사람도** 다른 Linux 컴퓨터에 지금과 똑같은 연구실을 만들 수 있게 썼다.
SOUL, 템플릿, 스크립트는 이 폴더(`hermes-team/`)에 있는 것을 그대로 쓴다.
구조와 각 직원이 어떻게 움직이는지는 `docs/Hermes_Lab_Overview.pptx`에 정리돼 있다.

> 걸리는 시간: 처음이면 2~3시간. 대부분은 Discord 봇 6개를 만드는 시간이다.
> 표기: `<이름>`은 실제 값으로 바꿔 넣는 자리다. 명령은 모두 일반 사용자로 실행하고, `sudo`는 쓰라고 한 곳에서만 쓴다.

---

## 0. 시작 전에

### 0-1. 어떤 경우인지 고르기

| 경우 | 할 일 |
|---|---|
| **A. 새 연구실을 하나 더 만든다** (다른 PC, 다른 사람, HPC 등) | 이 문서를 처음부터 끝까지 따라 한다. **봇 6개를 새로 만든다.** |
| **B. 지금 연구실을 이 PC에서 다른 PC로 옮긴다** | [부록 A](#부록-a-지금-연구실을-다른-pc로-옮기기)만 따라 한다. |

> **같은 봇 토큰을 두 컴퓨터에서 동시에 쓰면 안 된다.** 나중에 켠 쪽이 연결에 실패한다. 두 곳에서 동시에 돌리려면 봇을 따로 만든다.

### 0-2. 필요한 계정

| 계정 | 쓰는 곳 | 비고 |
|---|---|---|
| **ChatGPT 구독** (Plus/Pro) | 6명 직원의 두뇌 (Hermes 모델) | Hermes에서 "ChatGPT or Codex Subscription"으로 로그인 |
| **Claude 구독** (Pro/Max) | coder·writer의 작성 도구 **Claude Code** (`claude -p`) | **Hermes 모델로 연결하지 않는다** (약관). 명령줄 도구로만 쓴다 |
| **Google 계정** | scholar의 논문 읽기 도구 **Antigravity CLI** (`agy -p`) | |
| **Discord 계정 + 개인 서버** | 직원들과 대화하는 곳 | 서버 관리자여야 함 |
| GitHub (선택) | 예비 모델(Copilot), 원격 백업 | 지금은 예비 모델 없이 운영 중 |

### 0-3. 컴퓨터

- Linux (Ubuntu 22.04 이상 권장), 인터넷, 사용자 계정 하나
- `git`, `curl`, `python3`이 있어야 한다:
  ```bash
  sudo apt update && sudo apt install -y git curl python3
  ```

### 0-4. 검증된 버전 (2026-10-27, 원래 PC에서 `lab.py check` READY)

| 도구 | 버전 |
|---|---|
| Hermes Agent | v0.22.5 (2026.9.24, stable) |
| Claude Code | 2.1.311 |
| Antigravity CLI (`agy`) | 1.4.7 |
| uv | 0.13.5 |
| git | 2.55.0 |

더 새 버전이어도 대개 동작한다. 명령이 바뀐 것 같으면 `<도구> --help`로 확인한다.

### 0-5. ID 기록표 (설치하면서 채운다)

메모장에 아래 표를 복사해 두고 채워 나간다. **토큰은 비밀이다.** 채팅이나 git에 올리지 않는다.

```text
[Discord]
서버(guild) ID        :
로비 채널(#hermes) ID  :
Projects 카테고리 ID   :
내 사용자 ID           :

[봇]          Application ID       봇(사용자) ID         토큰(비밀)
PI(hermes-researcher):
coder               :
analyst             :
reviewer            :
writer              :
scholar             :
```

---

## 1. 기본 도구 설치

### 1-1. git 기본값
```bash
git config --global user.name  "<이름>"
git config --global user.email "<이메일>"
git config --global init.defaultBranch main
```
에이전트가 만드는 commit에 이 이름이 남는다. 마지막 줄을 넣어 두면 새 저장소의 기본 브랜치가 `master`가 아니라 `main`이 된다.

### 1-2. uv (프로젝트별 Python 환경)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv --version
```

### 1-3. Hermes Agent
```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.bashrc
hermes --version
```
- 코드는 `~/.hermes/hermes-agent/`, 명령은 `~/.local/bin/hermes`, 데이터는 `~/.hermes/`에 들어간다.
- `hermes: command not found`가 나오면 `source ~/.bashrc`를 한 번 더 하거나, 터미널을 새로 연다.

### 1-4. Claude Code
```bash
curl -fsSL https://claude.ai/install.sh | bash
claude            # 처음 한 번: Claude 구독 계정으로 로그인 → /exit
claude -p "OK라고만 답해" --max-turns 1
```
- 대화형으로 열면 "이 폴더를 신뢰하겠냐"고 묻는다. 홈 폴더(`~`)에서 열었다면 **No**를 고르고, 프로젝트 폴더에서 열었을 때만 Yes를 고른다. 에이전트가 쓰는 `claude -p` 모드는 이 질문 없이 동작한다.
- 마지막 줄에서 `OK`가 나오면 끝이다.

### 1-5. Antigravity CLI
1. Google Antigravity 공식 안내에 있는 **CLI 설치 방법**대로 `agy`를 설치한다.
2. `agy`를 한 번 실행해 Google 계정으로 로그인한다.
3. 동작을 확인한다:
   ```bash
   agy --version
   agy -p "Reply with OK" --output-format json --print-timeout 2m
   ```
   출력 JSON의 `"status"`가 `"SUCCESS"`면 된다. 권한 설정은 4-5단계에서 한다.

### 1-6. 이 폴더 가져오기
받은 `hermes-team-share.tar`를 풀면 **`~/Projects/hermes-team`**이 생긴다.
```bash
mkdir -p ~/Projects
tar xf hermes-team-share.tar -C ~/Projects       # 받은 파일이 있는 폴더에서
ls ~/Projects/hermes-team        # README_FIRST.md, INSTALL.md, set_name.sh, souls/, template/, tools/ 가 보여야 함
```
이 묶음은 배포용이라 비어 있다. 원래 연구실의 Discord ID, 프로젝트 목록, git 기록은 들어 있지 않다.

**연구자 이름 정하기:** SOUL에는 연구자 이름이 `<유저>`로 들어 있다. 직원들은 이 이름으로 나를 부르고 승인을 요청한다.
```bash
cd ~/Projects/hermes-team
bash set_name.sh <내이름>        # 예: minji 또는 김민지 (공백 없이). 나중에 다시 실행해도 된다
```

---

## 2. Discord 서버 준비

### 2-1. 개발자 모드 켜기 (ID 복사용)
Discord → 사용자 설정(톱니바퀴) → **고급** → **개발자 모드** 켜기.
이제 서버, 채널, 사용자를 우클릭하면 **ID 복사**가 나온다.

### 2-2. 서버 구성 만들기
| 만들 것 | 이름 (권장) | 용도 |
|---|---|---|
| 텍스트 채널 | `#hermes` | **로비.** 전체 상황, 새 프로젝트 요청. PI가 멘션 없이 답한다 |
| 카테고리 | `Projects` | PI가 프로젝트 채널을 **자동으로** 이 안에 만든다 |
| 텍스트 채널 (선택) | `#sandbox` | 시험용 |

서버 이름 우클릭 → ID 복사 (서버 ID), `#hermes` 우클릭 → ID 복사 (로비 ID), `Projects` 우클릭 → ID 복사 (카테고리 ID), 내 프로필 우클릭 → ID 복사 (내 사용자 ID). 모두 0-5 기록표에 적는다.

---

## 3. 직원 6명 만들기

| 직원 | Discord 봇 이름 | Hermes profile |
|---|---|---|
| PI | `hermes-researcher` | `default` (기본 profile) |
| coder | `coder` | `coder` |
| analyst | `analyst` | `analyst` |
| reviewer | `reviewer` | `reviewer` |
| writer | `writer` | `writer` |
| scholar | `scholar` | `scholar` |

### 3-1. Discord 봇 6개 만들기 (봇마다 반복)
1. https://discord.com/developers/applications → **New Application** → 이름 입력(위 표) → Create
2. **General Information** → **Application ID** 복사 → 기록표
3. 왼쪽 **Bot**
   - **Reset Token** → 토큰 복사 → 기록표 (다시 볼 수 없다)
   - **Message Content Intent** 켜기 (**필수.** 꺼져 있으면 봇이 접속하지 못한다) → **Save Changes**
4. 서버에 초대: 브라우저 주소창에 아래를 입력한다 (`APP_ID` 자리에 2번 값)
   ```text
   https://discord.com/oauth2/authorize?scope=bot+applications.commands&permissions=274878024768&client_id=APP_ID
   ```
   - 승인 화면 위쪽의 봇 이름이 **지금 만드는 봇인지** 확인 → 내 서버 선택 → 승인
5. 서버 멤버 목록에서 그 봇 우클릭 → **ID 복사** (봇 ID) → 기록표

### 3-2. PI(default) 설정
```bash
hermes model                 # "ChatGPT or Codex Subscription" 선택 → 화면의 코드로 로그인 → 모델 gpt-6.1-sol
hermes gateway setup         # Discord 선택 → PI(hermes-researcher) 토큰 → "Allow yourself?" y → Home channel 은 Enter
hermes chat -q "OK라고만 답해"
```
> `hermes setup`이 **Nous Portal** 로그인을 권하면 Ctrl+C로 나오고 위처럼 `hermes model`로 고른다 (Nous Portal은 별도 유료 서비스).

### 3-3. 직원 5명 profile 만들기
PI 설정(모델 로그인)을 복제해서 만든다:
```bash
hermes profile create coder --clone \
  --description "코드 구현·수정 담당. 실제 코드 작성은 Claude Code(claude -p)에 맡기고, 결과를 테스트로 검증해 보고한다. 연구 기록과 실험 명세는 수정하지 않는다."
hermes profile create analyst --clone \
  --description "실험 실행과 결과 분석 담당. 승인된 실험 명세만 실행하고, success_criteria 판정과 FINDINGS 수정안을 만든다. 코드는 수정하지 않는다."
hermes profile create reviewer --clone \
  --description "독립 검토 담당. 코드·분석 결과·논문 초안·문헌 조사를 검토하고, GPT가 만든 판정은 Claude 읽기 전용 2차 의견을 받는다. 직접 수정하지 않는다."
hermes profile create writer --clone \
  --description "논문·보고서 초안 담당. 작성은 Claude Code에 docs/paper/ 쓰기만 허용해 맡기고, 수치는 results와, 인용은 references.bib와 대조해 검증한다."
hermes profile create scholar --clone \
  --description "문헌 조사 담당. 관련 논문을 찾아 Antigravity로 읽고 근거 위치와 함께 정리하며, arXiv/DOI로 실제 존재를 검증해 docs/literature/와 references.bib에 남긴다."
hermes profile list
```

### 3-4. 직원마다 자기 봇 토큰 연결 (5번 반복)
`--clone`은 **PI의 토큰까지 복사**한다. 반드시 각자 자기 토큰으로 바꾼다.
```bash
hermes -p coder gateway setup      # Discord → coder 봇 토큰 → Allow yourself? y → Home channel Enter
hermes -p analyst gateway setup
hermes -p reviewer gateway setup
hermes -p writer gateway setup
hermes -p scholar gateway setup
```
각 직원의 모델이 PI와 같은지 확인한다. 로그인을 요구하면 같은 ChatGPT 계정으로 로그인한다:
```bash
for p in coder analyst reviewer writer scholar; do hermes -p $p chat -q "OK라고만 답해"; done
```

---

## 4. 팀으로 묶기

### 4-1. 팀 설정 파일 채우기
```bash
cd ~/Projects/hermes-team
nano team.json            # guild_id, category_id, lobby_channels 를 기록표 값으로
nano souls/_team_ids.md   # 7개 ID (나 + 봇 6개) 를 기록표 값으로. 형식: `<@숫자>`
```
`team.json` 예:
```json
{
  "guild_id": "111111111111111111",
  "category_id": "222222222222222222",
  "projects_root": "~/Projects",
  "profiles": ["default", "coder", "analyst", "reviewer", "writer", "scholar"],
  "lobby_channels": ["333333333333333333"],
  "reasoning": {"default": "medium", "coder": "low", "analyst": "medium", "reviewer": "medium", "writer": "low", "scholar": "low"}
}
```

### 4-2. 한 번에 적용
```bash
cd ~/Projects/hermes-team
python3 tools/lab.py env         # 6명 .env: 봇끼리 멘션 허용, 허용 사용자 = 나 + 봇 6개
python3 tools/lab.py reasoning   # 추론 수준: PI·analyst·reviewer medium / coder·writer·scholar low
python3 newproject.py sync       # 6명 config.yaml: 로비·프로젝트 채널 연결 (PI만 멘션 없이 응답)
bash install_souls.sh            # 6명 SOUL(역할·규칙) 설치 + 게이트웨이 재시작
```
- `lab.py env`가 설정하는 값: `DISCORD_ALLOW_BOTS=mentions`, `DISCORD_IGNORE_NO_MENTION=true`, `DISCORD_THREAD_REQUIRE_MENTION=true`, `DISCORD_ALLOWED_USERS=<7개 ID>`. 원본은 `.env.bak`으로 남긴다.
- `install_souls.sh`가 "주의: 채우지 않은 ID"를 출력하면 4-1로 돌아간다.

### 4-3. 직원 봇의 slash 명령 등록 (처음 한 번)
복제한 profile은 PI의 "명령 등록 완료" 기록까지 복사돼서 `/reset` 같은 명령이 등록되지 않는다. 한 번만 강제로 등록한다:
```bash
for p in coder analyst reviewer writer scholar; do echo 'DISCORD_COMMAND_SYNC_POLICY=bulk' >> ~/.hermes/profiles/$p/.env; done
hermes gateway restart --all
sleep 30
grep -h -i 'Synced.*slash' ~/.hermes/profiles/*/logs/gateway.log | tail -n 5
for p in coder analyst reviewer writer scholar; do sed -i '/^DISCORD_COMMAND_SYNC_POLICY=bulk$/d' ~/.hermes/profiles/$p/.env; done
hermes gateway restart --all
```
Discord에서 `Ctrl+R`로 새로고침하고 `/`를 입력했을 때 봇마다 명령 목록이 보이면 된다.

### 4-4. PI에게 채널 만들 권한 주기
Discord에서 `Projects` 카테고리 우클릭 → **카테고리 편집 → 권한** → 멤버 추가 `hermes-researcher` → **채널 관리** 허용 → 저장.
(서버 전체 권한이 아니라 이 카테고리 안에서만 허용하는 것이 안전하다.)

### 4-5. Antigravity 읽기 권한
`agy -p` 같은 헤드리스 실행은 허용되지 않은 사이트 읽기를 **오류 없이 조용히 거부**한다. 학술 사이트 읽기만 허용하고 페이지 조작은 막는다:
```bash
python3 ~/Projects/hermes-team/tools/lab.py agy-perms
```
`extras/antigravity-permissions.json`의 규칙(학술 도메인 20개 `read_url`, `execute_url(*)` 거부)을 `~/.gemini/antigravity-cli/settings.json`에 합친다. 기존 규칙은 유지되고, 원본은 `settings.json.bak`으로 남는다.

### 4-6. PI 홈 채널 + 아침 브리핑
1. Discord `#hermes`에서 `@hermes-researcher /sethome` (자동완성에서 **APP** 표시가 있는 항목을 고른다)
2. 매일 09:00 브리핑을 등록한다:
   ```bash
   hermes cron create "0 9 * * *" "$(cat ~/Projects/hermes-team/extras/morning-brief.prompt.txt)" \
     --name morning-brief --workdir ~/Projects --deliver discord
   hermes cron status          # Next run 이 내일 09:00 (+09:00) 인지 확인. 9시간 어긋나면 "0 0 * * *" 로 다시 만든다
   hermes cron run morning-brief   # 지금 한 번 시험 → 1~3분 뒤 #hermes 에 브리핑
   ```

### 4-7. 재부팅 후에도 계속 돌게 하기
```bash
sudo loginctl enable-linger $USER
hermes gateway status
```
원래 PC에서는 게이트웨이가 **`hermes-gateway.service`** 라는 systemd 서비스로 돈다 (`hermes gateway status` 첫 줄에 보인다). 새 PC에서 `running`이 아니면 `hermes gateway --help`에서 시작이나 서비스 설치 명령을 확인해 실행한다. 게이트웨이 **하나가 6명 모두를 맡는다** (`serving profiles default, coder, ...`).

---

## 5. 점검

### 5-1. 자동 점검
```bash
python3 ~/Projects/hermes-team/tools/lab.py check
```
도구, 팀 설정, 6명의 토큰 중복 여부, `.env` 협업 설정, SOUL 최신 여부, 채널 연결, 추론 수준, 게이트웨이, 아침 브리핑, Antigravity 권한을 확인한다. 아무것도 바꾸지 않는다. 마지막 줄이 `READY`면 통과다. `WARN` 줄에는 고치는 명령이 함께 나온다.

### 5-2. Discord 시험
| # | 어디서 | 보낼 메시지 | 기대 결과 |
|---|---|---|---|
| 1 | `#hermes` | `넌 누구야?` (멘션 없이) | PI만 답한다 |
| 2 | `#hermes` | `@coder 넌 누구야?` | coder만 답한다. PI는 `—`만 보내거나 조용하다 |
| 3 | `#hermes` | analyst, reviewer, writer, scholar에게도 2번처럼 | 각자 자기 역할을 소개한다 |
| 4 | `#hermes` | `새 프로젝트 만들자: 간단한 선형회귀 데모` | PI가 이름·태그를 제안 → "좋아" → `Projects`에 새 채널, `~/Projects/<이름>`, kanban 보드가 생기고 링크를 보고한다. **보고 직후 게이트웨이가 15초 뒤 재시작된다** (새 채널 연결을 읽으려고) |
| 5 | 새 프로젝트 채널 (4번 후 **30초쯤 기다렸다가**) | `상태 알려줘` | 첫 줄에 `[태그]`, 표 형식 상태 보고. PI는 새 채널에서 먼저 말을 걸지 않으므로 내가 첫 메시지를 보낸다 |
| 6 | 새 프로젝트 채널 | `데이터 생성 스크립트 하나 만들어줘` | PI가 카드 생성 → coder가 Claude Code로 작성 → reviewer 검토 → PI가 diff 보고 + commit 승인 요청 |
| 7 | 새 프로젝트 채널 | `@coder 기억해: 코드 스타일 — 타입 힌트 필수` | 답 끝에 `기억함: ...` |

6번 진행 상황은 터미널에서 볼 수 있다: `hermes kanban --board <프로젝트> list`

**반응이 없을 때**
1. 재시작 중일 수 있다 — 30초~1분 기다렸다가 다시 보낸다. 확인: `hermes gateway status`
2. 그래도 조용하면 그 채널에서 그 봇에게 `/reset` (`/` 입력 → 봇별 명령 목록에서 그 봇의 `/reset`) 후 다시 보낸다. 이전 대화가 옛 설정·옛 SOUL을 붙잡고 있을 때 생긴다
3. 그래도 안 되면 `python3 ~/Projects/hermes-team/newproject.py list`로 채널이 등록됐는지, `python3 tools/lab.py check`로 채널 연결 블록이 있는지 확인하고 `hermes gateway restart --all`

---

## 6. 매일 쓰는 법 (요약)

| 하고 싶은 것 | 방법 |
|---|---|
| 새 연구 주제 시작 | `#hermes`에서 PI에게 주제를 말한다 → 이름·태그 확인 |
| 진행 상황 | 프로젝트 채널에서 `진행 상황 알려줘`, 또는 매일 09:00 브리핑 |
| 특정 직원에게 직접 | `@analyst ...`처럼 멘션한다 (PI는 끼어들지 않는다) |
| 승인 | PI가 묻는 것(실험 실행, `research/` 수정, commit, `uv add`)에 답한다 |
| 결과 반영 | 에이전트는 `agent/<작업>` 브랜치에 commit만 한다. **main 병합은 사람이 한다:** `git switch main && git merge --no-ff agent/<작업>` |
| 막힌 카드 | `hermes kanban --board <프로젝트> list` → 원인 해결 → `hermes kanban --board <프로젝트> unblock <카드ID>` |
| 규칙(SOUL) 수정 | `souls/<역할>.md`를 고친다 → `bash install_souls.sh` → 그 채널에서 그 봇에게 `/reset` |
| 설정 전체 점검 | `python3 tools/lab.py check` |

---

## 부록 A. 지금 연구실을 다른 PC로 옮기기

같은 봇과 같은 프로젝트를 그대로 쓰는 경우다.

1. **새 PC**에서 1-1 ~ 1-5를 한다 (도구 설치, Claude·Antigravity 로그인).
2. **원래 PC**에서 백업한다:
   ```bash
   hermes backup                         # ~/hermes-backup-<시각>.zip (설정, 토큰, 기억, 스킬, 세션, profile 전부)
   tar czf ~/projects.tgz -C ~ Projects  # hermes-team + 모든 연구 프로젝트
   ```
   백업이 끝날 때 나오는 **빠진 파일 보고**를 확인한다.
3. **원래 PC의 게이트웨이를 멈춘다.** 같은 토큰으로 두 곳이 동시에 접속하면 안 된다.
4. **새 PC**에서 복원한다:
   ```bash
   hermes import ~/hermes-backup-<시각>.zip
   tar xzf ~/projects.tgz -C ~
   ```
5. **사용자 이름(홈 경로)이 바뀌었다면** `projects.json`의 `"path"`를 새 경로로 고친 뒤 채널 연결을 다시 만든다:
   ```bash
   cd ~/Projects/hermes-team
   sed -i "s#/home/<예전사용자>/#$HOME/#g" projects.json
   python3 newproject.py sync
   ```
6. `python3 tools/lab.py agy-perms`, 4-6(아침 브리핑)을 다시 한다. 브리핑이 백업에 포함돼 있으면 건너뛴다 (`hermes cron list`로 확인).
7. `bash install_souls.sh` → `python3 tools/lab.py check` → 5-2 시험.

> `hermes backup` zip에는 **봇 토큰과 로그인 정보가 들어 있다.** 옮긴 뒤에는 지운다.

## 부록 B. 다른 사람에게 넘기기 (넘겨주는 쪽)

원래 연구실 PC에는 **배포용 묶음이 따로** 있다. 지금 쓰는 `hermes-team`과는 별개다.

| 위치 | 내용 |
|---|---|
| `~/Projects/hermes-team-share/` | 배포용 폴더. 이름은 `<유저>`, 개인 ID·프로젝트 목록·git 기록 없음 |
| `~/Projects/hermes-team-share.tar` | **이 파일을 그대로 주면 된다.** 풀면 `hermes-team/`이 생긴다 |

받는 사람은 `README_FIRST.md` 순서대로 한다: tar 풀기 → `bash set_name.sh <이름>` → 이 문서.

SOUL, 템플릿, 스크립트를 고쳐서 배포본도 최신으로 하고 싶을 때만 다시 만든다 (원본은 건드리지 않는다):
```bash
bash ~/Projects/hermes-team/tools/make_handover.sh
```
남은 개인 흔적(Discord ID 형태의 긴 숫자, 홈 경로)이 있으면 화면에 보여 준다.

`docs/Hermes_Lab_Overview.pptx`는 원래 연구실을 설명하는 자료라 원래 연구자 이름과 사례(demo-bell-noise)가 그대로 들어 있다.

분야가 다르면 `souls/scholar.md`의 우선 출처(arXiv, PRL, PennyLane 등)와 `extras/antigravity-permissions.json`의 도메인도 바꾼다.

## 부록 C. 예비 모델 (선택)

ChatGPT 한도가 차면 **예비 모델 없이도** 카드가 실패로 세지 않고 대기열에서 기다리다가, 한도가 풀리면 자동으로 다시 시작한다.
**고장 난 예비 모델은 오히려 해롭다.** 예비 모델이 실패하면 진짜 실패로 세어지고, 2번 실패하면 카드가 `blocked`가 된다. 예비 모델을 붙이려면 이 순서를 지킨다:
1. 단독 시험: `hermes chat --provider <provider> -m <모델> -q "OK라고만 답해"`
2. 통과했을 때만 6명에게 추가: `for p in default coder analyst reviewer writer scholar; do hermes -p $p fallback add <provider> <모델>; done`
3. 문제가 생기면 즉시 비운다: `for p in default coder analyst reviewer writer scholar; do hermes -p $p fallback clear; done`

GitHub Copilot 메모: `403 not licensed` → 구독(학생 혜택 포함)이 활성화되지 않음. `400 model not available for integrator` → 그 모델을 이 연결로는 못 씀. https://github.com/settings/copilot/features 에서 모델을 켠 뒤 1번부터 다시.

## 부록 D. 문제 해결

| 증상 | 원인 / 해결 |
|---|---|
| 자동완성에 봇이 안 보임 | 서버에 초대되지 않음 → 3-1의 4번을 **그 봇의** Application ID로 다시 |
| 멘션했는데 반응이 없음 | 역할(role)을 고름 → 자동완성에서 **APP** 표시 항목을 고르거나 `<@봇ID>`를 직접 입력 |
| 봇이 오프라인 / 한 봇을 켜면 다른 봇이 꺼짐 | 토큰 중복 (`--clone`이 PI 토큰을 복사) → `lab.py check`로 확인 → 3-4 다시 |
| PI가 멘션해도 직원이 무시함 | `.env` 협업 설정 → `python3 tools/lab.py env` 후 재시작 |
| 다른 직원만 멘션했는데 PI도 답함 | 정상 동작은 `—` 한 글자다. 길게 답하면 PI SOUL이 옛것 → `install_souls.sh` + `/reset` |
| 규칙을 바꿨는데 예전처럼 행동함 | 이미 열린 대화는 예전 SOUL을 가지고 있다 → 그 채널에서 그 봇에게 `/reset` (칸반 작업과 브리핑은 자동으로 새 SOUL을 씀) |
| `config.yaml`을 고쳤는데 그대로 | `# discord:`로 시작하는 주석 예시를 고친 것. discord 설정은 `newproject.py sync`가 관리한다 |
| 새 프로젝트 만들 때 HTTP 403 | 4-4 카테고리 권한, `team.json`의 `category_id` 확인 |
| 카드 결과 파일이 사라짐 | workspace가 `scratch`였음 → 항상 `dir:<프로젝트 경로>` (PI SOUL에 규칙 있음) |
| `429` / rate limit | ChatGPT 한도. 카드는 대기했다가 자동 재개된다. 기다리면 된다 |
| 카드가 `blocked` | 같은 원인으로 2번 실패함. 원인을 고친 뒤 `hermes kanban --board <p> unblock <id>` |
| 브리핑 로그에 `BLOCKED: script execution via -e/-c` | 무인 실행에서는 `python -c` 같은 명령이 막힌다. 에이전트가 다른 방법으로 다시 시도하므로 무시해도 된다 |
| `git switch main` 실패 | 저장소 기본 브랜치가 `master`다 → `git branch`로 확인. 1-1의 `init.defaultBranch main`을 해 두면 새 저장소는 main이 된다 |
| `uv` 없음 / `.venv` 깨짐 | 프로젝트에서 `bash scripts/researchctl doctor --fix` |
| 그 밖의 문제 | `hermes doctor`, 로그: PI는 `~/.hermes/logs/`, 직원은 `~/.hermes/profiles/<이름>/logs/` |

## 부록 E. 파일 지도

```text
~/Projects/hermes-team/            ← 연구실 "설계도" (이 폴더만 옮기면 같은 연구실을 만들 수 있다)
├── INSTALL.md                     이 문서
├── SETUP.md                       처음 구축할 때의 단계별 기록 (참고용)
├── docs/Hermes_Lab_Overview.pptx  구조·직원별 동작 설명 슬라이드
├── team.json                      Discord 서버·카테고리·로비 ID, 직원 목록, 추론 수준
├── projects.json                  등록된 프로젝트 ↔ 채널 (newproject.py 가 관리)
├── newproject.py                  새 프로젝트: 폴더+git+uv, 채널, 채널 연결, kanban 보드
├── install_souls.sh               souls/*.md + _team_ids.md → 6명의 SOUL.md, 재시작
├── souls/                         직원별 역할·규칙 원본 (pi, coder, analyst, reviewer, writer, scholar, _team_ids)
├── template/                      새 프로젝트 뼈대 (AGENTS.md, research/, experiments/, scripts/researchctl …)
├── tools/lab.py                   설치 도우미: env / reasoning / agy-perms / rename / check
├── set_name.sh                    연구자 이름 바꾸기 (받은 사람이 처음 한 번)
├── tools/make_handover.sh         배포용 hermes-team-share/ + .tar 만들기·갱신
└── extras/                        Antigravity 권한, 아침 브리핑 프롬프트, 빈 설정 예시

~/.hermes/                         ← Hermes 데이터 (PC마다 따로, 비밀 포함 — git에 올리지 않는다)
├── config.yaml  .env  SOUL.md     PI(default)
├── memories/                      PI 장기 기억
└── profiles/<직원>/               직원별 config.yaml, .env(봇 토큰), SOUL.md, memories/, logs/

~/Projects/<프로젝트>/             ← 연구 프로젝트 하나 (git 저장소)
├── AGENTS.md                      이 프로젝트에서 에이전트가 따를 규칙
├── research/                      RESEARCH_STATE, HYPOTHESES, FINDINGS … (승인 후에만 수정)
├── experiments/  results/  src/  docs/
└── scripts/researchctl            doctor / validate / list / setup
```
