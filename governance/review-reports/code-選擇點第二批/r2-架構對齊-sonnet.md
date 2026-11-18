severity: clean

派工附的鎖 `88bfdf75…json.warming` 實際不存在(ls 回 No such file),沒有刪除或處理動作。

## 三問(逐問答)

**1. 分層與依賴方向:一致。**
- `scripts/lumos` 的改動只在 `_gov_choice_counts`、`_render_gov_choice` 內。它改呼叫既有的 `_loop_ts_newer`,該函式的 `scripts/lumos:20861` 與 `scripts/lumos:20926`、`scripts/lumos:20971` 的呼叫端用法相同。
- 沒有自寫時間比較,也沒有另讀一次帳。
- `check.py` 的改動留在既有的 `_choice_retired`,同一層、同一呼叫端。
- 沒有新增跨層呼叫。

**2. 命名與錯誤處理:一致。**
- `_choice_retired` 仍回 `(集合, 問題或None)`,問題訊息用同檔其他 `choice_tables` 問題的格式(繁中、指出「這裡是:…」)。
- `_CHOICE_RETIRED_RE` 的命名沒變。它去掉 `re.M` 改用 `.match`,是因為先逐行過濾,只影響內部寫法,不影響對外介面。
- 排序鍵的 `isascii() and isdecimal()` 沒有同功能的既有工具函式可借。`scripts/lumos:72498` 也用 `isascii()` 做同類守衛,是同一種寫法。

**3. 第二種做法:沒有。**
- api.yml 的 C-34、C-35、C-36、C-37 與 nul.yml 的 C-33,把 `inside:` 改成雙重否定。這是第一版 `sbr.yml` C-18 已有的做法(`sbr.yml:22-27` 註解明寫),等於沿用既有做法。
- C-34 的 `value-pos` 與 `sbr.yml:13` 逐字相同。C-36 與 C-37 的 `literal-arg` 兩份相同。測試 `scripts/test_lumos.py:146066-146067` 用 `_cb2_util_block` 比對這三組,有機械守衛,沒有悄悄分岔。
- C-34 的 `value-used` 內嵌展開 value-pos 邏輯、不再 `matches: value-pos`,是為了反向語意(不確定就不收)。檔內註解寫明,且 `value-pos` 本體仍在被內層 `matches` 引用。這是刻意偏離而非第二套做法。

## 圖譜鏡頭(固定席節點)
- `Systems/kotlin規則包`(家):改的就是它管的 `check.py`、api.yml,對齊上面三問,不影響。
- `Systems/bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle`、`測試假綠形態`、`lumos-cli-read`:這些 INVARIANT 是 code-loop 綁定測試、guard kill、reinject、search 過濾的合約。本 diff 只動統計列的時間選擇、排序鍵與規則檔,沒碰那些函式,判不影響。
- `pitfalls-code-loop`、`loop-convergence-recording`(RISK):只是共用 `_loop_ts_newer`,沒改它的實作,不影響。
- 其餘「只列名」節點沒有展開內容,未判定,也沒有對應的具體疑慮。

## 已驗的修復/正常路徑主張(同一案例)
- 主張:`已撤列號` 行被寫成清單符號開頭、或出現兩行時,修前靜默當成沒有(撤列守衛失效),修後報問題。
- 輸入:`## 選擇點表` 節內分別放 `- 已撤列號:C-1` 與 `已撤列號:C-1\n已撤列號:(無)`,用 `_choice_retired` 跑。
- 期望:頂格單行照舊解析,其餘報看不懂。
- 修前(eebb8459):清單版回 `(set(), None)`,兩行版回 `({'C-1'}, None)`(後一行被忽略)。
- 修後(6cc9ad8c):兩者都回 `(set(), 「…恰好一行、頂格…」)`,頂格單行 `已撤列號:C-1` 仍回 `({'C-1'}, None)`。
- 比較:壞輸入由靜默變成報錯,正常輸入不變。

## 未驗範圍
- 未實際跑 ast-grep 規則的命中與輸出大小(巢狀 LaunchedEffect 的平方成長是否消除),這是正確性與效能席的範圍。
- 未跑 `_gov_choice_counts` 的混時區時間案例。
- 未跑任何測試子集。

最嚴重:clean;blocking 共 0 條
不對齊共 0 條,其中 major 0 條
