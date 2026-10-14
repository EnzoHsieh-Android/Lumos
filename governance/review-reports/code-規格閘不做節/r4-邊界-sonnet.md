severity: minor

整體判斷:輕量審的帳列邏輯(同秒、壞行、截斷、`needs_light_review` 舊留痕沒有這欄)我沒找到會放行未審計劃的洞。找到的問題集中在輸出指令、錯誤處理、舊紀錄污染和測試守備。

已讀,無 finding 的部分:
- 同一秒:改比帳的 append 序,不比 ts,所以同秒沒有問題。
- 帳裡有壞行、帳被截斷:壞行或截斷的行會被跳過,結果是「沒審」而擋下,方向安全。
- 舊留痕沒有 `needs_light_review` 欄:推送前每次都用 `_door_judge` 重算,不信那欄,所以沒有問題。
- 迴圈編號含特殊字元與 NFD:帳裡的 loop 與要比對的編號都做了 NFC,比對沒問題。
- 粗體與括號剝除:我跑了 `**不做退款`、巢狀括號、全形括號、`(實作扣款)`、`不做退款 ** 扣款`。判成「略過」的那些行,危險詞仍會記進 `nogo_skipped`,照樣觸發輕量審。這個方向安全。

severity: minor
blocking: 否 — 只影響人照著複製指令時的可用性,推送前的擋關本身不受影響
引句:「return f"lumos loop next {_loop_id_for_plan(rel)} --tier light --orchestrator claude --spec {spec}"」
問題:印給人的 `lumos loop next …` 指令,迴圈編號與 `--spec` 路徑都沒有 shell 引號。
失敗情境:
- 我實跑 `_nogo_light_cmd`。計劃檔名叫「訂單 下單_計劃」時,印出 `lumos loop next 訂單 下單 --tier light … --spec docs/k/Projects/訂單 下單_計劃.md`,照貼會拆成多個參數。
- 檔名含 `'` 或 `;` 時,印出的指令同樣不安全。
- 指令會同時出現在規格閘輸出、推送前擋下訊息、治理事件三處。
- 改用 `shlex.quote` 即可。
佐證:``scripts/lumos: `_nogo_light_cmd` ``(改動後約第 8265 行)。

severity: minor
blocking: 否 — 只有手改過的帳或舊資料才會觸發,觸發時是整個推送檢查崩潰
引句:「if f is None or (sev == "clean" and f != 0) or (sev == "minor" and f < 1):」
問題:`_light_gate_fails` 是從 `loop status --light` 搬出來並共用的。`findings` 不是整數時,它會拋 TypeError。
失敗情境:
- 以前只有 `loop status --light` 會崩潰。現在推送前每份「不做清單略過危險詞」的計劃都經過它。
- 帳上最後一筆審查的 `findings` 若是字串,例如手改帳寫成 "2",我實測 `_light_gate_fails` 直接拋 `TypeError: '<' not supported between 'str' and 'int'`。
- `_spec_gate_push_light` 沒有 try/except 包住它,整個 `--push-check` 會帶 traceback 崩掉,連其他計劃的檢查也一起中斷。
- 這是擋住推送,不是漏放。但共用之後,這個崩潰面變大了。
- 建議在共用函式裡先判斷 `findings` 的型別。

severity: minor
blocking: 否 — 要先有同編號的舊審查紀錄才會觸發,而且是多擋,不是漏放
引句:「if any("round" in r for r in rounds):」
問題:`rounds` 收的是這個編號在整本帳的所有紀錄,包含最後一筆規格閘留痕「之前」的。同一個編號早先走過完整多席設計審的計劃,留下的紀錄有輪次欄也可能有 major。
失敗情境:
- 計劃早先因為有訊號走過完整設計審(紀錄有 `round`,可能有 major)。
- 作者後來把訊號拿掉,計劃變成風險低,不做清單略過了危險詞。
- 之後不論再記幾筆新的輕量審,都會被「有多人審格式的紀錄,light 判不了」或 ratchet 永久擋住。
- 訊息會叫人去寫 `plan_risk: high`,這與使用者實際已降級的意圖相反。
- 只該看最後一筆規格閘留痕之後的紀錄。
- 另一條安全方向的說明:`after` 的重算只管「有沒有晚於留痕」,但 ratchet 與 round 判斷看全部紀錄,兩者範圍不一致。

severity: minor
blocking: 否 — 屬測試守備不足,不是執行期漏洞
引句:「if any("round" in r for r in rounds):」
問題:我在副本上逐條改壞後清 `__pycache__` 重跑 `t_prepush_nogo_light_review_required`,三種改壞全都沒有變紅。
失敗情境:
- 拿掉 `nfc(...)` 比對:10 項全綠。測試只用 loop "甲",沒有 NFD 與 NFC 不一致的案例,所以 NFC 規範化的保護沒有測試守著。
- 拿掉 `round` 檢查:10 項全綠,這條守衛完全沒有測試。
- 拿掉 `gate_at != rec.get("token")` 那一段:10 項全綠。這段在現行流程下是死碼,因為 `rec` 本來就是同一份帳裡最後一筆。要嘛補測試,要嘛刪掉。
- 有變紅的改壞:不重置 `after`(⑦ 紅)、`cur_sha_override` 改 None(⑤ 紅)、拿掉 ratchet(⑨ 紅)。
- 另外 `_NGL_SMUGGLE` 的測試只在「前置至少一句判成風險低」時才跑得到推送那一頭,屬弱前置。
- 測試也沒有含空白或引號的計劃名,所以上面第一條 finding 沒有測試擋著。

severity: minor
blocking: 否 — 在計劃的已接受取捨範圍內,只是其中一個具體缺口值得知道
引句:「verdict, fails = _light_gate_fails(rounds, env.vault / prel, cur_sha_override=(rounds[-1].get("result_sha256") if rounds else None))」
問題:`cur_sha_override` 取該筆審查自己的 `result_sha256`,所以雜湊檢查只剩「自己等於自己」。
失敗情境:
- 審查綁的是「晚於這筆留痕」,並沒有綁到被審的檔就是這份計劃。
- `canary record --loop 甲 --spec 任何別的檔 --reviewed <該檔雜湊>` 一樣能過。
- 計劃〈取捨〉已承認不比整份計劃雜湊,這個缺口與單人依序操作的威脅模型一致。
- 如果記錄裡有 spec 路徑欄,至少可以比對路徑是不是這份計劃,成本很低。

最高等級 minor,blocking 0 條。
