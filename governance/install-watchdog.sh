#!/bin/bash
# 把看門狗那支排程真的裝到這台機器上(macOS launchd),或用 --status 看它裝了沒。
#
# ★為什麼需要這支★(2026-09-07 代碼審 r1 外家否決席判 blocker,查證屬實):
# 第一版只把 plist 加進 repo 就當交付了,但 repo 裡的 plist 不會自己變成一個排程
# ——實機 `launchctl print gui/501/com.enzo.lumos.wrapper-watchdog` 回「找不到」。
# 也就是說那批合進去之後,號稱的看門狗一次都不會跑。
# (對照組:每日治理那支的 plist 根本不在 repo 裡,只躺在系統目錄,誰裝的沒有紀錄
#  ——所以這裡沒有既有慣例可以照抄,是新開的。)
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LABEL="com.enzo.lumos.wrapper-watchdog"
SRC="$DIR/$LABEL.plist"
DEST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"

status() {
  echo "plist 來源     : $SRC"
  echo "裝到哪         : $DEST"
  if [ -f "$DEST" ]; then
    if diff -q "$SRC" "$DEST" >/dev/null 2>&1; then
      echo "裝好的那份     : 跟 repo 一致"
    else
      echo "裝好的那份     : ★跟 repo 不一樣★——重跑這支會用 repo 的蓋過去"
    fi
  else
    echo "裝好的那份     : 沒有"
  fi
  if launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1; then
    echo "launchd 認得它 : 是"
  else
    echo "launchd 認得它 : ★否——它一次都不會跑★"
  fi
}

case "${1:-install}" in
  --status|status) status; exit 0 ;;
  --uninstall)
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    rm -f "$DEST"
    echo "已移除。"; status; exit 0 ;;
esac

[ -f "$SRC" ] || { echo "找不到 plist:$SRC" >&2; exit 1; }
# plist 裡寫死了腳本的絕對路徑,先確認那個路徑跟這份 repo 對得上,不然裝了也是跑空氣。
want="$DIR/wrapper-watchdog.sh"
grep -q -- "$want" "$SRC" || {
  echo "★plist 裡的腳本路徑跟這份 repo 對不上★" >&2
  echo "  這份 repo 的腳本在:$want" >&2
  echo "  plist 裡寫的是    :$(grep -A1 'ProgramArguments' -A3 "$SRC" | grep string | tail -1)" >&2
  exit 1
}
plutil -lint "$SRC" >/dev/null || { echo "plist 格式不合法:$SRC" >&2; exit 1; }

mkdir -p "$(dirname "$DEST")"
cp "$SRC" "$DEST"
launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true    # 先卸再裝,才吃得到改過的內容
launchctl bootstrap "$DOMAIN" "$DEST" || { echo "launchctl bootstrap 失敗" >&2; exit 1; }
echo "裝好了。"
status
