severity: major

整份 diff 逐 hunk 讀完,新測試與相關子集全綠(contract_backing、contract_evidence、kill_log、guard_kill_add_covers、guard_kill 67、gov_ 99、dispositions 100、codeloop_record)。1 條 major、1 條 minor。

逐項沒有 finding:guard kill 七態與 rc 沒動;--json 只多四欄、補換行靜默;kill-add 判重欄位同舊寫法,非 dict 配方改成略過;detail=True 不影響既有呼叫點(git diff 出錯仍回 False,只是理由句變了);gov 改容錯讀取,cmd_gov 拿掉 import json 沒問題(模組層 `scripts/lumos:32151`),新欄位不影響 kill mapper 去重,順帶修掉 splitlines 把 U+2028 切壞;`_backing_warn` 只進 warnings、自己吞例外,warnings 在 `scripts/lumos:38168` 印出;gate=off 與 high-only 非高風險提早 return;carry 的假 backing 一律先 pop;fixture 無互相污染、monkeypatch 都在 finally 還原。

**N1 時間炸彈測試:t_gov_stats_contract_backing 從 2026-12-30 起必紅**
severity: major
blocking: 是——pre-push 要跑全套,這支一紅就擋住所有推送。
測試把事件 ts 寫死成 2026-10-01,卻用預設窗口 gov --stats(--since 預設 90,`scripts/lumos:38945`);cmd_gov 用 today-90 天過濾(`scripts/lumos:7329`),2026-12-30 後事件落出窗口,check ② 會紅;姊妹測試 t_gov_stats_dispositions 用 --since 9999 避開。重現(用過期事件模擬同一機制):governance-log 放一筆 ts 2026-06-01 的 dispositions 事件,gov --stats --since 90 → 窗口內無資料。修法:改成 run(v, "gov", "--since", "9999", "--stats") 或 ts 用今天。
引句:「    r = run(v, "gov", "--stats")」
file: `scripts/lumos:7329`
file: `scripts/lumos:38945`

**N2 gov --stats 背書分母的括號拆不平**
severity: minor
blocking: 否——只是顯示誤導。
bk-den 包含 n/a 的人工 na/todo/tension,括號只列有背書與做到了但沒有背書;fixture 輸出 3 ≠ 1+1;RETIRE-IF ① 要量繞開比例,讀的人得自己減。建議括號補其餘筆數或多印 bk-na。
引句:「            _bkt = (f"、背書分母 {_b['bk-den']}(有背書 {_b['bk-strong']}、做到了但沒有背書 {_b['bk-none']})" if _b["bk-den"] else "")」
file: `scripts/lumos:7090`

圖譜鏡頭:guard-kill、reversibility-governance-ledger、棧別提問表態閘 皆不影響既有合約;表態閘舊 KEY 行的鏡頭措辭是歷史紀錄,屬線索不構成矛盾。

最高嚴重度:major,blocking 1 條(N1)。
