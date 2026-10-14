severity: minor

我只讀程式與文件,沒有跑任何測試,也沒有做變異實驗。`spec-trace` 與 `lint` 實跑結果如下:S1–S63 全部綁了測試、懸空 0,計劃 lint 0 問題。

數字與名稱對照過,都一致:
- 門規則版本 8:程式常數、S5、Systems 的 KEY 行都是 8。
- 掃法版本 4:程式常數與計劃都是 4。
- S53、S60 改成擋下後,條款、測試與程式的行為一致。
- S59–S63 各自綁到對應的測試。
- 「看不見」的天花板(只顧中英文、Mn 整類刪除、空白與換行類不刪、同形字不管、未指派碼位跟 Python 的 Unicode 版本)在計劃、Systems 的 PITFALL、`_strip_zero_width` docstring 三處說法一致,且有 `REVISIT:2026-12-31`。
- `_INVISIBLE_EXTRA` 只剩歷史敘述(計劃、Systems、docstring 各一處說明它已被拿掉),沒有程式殘留。
- 「整類拿掉」在計劃第 63 行有「r9 已換掉」的指標,沒有誤導。

以下是 finding。

severity: minor
blocking: 否 — 只是擋下訊息的措辭自相矛盾,行為本身是對的(擋下)。
引句:「why += f"(審查帳有 {ctx['skipped']} 行讀不懂,已跳過)"」
問題:r9 把 (b) 改成壞行 fail-closed,但這句後綴還是「已跳過」。它附在 (a) 的原因後面,又用的是 `ctx["skipped"]`,所以 (b) 因壞行擋下時,訊息同時說「讀不懂,已跳過」。
具體失敗情境:
- 帳尾有一行被截斷的 major,推送前被擋,使用者讀到「已跳過」,會以為壞行沒影響判定,轉去查別的原因。
- S53 的 `"1 行讀不懂" in why` 與 S60 的 `"讀不懂" in why` 檢查的就是這個後綴字面,不是 (b) 處置閘自己的原話。測試能紅仍靠 rc1(拆掉 fail-closed 會放行),但訊息措辭沒被釘住。
- 手冊與條款都沒有 (a) 跳過、(b) 擋下的雙軌說明。Systems/規格閘.md 只在 PITFALL 提到。
佐證:``file: `scripts/lumos:9550` ``、``file: `scripts/test_lumos.py:64963` ``、``file: `scripts/test_lumos.py:64989` ``

severity: minor
blocking: 否 — 純屬文件舊說法,不影響行為。
引句:「版本 7 起去掉的隱形字元擴成整類,_door_keyword_hits」
問題:`_door_judge` 的 docstring 沒跟上 r9。它停在版本 7 的「整類」說法,沒提版本 8 的 `_is_invisible` 按類別判。這正是任務點名要找的舊說法殘留,而且是讀程式的人最先看到的地方,會讓人以為「整類」就是 Cf 加手列。
具體失敗情境:有人讀 `_door_judge` 的說明,把「整類」理解成 Cf 加手列碼位,以為蒙古文變體選擇符或組合記號不會被拿掉,就不去查 `_is_invisible`。
佐證:``file: `scripts/lumos:8135` ``

severity: minor
blocking: 否 — 屬測試守不住細節,不屬條款錯誤。
引句:「return "沒記分級"」
問題:`_nogo_full_review_shape` 對「全部沒記 tier」會擋,但 S59 只寫「沒帶輪次、或分級是 light」,沒有測試釘這個分支。同一支檢查也管「原編號自己帶輪次的完整設計審」那條出口,而這條出口沒記 `--tier` 的人會被擋。條款漏寫,行為已變。
具體失敗情境:有人用 `canary record` 記完整設計審時省略 `--tier`。這條擋法沒有任何測試守,哪天被改成放行,測試全綠。
佐證:``file: `scripts/lumos:9442` ``(函式),``file: `scripts/test_lumos.py:65031` ``(`t_prepush_nogo_std_needs_full_review_shape` 只測漏輪次與 light)

severity: minor
blocking: 否 — 守衛強度偏弱,但目前確實守住了 r8 三席引的舊句。
引句:「miss = [f"{f}:{i}" for f, i, ln in lines if "-std" not in ln]」
問題:S58 條款說「同一行應講抓到 major 就改開 -std 完整設計審」,測試只檢查該行含 `-std` 子字串,沒檢查 major。
具體失敗情境:手冊有一行寫「要一筆輕量審,另見 -std 編號」,沒說抓到 major 要改開,守衛照綠。
佐證:``file: `scripts/test_lumos.py:65185` ``

severity: minor
blocking: 否 — 數字不影響任何行為,只是計數口徑不實。
引句:「2026-10-14 本 repo 346 份計劃沒有檔名以 -std 結尾的」
問題:`Projects/` 底下全部檔案是 346 個,以 `_計劃.md` 結尾的只有 286 份。「346 份計劃」口徑不實。結論(0 份以 -std 結尾)是對的。
佐證:``file: `docs/lumos-toolchain-knowledge/Projects/規格閘不把不做節的詞算進風險_計劃.md:174` ``

另有一點供參考:S57 的窮舉測試,其「看得見」判準 `_zw_visible` 是用 Unicode 類別補集寫的(L/N/P/S/Zs/Mc/isspace),跟 `_is_invisible` 的類別集合幾乎互為鏡像,有重寫實作的味道。真正的新增價值在 ③ 的端到端比對與 ⑤ 的整條規格閘。我沒有把它列成 finding,是因為整條 `_door_keyword_hits` 實際被呼叫,過度刪除與漏刪都會紅。

最高等級 minor,blocking 0 條。
