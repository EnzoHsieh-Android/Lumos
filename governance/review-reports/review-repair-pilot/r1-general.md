severity: major

G1 試行把完整 finding 與驗證證據放進 intake，卻未要求記帳時帶 `--intake`；現行命令把它列為選配，處置閘也只重驗帳列中已附的 intake。因此在 `--refuted-set none` 的常見輪次，編排者可不附 intake，事後內容遭改仍不會被偵測，五案的缺陷歸因、根因組數與耗時證據便無法可靠回放。設計應明定試行每輪 carrier 一律帶 `--intake`，或把同等不可變證據移入必定雜湊的報告。

severity: major

blocking: 是

引句:「完整 finding id 和證據留在各輪入帳前的 intake；已入帳後才取得的資訊寫本計劃逐案紀錄」

file: `scripts/lumos:8431`

file: `scripts/lumos:19768`

file: `skills/lumos-code-loop/SKILL.md:46`

最小翻紅重現：建立含試行證據的 `r1-intake.md`，以 `--refuted-set none` 且不帶 `--intake` 完成 carrier 記帳，記帳後改寫該 intake，再執行 `lumos loop status <id> --disposal --spec <patch> --repo <root>`；預期應因試行證據雜湊不符回 rc1，依現行程式只掃帳列的 `intake_path`，實際仍可通過。未能重現：本席受唯讀、禁止寫檔與治理帳 mutation 限制。

範圍與條款：除 G1 外已讀，無 finding；major 處置仍一律折入，三輪上限、原席只驗原 finding、新席掃 delta 與 high 資安席覆蓋均有保留。

落點：已讀，無 finding。

試行登記與回顧入口：除 G1 外已讀，無 finding；五案取樣、中止計數、歷史對照、耗時與去重口徑可執行。

實務隱患：已讀，無 finding。

回退：已讀，無 finding。

總結：最嚴重 severity: major；blocking: 1 條。

