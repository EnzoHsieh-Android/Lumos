severity: minor

此 skill 的 python-idioms:`/Users/enzo/.claude/skills/python-idioms/SKILL.md` 有,但它管 asyncio、金額、逾時等通用不變量,沒有條款管「函式內 import 擺哪裡」或「取 git 頂層用哪支 helper」,所以沒有可引的條款。

## 不對齊

1. 函式內 `import filecmp` 擺在函式中段,不在函式開頭
severity: minor
blocking: 否
引句:「+    import filecmp
+    sib = None if _hooks_path_is_ours(root, hp) else」
file: `scripts/lumos:22815`(`_vendored_pending` 把 `import filecmp` 放在函式第一行)、`scripts/lumos:25837`(同一支 `enforcement_status` 開頭就有 `import json as _json`)
- 修補把 `filecmp.cmp(..., shallow=False)` 換掉自寫的 `_same_bytes`,這是對的:專案已有 `_vendored_pending` 用同一個呼叫,不再留第二份比檔案內容的寫法。
- 不一致的只有 import 位置。鄰居(`_vendored_pending`、`enforcement_status` 本身)都把函式內 import 放在函式最前面,這裡卻放在 ④⑤ 區塊中段。
- 這是位置問題,結構上沒有錯,所以列 minor。

## 三問

**1. 分層與依賴方向**
- 新函式 `_hooks_path_sibling_worktree` 放在 `_hooks_path_is_ours` 正後面(`scripts/lumos:22044`),緊鄰同一族的 hooksPath 判斷,位置跟鄰居一致。
- 路徑解析走共用的 `_hooks_path_dir`(`scripts/lumos:22012`)。該函式的 docstring 明講「解析只有這一份」,新碼照做,沒有另寫一份。
- 呼叫它的只有 `enforcement_status`(`scripts/lumos:26008`)。`_hooks_path_is_ours` 保持不變,拆除流程沒被牽動,這個分層邊界跟 diff 的 WHY 行一致。
- `_lens_git` 定義在 `scripts/lumos:45950`,屬於後段的審查工具區,卻被前段的 enforcement 相關碼呼叫。這不是新的跨層:`_events_root`(`scripts/lumos:25564`)已經這樣用,所以算既有慣例。
- 帶入 `_enforcement_prepush_gated`(`scripts/lumos:26116`)的方式,跟原本非工作樹路徑一樣,沒有繞過它。

**2. 命名與錯誤處理**
- 型別註記 `-> "Path | None"` 用引號,跟 `_expected_claude_body`(`scripts/lumos:22175`)、`_version_nudge`(`scripts/lumos:22461`)一致。
- git 呼叫改走 `_lens_git`,且 `timeout=3`、失敗回 `None` 時退回 `None`,跟 `_events_root`(`scripts/lumos:25559`)的做法與註解口徑相同。修補前自寫的 `subprocess.run(... timeout=10)` 加 `try/except` 已經拿掉。
- `_rev` 是函式內的小閉包,專案內類似的有 `scripts/lumos:6352` 的 `_git`,形式相近。
- 例外處理:修補後 `_rev` 不再自己捕例外,靠 `_lens_git` 吞 `OSError` 與逾時。`enforcement_status` 外層每層另有 `try/except` 兜底,跟鄰居一致。
- 附帶一個既有的差異,不是這份 diff 造成的:`enforcement_status` 開頭讀 `core.hooksPath` 的那行(`scripts/lumos:25998` 附近)仍是 `subprocess.run(..., timeout=10)`。同一函式因此並存兩種 git 呼叫方式。那行不在 diff 內,不列為本次 finding。

**3. 第二種做法**
- 修補前有兩處「第二種做法」,修補後都收斂了:
  - 自寫 `_same_bytes` 已刪,改用 `filecmp.cmp`(`scripts/lumos:22821` 已有同樣用法)。
  - 自寫的 `rev-parse --git-common-dir` 子程序已刪,改用 `_lens_git`。Grep 查到 `--show-toplevel` 在專案裡有十幾處都走 `_lens_git`,例如 `scripts/lumos:30449`、`scripts/lumos:33214`、`scripts/lumos:41021`,所以新增的 `_rev(other, "--show-toplevel")` 是同一種寫法。
- 少數還用裸 `subprocess` 取 `--show-toplevel` 的老碼是 `scripts/lumos:16057`、`scripts/lumos:21798`、`scripts/lumos:24226` 等,屬於舊寫法,新碼沒有跟著用,這是正確方向。
- 抽查 `--git-common-dir` 這個旗標,只有 `_events_root` 與新函式在用。新函式先組同一條 `rev-parse` 再跑兩次,沒有跟 `_events_root` 重複實作,因為兩者回傳的東西不同(一個回主 checkout 根,一個比兩個路徑是否相等)。這是兩種用途,不算第二種做法,但如果之後要收斂,可以抽成共用 helper。
- 測試 `t_hooks_path_sibling_worktree` 的結構、`_sp`/`_os` 別名、`_line` 抓列的方式、`cwd` 與 `timeout=180` 的寫法,都對齊 `t_hooks_path_forms_all_recognized`(`scripts/test_lumos.py:46449`)。
- 新測試的 `_repo` 與 `_line` 是測試內的小 helper,在這個檔案裡是常見形式。

不對齊共 1 條,其中 major 0 條
