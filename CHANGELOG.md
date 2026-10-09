# CHANGELOG

這份只記「對外放出去的版本」。標題格式固定為 `## vMAJOR.MINOR — YYYY-MM-DD`,
版本號的單一來源是 `scripts/lumos` 裡的 `LUMOS_VERSION`,有守衛盯著兩邊一致。

還沒發版的變更寫在 commit 訊息與知識圖譜裡,**不進這份**——
刻意不留常駐的「未發布」區塊,否則它會永遠是「最新一筆」,讓守衛每次推送都紅。

## v1.3 — 2026-10-09

兩道原本只提醒的「舊句」檢查改成預設擋(回頭重讀只在本機推送前擋;名稱消失檢查在本機推送前與 CI 的 `drift check` 那步都擋),推送前掛鉤跟著改,所以升版,讓還沒更新的專案被提示跑 `lumos update`:
- **回頭重讀守檔筆記在本機推送前擋**:推送前掛鉤的 `lumos note-audit reread-check` 多帶 `--gate`,`.lumos/config.json` 的 `note_reread.gate` 沒寫或寫壞時照 block。擋兩層——這次改程式又改到家筆記、還沒派判定者對照這一版程式的(第一層);判定點出的規則類條目(`RULE:`、`★INVARIANT★`、帶 `[test:]` 的摘要條目)還在、又沒表態的(第二層)。第二層照留用新的 `lumos drift ack <節點> <條目開頭行號> --kind reread --reason "…"`,表態要提交才算。
- **每次改程式又改到家筆記的推送都要先派判定者**(Claude 或 Codex)、記紀錄、提交;判定要把筆記全文與程式 diff 交給模型。沒有 Claude/Codex 環境、或程式碼不能送外部模型的專案,在 `.lumos/config.json` 寫 `{"note_reread": {"gate": "warn"}}`(只提醒)或 `"off"`(不跑)。單次略過照舊是 `LUMOS_SKIP_REREAD_CHECK=1 git push`(會留帳)。
- **本機掛鉤擋的時候,這道判不了也擋**:git 失敗、超過 30 秒、判定紀錄讀不懂、推送範圍的起點算不出來時回 1 擋下並印原因;確定是工具的問題就 `LUMOS_SKIP_REREAD_CHECK=1 git push` 單次略過(會留帳)。
- **已經用過回頭重讀的專案**:舊判定紀錄點出、從沒表態過的規則類條目,升級後第一次碰到那篇的推送會被擋,要逐條改掉或表態。
- 只有來源核對過的判定紀錄(`provenance_ok: true`)才算已對照;來源核對沒過的那份要重派判定者。
- 照既有手冊把 `reread-check` 接進自家 CI 的專案不受影響:CI 不帶 `--gate`,照舊只提醒、恆回 0。代價是用 `git push --no-verify` 跳過本機掛鉤時,這一道沒有 CI 兜底。
- 推送前掛鉤的這一段被訊號砍掉(回傳碼 128 以上)時整支推送停下,不再只認 Ctrl-C(130):這道會擋人之後,被外部砍掉也不該當作放行。舊版工具不認得 `--gate` 時這一段講一句「這次沒檢查」放行;`lumos enforcement` 會把沒帶 `--gate` 的生效掛鉤列為沒接上。
- **舊句檢查(名稱消失,`drift_check.old_sentence`)沒寫時照總開關 `drift_check.gate`**:總開關沒寫是 block,所以沒寫子開關的專案這一項改成擋;總開關設 warn 的跟著只提醒、設 off 的這一項也不跑(**行為變化**:原本 `gate=off`、`old_sentence` 沒寫的專案這一項照跑只印,現在不跑)。明寫的 `old_sentence` 照原義,不受總開關影響;設定檔讀不成 JSON 照 block。這一項本機推送前與 CI 的 `lumos drift check` 都照它擋:CI 接了 `drift check` 的專案,升級後有舊句要處理的推送 CI 也會紅;判不了(時間到、git 讀不出、筆記讀不出、內部出錯)在 block 下也回 1,CI 那步一樣會紅——CI 永遠是冷快取,大專案較容易碰到 30 秒上限,碰到時把 `drift_check.old_sentence` 設成 warn(回頭重讀才是 CI 不受影響的那一道)。

## v1.2 — 2026-10-01

推送前多一道只提醒、不擋的檢查,推送前掛鉤跟著改,所以升版,讓還沒更新的專案被提示跑 `lumos update`:
- 新增「回頭重讀守檔筆記」:這次改到的程式檔的家、而且這次也被改過的筆記,推送前會被列出來,提醒派一位判定者看「哪幾行被這次改動弄得不成立了」。指令是 `lumos note-audit reread-prepare`(出項目檔)、`reread-record`(記紀錄到 `governance/reread-verdicts/`,要提交)、`reread-check`(推送前掛鉤與 CI 呼叫)。
- **只提醒、不擋**:任何情況都放行;不想要的專案在 `.lumos/config.json` 寫 `{"note_reread": {"gate": "off"}}`,單次不跑用 `LUMOS_SKIP_REREAD_CHECK=1`。
- 判定者:Claude 編排時是 sonnet(兩次實驗都用它量的);**Codex 編排時的準度沒量過**。
- 紀錄檔屬於簿記,提交它不會讓代碼審留痕失效——但還沒更新的協作者沒有這一項豁免,別人提交的紀錄夾在他的留痕與推送之間時會被判留痕過時;請各專案先 `lumos update`(逃生是 `lumos code-loop pass --note` 重記一次)。

## v1.1 — 2026-09-30

注入每個專案 CLAUDE.md 與 AGENTS.md 的紀律區塊改了一條,所以升版,讓還沒更新的專案被提示跑 `lumos update`:
- 紀律鐵則 4 改寫:「還沒有 X」這類會過期的句子,把那一句本身搬成獨立一行回頭條件(可以寫成綁事件的條件式),不再是「原句照留、旁邊另寫一行」。
- 提交前的筆記形狀擋多一種只提醒、不擋的輸出:新寫的「還沒有/尚未…」現況句沒寫成回頭條件行時印出來;不想看可以用 `.lumos/config.json` 的 `note_shape.negation` 設成 off。

v1.0 之後其他的變更沒有逐條整理進這份,見 git log 與知識圖譜。

## v1.0 — 2026-09-07

首次正式標記對外線。在此之前是未標記的持續開發,不回頭編造歷史。

這一版對外提供:
- 圖譜 CLI(`lumos`,python3 零依賴,66 個頂層指令)
- 提交/推送關卡(git hooks)與給 AI 的四個時點提示(Claude / Codex 兩家共用同一批腳本)
- 設計審與代碼審兩套審查迴圈,連同記帳、處置閘與判定凍結
- 一鍵安裝(`get.sh` / `get.ps1` / `lumos bootstrap`)
