severity: minor

## 逐類結果
1. 不可信輸入:路徑——已看,無可寫出 repo 的路徑。cap-decision/retro 的編號過 `_retro_id_bad`(擋 `/`、`\`、`..`、控制字元),新增的寫入只有 `_gate_event` 追加治理帳;回顧檔只讀、只算 sha256,不寫。`canary record --loop` 的編號沒過 `_retro_id_bad`,但只走唯讀(is_dir/is_file/讀檔算指紋),結果不外洩內容。命令/shell 插值:已看,無(沒有新的 subprocess;`_shlex.quote` 用在提示字串)。反序列化:只用 json 模組,`RecursionError` 有接,無 eval/pickle。終端控制字元:見 F1。
2. 登入與權限:無登入;偽造治理帳/drafted_by 見 F2(推論)。
3. 密鑰與個資:已看,無(帳只記編號、輪次、理由、sha)。
4. 加密:指紋沿用 `_sha256_file`(SHA-256),已看,無。
5. 執行邊界:已看,無。hook/CI 沒新增執行不可信位置檔案的路徑;測試的 `_cr_repo` 用 `subprocess.run([...list...])` 與 `mkdtemp`,無 shell 插值。
6. 行動端:不適用。依賴:無新增(只用 json、shlex、os、hashlib)。

### F1 doctor [I2] 與 retro-stats 印出的 `cmd` 欄含未消毒的帳上編號,可注入終端控制碼與假輸出行
severity: minor
blocking: 否 — 只影響維護者終端顯示,輸出為提醒性質,不影響閘判定;縱深防禦類
- 誰:投稿 PR 的人(能改 `docs/.governance-log.jsonl` 與 `docs/.canary-log.jsonl`,內容隨 PR 進 repo)。
- 從哪裡:治理帳 gate=loop-retro 事件的 `loop` 欄、審查帳同編號列的 `loop`/`report_path`(兩本帳都是 PR 可帶的檔)。
- 送什麼:`loop` 值含 ESC 序列、BEL、換行(例如 `evil\x1b[2J\x1b]0;PWNED\x07\n✅ ALL GOOD`),並讓 `governance/review-reports/<該名>/` 資料夾與一列帶 report_path 的審查帳存在(這樣 applies 為真、狀態 none)。cap-decision 的 `_retro_id_bad` 只擋 CLI 寫入側,讀側 `_retro_gov_events` 對帳上 `loop` 不驗。
- 拿到什麼:維護者跑 `lumos loop retro-stats`(或 doctor [I2])時,`ent["cmd"]` / `_cap_retro_template_cmd(...)` 以 `shlex.quote` 組成後原樣印出;`shlex.quote` 不會跳脫控制字元,所以 ESC/BEL/換行原封印到終端(清屏、設標題、偽造一行「✅ ALL GOOD」)。同一行的 `c(e['loop'])` 有消毒,只有 `cmd` 漏。
引句:「ent["cmd"] = _cap_retro_template_cmd(root, lp)」
引句:「f"{_cap_retro_template_cmd(_rr_i2, _lp_i2)}")」
佐證行:file: `/Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos:10904`(`_esc_clean` 存在,只是這兩處沒套)
重現(retro-stats 已實跑):臨時目錄造上述兩本帳,`python3 scripts/lumos --vault $T/docs/kg loop retro-stats --repo $T | cat -v`,輸出 `…→ lumos loop retro 'evil^[[2J^[]0;PWNED^G` 換行 `✅ ALL GOOD' --template > …`,控制字元與換行都在。doctor [I2] 走同一支 `_cap_retro_template_cmd` 但我在臨時 vault 上沒讓該段列出該列 ⚠(未實跑確認,依程式讀出同型)。修法方向:`_cap_retro_template_cmd` 的輸出整體過 `_esc_clean`,或讀側對 `loop` 套 `_retro_id_bad`。

### F2 治理帳事件與 drafted_by 都是自報、無簽章,持寫入權者可偽造「已記回顧」過閘(推論)
severity: minor
blocking: 否 — 推論;與既有治理帳同信任等級(能改帳等於能改任何閘),無新增權限邊界
- 誰:能提交到 repo 的人。
- 從哪裡:`docs/.governance-log.jsonl`(append 純 jsonl,無鏈、無簽章)與回顧檔 `cap-retro.json`。
- 送什麼:手寫一筆 `{"gate":"loop-retro","kind":"recorded","loop":…,"retro_sha256":<回顧檔真實 sha>}`,回顧檔裡 `drafted_by` 填任一不在帳上 auditor 集合的名字。
- 拿到什麼:`_cap_retro_status` 判已記回顧,第八步 ✓、`canary record` 擋點放行,繞過「乾淨代理起草」的要求。`_cap_retro_check` 只比對 drafted_by 是否等於帳上 auditor 字串,無從驗證身分。這是設計上「自報不驗身分」的取捨(同檔 `--withdrawn-by` 註明相同),所以只標縱深;寫不出超出既有帳信任模型的新路徑。
引句:「if _retro_text_ok(db, 1) and db.strip() in auditors:」
佐證行:file: `/Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos:1445`(`_gate_event` 無簽章追加)

總結:最嚴重 minor,blocking 0 條
