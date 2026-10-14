severity: major

**Finding 1:一般編號清單重新編號就洗掉 major,而且正文一個字沒改**

severity: major
blocking: 是 — 這是 r6 G1 要堵的那個洗法(不改被略過行的字就洗掉 major),只是換成改編號。誠實作者在清單上方插一項也會誤觸。
引句:「只留 Unicode 字母與數字類別(去掉空白、標點、反引號與粗體記號)」
問題:`_nogo_line_key` 只留字母與數字類別。有序清單的編號 `1.`、`2)` 屬於數字(N 類),所以留在雜湊裡。`_door_keyword_hits` 現在掃每行原文,編號不會被剝掉。`-`、`*` 項目符號和粗體則會被濾掉。
具體失敗情境:
- `## 不做` 下面是 `1. 不做退款`,這一行被略過。輕量審對它抓到 major。
- 作者在它上面插一項,或把順序換成 `2. 不做退款`。字沒改,只有編號變。
- 實測:`k("1. 不做退款")==k("2. 不做退款")` 回 False,`k("- 不做退款")==k("* **不做退款**。")` 回 True。
- `_nogo_major_lookup` 比 `_nogo_rows_sha` 對不上,major 就找不到,`_nogo_major_carried` 回 None。接著補一筆乾淨的輕量審,綁到新快照,推送前放行。
- 反方向也有:已綁好的乾淨審,在只重新編號後變成「快照裡被略過的那幾行跟現在的不一樣」,要重審。
佐證:``scripts/lumos: `_nogo_line_key`(約 8083 行)``

**Finding 2:沒綁快照又沒有規格閘留痕的 major,完全不進索引**

severity: major
blocking: 是 — 計劃裡的「做完全綠計劃的出口」就是沒有留痕的情形。那條路上 ratchet 可以靠記帳不帶 `--snapshot` 繞過。
引句:「兩樣都沒有就比不了、不進索引」
問題:
- `_nogo_major_lookup` 先用快照算指紋。快照缺或驗不過,才用 `_nogo_ctx` 收的 `gate_sha`,也就是該編號在這筆 major 之前最近一筆同算法(`nogo_rows_v==2`)規格閘留痕的 `nogo_rows_sha`。
- 兩樣都沒有的 major 直接丟掉,不擋。
- `_light_gate_fails(ratchet=False)` 也不再看窗口裡的 major。舊版窗口內任何 major 都會讓 light 失效,這個保證被拿掉了。
具體失敗情境:
- 計劃跑不過規格閘,所以沒有留痕,走 `_spec_gate_push_nogo_only`。
- 第一筆輕量審抓到 major,記帳時沒帶 `--snapshot`。
- 作者不動被略過的行,再記第二筆乾淨審,這次帶 `--snapshot`、席名不是架構對齊席。
- 第一筆 major 沒有快照也沒有 `gate_sha`,不進 `major_by_fp`。`_light_gate_fails(ratchet=False)` 又不看它,所以第二筆審讓推送放行。
- 舊版同一情境會被窗口 ratchet 擋住。
- 舊版留痕(`nogo_rows_v` 缺或為 1)也有同樣的洞:`gate_sha` 被當成 None,快照一刪,major 就脫鉤。
佐證:``scripts/lumos: `_nogo_ctx`(約 9190 行)的 `gate_sha` 判斷、`_nogo_major_lookup`(約 9262 行)``

**Finding 3:指紋沒有計劃身分,別份計劃會被誤擋,且提示的出口不對症**

severity: minor
blocking: 否 — 計劃的〈做法〉自己列為代價,出口(改寫那幾行,或寫 `plan_risk: high`)也講了。但被擋的人拿到的修法不對症。
引句:「別份計劃被略過的行跟某筆舊 major 看過的一字不差,也會被擋」
問題:
- 整份指紋是 `[類, 詞, 行雜湊]` 的集合,不含計劃身分。
- 最常見的情形是只有一條被略過行,例如 `- 不做退款`。任何一份計劃的 major,不管是在講被略過行還是別處的設計問題,都會永久擋住所有被略過行同樣是那一條的計劃。
- 要放行只能把該行改寫成不同的字,和 major 的實際內容無關。
具體失敗情境:A 計劃的輕量審因為別處的設計問題抓到 major,B 計劃只有 `- 不做退款` 一條被略過行,推送被擋。
佐證:``scripts/lumos: `_nogo_major_carried`(約 9290 行)``

已讀,無 finding:
- `_canary_ledger_scan` 預設路徑(`spec_gate=False`)的行為與舊版一字不變。解碼失敗的回傳、spec-gate 列的過濾、`bad` 的記錄都沒變,三個既有讀者(約 13776、13793、15347 行)不受影響。
- `fields=` 白名單涵蓋了推送前檢查實際讀的欄位:`tests`、`clause_sha`、`door_rule`、`plan_risk`/`door`、`nogo_rows_sha`/`nogo_rows_v` 等都在。`round` 在裁欄位之前就判掉了。
- `ratchet=False` 之後,結果不是 `judged` 一律擋,窗口非空時 `ratchet`/`empty` 不會出現,`bad` 會擋。
- 審查帳讀不到時,`_spec_gate_push_scan` 開頭就回擋下原因。
- 誠實改了被略過行的字之後,指紋會變,major 不再命中,可以過。
- `_spec_gate_push_nogo_only` 對完成狀態的計劃沒有誤擋。
- `_under_root`、`_prov_read` 與 `_prov_check` 的外部行為相容。
- 席名 NFKC 與門規則版本 5 的 bump、`_DOOR_SCAN_RAW` 入指紋都對。
- 新舊 `nogo_rows_v`:v1 的留痕被視為不可比,不會誤比,代價是 Finding 2 的洞。

資料狀態五問:
- 起始狀態:帳可能缺欄位、`nogo_rows_v` 缺或為 1、快照被刪。
- 失敗狀態:major 沒綁快照、沒有留痕,或只有 v1 留痕,洗掉的路徑見 Finding 2。
- 回頭讀:v1 留痕被忽略,不誤讀。
- 重複執行:`setdefault` 讓第一筆 major 勝出,冪等。
- 規模:快照每筆最多讀一次,`fields` 裁欄位,沒看到效能問題。

最高等級 major,blocking 2 條。
