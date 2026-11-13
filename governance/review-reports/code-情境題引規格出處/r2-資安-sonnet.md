severity: minor

## x1 --plan 的新檢查只比對 Projects 解開後的位置,Projects 本身是符號連結時寫檔會跑出圖譜
severity: minor
blocking: 否
引句:「real_rel = ppath.resolve().relative_to((env.vault / "Projects").resolve())」
file: `scripts/lumos:75560`(`_situation_rule_plan`,在 1d535b07b 裡用 grep 找函式名)。真正寫檔的 `_write_refusal_reason`(`scripts/lumos:30492`)只用 lstat 看最後一層檔名,不看上層目錄是不是連結。
攻擊路徑:
- 誰:能讓使用者打開他的 repo 的人(陌生 repo 作者)。
- 從哪裡:repo 裡提交一個符號連結 `docs/<專案>-knowledge/Projects -> /Users/<受害者>/某資料夾`。
- 送什麼:受害者(或照常操作的 AI)跑 `lumos situation-rule --plan Projects/x`。`x.md` 解開後落在連結指到的資料夾裡,而那個資料夾本來就被當成 `Projects`。包含檢查拿「解開後的 Projects」當基準,所以 `relative_to` 成功、字串也相等,檢查通過。
- 拿到什麼:`_situation_rule_write` 把一行 `- [S<n>] ... [test:...]` 寫進圖譜外、任何含「## 驗收條款」節的 md。
- 前提很多:要先過段、列、殺傷力 killed 與終端確認,攻擊面窄,所以只標縱深。
- 修法:改拿 `env.vault.resolve()` 當基準,並確認 `(env.vault / "Projects")` 本身不是符號連結。

## x2 AI 帶任意 --consent 寫的人裁條款,規格閘認得跟人在終端點頭寫的一樣
severity: minor
blocking: 否
引句:「got[0] == e["clause_sha"] and got[1] == {e["test_name"]}」
file: `scripts/lumos:14539`(`_spec_gate_ruled_ids`;帳上有 origin 與 consent 欄,但閘不看)。
攻擊路徑:
- 誰:照常操作的 AI(自己決定少一次人工核可,屬刻意偽造,依範圍規則只標 minor)。
- 從哪裡:`lumos situation-rule` 在沒有終端時,只要帶任一非空 `--consent "<字串>"` 就過。
- 送什麼:一條新行為條款加一支已存在的測試,以及一組殺傷力 killed 的 old/new。
- 拿到什麼:該條款被規格閘當既有行為,免除「新行為條款要先紅」和預期值表簽核。`_spec_gate_ruled_ids` 只比 plan、條款編號、條款文字雜湊和 test_name,不看 `origin=="ai"`,也沒有像 `_lint_waiver_ai_unacked` 那種「AI 放行須人看過」的機制。
- 殺傷力 killed 仍然是硬門檻,所以免掉的只有「人點頭」這一半。
- 建議:閘對 origin 為 ai 的事件要求事後人 ack,或至少印一行提醒。

## 附:逐類結論
①提示注入:已看,無可利用的洞。
- 盲判指示已寫明 specs 是資料不是指令(`_KT_BJ_INSTRUCTIONS`),屬文字層防護。條款文字進盲判材料仍是 AI 讀作者可控內容的殘餘,但盲判只能填 `spec` 編號,而編號由機器驗存在,沒有可用的輸出通道。
- `_situation_rule_clause_problem` 已擋換行、`[test:`、`[S<數字>`、`[keeps]`、反引號外的 `|`,條款文字無法偽造別的條款或標記。

②讀寫與執行越界:有 x1(minor)。其餘已看,無。
- `--file` 必須等於段的檔(來自 diff,NFC 比對),再用 `_kill_plat_top` 從 repo 頂算路徑並擋 `..`。`cmd_guard_kill` 另有 `realpath` 加 `wt_real` 圍欄,所以逃不出平台根或工作樹。
- `{method}` 經 `shlex.quote`,`--test` 另有字元白名單,沒有 shell 插值。
- `.lumos-keep` 只寫在 mkdtemp 建的暫存父層,不在工作樹內,repo 內容無法預先放置標記。清殘骸只多了跳過條件,不會多刪;最壞是殘骸不被清,屬資源面,不報。
- 沒有新增密鑰、信箱、下載來源或環境變數可覆蓋的網址。

③非刻意、一步繞過的守衛:已看,無(x2 為刻意偽造類,另列)。
- macOS 大小寫不敏感:`--plan` 寫成與磁碟不同的大小寫時,`resolve()` 不會正規化大小寫,檢查會過,但帳上 plan 字串與真實路徑對不上,規格閘因此不認這條為人裁。方向是變嚴,不是放行。
- NFC/NFD:`nfc()` 兩邊都轉,沒有繞過。
- 規格閘比 refs 後,換綁或多綁測試都會讓條款回到一般條款規矩,我沒找到一步免掉新行為條款紅綠驗證的路。
- SIGTERM/SIGHUP 轉成 KeyboardInterrupt 後收尾路徑與 Ctrl-C 相同,計劃與帳都不寫。
- 殘留環境:`LUMOS_TTY` 若殘留指向可讀檔,既有的 `_confirm_tty_dev` 會被自動答覆,這是原有機制,本輪只是把開法抽成 `_confirm_tty_open`,沒有新增面。

最嚴重 severity: minor;blocking 共 0 條。
