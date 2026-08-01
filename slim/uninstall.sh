#!/usr/bin/env bash
# uninstall.sh — 薄殼:所有卸載邏輯已搬進 uninstall.py(stdlib only,Unix/
# Windows 共用同一份原始碼)。本檔案只做兩件事:①解析 $0 的 symlink 鏈以定位
# 套件目錄(PKG,與 install.sh 同款理由)②挑一支可用的 python 直譯器,把參數
# 原樣轉發給 "${PKG}/uninstall.py"。
#
# 用法(裝好之後,兩種都可):
#   ~/.lumos-slim/uninstall.sh
#   curl -fsSL https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/uninstall.sh | bash
set -eu

SOURCE="$0"
while [ -L "$SOURCE" ]; do
  DIR="$(cd "$(dirname "$SOURCE")" && pwd)"
  LINK="$(readlink "$SOURCE")"
  case "$LINK" in
    /*) SOURCE="$LINK" ;;
    *)  SOURCE="${DIR}/${LINK}" ;;
  esac
done
PKG="$(cd "$(dirname "$SOURCE")" && pwd)"

PY=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then
    PY="$cand"
    break
  fi
done
if [ -z "$PY" ]; then
  echo "ERROR: 找不到 python3 或 python 指令——請先安裝 Python 3 再重跑本腳本。" >&2
  exit 2
fi

exec "$PY" "${PKG}/uninstall.py" "$@"
