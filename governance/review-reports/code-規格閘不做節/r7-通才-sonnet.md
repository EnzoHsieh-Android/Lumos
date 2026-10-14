severity: major

**finding 1:有 major 的輕量審可以被洗掉**

severity: major
blocking: 是 — 推送前的守門在這個情境失效:同一組被略過的行,抓到 major 的審查被一筆乾淨審取代後就放行。
引句:「兩樣都沒有就比不了、不進索引」
問題:r7 拿掉窗口裡的 ratchet(`_light_gate_fails(..., ratchet=False)`),改成只靠 `_nogo_major_lookup` 的「被略過行指紋」索引來擋 major。這個索引只有兩個來源:major 那筆綁的凍結快照,以及它記帳當下同編號的規格閘留痕裡的 `nogo_rows_sha`。兩樣都沒有的 major 不進索引,等於沒有 ratchet。
- 從沒有任何東西能證明那筆 major 看過哪幾行,所以它既不被索引擋,也不在窗口 ratchet 裡。
- 這兩種情況在實務上都會出現:記 major 時漏帶 `--snapshot`(帶它不是強制的);或快照事後被清掉,例如暫存目錄被刪,而這個編號在 major 之前沒有規格閘留痕。
- 沒有規格閘留痕的情況,正是「做完、全綠的計劃」走 `_spec_gate_push_nogo_only` 的路徑。

具體失敗情境(我在 scratchpad 的複本裡加了探針測試,實際跑過):
1. 計劃是 `status: done`,沒有規格閘留痕,不做清單略過「退款」。
2. 記 `canary record none --severity major --findings 1`,不帶 `--snapshot`。推送前 rc1,原因是「最後一筆輕量審沒過:severity=major」。
3. 不改計劃任何一個字,再記一筆乾淨的輕量審(帶快照、`--spec` 指向這份計劃)。推送前 rc0,沒有任何擋下的訊息。
4. r6 與 `loop status --light` 在同樣的帳上都會因 ratchet 永久擋住;r7 把它放行了。
5. 現有的 `t_prepush_nogo_light_major_*` 測試的 `_ngl_review` 預設都會凍結快照,或者設定裡已有規格閘留痕,所以沒有測試走到這條路。

佐證:``scripts/lumos:9350`` 是 `ratchet=False`。``scripts/lumos:9277`` 附近的 `_nogo_major_lookup` 裡,`fp is None` 時不進索引。``scripts/lumos:9199`` 的 `gate_sha` 在同編號之前沒有規格閘留痕時是 None。

**finding 2:加一行被略過的危險詞就能洗掉 major**

severity: minor
blocking: 否 — 這是整份指紋比對的取捨,r5 的 `rows == nogo_skipped` 就是這樣;但 r7 新寫的說明稱「改標點空白都洗不掉」,容易讓人誤以為任何改動都洗不掉。
引句:「跟這份計劃現在被略過的行(正規化後,_nogo_line_key)整份相同,就照擋」
問題:`_nogo_major_carried` 拿 `_nogo_rows_sha(nogo_skipped)` 這份「整組」指紋去索引裡找。
- major 看過的是行集合 {A}。
- 作者不改 A,只在不做清單再加一行同樣會被略過的危險詞 B(例如 `- 不做 Stripe 扣款`),現在的集合是 {A,B},指紋不同。
- 這時 major 不進比對,針對 {A,B} 的一筆乾淨審就放行。
- A 這行當初被點出的問題沒有被處理過。
佐證:``scripts/lumos:9306`` 的 `_nogo_major_carried`,以及 ``scripts/lumos:9283`` 的 `idx.setdefault(fp, r)`(索引的鍵是整組指紋)。這點我只從程式碼推出,沒有實跑。

**finding 3:提示文字沒跟上版本 5**

severity: minor
blocking: 否 — 只影響訊息正確性,不影響判定。
引句:「判高可能是新規則的結果(例:版本 4 起程式碼圍欄裡的危險詞也算)」
問題:版本 5 之後,行內反引號、圍欄標記行、落單反引號之後的字也都算,舊留痕被判高的主因更常是這些。但 `older` 提示只舉圍欄的例子。
具體情境:我拿現有帳上 18 份風險低留痕,用現行 `_door_judge` 重判,只有 `Projects/派工鏡頭跨repo不再靜默_計劃.md` 第 60 行變成「守衛面:錨點」。命中的字在行內反引號裡,圍欄不是原因。該計劃是 done,被推送範圍碰到時只走不做清單檢查,不會被擋。若換成 doing 的計劃,作者會看到一個無法對上的例子。
佐證:``scripts/lumos:9161`` 附近的 `older` 字串。

**已讀,無 finding 的部分**
- **讀帳核心 `_canary_ledger_scan`**:預設(`spec_gate=False`)路徑與原來逐行等價,`loop next`、`canary record` 定錨檢查和跑滿回顧一族不受影響。`spec_gate=True` 逐位元組解碼,與舊 `_spec_gate_ledger_index` 的 `errors="replace"` 等價。規格閘留痕本身不帶 `round`,不會被誤濾;`fields=` 的白名單涵蓋推送前與 `_light_gate_fails`、`_hash_chain_check` 讀的欄位。
- **處置閘留痕重驗**:`_prov_path` 換成 `_under_root`,與原寫法等價(`root is None` 或絕對路徑原樣)。`_prov_check` 變成 `_prov_read` 的薄包裝,簽名與回傳不變。手改帳路徑含 NUL 時,原本會丟 `ValueError` 崩潰,現在回 `unreadable`,是改善。資安席一步和 intake 的呼叫端無需改。
- **`loop status --light`**:預設仍是 `ratchet=True`,唯一的 `ratchet=False` 呼叫端是 ``scripts/lumos:9350``。
- **門規則版本升 5**:`_nogo_rows_v` 與 `nogo_rows_sha` 版本不同的舊留痕不互比,舊留痕只是退回快照那條路,不會崩潰。r6 版本沒有上過主線,不影響已推送的留痕。
- **`_nogo_skipped_rows` 的 `only=`**:已排除行與不做清單兩節互斥,所以不傳 skip 也一致。
- **執行測試**:`-k light_gate`(15 項)、`disposal_snapshot_prov`、`disposal_loop_requires` 都過。
- **replace 測試 ② 拿掉**:我沒有逐行審;改看環境的做法沒發現會誤綠的地方。

我的實驗只放在 scratchpad 的複本,已刪掉自己留下的 `gctl-run-*` 現場,原程式碼沒動。

最高等級 major,blocking 1 條。
