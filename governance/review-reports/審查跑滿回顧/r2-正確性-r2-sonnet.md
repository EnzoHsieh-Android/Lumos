severity: major

### F1 「跑滿未過」訊號①只看 cap-reached 事件存在,沒排除後來 converged 的迴圈
severity: major
blocking: 是 — 〈名詞〉的機械判法與 d4「剛好在最後一輪過閘的不算」自相矛盾,doctor、retro-stats 與退場條件的分母都會算錯
- spec 段落:〈名詞〉跑滿未過。
- 引句:「①治理帳有這個編號的 `cap-reached` 事件(`loop next` 在到上限、處置閘沒過時寫的那筆)」
- 引句:「剛好在最後一輪過閘的不算(Enzo 2026-10-05 裁,見決策 d4)」
- 問題:`cmd_loop_next` 每被問一次、只要輪數達上限且閘當下沒過,就寫一筆 cap-reached;`converged` 排在它前面,但先前已寫的 cap-reached 不會被抹掉。spec 的判法沒有「且沒有 converged / rewrite」的條件。既有的 `gov --stats` 反而有:`"cap-reached" in k and "converged" not in k and "rewrite" not in k`。
- 輸入→結果:standard 迴圈跑 3 輪。第 3 輪記完閘因留痕或引句問題沒過,問一次 `loop next` 寫下 cap-reached。補好後同一輪重問,converged,迴圈在輪數 3 收斂。照 spec 這個迴圈仍是「跑滿未過」,會進 doctor 清單與 `retro-stats` 的「兩者都沒有」清單,而且清不掉:閘不管它(輪數不超過上限,第八步不適用),只能 `--skip`。這會讓退場條件②「跳過次數多過寫了回顧的次數」被灌水。
- 反向情形:人裁判整份重寫而開新編號收尾的舊編號(cap-reached 加 rewrite),在 spec 判法下也算跑滿未過。
- file: `scripts/lumos:13248`(rounds_count >= cap 即寫 cap-reached,每問一次一筆)
- file: `scripts/lumos:8145`(既有 gov --stats 的正確排除寫法)
- 真帳:`docs/.governance-log.jsonl` 目前只有 3 個編號有 cap-reached,都在 2026-08-24,沒有同時 converged 的。所以這個洞現在不會現形,上線後才會冒出來。

### F2 只靠訊號①的跑滿(人裁「不開第四輪」)沒有任何擋點,只有提醒
severity: major
blocking: 是 — spec 自己舉的動機案例(事件帳那次)在新機制下擋不到,第八步與破例擋點都不會觸發
- spec 段落:〈為什麼要做〉實例、〈三、擋點〉2。
- 引句:「第三輪仍有 major,Enzo 裁全修不開第四輪」
- 引句:「輪數已超過上限的迴圈,`loop status --disposal` 要求合格回顧」
- 問題:第八步與 S1 的擋點只在「輪數超過上限」成立。到上限就停(輪數 = 上限)的迴圈只有訊號①,也就只有 `loop next` 多印的那一行。動機實例就是這種形狀,不會被任何閘或記帳擋住。〈三〉只承認「人裁直接放行擋不到」,沒承認「到上限不開破例輪」這條也擋不到,而這條才是常態。
- 輸入→結果:3 輪、不開第四輪、人裁放行。第八步不適用,canary record 沒有第四輪要擋。只剩 doctor 列出,且不算 issues。
- 建議:至少在〈誠實界線〉與 REVISIT 明說只有「超過上限」那類被擋;並釐清 F1 的排除條件。

### F3 `--record` 與 `--skip` 靠 `_loop_gov_mark` 式寫帳,寫不進去也回成功,閘卻永遠 ✗
severity: minor
blocking: 否 — 只在非 git 或無 HEAD 提交等少見環境觸發
- spec 段落:〈二、指令〉、〈實務隱患〉併發。
- 引句:「治理帳寫入照 `_loop_gov_mark` 既有做法(失敗不擋)」
- 問題:`_append_governance_log` 在取不到 HEAD 提交時直接 return,寫檔遇 OSError 也靜默吞掉。`--record` 與 `--skip` 的唯一憑證就是這筆事件,「失敗不擋」套在這裡會變成回 0 並印「已記」,但治理帳沒有事件。
- 輸入→結果:新 clone 還沒有提交,或帳檔唯讀。`--skip --note` 回 0,下一次問閘第八步仍 ✗,使用者以為已跳過。
- 建議:這兩個指令要檢查寫入結果,照 `_gate_event` 回傳 bool 的前例。
- file: `scripts/lumos:1551`(`_append_governance_log` 無提交即 return、OSError 吞掉)

### F4 「最新一筆 cap-retro」若沿用 `gov` 的讀帳去重,會取到舊的那筆
severity: minor
blocking: 否 — spec 沒指定讀法,是否發作取決於實作選擇;但這是銜接處的陷阱,值得在 spec 寫死
- spec 段落:〈名詞〉合格回顧、〈三〉S3。
- 引句:「治理帳最新一筆 `cap-retro` 事件記的指紋等於檔案現在的指紋」
- 問題:`lumos gov` 的載入器依 ts 排序後,以 (commit, nodes, gate, kind, token, check) 去重並保留第一筆。cap-retro 沒有 token,所以同一個 HEAD 提交上同編號的兩筆 `--record` 會折成較舊的那筆。
- 輸入→結果:同一提交上先 `--record`,改檔後再 `--record`。若實作重用那個載入器,「最新」其實是第一筆,指紋對不上,S3 第八步 ✗。
- 另一個讀帳細節:`_gov_row` 把 nodes 轉成 stem,編號含特殊字元時要確認比對一致。
- 建議:spec 明寫「直接讀原始 jsonl、取檔內最後一個合法行、壞行跳過」,並補測壞行與多筆各一案。
- file: `scripts/lumos:8392-8399`(去重鍵與保留第一筆)

### F5 `--skip` 事件不綁輪次也不綁迴圈狀態,一次跳過永久有效
severity: minor
blocking: 否 — 屬寬鬆而非誤判,且 spec 有意留出口;但與「跳過次數」統計的意義有落差
- spec 段落:〈名詞〉合格回顧。
- 引句:「或治理帳有一筆 `cap-retro-skipped` 事件」
- 問題:合格回顧的後半句不帶輪次或指紋。任意時刻(甚至迴圈還沒跑滿時)對任意編號 `--skip` 一次,之後第 4、5、6 輪都不再擋,破例擋點與第八步都永久通過。
- 輸入→結果:第 3 輪就預先 `--skip --note "先跳過先跳過"`。之後連開三個破例輪都不擋,`retro-stats` 只算「跳過 1 次」。
- 建議:跳過事件記下當下輪數,並只在該輪數內有效。

### F6 訊號②用 `_disposal_round_groups`,帳序損壞時回錯誤而 fail-open,與訊號①、loop next 的算法不一致
severity: minor
blocking: 否 — 只在帳被手改或異常時發生
- spec 段落:〈適用範圍〉觸發、S12。
- 引句:「輪數、分級、上限一律用新抽出的共用函式,跟 `_cap_hint` 同一套」
- 問題:`cmd_loop_next` 的 `rounds_count` 是 `len({r["round"] ...})`。`_cap_hint` 用的 `_disposal_round_groups` 遇到 round-id 被隔開後重現、或 `__` 開頭輪次時回 `(None, err)`,`_cap_hint` 直接回 None。
- 輸入→結果:帳上 r1,r2,r1,r3,r4 這類亂序。loop next 照集合算已超過上限,共用函式回「不是跑滿」,擋點全放行。處置閘本身雖會 rc2,但 `canary record` 的破例檢查不走處置閘。
- 建議:共用函式要區分「不適用」與「帳壞」,帳壞時 canary record 要 fail-closed 或至少印警告。S12 只釘 `_cap_hint` 輸出不變,抓不到這點。
- file: `scripts/lumos:12943`(集合算輪數)
- file: `scripts/lumos:22477`(`_disposal_round_groups` 的錯誤分支)
- file: `scripts/lumos:8828`(`_cap_hint` 遇 err 回 None)

### 其他節
- 〈一、回顧檔〉、〈二、指令〉其餘部分、〈四、doctor〉、〈五、誰來寫〉、〈回退〉:已讀,無 finding。
- 編號檢查所引的 `cmd_loop_replay` 既有規則存在(含 `/`、`\`、`..`),spec 這一點屬實。
- `_cap_hint_scope`、`_cap_hint_round`、`_report_findings_missing_severity`、`LOOP_NOT_CLOSE_EVENTS` 都存在,而且與 spec 描述一致。
- `t_loop_close_kinds_classified` 這條守衛:新事件登記為 `("design-loop", ...)` 是對的。若 gate 名寫成別的,該測試會翻紅。
- ⚠ 破例輪檢查在 `canary record` 對「沒帶 --round」的新列:`cmd_canary` 寫側沒有擋,該列不計入輪數,但之後處置閘會因混用 rc2。本席沒找到可繞過閘的具體路徑,不標 finding。

總結:最嚴重 major,blocking 2 條
