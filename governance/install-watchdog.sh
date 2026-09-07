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

# ★桌面通知的圖示要換成 Lumos 的四角星,得包一個 app★
# 事實先講清楚:`osascript ... display notification` 顯示的是**呼叫它那支程式**的圖示
# (從 launchd 跑就是 Script Editor 那個),沒有辦法在指令裡指定圖片。要自訂圖示只有兩條路:
#   ①裝 terminal-notifier —— 新增一個外部依賴,這個 repo 的家規是零依賴,不走。
#   ②自己包一個最小的 .app —— 只用 macOS 內建的 osacompile / sips / iconutil / plutil,不加依賴。
# 走②。app 是「建出來的東西」不是原始碼,所以不進版控,裝的時候現建。
# ★放 repo 樹內、用 .gitignore 蓋掉,不放家目錄★(代碼審 r1 架構對齊席判 major,查證屬實):
# 這個 repo 既有的「安裝時產生東西」慣例是放 repo 樹內的忽略路徑——
# scripts/fetch-notesmd.sh 把下載的二進位放 scripts/bin/(.gitignore 第 3 行蓋住),
# dist/、.lumos/test-cache*.json 同款。這個 repo 會碰家目錄的只有兩種:
# OS 逼你放那裡的(LaunchAgents 的 plist),以及安裝器做 symlink / 改設定檔——
# 從來沒有在家目錄底下自建二進位或 bundle。第一版放 ~/Library/Application Support/,
# 是在版控管不到、也不是 OS 強制的地方開了第二種存放法。
# 尾巴的 .v2 是刻意的:見下面 build_notifier 的第③點(通知中心會快取圖示,
# 換識別碼是唯一逼它重讀的辦法)。圖示邏輯以後再動,這個號要往上加。
NOTIFIER_ID="com.enzo.lumos.watchdog-notifier.v2"
NOTIFIER_DIR="$DIR/.notifier"
NOTIFIER="$NOTIFIER_DIR/LumosWatchdog.app"
ICON_SRC="$(cd "$DIR/.." && pwd)/assets/lumos-icon.png"

# 建好之後要能證明它是完整的,不能只看目錄在不在。
verify_notifier() {   # $1 = bundle 路徑
  [ -x "$1/Contents/MacOS/applet" ] || return 1
  [ -f "$1/Contents/Resources/applet.icns" ] || return 1
  [ "$(plutil -extract CFBundleIdentifier raw "$1/Contents/Info.plist" 2>/dev/null || echo '')" \
    = "$NOTIFIER_ID" ] || return 1
  # ★簽章也要驗★(代碼審 r1 通才席實測抓到,而且是這批最深的一條):
  # osacompile 會幫 app 簽章,而簽章的雜湊★包含 Info.plist 的內容★——所以「簽完之後才用
  # plutil 改 Info.plist」等於簽完名才改合約,章當場作廢。實測:剛編完 codesign 是 valid,
  # 跑完兩行 plutil 之後變成「invalid Info.plist (plist or signature have been modified)」,
  # 而且系統的權限守門(tccd)會在 log 裡說「認不出這支 app 的身分」。
  # 後果不只是難看:章壞掉時 applet 裡的 do shell script 會被★靜默擋掉★
  # ——我原本用它來回報「我真的跑到了」,結果那條回報永遠不會發生。重簽之後兩件事都好了。
  codesign --verify --deep --strict "$1" >/dev/null 2>&1 || return 1
  return 0
}

build_notifier() {
  for c in osacompile sips iconutil plutil; do
    command -v "$c" >/dev/null 2>&1 || { echo "缺 $c,跳過通知圖示這一步(通知照發,只是用系統預設圖示)"; return 1; }
  done
  [ -f "$ICON_SRC" ] || { echo "找不到圖檔 $ICON_SRC,跳過通知圖示這一步"; return 1; }
  local tmp; tmp="$(mktemp -d)" || return 1
  # ★中途被砍也要清掉暫存★(代碼審 r1 外家席):沒有 trap 的話 signal 中止會留下整個目錄。
  trap 'rm -rf "$tmp" 2>/dev/null || true' RETURN
  local iset="$tmp/lumos.iconset"; mkdir -p "$iset" || return 1
  local s
  for s in 16 32 128 256 512; do
    sips -z "$s" "$s" "$ICON_SRC" --out "$iset/icon_${s}x${s}.png" >/dev/null 2>&1 || return 1
    sips -z $((s*2)) $((s*2)) "$ICON_SRC" --out "$iset/icon_${s}x${s}@2x.png" >/dev/null 2>&1 || return 1
  done
  iconutil -c icns "$iset" -o "$tmp/lumos.icns" >/dev/null 2>&1 || return 1

  # ★applet 一定要 quit★:不加的話它會留在事件迴圈裡不結束,每小時一則就是每小時一個殭屍行程。
  # ★訊息用檔案傳,不用 open --args★(2026-09-07 實測):`open -a APP --args …` 傳的參數
  #   **不會**進到 applet 的 `on run argv`——探針證明 applet 有被啟動、但 argv 是空的。
  # ★放棄「留印子回報有沒有送出」那條★:本來想讓 applet 用 do shell script 摸一個檔案回報,
  #   實測未簽名 app 的 do shell script 會被系統**靜默擋掉**(不報錯、什麼都不做),
  #   寫了也是死碼。誠實的結論寫在 notify() 那邊。
  # ★handler 一定要寫成 `on run`,不能寫 `on run argv`★(實測):有 argv 的版本用
  #   `open -a APP --args …` 啟動時,applet ★整個不會執行★(連第一行都沒跑到),
  #   而 open 照樣回 0。所以訊息用檔案傳。
  cat > "$tmp/notify.applescript" <<APPLESCRIPT
on run
	set msgFile to "$NOTIFIER_DIR/message.txt"
	set markFile to "$NOTIFIER_DIR/.ran"
	set theMsg to "(讀不到訊息)"
	try
		set theMsg to (read POSIX file msgFile as «class utf8»)
	end try
	display notification theMsg with title "Lumos 治理看門狗"
	try
		do shell script "/usr/bin/touch " & quoted form of markFile
	end try
end run
APPLESCRIPT

  # ★在暫存區建完、驗過,才換上去★(代碼審 r1 外家席判 major):
  # 第一版是「先 rm 掉正式的那份,再直接在正式路徑編譯」——編譯失敗就留下半成品,
  # 而 notify() 只用 `[ -d ]` 判斷,會把半成品當成可用,靜默走進一條發不出通知的路。
  local staged="$tmp/LumosWatchdog.app"
  osacompile -o "$staged" "$tmp/notify.applescript" >/dev/null 2>&1 || return 1
  cp "$tmp/lumos.icns" "$staged/Contents/Resources/applet.icns" || return 1
  plutil -replace CFBundleIdentifier -string "$NOTIFIER_ID" "$staged/Contents/Info.plist" >/dev/null || return 1
  plutil -replace CFBundleName -string "Lumos 治理看門狗" "$staged/Contents/Info.plist" >/dev/null || return 1
  # ★換圖示要三件事一起做,少一件都還是預設的卷軸★(2026-09-07 一步一步試出來的):
  #  ① 把 osacompile 附的 Assets.car 刪掉。那是一份「編譯過的圖示目錄」,裡面裝著預設的
  #     applet 圖示,而 macOS ★優先用它★,不看我們放的那個 .icns。只放 icns 沒有用。
  #  ② 重簽(下面那行)。簽章的雜湊包含 Info.plist,改完不重簽章就作廢。
  #  ③ 換一個 bundle 識別碼並重新註冊。★通知中心會記住某個識別碼第一次註冊時的圖示★
  #     ——前兩件做對了但沿用舊識別碼,它還是給你看快取住的舊圖示。
  #     所以識別碼帶一個版本尾巴;圖示邏輯以後再改,把尾巴往上加一號。
  #     代價:換識別碼等於一個新 app,通知權限要重新給——所以裝完一定要當場發一則請人確認。
  rm -f "$staged/Contents/Resources/Assets.car"
  plutil -remove CFBundleIconName "$staged/Contents/Info.plist" >/dev/null 2>&1 || true
  plutil -replace CFBundleIconFile -string "applet" "$staged/Contents/Info.plist" >/dev/null || return 1
  codesign -f -s - "$staged" >/dev/null 2>&1 || { echo "重簽失敗" >&2; return 1; }
  verify_notifier "$staged" || { echo "建出來的 app 不完整或簽章不對,不換上去(舊的那份原封不動)" >&2; return 1; }

  mkdir -p "$NOTIFIER_DIR" || return 1
  local old="$NOTIFIER.old.$$"
  if [ -d "$NOTIFIER" ]; then mv "$NOTIFIER" "$old" 2>/dev/null || return 1; fi
  if ! mv "$staged" "$NOTIFIER" 2>/dev/null; then
    [ -d "$old" ] && mv "$old" "$NOTIFIER" 2>/dev/null || true   # 換不上去就把舊的放回來
    return 1
  fi
  rm -rf "$old" 2>/dev/null || true
  # 明確叫 LaunchServices 重讀這支(只 touch 不夠可靠)
  local lsr="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
  [ -x "$lsr" ] && "$lsr" -f "$NOTIFIER" >/dev/null 2>&1
  touch "$NOTIFIER"
  return 0
}

# 發一則通知。回 0 = ★applet 真的跑到了★(它自己摸了一個印子),
# 回 1 = 沒跑到(bundle 壞了、啟動失敗、或簽章壞到 do shell script 被擋)。
# ★但「跑到了」≠「使用者看得到」★:通知權限被關掉時 display notification 不報錯,
# shell 這一層分辨不出來。實測過三條路,沒有一條能確認「真的顯示了」:
#   ①open 的回傳碼——app 一跑就失敗它照樣回 0(故意 error 的 applet 實測 rc=0);
#   ②applet 自己回報——就是現在這條,它證明「跑到了」但不證明「看得到」;
#   ③查通知權限——沒有官方 CLI,去翻 NotificationCenter 的 sqlite 是 SIP 保護、格式沒保證,
#     為了一個提醒功能賭未公開內部格式不划算,不做。
# 所以「權限被關掉 = 靜默不喊」這個洞★這一層補不起來★,只能靠安裝時請人確認一次,
# 加上另外兩條不受通知權限影響的通道(這支的紀錄檔、健檢的 [A1] 段)。
try_notify() {   # $1 = 訊息
  mkdir -p "$NOTIFIER_DIR" 2>/dev/null || return 1
  printf '%s' "$1" > "$NOTIFIER_DIR/message.txt" 2>/dev/null || return 1
  rm -f "$NOTIFIER_DIR/.ran" 2>/dev/null || true
  open -a "$NOTIFIER" >/dev/null 2>&1 || return 1
  local i
  for i in 1 2 3 4 5 6 7 8 9 10; do
    [ -f "$NOTIFIER_DIR/.ran" ] && return 0
    python3 -c "import time;time.sleep(0.5)" 2>/dev/null || sleep 1
  done
  return 1
}

case "${1:-install}" in
  --status|status) status; exit 0 ;;
  --rebuild-notifier)
    build_notifier || { echo "通知 app 建不起來——看門狗會退回系統預設圖示的通知" >&2; exit 1; }
    echo "通知 app 重建好了:$NOTIFIER"
    try_notify "重建完成——這則通知左邊應該是 Lumos 的四角星。" \
      || { echo "★通知送不出去★:app 建好了但沒跑到,先查 $NOTIFIER" >&2; exit 1; }
    exit 0 ;;
  --uninstall)
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    rm -f "$DEST"
    rm -rf "$NOTIFIER"    # 建出來的通知 app 也一起清(代碼審 r1 外家席:第一版留著不刪)
    echo "已移除(含通知 app;系統設定裡那筆通知權限要自己清)。"; status; exit 0 ;;
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

# 通知 app 一併建起來,並且★當場發一則★——不是為了好看,是為了讓 macOS 現在就問你
# 「要不要允許這個 app 發通知」。不在安裝時問,第一次真的出事那天通知會被靜默丟掉,
# 而那正是這支看門狗存在的理由。
NOTIFY_OK=unknown
if build_notifier; then
  if try_notify "看門狗裝好了。之後它有話要說,就會長這樣。"; then
    NOTIFY_OK=sent
  else
    NOTIFY_OK=failed
  fi
else
  NOTIFY_OK=nobundle
fi

echo ""
case "$NOTIFY_OK" in
  sent)
    echo "★剛才發了一則測試通知,請確認兩件事★"
    echo "  1. 右上角有沒有真的跳出來?★沒跳出來就是通知權限沒開★——"
    echo "     到「系統設定 → 通知」把「Lumos 治理看門狗」打開。"
    echo "     ★這一步只有你能確認★:通知被權限擋掉時,系統不會給腳本任何錯誤,"
    echo "     所以它永遠沒辦法自己發現「我喊了但沒人看到」。"
    echo "  2. 圖示是不是 Lumos 的四角星?不是的話重建一次:"
    echo "       bash governance/install-watchdog.sh --rebuild-notifier" ;;
  failed)
    echo "⚠ 通知 app 建好了,但測試通知沒送出去(applet 沒跑到)。"
    echo "  看門狗仍然會用系統預設圖示的方式發通知,話講得出去,只是圖示不是自己的。"
    echo "  想查:bash governance/install-watchdog.sh --rebuild-notifier" ;;
  nobundle)
    echo "⚠ 沒有建成自訂圖示的通知 app(缺工具或缺圖檔)。"
    echo "  不影響告警:看門狗會退回系統預設圖示的通知。" ;;
esac
echo ""
echo "★不管哪一種,桌面通知都只是三條通道裡的一條★——另外兩條是"
echo "  governance/logs/wrapper-watchdog.log 和 lumos doctor 的 [A1] 段,"
echo "  那兩條不受通知權限影響。"

echo ""
echo "裝好了。"
status
