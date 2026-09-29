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

# ── python-launcher begin(三支 git 掛鉤與四支安裝腳本內嵌同一段,t_python_launcher_blocks_agree 逐字守一致)──
# 只負責找一支任何版本的 python 把 lumos 叫起來;版本判斷全交給 lumos(Systems/python直譯器選擇)。
# 固定位置排在 python3 前面:圖形用戶端的 PATH 很短,先執行 /usr/bin/python3 會在沒裝開發工具的 Mac 跳安裝對話框。
# LUMOS_PYTHON_SEARCH_DIRS(冒號分隔)有設就換掉固定位置——測試接縫,跟 lumos 內部那份同一個。
# LUMOS_PYTHON 有設就先試它:找不到時的說明叫人設它,第一步就不能不認。只收絕對路徑、而且真的是 python
# (post-commit 直接把程式交給它跑,不經 lumos 驗;設成 /usr/bin/true 會假成功、漏寫跳過帳);不合格就記下原因往下找,
# 版本夠不夠仍由 lumos 判。LUMOS_PYTHON 被略過、改用別支時當場印原因與後果:lumos 自己只認 LUMOS_PYTHON,
# 之後的檢查會因同一個值擋下(代碼審 r3、r4;印在這段裡,七個呼叫端不必各寫一份)。
_lumos_any_python() {
  if _lumos_any_python_find; then
    if [ -n "$_LUMOS_ANY_NOTE" ]; then
      printf '%s改用 %s;但 lumos 只認 LUMOS_PYTHON,之後提交與推送前的檢查會因這個值擋下——修正它或 unset LUMOS_PYTHON。\n' \
        "$_LUMOS_ANY_NOTE" "$_LUMOS_ANY_EXE${_LUMOS_ANY_ARG:+ $_LUMOS_ANY_ARG}" >&2
    fi
    return 0
  fi
  _LUMOS_NO_PY_MSG="$_LUMOS_ANY_NOTE$_LUMOS_NO_PY_BASE"
  return 1
}
_lumos_any_python_find() {
  _LUMOS_ANY_EXE=""; _LUMOS_ANY_ARG=""; _LUMOS_ANY_NOTE=""
  if [ -n "${LUMOS_PYTHON:-}" ]; then
    case "$LUMOS_PYTHON" in
      /*|[A-Za-z]:[\\/]*)
        if [ -x "$LUMOS_PYTHON" ] && [ "$("$LUMOS_PYTHON" -c 'print("LUMOS_PY_OK")' 2>/dev/null | tr -d '\r')" = "LUMOS_PY_OK" ]; then
          _LUMOS_ANY_EXE="$LUMOS_PYTHON"; return 0
        fi
        _LUMOS_ANY_NOTE="LUMOS_PYTHON=$LUMOS_PYTHON 不存在、不能執行或不是 python,略過。
" ;;
      *) _LUMOS_ANY_NOTE="LUMOS_PYTHON=$LUMOS_PYTHON 不是絕對路徑,略過(相對路徑會隨目前目錄解析到別的檔)。
" ;;
    esac
  fi
  for _c in python3.14 python3.15 python3.16; do
    if command -v "$_c" >/dev/null 2>&1; then _LUMOS_ANY_EXE="$(command -v "$_c")"; return 0; fi
  done
  if [ -n "${LUMOS_PYTHON_SEARCH_DIRS+x}" ]; then
    _dirs="$LUMOS_PYTHON_SEARCH_DIRS"
  else
    _dirs="/opt/homebrew/bin:/usr/local/bin:${HOME:-/nonexistent}/.local/bin"
  fi
  _ifs="$IFS"; IFS=":"
  for _d in $_dirs; do
    if [ -n "$_d" ] && [ -x "$_d/python3.14" ]; then IFS="$_ifs"; _LUMOS_ANY_EXE="$_d/python3.14"; return 0; fi
  done
  IFS="$_ifs"
  for _c in python3 python; do
    if command -v "$_c" >/dev/null 2>&1; then _LUMOS_ANY_EXE="$(command -v "$_c")"; return 0; fi
  done
  if command -v py >/dev/null 2>&1; then _LUMOS_ANY_EXE="$(command -v py)"; _LUMOS_ANY_ARG="-3"; return 0; fi
  return 1
}
_LUMOS_NO_PY_BASE="找不到任何 python(試過 python3.14、python3.15、python3.16、固定位置、python3、python、py)。
安裝 3.14:macOS 用 brew install python@3.14 或 uv python install 3.14;Linux 用發行版的 python3.14 套件或 uv;
Windows 用 python.org 的安裝器或 winget install Python.Python.3.14。裝在別處就設 LUMOS_PYTHON=<那支 3.14 的絕對路徑>。"
_LUMOS_NO_PY_MSG="$_LUMOS_NO_PY_BASE"
# ── python-launcher end ──

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
  _lumos_any_python || { printf '%s\n' "$_LUMOS_NO_PY_MSG" >&2; exit 2; }
  LUMOS_HOME="$LUMOS_HOME" "$_LUMOS_ANY_EXE" ${_LUMOS_ANY_ARG:+"$_LUMOS_ANY_ARG"} "$LUMOS_HOME/scripts/lumos" bootstrap ${ARGS[@]+"${ARGS[@]}"}

  echo
  echo "✓ 完成。最後一步:**重啟 Claude Code session**(hooks 在 session start 載入)"
}

main "$@"; exit
