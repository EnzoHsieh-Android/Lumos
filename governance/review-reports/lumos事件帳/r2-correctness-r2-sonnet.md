severity: major

整體:r1 的七條主修復與六個小項大多真的修好了,寫入端(同步取走緩衝、串行佇列、唯一塊檔名)、安裝來源(`_lumos_src()`)、測試隔離都站得住。新增的移除段有一個 blocking 洞:spec 想掛外掛移除的函式,`lumos uninstall` 與 `lumos teardown` 其實都不會呼叫。

我實查了這些 mod API 與程式碼假設,結果相符:
- `$.process.run(argv, { cwd, timeoutMs })` 的簽名、`$.fs.write` 會自動建目錄、`$.fs.list` 的 `kind` 欄位、`$.session.cwd()` 與 `$.session.id()` 都存在。
- `turn.complete` 的 `reason` 四值、`agent.spawn` 結果的 `agentId`、`session.append` 的 `door` 篩選與 `origin.kind`、`session.end` 的 `sessionId` 與共用短時限都存在。
- 本機 git 2.39.2 對 `--path-format=absolute --show-toplevel --git-common-dir` 的輸出,在 worktree 與主 checkout 都符合 spec 的解法。
- `claude plugin marketplace add/remove`、`plugin install/uninstall` 都有 `--scope`;`marketplace list --json` 與 `plugin list --json` 都存在。
- `t_enforcement_never_raises_on_missing` 現在確實釘 23 列(`scripts/test_lumos.py:31327`)。
- 測試執行器已有統一隔離(`_isolate_environment`,`scripts/test_lumos.py:441` 一帶),S10 把開關加在那裡可行。

### F1 外掛移除掛在 `_teardown_global_claude`,但 uninstall 與 teardown 都不經過它
severity: major
blocking: 是 — 照 spec 實作,真實的 `lumos uninstall` 與 `lumos teardown` 都不會移除外掛,回退第 1 步靜默失效,而 S7 測試仍會綠。
- spec 段落:範圍 5、做法 4「位置」與「移除流程」、S7、回退第 1 步、實務隱患「不可逆」。
引句:「可以用 `lumos uninstall` 撤回;程式回退要照回退節兩步的順序」
- 問題:
  - spec 說移除在 `_teardown_global_claude` 裡做,且 `uninstall`、`teardown` 都會經過它。
  - `_teardown_global_claude` 只是相容包裝,轉呼叫 `_teardown_global_hooks(src, "claude")`。
  - `cmd_teardown` 直接呼叫 `_teardown_global_hooks(..., "claude")` 與 `"codex"`,不經過包裝。
  - `cmd_uninstall` 完全沒有呼叫任何全域 hook 或外掛移除,只收 symlink 與 skills。
  - 所以全 repo 只有測試會呼叫那個包裝函式。
- 具體失敗場景:
  1. 實作者照 spec 把移除段放進 `_teardown_global_claude`。
  2. S7 的測試沿用既有 `_teardown_run(home, "_teardown_global_claude")` 的寫法呼叫包裝,綠燈。
  3. 使用者照回退第 1 步跑 `lumos uninstall`,外掛與市集都還在,沒有任何訊息。
  4. 回退第 2 步刪掉 `mods/` 後,每台機器都留下失效的市集登記,而 spec 宣稱這只會發生在「漏跑」的機器上。
  5. 用 `lumos teardown` 也一樣不會移除,因為它直接呼叫 `_teardown_global_hooks`。
- 佐證:
  - file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:18776` 是包裝;`:17100` 是 `cmd_teardown` 直接呼叫 `_teardown_global_hooks`。
  - file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:16969` 的 `cmd_uninstall` 全函式沒有任何 hook 或外掛移除。
  - file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/test_lumos.py:689` 與 `:9288` 是只有測試呼叫包裝。
  - 注意 `cmd_teardown` 在來源 repo 內會直接擋下,所以來源 repo 這台機器只能靠 `uninstall` 撤回。

### F2 緩衝為空時的寫塊沒有規定,會寫出空塊檔與空會談資料夾
severity: minor
blocking: 否 — 只造成垃圾檔與讀取端雜訊,不丟資料也不覆蓋。
- spec 段落:做法 2 寫入。
引句:「觸發時機:`turn_end`、緩衝滿 50 筆、`session.end`」
- 問題:
  - `turn_end` 已經排了一次寫塊,`session.end` 又排一次,串行佇列讓第二次拿到的是空緩衝。
  - spec 沒寫「緩衝空就不寫」,「寫塊時先解位置、判圖譜、補 `.gitignore`」這些動作會照做。
- 具體失敗場景:
  - 每個會談結束都多一個內容為空的塊檔。
  - 只有一個子代理 `turn_end` 被另一次寫塊搶先清空時,同樣多出一個空塊。
  - 空塊會刷新會談資料夾的修改時間,`lumos events` 的最近 10 個排序與 enforcement 的 7 天判定都會被它影響。

### F3 `session.end` 規則自相矛盾:先寫塊再 `next`,又說不等
severity: minor
blocking: 否 — 不影響其他事件,只影響最後一塊能不能落地。
- spec 段落:做法 2。
引句:「引擎對結束只給一段很短的共用時間」
- 問題:
  - 前半要求先 `await` 寫塊再呼叫 `next(e)`,後半說寫不完就算了、不等。
  - 這個 hook 沒有競賽邏輯就做不到「寫不完就算」。
  - 照字面實作會讓 hook 在寫塊 `await` 期間占住結束鏈,可能吃掉共用短時限,拖累其他外掛的 `session.end`。
  - 照後半實作不 `await`,則行程可能在寫完前結束。
- 佐證:file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:4275` 一帶的 `session.end` 說明,以及 `:10506` 的 `SessionEndInput`。

### F4 回退第 2 步少列 S12 的測試與 S13
severity: minor
blocking: 否 — 回退後 CI 才會紅,有明確可補的清單。
- spec 段落:回退。
引句:「刪 S4–S11 的測試」
- 問題:
  - S12 的 `t_events_reader_from_worktree` 排在 S4 與 S11 的編號區間之外,而且它呼叫 `_events_read` 與 `_events_root`。
  - 回退拿掉這兩個函式後,這支測試會紅。
  - S13 的 `ledger.test.ts` 隨 `mods/` 一起刪,不受影響。

### F5 外掛同步的觸發點說明漏了 init 與 vendor 路徑
severity: minor
blocking: 否 — 實作者照 spec 掛在 `_sync_global_hooks` 內,行為本身沒錯,只是測試與文件對觸發範圍寫錯。
- spec 段落:做法 4「位置」。
引句:「`lumos install`、`update`、`bootstrap` 都會經過它」
- 問題:
  - `_sync_global_hooks` 還被 `_sync_global_from_project`(`scripts/lumos:18831`)與 `_install_hooks_py`(`:18844`)呼叫。
  - `cmd_init` 與 `_vendor_toolchain`(`:18040`)走的就是這兩個函式。
  - 所以在任何消費專案跑 `lumos init` 也會呼叫 `claude plugin` 最多約 5 步、每步最長 30 秒。
  - 這在測試隔離下被開關擋掉,但真實使用時 init 也有這個副作用,spec 沒寫。

### 前輪修復驗收
- r1 F1(緩衝寫完才清空):已修好。同步取走緩衝、串行佇列、唯一塊檔名都到位;新引入的空塊問題見本輪 F2。
- r1 F2(序號在模組變數、熱重載覆蓋):已修好。改成毫秒加隨機字串的唯一檔名,不靠序號,熱重載與 resume 都不會覆蓋;誠實界線也補了熱重載會丟緩衝。
- r1 F3(安裝來源綁 worktree):已修好。來源改用 `_lumos_src()`,同名不同來源先移除再加;但回退與撤回依賴的 `uninstall` 路徑有新洞,見本輪 F1。
- r1 F4(bootstrap 描述錯):已修好。bootstrap 以子行程跑 `install --force` 的描述正確,新版改靠 `/reload-plugins`。
- r1 F5(既有測試會呼叫真 claude):已修好。`LUMOS_SKIP_CLAUDE_PLUGIN` 加清掉 `CLAUDE_CONFIG_DIR`,掛在已有的統一隔離處(S10)。
- r1 F6(enforcement 列定義):已修好。單列 `claude-event-ledger`、三值、列數 23 改 24,與程式碼相符。
- r1 F7(無保留期限、掃描無上限):已修好。`lumos events --prune` 加只看資料夾層的 mtime;`_events_root` 只掃會談資料夾。
- r1 小項 `origin.kind`:已修好。
- r1 小項 `turn_start` 只有主迴圈:已修好,並加了讀取端的回合框法。
- r1 小項 `spawn` 的 `agent` 欄位與 `child`:已修好。
- r1 小項 `notebook_path`:已修好。
- r1 小項 uninstall 沒裝過時誤報失敗:修出新問題。先判定的設計到位,但掛點選錯,見本輪 F1。
- r1 小項 `session.end` 時限:修一半。補了先寫再 `next` 與用事件自己的 `sessionId`,但「寫不完就算了」與先 `await` 寫塊矛盾,見本輪 F3。

最嚴重 severity:major,blocking 共 1 條(F1)。
