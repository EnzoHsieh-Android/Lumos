severity: major

## b31 放行(lint-waive)抽中的存活行會讓種子換掉,回報上限的「穩定回報」破功
severity: major
blocking: 是 — 破壞計劃〈回報上限〉與 S16 宣稱的合約:放行一行就會讓已處置的抽中集合重洗、冒出沒被要求過的新擋下行。

走到哪:`_choice_push_judge` 迴圈裡,放行過的鍵先 `continue`,所以沒進 `ever`。`ever` 是 `_choice_cap_pick` 的種子集合,放行就把該鍵從種子拿掉,整批重洗。計劃第 98 行寫明「曾經存活過的行」是「帳上同鍵有任一筆 survived」,「已處置的仍算處置」,「新的存活行出現時集合變了才重抽」。放行檔裡的行帳上仍有 survived,不該離開種子集合。

輸入:兩支檔共 20 行,帳上全是 survived,cap=14。第一次抽中 14 行。人放行其中 1 行(最自然的處置動作)再推。

重現(臨時目錄 `/tmp/lumos-seat-work/code-改動選擇點/邊界p3-sonnet/rp.py`,以 `importlib` 直接載入 repo 的 `scripts/lumos`,沒改 repo):
```
python3.14 rp.py
14
waived one picked; still-required old picks: 10 of 13 ; newly required not previously picked: 4
```
預期:放行後抽中集合是原本的 13 行(不變),沒有新行被要求。實際:原本抽中的 3 行掉出集合,另外 4 行原本沒被要求的存活行變成要擋。使用者每放行一行,就可能冒出新的擋下行。現有 S16 測試只用 killed 處置、不用放行,所以測試抓不到這條。

引句:「        if any(e.get("verdict") == "survived" for e in evs):」
file: `scripts/lumos:78205`(`_choice_push_judge` 內,位置約在此;以 `grep -n "def _choice_push_judge" scripts/lumos` 為準)
file: `docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md:98`
修法方向:把「放行過的鍵」也加進 `ever`(`ever.add` 移到 `if key in waived` 之前),但放行過的行不進 `survivors`。

## b32 回報上限提醒印的「曾經存活的 N 行」其實是抽中數,不是存活數
severity: minor
blocking: 否 — 只是訊息數字錯,不影響擋與不擋。

輸入:曾經存活 20 行、cap=14。`_choice_push_judge` 回傳的第三個值是 `len(picked)`(=14),`_choice_push_verdict` 把它印成「曾經存活的 14 行之外這次不要求」。實際曾經存活的是 20 行,同一則訊息裡的 `另有 6 行存活沒抽中` 與這個 14 對不上。

引句:「f"曾經存活的 {n_ever} 行之外這次不要求:")」
file: `scripts/lumos`(`_choice_push_verdict` 內 `n_ever` 的使用處)

## 圖譜鏡頭
這次沒附固定席節點(派工詞寫「鏡頭計算超時」),所以我只判 diff 本身能對上的部分,沒有逐條判固定席。

## 其餘逐項檢查後沒有 finding
- **判定順序與生效日**:`since` 晚於今天就整圈不跑;`_choice_requirement` 先判平台、改到的 .kt、碰到的計劃,才掃描。生效日的比較都是本機日期,只有 pre-push 掛鉤會呼叫,所以台北凌晨一點不會落到 UTC 前一天的問題。
- **舊新版本互讀**:掛鉤用 `dest="sg_push_remote"`/`dest="sg_pushed_ref"` 探針,舊 lumos 不帶新參數;新 lumos 配舊掛鉤時 `push=None`,走推送範圍本身。
- **舊 `killing_test`(沒有平台前綴)**:預設平台的舊紀錄靠 `_choice_bound_names` 多收的裸名還算有效;非預設平台的舊紀錄會變「過期」。編排者 2026-11-14 已裁,不另報。
- **讀被推版本**:帳走 `_gov_rows_at`,放行檔走 `_residual_blob_at` 再 `_lint_waivers_parse`,時限用完記 unverified,帳不在或讀不出擋。這部分與 S19、S20 一致。
- **blocked 去重**:`_choice_push_event` 以 `head_sha` 加 reason 名單去重,`_gate_event_build` 確實寫入 `head_sha`。
- **gov --stats**:`secs` 在 `_GOV_FIELD_TYPES` 已收 `(int, float, None)`,不會被型別檢查整筆丟掉;舊放行事件缺 `row`/`decl` 有 `isinstance` 保護。

最嚴重:major;blocking 共 1 條
