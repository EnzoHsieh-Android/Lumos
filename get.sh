#!/usr/bin/env bash
# get.sh — 遠端一鍵裝:clone Lumos 後整段委派 bootstrap(機器層+專案層自動接線)。
# 用法:  curl -fsSL https://raw.githubusercontent.com/EnzoHsieh-Android/Lumos/release/get.sh | bash
#   旗標: --pull(既有 clone 也拉最新)/--init(無 vault 的 repo 免確認建圖譜)
#         curl -fsSL <url> | bash -s -- --pull --init
#   環境變數:LUMOS_HOME(預設 ~/harness/lumos-toolchain)、LUMOS_URL(預設 GitHub)、
#            LUMOS_BRANCH(預設 release;開發線是 main)
# 站在專案 repo 內跑 → bootstrap 會問「要建成 lumos 專案嗎?」(y 才建;非互動跳過)。
#
# ★為什麼整段包在 main() 裡★(2026-09-07 #7):這支是拿 curl 串流進 bash 執行的。
# 網路在中途斷掉時,bash 會把「已經收到的那半段」照樣跑完——裝到一半、沒有任何錯誤訊息。
# 包成函式再在最後一行呼叫,就要等整份收完才會開始跑;檔案沒收完,呼叫那一行根本不存在。
# 最後一行的 `; exit` 是同一個理由的第二道:確保 bash 不會再往下讀到殘留的位元組。
set -euo pipefail

main() {
  LUMOS_HOME="${LUMOS_HOME:-$HOME/harness/lumos-toolchain}"
  LUMOS_URL="${LUMOS_URL:-https://github.com/EnzoHsieh-Android/Lumos}"
  LUMOS_BRANCH="${LUMOS_BRANCH:-release}"

  # 迴圈解析(舊碼單點比對 $1,並帶兩旗標會無聲吃掉第二個);未知旗標 warn 忽略
  ARGS=()
  for a in "$@"; do
    case "$a" in
      --pull|--init) ARGS+=("$a") ;;
      *) echo "提醒:不認得 $a 這個選項,略過(只認 --pull 和 --init)" >&2 ;;
    esac
  done

  if [[ -f "$LUMOS_HOME/scripts/lumos" ]]; then
    echo "[clone] Lumos 源已在: $LUMOS_HOME"
  else
    echo "[clone] clone Lumos($LUMOS_BRANCH 對外線)→ $LUMOS_HOME …"
    mkdir -p "$(dirname "$LUMOS_HOME")"
    # 對外線抓不到就退回預設分支:release 分支可能還沒開,冷啟動不該因此炸掉。
    # 用分支不用 tag,是因為 tag 會進 detached HEAD,之後 git pull / lumos update 全部靜默停住。
    if ! git clone --branch "$LUMOS_BRANCH" "$LUMOS_URL" "$LUMOS_HOME" 2>/dev/null; then
      echo "  提醒:抓不到 $LUMOS_BRANCH 這條對外線(分支還沒開、或名字改了),改用預設分支。" >&2
      echo "  這代表你拿到的是開發線的內容,可能還沒發布過。" >&2
      git clone "$LUMOS_URL" "$LUMOS_HOME"
    fi
  fi

  # 其餘全交 bootstrap(機器層 install+skills、專案層四分流;set -e 保錯誤傳播)
  LUMOS_HOME="$LUMOS_HOME" python3 "$LUMOS_HOME/scripts/lumos" bootstrap ${ARGS[@]+"${ARGS[@]}"}

  echo
  echo "✓ 完成。最後一步:**重啟 Claude Code session**(hooks 在 session start 載入)"
}

main "$@"; exit
