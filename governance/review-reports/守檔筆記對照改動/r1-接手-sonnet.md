severity: major

# 接手鏡頭報告(接手-sonnet)

## F1 skill 推送前那一節只有一句話,沒有落點、沒有條款、沒講跟筆記內容審那節怎麼分工
severity: major
blocking: 是
引句:「skill 推送前那一節補操作順序」
file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:32`
1. 〈範圍〉只有這一句提到 skill;〈做法〉、〈條款〉、〈回退〉都沒有對應段落與 [test:],lands_in 也只列 Systems/筆記內容審。接手的人不知道改哪支檔(06 的現有那節是「筆記內容審」,第 36 行寫著「目前還沒接進推送前掛鉤與 CI」;reference.md、INDEX.md 也提到 note-audit),不知道新增獨立小節還是併進去,也不知道「操作順序」要寫什麼。
2. 順序關鍵點都沒寫:reread-check 提醒 → prepare → 派 sonnet(Agent model:sonnet 或 codex 指令)→ 報告存檔 → record → git add governance/reread-verdicts && commit → 再推;跟筆記內容審(先審、再代碼審留痕、再推)及存量漂移(drift ack)三者誰先誰後、能否併發,spec 沒說。reread-verdicts 雖是簿記,不影響留痕,但 spec 沒把這句寫出來。
3. 沒有條款綁 skill 文字,實作提交可以完全漏改而所有 [test:] 照綠。另外 pre-push 掛鉤(scripts/hooks/pre-push)、.github/workflows/ci.yml 的家與 Systems/存量漂移守衛的文字要不要改,也沒講。

## F2 兩週量準度要用的資料,治理帳事件沒帶,REVISIT 那天算不出
severity: major
blocking: 是
引句:「治理帳記 `reread-reminded`(帶沒對照的篇數)或 `reread-skipped`(帶原因)。」
file: `scripts/lumos:6943`
1. 〈做法〉5 要算「有候選的推送占比」「reread-check 提醒後真的去對照的占比」,〈做法〉4 要看「修完被重列占提醒的一半以上」。但 reread-reminded 只帶篇數,沒有筆記路徑與指紋,無法跟 reread-recorded(帶指紋)對上,算不出提醒後有沒有去對照,也分不出「修完被重列」。
2. 候選是空、或候選全部已有紀錄時,沒有指定任何事件(只說印一行、rc0),所以分母(推送次數、有候選占比)在帳上沒有;只能靠 git 歷史另推,而且 CI 那邊的事件不會進本機治理帳。
3. 兩週後接手者照〈做法〉5 動手,第一步就卡住。要嘛事件補欄位(路徑、指紋、推送頂端 sha、來源是掛鉤或 CI),要嘛把這幾個量從 REVISIT 拿掉。

## F3 S10 不是自足的:腳本要的 rtb clone 與 prompt 沒進版控,也沒說怎麼把正式範本換進去
severity: minor
blocking: 否
引句:「照 governance/eval/home-check/validate 的腳本換成正式範本重跑,數字寫進本計劃」
file: `governance/eval/home-check/report-2026-09-30.md:48`
1. 報告寫明 clone(validate/rtb、tune/rtb)與 7.8 MB prompt 全文沒收進來,腳本(vcommon.py 的 VAL + "/rtb")要求它們在原位;新會談要先自己 git clone --shared rtb、重做 selection(selection.json 有 15 個提交,可重用,但 spec 沒講)。
2. 腳本是逐提交跑、import 的是舊 V3 模組(build_prompt),沒有「換成 note-audit-reread.md 範本」的開關;spec 沒指是改腳本、還是走 reread-prepare 對單提交範圍。約 12 美元(報告成本行),spec 也沒交代誰付、跑幾次。
3. 「真漂移少於 14 行」在判定不穩(實驗一 29 對 27)下單次重跑就決定接不接線,沒寫落在 13–15 行時是否重跑。
4. 順序也含糊:S8 要求掛鉤與 CI 接線的測試綠,S10 又禁止在補數字前接線;實作提交怎麼分(先三子指令、再 S10、再接線,還是同一提交)沒寫,而 CLAUDE.md 要求一個功能一個提交。

## F4 RETIRE-IF 的 8 週條件與成本條件沒有對應的 REVISIT,也沒有資料可量
severity: minor
blocking: 否
引句:「上線後連續 8 週,所有提醒點出的行裡被作者真的改掉的是 0 行(提醒沒人用)」
file: `governance/review-reports/守檔筆記對照改動/r1-snapshot.md:29`
1. 唯一的 REVISIT 是 2026-10-21(兩週);8 週那天(約 2026-11-25)沒有任何獨立一行 REVISIT,doctor 到期不會唸,CLAUDE.md 鐵則 4 要求的接電缺一半。
2. 「判定成本中位數超過 1 美元」而〈做法〉5 自承「報告沒有成本欄時用項目檔大小估」,判準是列價、量法是估算,接手者無法客觀判撤;且判定跑在編排者會談裡,工具帳上根本沒有成本。

## F5 掛鉤「回傳值不看」會吞掉 Ctrl-C,跟鄰居那段的處理不一致
severity: minor
blocking: 否
引句:「在存量漂移檢查那一段(逐 ref、帶 `--push-remote`、`--pushed-ref` 的那段)之後加一段,參數照它;回傳值不看。」
file: `scripts/hooks/pre-push:479`
1. 鄰居那段用 pp_stop_if_signaled,rc>=128(被訊號殺)整支掛鉤停下、不往下跑 8 分鐘全套測試。新段「參數照它、回傳值不看」,接手者字面照做時,使用者在 reread-check 期間按 Ctrl-C,掛鉤會繼續往下跑全套測試。
2. 建議寫成:只保留 pp_stop_if_signaled,其餘 rc 一律放行。

## F6 提醒後的操作終點沒講:修完筆記就會再被提醒,除非重付一次判定
severity: minor
blocking: 否
引句:「對照過之後又改了那篇筆記(照判定者的話修掉舊句),指紋就變、會再列一次。這是刻意的」
file: `governance/review-reports/守檔筆記對照改動/r1-snapshot.md:69`
1. 接手者收到 record 印的「改掉那幾行、或確認是誤判就不動」後,若改了筆記,下次推送(甚至同一次 amend 後)reread-check 又列同一篇,唯一出口是再跑 prepare→派席→record→commit(約 0.2 美元)或 LUMOS_SKIP_REREAD_CHECK=1。提示文字沒告訴使用者這一點,也沒說「只提醒版,忽略即可推送」。
2. 建議 reread-check 輸出加一行:這只是提醒、不擋,忽略照推。

## F7 「上線公告」與判定者模型別名沒有定義
severity: minor
blocking: 否
引句:「★準度沒量過,上線公告要寫明★」
file: `scripts/lumos:25780`
1. 「上線公告」沒說由誰、發在哪(實作紀錄?圖譜節點?rtb 會談訊息?)。另 rtb 要交資料(〈做法〉5)也要先 lumos update 拿到新掛鉤與範本,spec 沒有「通知 rtb 更新」這一步,兩週後 rtb 可能一份紀錄都沒有。
2. 判定者模型寫「`sonnet`」是別名,會隨環境漂移(專案記憶裡有記錄過別名解析到 5.5);項目指紋只含範本版本、不含模型,S4 也只釘範本雜湊。「換模型要重跑實驗」沒有任何機械守衛能偵測到換了。

已讀,無 finding:〈PRIOR-ART〉、〈回退〉、〈實務隱患〉、〈附錄〉、〈誠實界線〉(自洽)。

最高等級:major;blocking 共 2 條
