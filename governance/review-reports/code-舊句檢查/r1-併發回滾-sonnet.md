severity: minor

# 舊句檢查 代碼審 r1:併發回滾-sonnet(審 r1-snapshot-code.patch)

實驗環境:`git clone --shared` 出工具(HEAD 620a6f73)與 rtb-mainwt(666 提交、276 支 .py)到臨時目錄,`HOME` 換成空目錄,直譯器 /opt/homebrew/bin/python3。

## F1 家目錄是 umask 002 時定義快取與漏記痕跡都建不起來,每次都冷跑
severity: minor
blocking: 否
引句:「if not _mkdir_trusted_under_home(".cache", "lumos", "drift-defs"):」
佐證行:file: `scripts/lumos:34687`(`_mkdir_trusted_under_home` 對每一層檢查 S_IWGRP,剛用 umask 建出的 0775 那層立刻被判不可信)
1. 重現:`umask 002; export HOME=<空目錄>; python3 scripts/lumos drift check --diff HEAD~30..HEAD`(工具鏈自己的 repo,改到 scripts/lumos 與 test_lumos.py)連跑兩次。
2. 輸出:兩次 9.37 秒、8.74 秒(macOS M 系列);`~/.cache/lumos` 沒有建出來;帳上 `"cache_hits": null`。同樣的指令在 umask 022 的第二次是 1.66 秒、快取 361 支。
3. 壞在哪:`_drift_m1_cache_dir` 的第一層 `~/.cache` 用預設 umask 建出來(Debian/Ubuntu 使用者預設 umask 是 002 → 0775),被 `_mkdir_trusted_under_home` 判不可信而回 False;`_home_cache_write` 裡那句 `os.chmod(path.parent, 0o700)` 只在通過檢查之後才會跑到,救不了。`_drift_m1_ledger_miss` 走同一個入口,所以同一台機器上「治理帳寫不進去」的留痕檔也永遠寫不出來。
4. 計劃〈誠實界線〉只列了「磁碟滿、家目錄唯讀」兩種家目錄失效,沒有列 umask 002;症狀(`cache_hits` 一路 null)看得出來,但原因與處置沒寫。冷跑的量測:工具鏈 repo 9 秒、記憶體尖峰 700 MB(對照熱跑 1.7 秒、230 MB),慢兩三倍的機器會碰到 m1 自己的 30 秒。

## F2 沒有起點版可比那筆帳記成 skipped,`gov --stats` 把它算進「被跳過」
severity: minor
blocking: 否
引句:「kind = "skipped" if st == "no-base" else」
佐證行:file: `scripts/lumos:7136`(`skipped = [r for r in ded if str(r.get("kind", "")).startswith("skipped")]`,「被跳過」那行)
1. 重現:新 repo、沒有遠端與主線、`docs/p-knowledge/` 在、有一支 .py,`python3 scripts/lumos drift check --diff 4b825dc642cb6eb9a060e54bf8d16288ebfb32e..HEAD`,帳多一筆 `{"gate":"drift-check","kind":"skipped","state":"no-base"}`。
2. 再跑 `python3 scripts/lumos gov --stats`,輸出「被跳過 1 次:drift-check 1  ← ★這一行是「哪一道最常被跳」的答案★」。
3. 壞在哪:那一行的語意是人用環境變數或旗標略過閘(既有 drift-check 的略過寫的是 `skipped-env`),這裡是工具自己判「沒起點、不判」,沒人略過任何東西。〈回退〉那句「帳的 kind 都是既有結果詞,舊版讀取端不看新欄位」對回退相容成立(見下),但讀取端(新舊版都一樣)是看 kind 的,這筆會讓「哪一道最常被跳」的答案多一個假的 drift-check。

## F3 同一次推送的 c 類事件與 m1 事件在 gov 去重時被折成一筆
severity: minor
blocking: 否
引句:「同一次推送同一個 gate 會有 c 類與 m1 兩筆事件」
佐證行:file: `scripts/lumos:7321`(去重鍵 `(commit, frozenset(nodes), gate, kind, token)`,沒有 `check` 欄)
1. 重現:在 nodes、commit、kind 相同的情況下記兩筆 drift-check 事件(一筆沒有 `check` 欄,一筆帶 `check: old-sentence`),`python3 scripts/lumos gov --full` 只印一筆,帶 `check` 那筆不見。
2. 場景:warn 模式下同一個提交,c2 的要處理節點與 m1 的要處理節點是同一篇筆記(舊名稱寫在已收尾計劃的 Issue 連結旁,兩種都會命中同一篇),兩筆都是 `warned`、nodes 相同 → m1 那筆在 `gov` 消失。
3. 上面 Issue 補的那句說「讀帳時用有沒有 `check` 欄分」,但 `gov` 這條讀取路徑沒有分;原始帳檔(REVISIT 用來抽樣的那份)不受影響,只有 `gov --full`/`--stats` 的呈現少算。

## 查過、沒有問題的項目(不列 finding)
- 併發讀寫快取:6 個行程同時冷跑同一範圍,`drift-defs/` 361 支全是合法 JSON、沒有殘留 `.tmp`,6 份輸出逐字相同。寫入是同目錄 mkstemp 唯一名 + `os.replace`,讀取端驗 owner/權限/保鮮期,讀到半份不可能。
- 兩個推送同時寫治理帳:上面 6 行程各記一筆,帳共 7797 行、0 行壞掉。`_gate_event` 是 O_APPEND 單次 write;m1 的事件量到 4003 位元組(超過 4096 時 `_drift_m1_fit` 先丟 rows,`rows_truncated: true`),沒有交錯。
- 淘汰:`_drift_m1_cache_evict` 只刪 mtime 過期的一般檔、目錄不可信時一支都不碰,與並行寫入不互相踩(新寫的 mtime 是現在)。
- 資源:rtb 舊 200 個提交 3.96 秒/220 MB、60 個提交 3.04 秒/223 MB;人造「一次刪 2399 個定義、筆記全提到」6.64 秒/583 MB(名稱先篩把不在筆記詞集裡的丟掉);都在 30 秒內。剖檔記憶體與批次讀無上限已是計劃〈實務隱患〉接受項,不重報。
- 回退:用 25f6a459 的舊版讀新版寫的帳與表態檔——`gov --stats`、`drift scan`、`doctor` 都不出錯;新版寫的 `--kind m1 --name=…` 表態行被舊版 `_drift_load_acks` 的種類過濾丟掉,無害。新版讀舊表態檔沒有 `names` 欄的 m1 行:不涵蓋任何名稱,只會多列不會漏列。
- git 失敗與逾時:列樹或讀內容失敗 → `fail()` 依時鐘記 timeout 或 git-failed,都進 `_DRIFT_M1_UNKNOWN`,block 擋、warn 提醒,帳照記;`gate=off` 或 `LUMOS_SKIP_DRIFT_CHECK` 在 m1 之前就回了。

## 圖譜鏡頭固定席逐條判定
- Systems/lumos-cli-read(INVARIANT:search 預設排除 superseded):diff 不碰 search 與其濾網。不影響。
- Systems/bound-tests-gate(INVARIANT:綁定測試逐支真跑):diff 不碰 code-loop check 與綁定測試閘;drift-check 帳的新事件不是它讀的種類。不影響。
- Systems/guard-kill(INVARIANT:rc 優先序、--json 純度):diff 不碰 guard kill。不影響。
- Systems/授權與歸屬(INVARIANT:授權檔不進 _VENDORED_TOOLKIT、主程式檔頭帶 SPDX 與 MIT):diff 沒改檔頭,也沒動 `_VENDORED_TOOLKIT`;新增的家目錄快取不進版控。不影響。
- Systems/測試假綠形態(INVARIANT:還原翻紅釘要配前置斷言):屬測試,不在本份 patch(code)範圍;實作紀錄自述 18 條有還原翻紅,本席未審測試。
- Systems/lumos-cli-lifecycle(INVARIANT:re-inject 只覆蓋 sentinel 之間):不碰 inject。不影響。
- Systems/design-loop(INVARIANT:處置閘第五步審材必須是 .md):不碰設計審。不影響。
- Systems/pitfalls-code-loop(RISK):不碰 pitfalls 分級;`_lens_cache_write` 改為轉呼叫 `_home_cache_write`,寫法與檢查順序逐項相同(仍是逐層建、逐層檢查、mkstemp、chmod 0600、replace),只多回傳布林,派工鏡頭的行為不變。
- 只列名的節點(loop-convergence-recording、reversibility-governance-ledger、節點範圍與索引守衛 等):reversibility-governance-ledger 是治理帳寫入器的家,本 patch 新增的寫入者與無鎖現況已由 F3 之外的既有 Issue 補記,判「不影響其合約」;其餘與本 diff 無牽連。

最高等級:minor
