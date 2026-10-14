severity: minor

白名單、40/64 碼編號檢查、候選上限三塊的程式行為都對。我沒找到會放行危險輸入的 bug,只有 1 個行為落差和 3 個測試缺口,全是 minor。實驗目錄已刪。

我在複製出來的工作樹上各改壞一處,再跑 `-k dispatch_lens_spec` 與 `-k spec_freeze`(已清 `__pycache__`)。基準是 152 與 89 條全過。

已讀,無 finding 的部分:
- **白名單邊界**:80 字剛好過、81 字不過;計劃路徑 300 字剛好過、301 字不過。全形空白 U+3000、不換行空白 U+00A0、私用區、零寬連接字元(ZWJ)、異體選擇符(VS)、全形冒號與句號都被擋。NFD 的日文濁點(か+U+3099)與全形括號放行。
- **本 repo 節點名**:用 `git ls-files` 掃 229 個 Systems/Issues 節點,全部符合白名單,固定席過濾不會誤砍現有節點。
- **上限邊界**:4999、5000 個候選不截斷,5001 個才截斷。重複與非法候選不佔名額(5000 個有效候選夾雜重複與非法項,仍不截斷)。5000 個非 ASCII 候選(實際問 1 萬行)耗時 1.6 秒。NFC 與 NFD 同一檔名只算一個。
- **編號檢查**:大寫 40 碼放行並回小寫;附註標籤物件、39 碼、41 碼、64 碼(在 SHA-1 repo)、前後帶空白都回 None。
- **實驗以外**:`_vault_node_read` 與 `_read_wt` 的改法沒發現問題。

severity: minor
blocking: 否 — 只影響極罕見的相容漢字檔名,結果是少列一個只在提交裡的節點,不會放行任何危險內容
引句:「每個候選的 NFC 與 NFD 兩種寫法都問(r3 正確性1:提交本身存 NFD 時只問 NFC 查不到)」
問題:白名單放行 U+F900 到 U+FAFF 的相容漢字區,但 `_spec_commit_cands_norm` 把候選轉成 NFC 後,這些字會被改寫成一般漢字(U+F900 變 U+8C48)。NFC 與 NFD 兩種問法都不會變回 U+F900,所以問不到 git 裡實際存的名字。`_spec_commit_path_bad` 也要求計劃路徑必須是 NFC,同一族的字元在那裡同樣被擋。
失敗情境:提交裡有 `Systems/\uf900.md`,計劃寫 `[[Systems/\uf900]]`,會談目錄沒有這篇。我呼叫 `_spec_commit_present` 實測,回傳 `{'docs/x-knowledge/Systems/豈.md': False}`,即使提交裡真的有,也被當成「找不到」,不會列為「只在那個提交裡」。
佐證:``scripts/lumos: `_spec_commit_cands_norm` 與 `_LENS_SPEC_NAME_CHARS` 的 豈-﫿 範圍``

severity: minor
blocking: 否 — 只是測試沒釘住行為,程式本身目前是對的
引句:「_LENS_SPEC_PATH_BAD_CATS = _PATH_SPECIAL_CATS | {"Co", "Cn"}   # 控制、格式、行段分隔、代理(_PATH_SPECIAL_CATS)加私用、未指派」
問題:`Co`(私用)在字元集範圍外本來就進不來,實際有作用的只有 `Cn`(範圍內未指派的碼位,如 U+3040、U+9FFD 以外的空位、U+D7A4)。測試沒有任何範圍內未指派碼位的案例。
失敗情境:我把 `_lens_spec_charset_ok` 的 `not any(category in BAD_CATS)` 改成 `True`,152 條與 89 條測試全過。之後誰刪掉類別檢查,U+3040 這類未指派碼位就會進派工詞,測試不會紅。
佐證:``scripts/test_lumos.py: 新增的 t_dispatch_lens_spec_source_line_sentence_path_hidden 只測半形逗號、冒號與全形句號``

severity: minor
blocking: 否 — 只是測試沒釘住行為
引句:「_LENS_SPEC_NODE_NAME_RE = re.compile(f"[{_LENS_SPEC_NAME_CHARS}]{{1,80}}")」
問題:80 與 300 的長度上限、白名單字元集的擴張,測試都沒有邊界案例。
失敗情境:我把 80 改成 81、300 改成 301,測試全過。把全形空白 U+3000 加進 `_LENS_SPEC_NAME_CHARS`,測試也全過。上限放寬或字元集擴張都不會被測試發現。
佐證:``scripts/test_lumos.py: 新增測試只測「一整句」與全形括號/冒號``

severity: minor
blocking: 否 — 只是測試沒釘住行為
引句:「LENS_SPEC_COMMIT_CANDS_MAX」(測試用 `cap + 100` 個候選)
問題:候選上限的測試只用 `cap+100` 個候選,沒有剛好 5000 個、剛好 5001 個的案例。
失敗情境:我把 `len(q) >= MAX` 改成 `>` 會讓 `t_dispatch_lens_spec_commit_cands_capped` 紅,所以改壞整段邏輯抓得到。但要是有人把「剛好 5000 個也算超過」之類的差一錯誤放進來,只要 `cap+100` 的案例仍成立,測試就不會紅。另外,非 ASCII 名字實際會送出 2 倍的行數(NFC 與 NFD 各一行),測試註解只講了 ASCII 的情況。
佐證:``scripts/test_lumos.py: t_dispatch_lens_spec_commit_cands_capped``

最高等級 minor,blocking 0 條。
