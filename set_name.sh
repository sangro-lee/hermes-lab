#!/usr/bin/env bash
# 이 연구실 묶음 안의 연구자 이름(<유저>)을 내 이름으로 바꾼다.
# 사용: bash set_name.sh <내이름>      예) bash set_name.sh minji   /   bash set_name.sh 김민지
# 직원들이 Discord에서 이 이름으로 나를 부르고 승인을 요청한다. 공백 없이 쓴다. 나중에 다시 실행해도 된다.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if [[ $# -ne 1 ]]; then
  echo "사용: bash set_name.sh <내이름>   (지금: $(grep -oP '연구자\s+\K[^\s:`]+' souls/_team_ids.md | head -1))"
  exit 1
fi
python3 tools/lab.py rename "$1"
if [[ -f "$HOME/.hermes/SOUL.md" ]]; then
  echo "이미 설치한 상태라면: bash install_souls.sh"
else
  echo "다음: INSTALL.md 를 처음부터 따라 한다."
fi
