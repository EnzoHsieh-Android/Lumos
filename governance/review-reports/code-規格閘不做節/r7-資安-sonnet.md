severity: major

資安席第七輪報告。修補還是能繞,我打穿三條路,每條都用實際推送前檢查(`spec-gate --push-check`)跑過,都是先擋(rc1),繞過後放行(rc0)。實驗用 git clone 造的暫存 repo,在副本的 `scripts/test_lumos.py` 加臨時測試跑,跑完已刪。原 worktree 沒動。

「只改一個字讓行雜湊不同」這類改字本身,依規則設計就算重新來過。真正的洞是下面三個:major 會因為旁邊的事消失,卻不用改被點名的那一行。

severity: major
blocking: 是 — 不改被 major 點名的那一行,只多加一行不做清單裡的危險詞,major 就脫鉤,再補一筆乾淨審即放行,ratchet 形同虛設
引句:「r = _nogo_major_lookup(env, ctx, _nogo_rows_sha(nogo_skipped))」
攻擊步驟:
1. 計劃 `## 不做` 節有「- 不做退款」「- 不做匯出報表」。記一筆輕量審 major,綁凍結快照。推送前檢查 rc1,訊息是「帳上有一筆輕量審抓到 major…ratchet」。
2. 在同一節多加一行「- 不做扣款」。這行本身也是不做,「退款」那行一字未改。
3. 重跑規格閘,再記一筆乾淨的輕量審(`通才-sonnet`),綁新快照。
4. 推送前檢查 rc0,輸出「甲_計劃:留痕裡的 1 支測試全綠」。
原因:`_nogo_major_carried` 用「被略過行整份」的 `_nogo_rows_sha` 去比。整份比對是全有全無,加一行誘餌就整份不同。被 major 點名的那一行其實完全沒變。
實驗證據:臨時測試 `t_zz_atk1_decoy_row` 印出 `BASE rc 1` 和 `DECOY rc 0`。
file: `scripts/lumos:9276`(`_nogo_major_lookup`,`fp == fp_now` 在 9298)
建議:major 的比對改成逐行。這筆 major 看過的每個 [類, 詞, 行雜湊] 只要有任何一行還在現在的被略過行裡就擋。

severity: major
blocking: 是 — 把 major 記在沒有規格閘留痕的別名編號下並刪掉快照,或記帳時不帶快照,major 就「不進索引」,整條規則對它失效
引句:「兩樣都沒有就比不了、不進索引」
攻擊步驟:
1. 席報告給 major。編排者用別的編號記帳:`canary record none --loop 甲別名 --severity major --findings 1 --spec <計劃>`,不帶 `--snapshot`。(實驗另跑一次:帶快照記帳,之後把快照檔刪掉。)
2. 這個別名編號底下沒有 spec-gate 留痕,所以 `gate_sha` 是 None。快照缺或沒綁,`fp` 也是 None,major 在 `_nogo_major_lookup` 被略過,不進索引。
3. 在正式編號 `甲` 記一筆乾淨的輕量審。推送前檢查 rc0。
實驗證據:`t_zz_atk3_loopalias` 和 `t_zz_atk4_nosnap` 都是 rc0。後者的記帳指令本身也成功(rc0),`canary record` 沒有要求輕量審一定要帶快照。
原因:fail-open。規則的前提是 major 一定有快照或同編號的留痕,但編號與是否帶快照都是編排者自己填的。
file: `scripts/lumos:9296`(`if fp is not None:`),`scripts/lumos:9201` 附近的 gate_sha 收集
建議:算不出指紋的 major,在這份計劃有被略過的行時一律當成擋(fail-closed),或記帳時強制 `--snapshot`、`--spec`。

severity: major
blocking: 是 — 用合法的 `--round` 旗標把輕量審的 major 記成完整設計審紀錄,讀帳核心整筆丟掉,窗口和 ratchet 都看不到
引句:「or (spec_gate and "round" in d)」
攻擊步驟:
1. 席報告給 major。編排者記帳時加 `--round r1 --tier light`,綁快照與 `--spec`。記帳 rc0。
2. 再記一筆乾淨的輕量審。推送前檢查 rc0。
實驗證據:`t_zz_atk2_round` 印出 `ROUND rc 0`。既有測試 `t_prepush_nogo_light_full_review_major_ignored` 只守「真的完整設計審的 major 不該擋」,沒有守這個混用。
原因:「帶 round 就不算輕量審」是靠編排者自填欄位區分,沒有別的依據(例如 `--tier light` 與 round 互斥)。
file: `scripts/lumos:13756`(`_canary_ledger_scan`)
建議:紀錄帶 `--tier light` 或沒有完整設計審的派工單來源時,就算有 round 也進輕量審判斷。或讓 canary record 拒絕同時帶 `--round` 與 `--tier light`。

沒找到可用的洞:
- 行雜湊只留字母數字,換標點、空白、反引號、粗體、NFD 都不脫鉤,規格閘留痕的 `nogo_rows_sha` 也一致。
- 把一行拆兩行或兩行併一行、換同義詞或加一個字,都會使指紋不同。依設計這算重新來過,要補一筆乾淨審,沒有額外的洞。
- 「排除萬難…」這類開頭是否定片語的藉口句會被略過,但略過只會多要一筆輕量審,不是漏審。真正的防線是上面三條講的 ratchet 和帳。

最高等級 major,blocking 3 條。
