#!/usr/bin/env bash
# install.sh — 薄殼:安裝邏輯已收進 python 單一源(scripts/lumos)。保留檔名供舊文檔/離線使用(cmd_bootstrap 已改探測 scripts/lumos,2026-07-25 F3)。
# 等價於 `lumos install --force`:裝全域 lumos + user-scope skills(symlink → ~/.claude/skills/* 與 Codex 讀的 ~/.agents/skills/*)
# + 兩家 hook 註冊(~/.claude/settings.json、~/.codex/hooks.json;Codex 的 hook 要你開一次互動 codex 審過才會跑)。
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
_lumos_any_python || { printf '%s\n' "$_LUMOS_NO_PY_MSG" >&2; exit 2; }
exec "$_LUMOS_ANY_EXE" ${_LUMOS_ANY_ARG:+"$_LUMOS_ANY_ARG"} "$(cd "$(dirname "$0")" && pwd)/scripts/lumos" install --force "$@"
