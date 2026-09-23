severity: major

## F1 逐字複本守衛用寫死兩個路徑比對,不是掃全部——跟本 repo 已踩過同一種坑後改掉的既有做法不一樣

severity: major
blocking: yes

本 repo 對「hook 間逐字相同複本」已經有一套成熟做法,而且是踩過一次事故才定下來的:`hook信任邊界` 那組守衛原本寫死三支 hook 的名字去比對,結果第四支(`dispatch-lens-hook.py`)沒被列進去、複本漂掉也沒人抓到,2026-09-07 之後改成動態掃 `hooks_dir.glob("*.py")` 再判斷「真的用得到這段的才比」,不再寫死清單。`逾時預算` 那組守衛也是同一種掃全部寫法,而且它的測試註解自己講白了同一個教訓:「程式碼註解自己寫著『這段在幾支 hook 裡是逐字相同的複本,有守衛盯著不准漂』——但那句話當時是假的……只有這段沒有〔守衛〕」,補的做法一樣是 `for _f in sorted(hooks_dir.glob("*.py")):` 掃全部再比對簽章。

這次新增的 `t_ci_latest_attempts_copies_identical` 反過來,直接寫死兩個路徑去抓函式比對:

引句:「    a = body(base / "lumos")」
引句:「    b = body(base / "hooks" / "claude" / "ci-status-hook.py")」

跟既有兩組守衛(`hook信任邊界`、`hook逾時預算`)的寫法不一樣——既有寫法是「掃 hooks 目錄下全部 .py,篩出真的含這段函式的才比」,這支是「寫死我知道的兩個檔」。現在只有這兩份複本,功能上不會錯;但這正是 repo 自己 PITFALL 記錄過會翻船的形狀:以後如果第三支 hook 或某支工具也需要 `_ci_latest_attempts`(例如未來 `lumos gov` 或別的讀帳路徑也要吃同一個判法),寫死清單的守衛不會自動涵蓋它,得靠人記得回來加,而這正是「動態掃」被引入取代「寫死清單」要解決的問題。

佐證(既有慣例的兩處出處,非引自本次 patch):
- `scripts/test_lumos.py:15636`:`# ★2026-09-07 改成掃全部,不寫死清單★:第一版寫死三支,結果第四支`
- `scripts/test_lumos.py:15640`:`all_hooks = sorted(f.name for f in hooks_dir.glob("*.py"))`
- `scripts/test_lumos.py:16097`:`for _f in sorted(hooks_dir.glob("*.py")):`
- `scripts/test_lumos.py:16102`:`"★前置★ 現場成立: 至少五支 hook 有那段預算複本"`

建議改法:`t_ci_latest_attempts_copies_identical` 比照這兩組既有守衛,改成掃 `scripts/hooks/claude/*.py`(以及 `scripts/lumos`)裡「真的定義了 `_ci_latest_attempts`」的檔案,全部互相比對,而不是寫死兩個路徑——這樣以後多一份複本時守衛自動涵蓋,不用回頭記得改測試。

## 已驗過:家節點寫法

比對 `docs/lumos-toolchain-knowledge/Systems/CI回流開場提醒.md` 跟另一篇同型態(單支 hook、近期新建)的家節點 `docs/lumos-toolchain-knowledge/Systems/記憶過期清掃.md`:兩者都有 `responsibility` 欄位(負責/不負責寫法一致)、`aliases: []`、`about_code` 只列自己那支檔、`tags` 都含 `scope/guards-gates`。`CI回流開場提醒` 另外多帶 `related` 連回 `[[Projects/CI回流閉環_計劃]]`,這點在 `棧別提問表態閘.md` 等較早的節點裡也看得到同樣用法,不是新花樣。沒有發現跟既有同類節點衝突的地方,列出來備查,不算擋。

---

驗過的路徑:`scripts/lumos`、`scripts/test_lumos.py`(t_ci_rerun_latest_attempt_wins / t_ci_latest_attempts_copies_identical 兩支新測試、既有 hook信任邊界與 hook逾時預算兩組漂移守衛)、`scripts/hooks/claude/ci-status-hook.py`、`docs/lumos-toolchain-knowledge/Systems/CI回流開場提醒.md`、以及全 repo grep `逐字相同的複本` / `語法樹` / `hooks_dir.glob` 找出的既有同類守衛與家節點作對照。
