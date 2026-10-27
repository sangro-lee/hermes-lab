#!/usr/bin/env bash
# 팀 SOUL 일괄 설치: souls/<역할>.md + souls/_team_ids.md → 각 profile의 SOUL.md
# 사용: bash ~/Projects/hermes-team/install_souls.sh [--no-restart]
set -euo pipefail

SOULS="$(cd "$(dirname "${BASH_SOURCE[0]}")/souls" && pwd)"
IDS="$SOULS/_team_ids.md"

install_one() {   # $1=역할 파일 이름, $2=대상 SOUL.md 경로
  local src="$SOULS/$1.md" dst="$2"
  if [[ ! -d "$(dirname "$dst")" ]]; then
    echo "SKIP  $1 (profile 없음: $(dirname "$dst"))"; return
  fi
  [[ -f "$dst" ]] && cp -p "$dst" "$dst.bak"
  cat "$src" "$IDS" > "$dst"
  echo "OK    $1 → $dst  (첫 줄: $(head -1 "$dst"))"
}

install_one pi "$HOME/.hermes/SOUL.md"
for r in coder analyst reviewer writer scholar; do
  install_one "$r" "$HOME/.hermes/profiles/$r/SOUL.md"
done

if grep -q -E '_USER_ID|_BOT_ID|<유저>' "$IDS"; then
  echo
  echo "주의: _team_ids.md 에 아직 채우지 않은 ID가 있습니다:"
  grep -n -o -E '[A-Z_]+_(USER|BOT)_ID|<유저>' "$IDS" | sort -u
fi

echo
if [[ "${1:-}" == "--no-restart" ]]; then
  echo "재시작 생략 (--no-restart). 진행 중인 작업이 끝나면: hermes gateway restart --all"
  exit 0
fi
echo "게이트웨이 재시작..."
hermes gateway restart --all
echo "완료. Discord에서 각 봇에게 /new 를 보낸 뒤 '넌 누구야?' 로 확인하세요."
