#!/usr/bin/env python3
"""새 연구 프로젝트를 한 번에 만든다 (PI가 실행하는 용도). 표준 라이브러리만 사용.

  create NAME --tag TAG --desc "설명"   폴더(템플릿)+git, Discord 채널, 등록, 채널 연결, kanban 보드
  adopt  NAME --tag TAG --desc "설명"   이미 있는 폴더를 등록 (폴더는 건드리지 않음)
  sync                                  projects.json 기준으로 5개 profile의 discord 설정 재생성
  list                                  등록된 프로젝트 목록
  lobby add|remove|show [채널ID]         PI가 멘션 없이 답하는 로비 채널(예: #hermes) 관리

공통 옵션:
  --channel-id ID   채널을 직접 만든 경우 그 ID 사용 (Discord API 호출 안 함)
  --no-channel      채널 만들기 건너뜀
  --restart         끝난 뒤 15초 후 게이트웨이 재시작 예약 (PI가 답장을 마칠 시간)
  --dry-run         무엇을 할지만 출력

보안: PI 봇 토큰은 ~/.hermes/.env 에서 읽어 Discord API 호출에만 쓰고 출력하지 않는다.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

TEAM_DIR = Path(__file__).resolve().parent
TEMPLATE = TEAM_DIR / "template"
REGISTRY = TEAM_DIR / "projects.json"
TEAM_CFG = TEAM_DIR / "team.json"
HERMES = Path.home() / ".hermes"
BEGIN = "# >>> hermes-team managed discord block (newproject.py sync) >>>"
END = "# <<< hermes-team managed discord block <<<"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")
TAG_RE = re.compile(r"^[A-Z][A-Z0-9]{1,7}$")


# ---------------------------------------------------------------- helpers
def load_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def team():
    cfg = load_json(TEAM_CFG, None)
    if cfg is None:
        sys.exit(f"ERROR: {TEAM_CFG} 가 없습니다.")
    cfg["projects_root"] = str(Path(os.path.expanduser(cfg.get("projects_root", "~/Projects"))))
    return cfg


def profile_home(p):
    return HERMES if p == "default" else HERMES / "profiles" / p


def read_env_value(env_path, key):
    if not env_path.exists():
        return None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def step(msg):
    print(f"• {msg}")


# ---------------------------------------------------------------- discord
def create_channel(cfg, name, desc, dry):
    guild = cfg.get("guild_id")
    if not guild:
        sys.exit("ERROR: team.json 에 guild_id 가 없습니다.")
    token = read_env_value(HERMES / ".env", "DISCORD_BOT_TOKEN")
    if not token:
        sys.exit("ERROR: ~/.hermes/.env 에서 PI 봇 토큰을 찾지 못했습니다.")
    body = {"name": name, "type": 0, "topic": desc[:1000]}
    if cfg.get("category_id"):
        body["parent_id"] = str(cfg["category_id"])
    if dry:
        step(f"[dry-run] Discord 채널 생성: #{name} (guild {guild}, category {cfg.get('category_id')})")
        return "DRYRUN_CHANNEL_ID"
    req = urllib.request.Request(
        f"https://discord.com/api/v10/guilds/{guild}/channels",
        data=json.dumps(body).encode(),
        method="POST",
        headers={
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot (hermes-team newproject, 1.0)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        hint = ""
        if e.code == 403:
            hint = ("\n  → PI 봇에 '채널 관리' 권한이 없습니다. 서버 설정 > 역할 > hermes-researcher(또는 "
                    "Projects 카테고리 권한)에서 '채널 관리'를 허용하세요. 또는 채널을 직접 만들고 --channel-id 로 지정하세요.")
        sys.exit(f"ERROR: Discord 채널 생성 실패 (HTTP {e.code}): {detail}{hint}")
    step(f"Discord 채널 생성: #{data['name']} (ID {data['id']})")
    return data["id"]


# ---------------------------------------------------------------- folder
def scaffold(root, name, tag, desc, dry):
    if root.exists():
        sys.exit(f"ERROR: {root} 가 이미 있습니다. 기존 폴더를 등록하려면 adopt 를 쓰세요.")
    if dry:
        step(f"[dry-run] 템플릿 복사 → {root}, AGENTS.md/project.yaml/RESEARCH_STATE 작성, git init")
        return
    shutil.copytree(TEMPLATE, root, ignore=shutil.ignore_patterns("*.tmpl"))
    for p in (root / "scripts").glob("*"):
        p.chmod(0o755)
    home_rel = "~/" + str(root.relative_to(Path.home())) if str(root).startswith(str(Path.home())) else str(root)
    agents = (TEMPLATE / "AGENTS.md.tmpl").read_text(encoding="utf-8")
    for k, v in {"{{NAME}}": name, "{{TAG}}": tag, "{{ROOT}}": home_rel, "{{SUMMARY}}": desc}.items():
        agents = agents.replace(k, v)
    (root / "AGENTS.md").write_text(agents, encoding="utf-8")
    pyproject = (TEMPLATE / "pyproject.toml.tmpl").read_text(encoding="utf-8")
    pyproject = pyproject.replace("{{NAME}}", name).replace("{{SUMMARY}}", desc.replace('"', "'"))
    (root / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    (root / "config" / "project.yaml").write_text(f"""project:
  name: {json.dumps(name)}
  tag: {json.dumps(tag)}
  description: {json.dumps(desc, ensure_ascii=False)}
  owner: "<유저>"
  repository_root: {json.dumps(home_rel)}

research:
  primary_question: "REPLACE_WITH_CURRENT_RESEARCH_QUESTION"
  baseline: "REPLACE_WITH_BASELINE"
  candidate_method: "REPLACE_WITH_METHOD"
  primary_metrics:
    - "REPLACE_WITH_PRIMARY_METRIC"
  data_version: "REPLACE_WITH_DATA_VERSION"

runtime:
  scheduler: "local"          # HPC 사용 시 "slurm" 으로 바꾸고 아래 값 조정
  default_time_limit: "00:30:00"
  default_gpu_count: 0
  default_cpu_count: 4
  default_memory: "16G"

paths:
  experiment_specs: "experiments/"
  research_state: "research/RESEARCH_STATE.md"
  results: "results/"
  logs: "logs/"

notes:
  - "API 키, 비밀번호, SSH 개인키를 이 파일에 넣지 말 것."
""", encoding="utf-8")
    rs = root / "research" / "RESEARCH_STATE.md"
    rs.write_text(rs.read_text(encoding="utf-8").replace(
        "# Research State", f"# Research State — {name} [{tag}]", 1).replace(
        "- [연구의 최종 목표를 한두 문장으로 작성]", f"- {desc}", 1), encoding="utf-8")
    step(f"프로젝트 폴더 생성: {root}")
    uv = shutil.which("uv") or (str(Path.home() / ".local/bin/uv") if (Path.home() / ".local/bin/uv").exists() else None)
    if uv:
        r = subprocess.run([uv, "sync", "--quiet"], cwd=root, capture_output=True, text=True)
        step("uv sync: .venv + uv.lock 생성" if r.returncode == 0
             else f"경고: uv sync 실패 — 나중에 scripts/researchctl setup ({(r.stderr or '').strip()[-200:]})")
    else:
        step("경고: uv 가 없어 환경을 만들지 않음 — 설치 후 scripts/researchctl setup")
    try:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", f"init {name} from hermes-team template"], cwd=root, check=True)
        step("git init + 첫 commit")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        step(f"경고: git 초기화 실패 ({e}). git config user.name/email 을 확인하세요.")


# ---------------------------------------------------------------- configs
LOBBY_PROMPT = ("이 채널은 연구실 로비다. 특정 프로젝트 채널이 아니다. 전체 현황, 새 프로젝트 요청, 일반 질문을 여기서 받는다. "
                "프로젝트 작업은 해당 프로젝트 채널에서 진행하도록 안내한다 (목록: python3 ~/Projects/hermes-team/newproject.py list). "
                "답변에 프로젝트 태그를 붙이지 않는다.")


def discord_block(projects, free_response=False, lobbies=()):
    """free_response=True 인 profile(기본: PI)은 등록된 프로젝트 채널과 로비 채널에서 멘션 없이 응답한다."""
    ids = [str(p["channel_id"]) for p in projects if p.get("channel_id")] + [str(c) for c in lobbies]
    free = ",".join(ids) if free_response else ""
    lines = [BEGIN,
             "discord:",
             "  require_mention: true",
             f"  free_response_channels: {json.dumps(free)}",
             "  free_response_auto_thread: false",
             "  auto_thread: false",
             "  thread_require_mention: true",
             "  channel_prompts:"]
    for p in projects:
        if not p.get("channel_id"):
            continue
        prompt = (f"이 채널은 {p['name']} 프로젝트다. 루트: {p['path']}. "
                  f"작업 전 그 폴더의 AGENTS.md와 research/RESEARCH_STATE.md를 읽고 따른다. "
                  f"답변 첫 줄 태그 [{p['tag']}]. kanban 보드: {p['name']} "
                  f"(카드 workspace는 dir:{p['path']}).")
        lines.append(f"    {json.dumps(str(p['channel_id']))}: {json.dumps(prompt, ensure_ascii=False)}")
    for c in lobbies:
        lines.append(f"    {json.dumps(str(c))}: {json.dumps(LOBBY_PROMPT, ensure_ascii=False)}")
    if lines[-1] == "  channel_prompts:":
        lines[-1] = "  channel_prompts: {}"
    lines.append(END)
    return "\n".join(lines) + "\n"


def strip_discord(text):
    """관리 블록과, 사람이 추가했던 최상위 `discord:` 블록을 제거한다 (주석 예시는 유지)."""
    text = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", "", text, flags=re.S)
    out, skipping = [], False
    for line in text.splitlines(keepends=True):
        if re.match(r"^discord:\s*(#.*)?$", line):
            skipping = True
            continue
        if skipping:
            if line.strip() == "" or line.startswith((" ", "\t")):
                continue
            skipping = False
        out.append(line)
    return "".join(out).rstrip("\n") + "\n"


def sync_configs(cfg, projects, dry):
    free_profiles = set(cfg.get("free_response_profiles", ["default"]))
    for prof in cfg["profiles"]:
        block = discord_block(projects, free_response=prof in free_profiles,
                              lobbies=cfg.get("lobby_channels", []))
        path = profile_home(prof) / "config.yaml"
        if not path.exists():
            step(f"건너뜀: {prof} (config.yaml 없음)")
            continue
        old = path.read_text(encoding="utf-8")
        new = strip_discord(old) + "\n" + block
        if dry:
            step(f"[dry-run] {path} discord 블록 갱신 ({len(projects)}개 프로젝트)")
            continue
        if new != old:
            shutil.copy2(path, path.with_name("config.yaml.bak"))
            path.write_text(new, encoding="utf-8")
            step(f"채널 연결 갱신: {prof}")
        else:
            step(f"변경 없음: {prof}")


# ---------------------------------------------------------------- kanban / restart
def hermes_bin():
    return shutil.which("hermes") or str(Path.home() / ".local/bin/hermes")


def create_board(name, dry):
    if dry:
        step(f"[dry-run] kanban 보드 생성: {name}")
        return
    r = subprocess.run([hermes_bin(), "kanban", "boards", "create", name, "--name", name],
                       capture_output=True, text=True)
    if r.returncode == 0:
        step(f"kanban 보드 생성: {name}")
    else:
        msg = (r.stderr or r.stdout).strip().splitlines()
        step(f"kanban 보드: {msg[-1] if msg else 'exit ' + str(r.returncode)} (이미 있으면 무시해도 됨)")


def schedule_restart(dry):
    cmd = ["systemd-run", "--user", "--on-active=15", "--unit", "hermes-team-restart",
           "--collect", hermes_bin(), "gateway", "restart", "--all"]
    if dry:
        step("[dry-run] 15초 후 게이트웨이 재시작 예약")
        return
    if shutil.which("systemd-run"):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            step("15초 후 게이트웨이 재시작 예약됨")
            return
    step("재시작 예약 실패: 터미널에서 `hermes gateway restart --all` 을 실행하세요.")


# ---------------------------------------------------------------- commands
def register(args, adopt):
    cfg = team()
    if not NAME_RE.match(args.name):
        sys.exit("ERROR: 이름은 영문 소문자/숫자/하이픈 2~41자 (예: vqc-diffusion)")
    if not TAG_RE.match(args.tag):
        sys.exit("ERROR: 태그는 대문자로 시작하는 대문자/숫자 2~8자 (예: VQC)")
    projects = load_json(REGISTRY, [])
    if any(p["name"] == args.name for p in projects):
        sys.exit(f"ERROR: {args.name} 는 이미 등록돼 있습니다 (list 로 확인).")
    if any(p["tag"] == args.tag for p in projects):
        sys.exit(f"ERROR: 태그 {args.tag} 는 이미 사용 중입니다.")

    root = Path(cfg["projects_root"]) / args.name
    if adopt:
        if not root.is_dir():
            sys.exit(f"ERROR: {root} 가 없습니다.")
        step(f"기존 폴더 등록: {root}")
    else:
        scaffold(root, args.name, args.tag, args.desc, args.dry_run)

    if args.channel_id:
        channel_id = args.channel_id
        step(f"기존 채널 사용: {channel_id}")
    elif args.no_channel:
        channel_id = None
        step("채널 생성 건너뜀")
    else:
        channel_id = create_channel(cfg, args.name, args.desc, args.dry_run)

    entry = {"name": args.name, "tag": args.tag, "description": args.desc,
             "path": str(root), "channel_id": channel_id}
    if not args.dry_run:
        projects.append(entry)
        save_json(REGISTRY, projects)
        step("projects.json 등록")
    sync_configs(cfg, projects + ([entry] if args.dry_run else []), args.dry_run)
    create_board(args.name, args.dry_run)
    if args.restart:
        schedule_restart(args.dry_run)

    print("\n완료:", json.dumps(entry, ensure_ascii=False))
    if channel_id and cfg.get("guild_id") and not args.dry_run:
        print(f"채널 링크: https://discord.com/channels/{cfg['guild_id']}/{channel_id}")
    if not args.restart:
        print("채널 연결을 확실히 적용하려면 `hermes gateway restart --all` (또는 --restart 옵션).")


def cmd_sync(args):
    cfg = team()
    sync_configs(cfg, load_json(REGISTRY, []), args.dry_run)
    if args.restart:
        schedule_restart(args.dry_run)


def cmd_lobby(args):
    cfg = load_json(TEAM_CFG, None)
    if cfg is None:
        sys.exit(f"ERROR: {TEAM_CFG} 가 없습니다.")
    lobbies = [str(c) for c in cfg.get("lobby_channels", [])]
    cid = str(args.channel_id) if args.channel_id else None
    if args.action == "add":
        if not cid or not cid.isdigit():
            sys.exit("ERROR: 채널 ID(숫자)를 주세요: lobby add <채널ID>")
        if cid not in lobbies:
            lobbies.append(cid)
    elif args.action == "remove":
        lobbies = [c for c in lobbies if c != cid]
    else:
        print("로비 채널:", ", ".join(lobbies) or "(없음)")
        return
    cfg["lobby_channels"] = lobbies
    if not args.dry_run:
        save_json(TEAM_CFG, cfg)
    step(f"로비 채널: {', '.join(lobbies) or '(없음)'}")
    cfg["projects_root"] = str(Path(os.path.expanduser(cfg.get("projects_root", "~/Projects"))))
    sync_configs(cfg, load_json(REGISTRY, []), args.dry_run)
    if args.restart:
        schedule_restart(args.dry_run)
    else:
        print("적용: hermes gateway restart --all")


def cmd_list(_args):
    projects = load_json(REGISTRY, [])
    if not projects:
        print("(등록된 프로젝트 없음)")
    for p in projects:
        print(f"[{p['tag']:<6}] {p['name']:<24} channel={p.get('channel_id') or '-':<20} {p['path']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("create", "adopt"):
        s = sub.add_parser(name)
        s.add_argument("name")
        s.add_argument("--tag", required=True)
        s.add_argument("--desc", required=True)
        s.add_argument("--channel-id")
        s.add_argument("--no-channel", action="store_true")
        s.add_argument("--restart", action="store_true")
        s.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("sync")
    s.add_argument("--restart", action="store_true")
    s.add_argument("--dry-run", action="store_true")
    sub.add_parser("list")
    s = sub.add_parser("lobby", help="PI가 멘션 없이 답하는 로비 채널 관리 (예: #hermes)")
    s.add_argument("action", choices=["add", "remove", "show"])
    s.add_argument("channel_id", nargs="?")
    s.add_argument("--restart", action="store_true")
    s.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cmd == "create":
        register(args, adopt=False)
    elif args.cmd == "adopt":
        register(args, adopt=True)
    elif args.cmd == "sync":
        cmd_sync(args)
    elif args.cmd == "lobby":
        cmd_lobby(args)
    else:
        cmd_list(args)


if __name__ == "__main__":
    main()
