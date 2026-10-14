severity: minor

我先看修補差異,再跑相關測試子集(nogo、door_rule、door_scan、ledger、light_gate、spec_gate_push),都綠。另外實測了一份對照:拿 871 篇圖譜筆記比較「原文比對」與「NFKC 加去零寬」的門命中。只有 2 篇多出命中,而且都是本次在講全形與零寬危險詞的說明行。計劃目錄下沒有任何計劃的不做清單同時略過危險詞,所以沒有既有計劃被這次改動新擋下。

severity: minor
blocking: 否 — 只是手冊指引過時,工具擋下時的訊息本身指的出口是對的,不會讓壞東西放行
引句:「推送前檢查只認不帶 `-std` 的原編號,所以照下面這行手寫記帳,一席一行、不帶 `--round`」
問題:`templates.md` 的「`loop next` 回 escalate 或 cap-reached 時怎麼記這筆」一段,這次修補沒更新,和新行為矛盾。這段說窗口外有 major 時「推送前檢查只認原編號」,叫人手寫一筆輕量審記在原編號。但這次修補後,`_nogo_light_gate` 會讀原編號帳上全部非留痕紀錄,餵給預設帶 ratchet 的 `_light_gate_fails`。原編號只要曾有一筆 major 以上,不管在留痕前後,light 都永久失效。推送前檢查也已經認 `-std` 的處置閘。
具體失敗情境:某計劃的輕量審抓到 major,`loop next` 回 escalate。使用者照這段手冊手寫一筆 clean 記在原編號,推送前仍被擋,訊息說 light 永久失效、出口是 -std。使用者白做一輪,而且手冊還說「窗口外有 major」可以手記,與同一份檔案上方新寫的「ratchet 洗不回來」互相打架。
佐證:``file: `skills/lumos-design-loop/templates.md:71` `` 與 ``file: `scripts/lumos:9299` ``(`rows` 取全帳、不分窗口)。

已讀,無 finding 的部分:
- `_light_gate_fails` 拿掉 `ratchet=`:全 repo 只剩兩個呼叫端(`loop status --light` 在 `scripts/lumos:13516`,推送前輕量審在 `scripts/lumos:9305`)。前者行為和原本相同,`t_m1_light_gate` 與 `t_light_gate_fails_bad_types` 綠。
- `_canary_ledger_scan` 恢復只吃 env:三個既有讀者(`:13819`、`:13836`、`:15390`)都只傳 env,回傳還是三元組。我對照了基準版 `e0da694b` 的函式:壞行、非物件行、規格閘留痕、輪次非字串的處理都一致。
- 改成串流後:整本不是 UTF-8 仍回 `({}, {}, e)`,`e.start` 已換算成整本位元組位置,`\r`、`\r\n`、U+2028 的切行規則沿用 `_ledger_lines`。
- 規格閘留痕不再寫 `nogo_rows_sha`:讀端 `_SPEC_GATE_PUSH_FIELDS` 同步拿掉,舊留痕上多出的欄位被忽略,不影響。全 repo 已無 `_nogo_major_*`、`_NOGO_ROWS_V`、`_DOOR_SCAN_RAW` 的殘留引用。
- 門規則版本升 6:舊風險低留痕若在新規則下判高,會走 `older` 訊息(已補全形與零寬的說明)。`t_door_rule_version_pin`、`t_door_scan_logic_version_pin`、`t_spec_gate_push_stale_older_hint_versions` 都綠。
- `_nogo_line_key` 退回只去空白:只影響本分支上 r6 版算法寫過的本機留痕,那版沒上過主線;最差是 clause_sha 對不上,重跑規格閘即可。
- `cmd_loop_status(readonly=True)` 被推送前呼叫:`_loop_status_disposal` 裡寫 `roster-alerts.log`、治理標記、跑滿上限提示的路徑都有 `if not readonly` 擋住,fail banner 只印字。
- `_nogo_std_gate` 的 NFC 與非 NFC 編號不一致:會找不到紀錄,方向是多擋,不是漏放。

最高等級 minor,blocking 0 條。
