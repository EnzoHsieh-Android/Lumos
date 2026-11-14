severity: major

範圍:第一段(choice-points、規則與樣本、型錄兩節、check.py)。我在 `/tmp/lumos-seat-work/code-改動選擇點/邊界p1-sonnet/` 的複本裡用真的 ast-grep 0.51.2 跑過空範圍、刪檔、改名加改內容、純縮排、CRLF、BOM、非 UTF-8、無結尾換行、中文識別字、6000 行大檔,以及 27 種運算與陳述寫法的全候選展開。大多正常,下面是找到的洞。

## b11 連續相同行用「不重疊計數」判唯一,5 行以上相同時誤判成唯一、壞法落到別行
severity: major
blocking: 是 會讓壞法套到別的行、帳的鍵(檔, 行指紋)對錯行,且測試抓不到。

- 輸入:同一函式內連續 5 行完全相同的 `        save(count)`。
- 走到哪:`_choice_identity` 往外帶行求唯一時,用 Python 的 `str.count` 判「整支檔恰好一次」。`str.count` 只算不重疊的出現。5 行相同時,3 行一組的 `old` 在檔內其實出現 3 次(重疊),但 `count` 回 1,所以判成唯一。
- 預期(S3 預期值表「兩行完全相同、前後各兩行也相同」,〈用詞〉壞法身分):標不唯一、不跑。
- 實際:全部標 mutant。我的重現腳本在複本的 `h/t7.py`,輸出如下。

```
claimed line 7 count(old)= 1 true occurrences= 3 replace-first changes line [7]
claimed line 8 count(old)= 1 true occurrences= 3 replace-first changes line [7]
claimed line 9 count(old)= 1 true occurrences= 3 replace-first changes line [7]
```

  第 8、9 行宣稱的壞法,實際套上去改的是第 7 行。第 7、8 行的行指紋也相同(`55d9727e8a2fb8f0`)。後段 choice-kill 的殺傷力結果、放行鍵(檔, 行指紋)都會掛到錯的行。
- 引句:「        if text.count(old) == 1:」
- file: `scripts/lumos:77205`
- 為什麼測試抓不到:`t_choice_points_stable` 的重複案例是 `go go save go go` 之間隔了 `stop()`,只有兩份不重疊的區塊,不會觸發重疊。
- 同一個計數若也用在 guard kill,同樣會誤判。我沒有追到後段,但計劃寫的是「同 guard kill」。
- 修法方向:改用重疊計數,例如 `len(re.findall("(?=%s)" % re.escape(old), text))`。

## b12 一支極端檔讓整批掃描全部算不出來
severity: minor
blocking: 否 結果是明確的 rc 3「沒檢查到」,不是靜默錯。

- 輸入:一行 3000 項的串接 `val s = a0 + a1 + … + a2999`(約 22KB)。
- 走到哪:`_choice_scan` 對整個暫存目錄只跑一次 ast-grep。每個巢狀 `+` 節點都帶一份很長的後設變數原文,輸出是 O(n²)。
- 實際:輸出超過 64MB 的檔案大小上限,ast-grep 被 SIGXFSZ 中斷,拋 `_ChoiceUnverifiable: ast-grep 掃描回 -25`(複本 `h/t9.py 3000` 重現;1500 項時正常)。同一範圍內其他正常檔也一起沒檢查到。
- 我另外量到密集運算式的輸出約為原始碼的 79 倍。
- 引句:「            if out_path.stat().st_size > _LINT_SARIF_MAX_BYTES:」
- file: `scripts/lumos:76984`

## b13 字串串接的型別前提只看當下節點的兩個運算元,左巢狀串接的內層節點會挑到編不過的壞法
severity: minor
blocking: 否 設計寫明是「語法情境近似」,但那一行唯一的壞法位置被佔掉,只能走放行。

- 輸入:`val u = f1 + id + "/"`(f1、id 是 String 變數)。
- 走到哪:`_choice_excluded` 只看該節點的 A、B 開頭是不是 `"`。外層節點 B 是字面值,被排除;內層 `f1 + id` 兩邊都沒字面值,不排除。排序是由左到右,內層先被取。
- 實際:挑到 `(f1 % id) + "/"`、`f1 - id + "/"`,這類壞法在 Kotlin 編不過(複本 `h/t10.py`)。
- 預期:外層已經是字串串接,內層被它包著的左子節點也該排除。
- 引句:「        return any(x.startswith('"') for x in ops)   # 字串字面值、字串樣板,或左邊開頭就是字串的串接」
- file: `scripts/lumos:77115`

## 已逐一確認沒問題的邊界
- **行列與位元組換算**:多位元組、BOM、CRLF、無結尾換行、非 UTF-8 檔,位元組位移到行號都正確。
- **ERROR 略過**:中文識別字讓 ERROR 範圍跨多行,範圍內的行都略過,符合計劃「命中節點所在的任一行含 ERROR」。
- **空與刪檔**:空範圍、刪檔、空 .kt、純縮排都得到「改到的行 0」、rc 0。改名加改內容只算新增的行。
- **括號與優先層級**:27 種運算寫法的全候選展開,沒有發現優先層級被改壞的組法。
- **資源收尾**:暫存目錄與子程序在例外與逾時路徑都有收。大檔 500 到 6000 行耗時 1.6 到 5.8 秒,接近線性。

## 圖譜鏡頭
這次沒有附固定席節點(鏡頭計算超時),派工詞說不用自己補算,所以沒有逐節點判。我只讀了 diff 牽連的兩處:

- **`_lint_wt_allow` 抽出 `_lint_wt_cfg_inside`**:路徑檢查邏輯與回傳訊息逐字相同,不影響既有行為。
- **`dt_table` 一般化成 `section_table`**:表頭與欄數的錯誤訊息文字不變。`check.py --catalog-only` 在這個範圍回報「型錄問題 0 個」。

最嚴重:major;blocking 共 1 條

我留了 `/private/tmp/lumos-seat-work/code-改動選擇點/邊界p1-sonnet/`,內含 repo 複本 `wt` 與重現腳本 `h`,收貨後依派工詞由編排者刪。
