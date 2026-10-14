severity: minor

我讀了文件修補、測試修補,也在 reread-fp 工作樹跑了相關測試(`-k reread_fp_timeout`、`reread_fp_hunk`、`reread_fp_chain`、`reread_fp_prefetch`,全綠)。`lumos lint` 對計劃和 `Systems/筆記內容審` 都是 0 問題。

- **「所在函式名」換成縮排鏈:** 計劃〈做法〉1、S8、S20 到 S22、`Systems/筆記內容審`、手冊 `06-代碼審與推送.md` 的第一層說法,全都換成縮排鏈了。`scripts/lumos` 和測試裡剩下的「函式名」字樣只是歷史說明或 `headers` 的預設行為,不算舊說法。
- **條款與綁定測試:** S8、S20 到 S30 綁的每支測試都在 `scripts/test_lumos.py` 裡。舊測試 `t_reread_fp_ignores_function_header` 已刪,沒有懸空綁定。
- **REVISIT 行格式:** 新增的 `REVISIT:2026-12-15 …` 是獨立一行,並且依「承認風險要附回頭條件」的規則,放在盲區那句之後。
- **逾時不擋與程式一致:**
  - `_note_reread_blocking` 把 `res["late"]` 排除在擋的判斷之外,整次掃描逾時仍是判不了、照擋。
  - 清單文字、帳上的 `late` 欄、事件種類 `reminded` 都跟文件說的一致。

兩條不一致,都是文件沒改乾淨,不影響程式行為:

severity: minor
blocking: 否 — 只是〈實作紀錄〉變異驗證那一句沒跟著改,不影響行為。
引句:「-- 變異驗證(每條改一處、跑那支測試、還原後再跑一次綠):S4 把 v1 的雜湊輸入多加一行」
問題:計劃的〈實作紀錄〉第 136 行寫「算函式名標頭(S8 ③紅)」,這是舊測試 `t_reread_fp_ignores_function_header` 的斷言。現在 S8 綁的測試是 `t_reread_fp_chain_stable_on_other_edits`,它的 ③ 已改成 S22 的代價斷言。這條修補把 S8 改寫了,卻沒更新這句。
具體失敗情境:之後有人照這句重做「指紋改回算 git 段落標頭」的變異驗證,會預期 ③ 紅。實際上標頭一變,②(主線在上方插頂格賦值)就先紅,③ 是「指紋會變」,本來就會過。依這句操作的人會誤判這道守衛沒守住。
佐證:``docs/lumos-toolchain-knowledge/Projects/回頭重讀指紋不因主線前進失效_計劃.md:136``

severity: minor
blocking: 否 — 只是〈做法〉5 的「不會漏判」跟 S27 的新行為有出入,實際行為由程式和 S27 說清楚了。
引句:「退回只會讓已對照的被多列,不會漏判。」
問題:〈做法〉5 把「git 呼叫逾時」跟其他退回 `v1` 的情形並列,保證只會多列、不漏判。但這輪新增的 S27 已讓逾時的那幾篇「照實列出但不擋」。block 加 `--gate` 時,它們在這個閘上沒有擋下,等於放過去。〈做法〉5 沒回頭修,跟 S27 互相打架。其餘退回原因(太大、型別變更、查大小失敗)仍照擋,所以逾時這一項和其他幾項的效果其實不同。
具體失敗情境:新手冊或下一個 session 的 AI 只讀〈做法〉5,會以為逾時退回只多列、仍會擋。實際上大改動讓指紋那一步逾時時,那幾篇不會擋下。
佐證:``docs/lumos-toolchain-knowledge/Projects/回頭重讀指紋不因主線前進失效_計劃.md:60``;程式在 ``scripts/lumos:37673``(`_note_reread_blocking`)

最高等級 minor,blocking 0 條。
