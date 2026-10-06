severity: major

### F1 跑滿未過的判法①幾乎永遠不觸發,而且沒排除「事後過閘」
severity: major
blocking: 是 — 觸發條件的定義跟 d4 自相矛盾,「跑滿未過」的認定、doctor 清單和 `retro-stats` 的分母都會錯
- spec 段落:〈名詞〉跑滿未過、d4
- 問題一:判法①只看治理帳有沒有 `cap-reached` 事件,沒看同一編號後來有沒有 `converged`。d4 明寫「剛好在最後一輪過閘的不算」,現有統計程式碼卻已經知道要排除。
  - 情境:`loop next` 在第 3 輪判到 cap(閘當下沒過),寫下 `cap-reached`。編排者隨後補完處置,同一輪過閘、寫下 `converged`。
  - 結果:這個迴圈依①算跑滿未過,doctor 會列它,`retro-stats` 會把它算進分母。這正是 d4 要排除的那一類。
  - 引句:「治理帳有這個編號的 `cap-reached` 事件(`loop next` 在到上限、處置閘沒過時寫的那筆)」
  - file: `scripts/lumos:8145`:現有 gov 統計用 `"cap-reached" in k and "converged" not in k and "rewrite" not in k` 排除。
  - file: `scripts/lumos:13248`:`cap-reached` 只在 `rounds_count >= cap` 且閘沒過時才寫。
- 問題二:判法①在現實帳上幾乎是死路。
  - 我統計了 `docs/.governance-log.jsonl` 的 `design-loop` 事件:`cap-reached` 全帳 3 筆,全在 2026-08;九月、十月是 0 筆,`converged` 則有 448 筆。
  - 同期 `docs/.canary-log.jsonl` 裡非 light、輪數超過 3 的迴圈有 19 個(例如 `code-記憶過期清掃` 12 輪、`code-存量漂移防線甲` 6 輪),剛好 3 輪的有 95 個。
  - 結果:實際的觸發全靠判法②(輪數超過上限)。
  - ⚠ 無法確認原因:可能是 code-loop 沒呼叫 `loop next`,也可能是到上限就直接過閘。
  - 後果:RETIRE-IF ③「三個月內零次跑滿未過」的判讀基礎要用②重新量。
  - 後果:spec 沒寫①的存在理由,三個月後的人會以為①是主路徑,去查一條不存在的事件流。
- 建議:改成「輪數超過上限,或有 `cap-reached` 且無後續 `converged`」,並註明①實際上幾乎無觸發。

### F2 閘、doctor、`retro-stats` 對「有回顧」的定義不同
severity: minor
blocking: 否 — 屬提醒層與閘層的口徑漂移,不影響閘本身的正確性
- spec 段落:〈名詞〉合格回顧、〈四〉、S10、S11
- 問題:閘要求「檔案通過 `--check`、指紋一致、`rounds` 與帳完全一致」,doctor 與 `retro-stats` 卻只看「帳上有沒有 `cap-retro` / `cap-retro-skipped` 事件」。
- 情境:第 3 輪後記了回顧,第 4 輪記進帳,回顧的 `rounds` 變成過期。閘第八步 ✗。
- 結果:doctor 不列它,`retro-stats` 還把它算進「記了回顧」。三個月後的人讀 `retro-stats` 會以為覆蓋率是 100%,實際上閘正在擋。
- 引句:「上線之後跑滿未過、但治理帳沒有 `cap-retro` 也沒有 `cap-retro-skipped` 事件的迴圈,逐個列出並附 `--template` 指令」
- 建議:兩處共用同一個「合格回顧」判定函式,或至少 `retro-stats` 另列「過期」。

### F3 每多一輪就要重寫一次回顧,跳過卻是一次永久有效
severity: minor
blocking: 否 — 屬誘因設計不對稱,有跳過出口,沒有硬失敗
- spec 段落:〈一〉`rounds`、〈三〉1、`cap-retro-skipped` 定義
- 問題:`rounds` 必須跟帳完全一致,第 4 輪一進帳舊回顧就失效;人裁加到第 5、6 輪,每次記帳前都要重寫並重新 `--record`。起草還得重新派乾淨代理(d2)。`cap-retro-skipped` 事件沒有綁輪次或指紋,記一筆後之後所有輪次都不再擋。
- 情境:`code-記憶過期清掃` 跑了 12 輪,從第 4 輪起每一輪都要重派代理。一次 `--skip --note`(10 字)就能全部繞過。
- 結果:最省事的路徑是跳過,RETIRE-IF ② 容易自己觸發。
- 引句:「跑滿後又破例多開一輪,舊回顧就不再合格,要更新後重新記(見〈二〉)」
- 另:這句指向的「見〈二〉」沒有講怎麼更新,擋點在〈三〉1,是懸空引用。
- 建議:明講跳過是否也要綁輪次,並補上「第 N 輪之後的更新流程」。

### F4 沒有現成的「條號辨識共用函式」可以抽
severity: minor
blocking: 否 — 屬 spec 對現況的假設不符,實作時要新寫
- spec 段落:PRIOR-ART、〈一〉`evidence`、S13
- 問題:spec 說從 `_report_findings_missing_severity` 抽出條號辨識成共用函式,並用它在報告裡「找得到 `F<n>` 那一段」。該函式只回傳「發現段數量與缺漏」,沒有取出號碼。
- 它的 docstring 明寫「只數數量、不分析標題結構」,理由是逐段找範圍的做法每輪都被標題寫法打穿。標題含「已驗過/沒問題/已看,無」的段也被排除。
- 情境:evidence 寫 `#F3`,而報告裡 F3 的標題帶「已讀,無 finding」,「找得到」會判不存在;或需要重新引入「按 F<n> 找段」的邏輯,正是那條 docstring 說會被打穿的形狀。
- 引句:「報告條號辨識抽出 `_report_findings_missing_severity` 裡既有那條規則成共用函式」
- file: `scripts/lumos:8684`
- 建議:S13 只釘計數行為;`#F<n>` 存在性要另寫並另立測試(不要改既有函式),且排除字詞要有定論。

### F5 凍結的第一趟處置閘沒有 `spec_sha_override`,第八步不會印「—」
severity: minor
blocking: 否 — 只造成凍結輸出的雜訊與一次多餘的讀檔
- spec 段落:〈三〉2、S4
- 問題:spec 說凍結的第二趟與回放印「—」不重判,但凍結第一趟用 `readonly=True`、不帶 `spec_sha_override`。若第八步用「`spec_sha_override is not None` 才略過」(照第六步「落點」),第一趟會真的讀回顧檔並印 ✗ 與 `DISPOSAL GATE FAIL`。
- 情境:對一個超過上限、回顧已過期的迴圈跑 `loop replay --freeze`,輸出先印一次 FAIL(第一趟),再印一次含「—」的第二趟,操作者以為凍結失敗。
- 引句:「凍結的第二趟與回放(帶 `spec_sha_override`)印 — 不重判,所以凍結與回放的行為與既有一致」
- file: `scripts/lumos:1067-1073`(第一趟無 override)、`scripts/lumos:22650`(落點步驟只認 override)
- 建議:第八步在 `readonly=True` 時也略過,不要只靠 override。

### F6 為 scratch 迴圈建卷證資料夾,會改變既有的「無資料夾」判斷
severity: minor
blocking: 否 — 只在無卷證資料夾的 scratch 迴圈出現
- spec 段落:〈一〉位置
- 問題:spec 說「沒有這個資料夾就建」。既有程式用「資料夾存在與否」判斷是不是 scratch 迴圈(例如自主迴圈在 /tmp 工作區)。
- 情境:自主迭代迴圈沒有卷證資料夾,超過上限後為了寫 `cap-retro.json` 建出資料夾。處置閘從此印「⚠ intake 缺」(`_intake_dir_status` 由 no-dir 變 missing)。
- 同時 doctor 的「前掃宣告行滾動窗」(只排除 `code` 開頭的目錄)會把這個只有回顧檔的目錄算成一個迴圈,污染窗口。
- 另:這類迴圈的席報告常不在 repo 內,`evidence` 要求 repo 相對的 `report_path`,等於寫不出合格回顧,只能跳過。無人值守的自主迴圈在 `canary record` 被擋(回 2)時也沒有人去下 `--skip`。
- 引句:「位置:`governance/review-reports/<編號>/cap-retro.json`(沒有這個資料夾就建」
- file: `scripts/lumos:8590-8600`
- file: `scripts/lumos:2222-2240`
- 建議:scratch 迴圈(無卷證資料夾)明確列為不適用,或回顧檔另存位置。

### F7 〈做法〉說要「抽出」`_cap_hint_scope`,但它早已是獨立函式
severity: minor
blocking: 否 — 屬敘述與現況不符,不影響行為
- spec 段落:PRIOR-ART、〈適用範圍〉
- 問題:`_cap_hint_scope` 已存在並被 `_cap_hint` 呼叫。真正沒抽出的是 `_cap_hint` 開頭過濾 `kind != "spec-gate"`,以及 `len(groups) >= cap` 的輪數算法。`loop next` 用的 `rounds_count` 是另一套(`len({r["round"]…})`),跟 `_cap_hint` 的 `_disposal_round_groups` 並列。
- 情境:實作者照字面理解會重複抽出,或漏掉 spec-gate 過濾,讓 S12「與原本相同」測不到。
- 引句:「跑滿判定抽出 `_cap_hint_scope` 與 `_cap_hint` 已有的輪數、分級、上限算法成共用函式(三方共用,不另寫)」
- file: `scripts/lumos:8828-8862`、`scripts/lumos:12943`
- 建議:明列共用函式要包含「濾掉 spec-gate、數輪數、至上限」這三件事,並說清楚 `loop next` 與 `_cap_hint` 兩套輪數的取捨。

已讀,無 finding 的節:一句話、為什麼要做、回退、實務隱患(併發/效能/已排除各條)、誠實界線、審計修正紀錄。

總結:最嚴重 major,blocking 1 條
