severity: major

# 併發-sonnet 第 1 輪報告:守檔筆記對照改動_計劃

量測(clone 在 rr-r1-work-併發-sonnet/repo):2328 提交、5530 檔;41 篇 Systems 的 about_code 列了主程式 `scripts/lumos`;既有的 `drift check --diff HEAD~30..HEAD` 一次 5.5 秒;主程式 300 提交的 diff 約 2 MB(git 算 0.06 秒,慢的不是 diff 本身,是每篇要重做的載入與判定);`git log -S` 找上線點 0.04 秒。

## F1 reread-check 沒有時間預算,候選越多、推的 ref 越多越慢,而且要先建好每篇的 diff 才知道有沒有紀錄
severity: major
blocking: 是
引句:「對每篇算當下的項目指紋,看被推頂端提交的樹裡 `governance/reread-verdicts/` 有沒有檔名以這個指紋開頭的紀錄」
file: `scripts/lumos:26618`
1. 項目指紋含「給的 diff 全文雜湊」(〈做法〉2),所以 reread-check 對每一篇候選都得先照第 2 節整套組 diff(pathspec 含改名舊路徑、找同層沒被列的測試檔、超過 10 萬字元再重跑縮上下文、再各檔截斷),之後才能拿指紋去比檔名。只列目錄比前綴省的是讀紀錄檔,省不到這一大塊。
2. 主程式被 41 篇 Systems 列為 about_code。一次推送同時改到 `scripts/lumos` 和其中幾十篇家筆記(這個 repo 的日常),候選就是幾十篇,每篇一輪 git(diff、ls-tree 找測試、可能重跑 -U0)。`_lens_git` 每次呼叫上限 20 秒(`scripts/lumos:34795`),沒有整體預算,最壞是幾十篇乘好幾次乘 20 秒,掛鉤卡在推送前。
3. 既有的同類檢查有明確整體預算:`_DRIFT_BUDGET_SEC = 60`(`scripts/lumos:26618`),`_notes_status_flipped` 也有 `deadline` 參數,註解寫明是代碼審 r1 併發席實測首推逐篇讀 67 秒才加的。spec 說要抽共用函式、行為不變,那個函式預設 deadline=None,spec 沒說 reread-check 要不要傳;〈實務隱患〉也只算美元成本、沒算掛鉤時間,「reread-check 花的時間」只列在兩週後才量。
4. 掛鉤是逐 ref 跑(`scripts/hooks/pre-push:318` 那一圈),推 N 個分支就整套重跑 N 次(每次至少重建一次 `_nodehome_side`,drift check 這個量級是 5 秒)。
5. 「任何情況都回 0」只涵蓋錯誤,沒涵蓋「慢」。spec 要補:整體時間上限(例如比照 drift 的 60 秒)、超過時的處理(印「這次沒提醒:逾時」、記 `reread-skipped`、回 0)、一次推送裡各 ref 是否共用預算、候選超過多少篇就只算篇數不算指紋(先用「候選篇數超過上限」短路,不進組 diff)。

## F2 掛鉤「回傳值不看」會把 Ctrl-C 吞掉,中斷後照樣往下跑 8 分鐘全套
severity: major
blocking: 是
引句:「參數照它;回傳值不看。`LUMOS_SKIP_REREAD_CHECK=1` 單次不跑。」
file: `scripts/hooks/pre-push:50`
1. 掛鉤裡每一道有訊號處理的檢查都接 `pp_stop_if_signaled`(rc 大於等於 128 就整支停下,`scripts/hooks/pre-push:50-55`);drift 那段註解明寫「128 以上(被訊號殺掉,多半是 Ctrl-C)→ 整支掛鉤停下、不放行、不往下跑全套」,來源是代碼審 r1 併發回滾席。
2. spec 這段說回傳值不看。照字面寫成 `... || true` 或 `rc=$?` 不判斷,使用者嫌 reread-check 慢按 Ctrl-C,掛鉤只是少了一個提醒、繼續往下跑全套(約 8 分鐘)甚至放行推送,等於 Ctrl-C 失效,而 F1 又讓「慢」成為常見情況。
3. 需要改成:提醒版恆放行,但 rc 大於等於 128 照 `pp_stop_if_signaled` 停下(reread-check 自己保證的「恆回 0」不含被訊號殺掉)。CI 那邊 `|| true` 沒有這個問題(沒人按 Ctrl-C),但 CI 上被 OOM 或逾時殺掉也被吞掉,應在 spec 註明是刻意的。

## F3 兩個會談對同一份項目 prepare,項目指紋相同但檔頭的編排者與判定者不同,後寫的蓋掉先寫的
severity: minor
blocking: 否
引句:「項目指紋 = (筆記路徑、筆記終點內容雜湊、給的 diff 全文雜湊、範本版本)的 16 個十六進位字雜湊。」
file: `scripts/lumos:26326`
1. 指紋不含編排者、判定者模型。會談甲(claude,sonnet)與會談乙(codex)對同一次推送、同一篇筆記各自 prepare,得到同一個項目指紋、同一個檔名 `reread-<指紋>.md`;`_write_lf` 是原子寫入,不會半截,但後寫的檔頭(編排者、判定者模型)蓋掉先寫的。
2. 會談甲隨後 reread-record:報告的 `provider`/`model` 跟被蓋掉後的檔頭不同,被標 `provenance_ok: false` 並印警告。提醒版只是紀錄所以不出大事,但兩週抽樣時 `provenance_ok` 會有這種假的 false、也少了「哪個模型判的」的可靠來源。
3. 建議:檔名或檔頭帶編排者(或 record 以報告自己的 provider/model 為準、不跟檔頭比),spec 寫明同指紋重 prepare 的處理。

## 其餘節
- 〈範圍〉〈回退〉〈條款 S1 到 S12〉:已讀,無 finding(除 F1 需補時間預算的條款與測試)。
- 治理帳多寫入者:`_gate_event` 以 append 模式寫單行(`scripts/lumos:1227`),多會談並行不互蓋,已讀,無 finding。
- 紀錄檔並行:亂數檔名 + `_write_lf` 原子寫入,兩會談對同一篇 record 不互蓋,已讀,無 finding。
- 工作目錄 14 天清檔:只清 `*.md`、只在 `_note_audit_work_dir` 被呼叫時清,項目檔超過 14 天才被刪,與兩週量測窗口不衝突(抽樣靠紀錄檔);已讀,無 finding。
- CI 耗時:CI 有 45 分鐘上限、fetch-depth 0,reread-check 加在 drift check 後 `continue-on-error`,在 CI 上即使 F1 的慢也不會紅;已讀,無 finding。

最高等級:major;blocking 共 2 條
