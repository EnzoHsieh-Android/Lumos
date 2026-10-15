severity: clean

我讀了凍結改動(`r1-snapshot.patch`)和範本 §7.6,逐項對照既有寫法,沒有找到第二種做法或跨層直呼。

**1. 分層與依賴方向:對齊**
- `cmd_loop_next` 裡新加的 `lens_scope` 區塊放在「修正關卡提醒」之後、輸出之前,是只附加、不改 phase 與退出碼的同一型區塊。
  - 對照 `file: scripts/lumos:16417-16433`(修正關卡 try 與 `out["fix_check"]`,新區塊緊接其後)。
- 判別工具鏈本 repo 用的是既有的 `_is_toolchain_repo`,沒有另寫判別。
  - 對照 `file: scripts/lumos:25452`(定義)。
  - 同一支函式在 `file: scripts/lumos:25466`、`26193`、`33045`、`33472`、`33606` 被呼叫,新呼叫處用法一樣。
- repo 根的算式 `Path(repo).resolve() if repo else _vault_repo_root(env)` 是第三次照抄,不是新規則。
  - 對照 `file: scripts/lumos:16399` 與 `16528`,兩處寫法逐字相同,連 `resolve` 都沒少。
  - 這支函式裡既有的註解就說少一個 `resolve` 會變第二套規則,新區塊沒有踩到。
  - 新區塊自己的註解也寫明「照本指令既有算式獨立再算一次」,是有意為之。
  - 不是 major 也不是 minor:兩處既有呼叫本來就各自重算,沒有共用的 helper 可以借。
- 輸出沒有跨層:人讀印固定字串常數 `_LENS_SCOPE_TOOLCHAIN_LINE`,JSON 多一個鍵 `lens_scope`。這跟 `fix_check`、`cap_hint` 兩個鍵的處理方式一致。

**2. 命名與錯誤處理:對齊**
- try 包法跟修正關卡一樣:`try: … except Exception:` 退回預設值(fail-open)。
  - 對照 `file: scripts/lumos:16420-16425`(`_fc = _fix_check_status(...)`,失敗退 `None`)。
  - 新區塊失敗時退 `"default"`。
- 常數用 `_` 開頭加全大寫,放在函式正上方。對照 `file: scripts/lumos:28619`(`_EVENTS_MAX_LINE`)。
- 測試命名與結構(`t_…`、`check("①…")`、`_need_src`、`Path(GRAPHCTL).resolve().parent.parent`、`_load_lumos_inproc`、`mkvault`)都是既有慣例。
  - `_need_src` 約 168 處、`Path(GRAPHCTL)…parent.parent` 約 165 處,後者另見 `file: scripts/test_lumos.py:146-153`。
  - `t_loop_next_lens_scope_fail_open` 的注錯寫法是把 `m._vault_repo_root` 換成丟例外的版本,用的是 `_load_lumos_inproc` 註解寫明的用途(fail-open 注錯)。
- 範本新增的 `###` 小節和 `{…}` 填空,跟 `§3` 既有的 `### §3 編排者派工前須知` 和 `{鄰居檔清單,pitfalls --diff 會吐}` 同型。
- 筆記的 `RULE:` 行帶齊 `[依據:人] [since:] [retire:人裁] [until:] [confirmed:]`,`WHY:` 帶 `[出處:] [因:] [test:]`,`REVISIT:` 帶日期,都合 CLAUDE.md 的表格。

**3. 第二種做法:無**
- 新的 `_tpl_dispatch_fences` 逐行掃描所有圍欄,而 `t_seat_templates_carry_marker` 是按固定標題清單切段。
  - 對照 `file: scripts/test_lumos.py:96285-96305`。
  - 兩者目的不同:前者要列舉「第一行是 `LUMOS-SEAT:` 的全部圍欄,再加 §5、§6」,後者只驗六個指定標題。
  - 不算同功能重寫,我判為對齊。
- `t_toolchain_lens_scope_doc_sync` 是逐檔切段再比對,沿用 `t_security_seat_doc_sync` 的逐檔列舉寫法。
  - 對照 `file: scripts/test_lumos.py:57838-57857`。
  - 它多做了切到那一段再搜字(不整檔搜),這是更嚴的同一做法。
- `t_templates_toolchain_lens_scope` 用 `split("## 7.8 ")` 切段再斷言關鍵字,跟 `t_templates_security_seat_section` 同一做法。
  - 對照 `file: scripts/test_lumos.py:57859-57873`。
  - 新增的 `_sub_block` 只是把「切 `###` 小節」包成小函式。

**備註(不列 finding)**
- 同一條 RULE 的全文同時出現在 `Systems/pitfalls-code-loop.md` 和計劃筆記(patch 第 240 行與第 455 行)。計劃筆記的決策段重述規則是既有做法,不是第二套規則。

最高等級 clean,blocking 0 條。
