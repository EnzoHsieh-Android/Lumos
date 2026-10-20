severity: minor

審完 `r2-repair-lumos-a.patch` 全部 hunk(1444 行)。我另外讀了被審版本 7655a12d 的 scripts/lumos 當上下文,沒有找到 blocker 或 major。找到 2 條 minor。

## 1. exception 放寬後,`security approvals payload` 遇到壞的 covers_kinds 會崩潰
severity: minor
blocking: 否

引句:「probs += [f"exception.{k} 要是非空字串" for k in ("decision_ref", "reason") if not _secinv_is_text(ex[k])]」

失敗場景:
- 修補把 `covers_kinds` 的型別檢查從登記階段拿掉,改由閘門的 `_secev_exception` 判 `exception_fields_missing`。閘門那一條路的確有驗型別。
- 但同一批資料的鄰近路徑 `_secapr_c_exception`(`security approvals payload` 算 exception 簽署內容)沒跟著驗,直接 `sorted(r['exception'].get('covers_kinds') or [])`。這個路徑只接 `(OSError, ValueError)`。
- 修前,壞的 `covers_kinds` 會讓整筆登記無效,進不到這裡。修後,壞值通過登記,payload 子指令丟 TypeError traceback,不是「擋下:…」的訊息。

重現(載入 7655a12d 的 scripts/lumos):
- 呼叫 `_sc_exception({"exception": {decision_ref, reason, expires_on, "covers_kinds": [1, "a"]}}, probs, 2)`,得到 `probs == []`,登記通過。
- 呼叫 `_secapr_c_exception(at, "c1#x")`,`covers_kinds=[1,"a"]` 得到 `TypeError: '<' not supported between instances of 'str' and 'int'`。
- 同一個呼叫,`covers_kinds=5` 得到 `TypeError: 'int' object is not iterable`。
- 上述兩個 TypeError 是我直接呼叫函式實測的。我沒有端到端跑 CLI,所以沒確認 CLI 層最後會不會把它包起來。

歸因:有證據的修復回歸。
- 修前版:同樣的壞值在登記階段就被 `_secinv_str_list` 擋下,不會走到 payload。我是讀程式推出來的,沒有實跑修前版。
- 修後版:登記通過,payload 崩潰,上面已實測。

file: `scripts/lumos:11264`(7655a12d 版)。`want = f"{cid}#{','.join(sorted(r['exception'].get('covers_kinds') or []))}"` 前面沒有驗型別。

## 2. 主線 tip 版 config 的 mainline 覆寫,讀失敗時悄悄當成沒設
severity: minor
blocking: 否

引句:「cfg = _secev_config(got[0] if got else None, for_mainline=True)」

失敗場景:
- 同一份修補在閘門主線上新增了 `read_status`,把「單檔太大」和「不存在」分開。理由寫得很清楚:「太大不是『沒有』」。
- 這一處新增的 `_secev_mainline_override` 沒有套用同樣的區分。`_nodehome_cat_blobs_capped` 在 git 失敗、截止時間用完、檔案超過 `_SECEV_FILE_MAX`(16MB)時,回傳 `None` 或 `[None]`。
- 這幾種情況在這裡都落成 `raw=None`,config 取預設值,mainline 覆寫消失。接著沿用 `_secev_mainline_pick` 挑的主線,沒有回 `mainline_unknown`,也沒有警告。
- 結果是「主線 tip 設定了指定主線,但這次讀不到」時,凍結比對和核可鏈前綴改拿另一個基準,而且不報錯。

這條我沒有重現:沒有建出主線 config 超過 16MB 或 git 逾時的 repo,所以已自降。

歸因:未判定。這個函式是修補新增的,修前版沒有覆寫機制,所以沒有修前行為可比,我也沒跑兩版。

file: `scripts/lumos:9785`(7655a12d 版)。

## 三問回答

**①原問題的修復效果有何行為證據**

我只靠靜態閱讀加少量實測,沒有跑測試套件。已驗的主張:
- `_secev_sha` 已全數改為 `_sha256_bytes`。我 grep 7655a12d 版沒有殘留引用。
- `_secev_mainline`、`_secev_config`、`_secev_backing_rows` 三個簽名改動的所有呼叫端,在 7655a12d 版都已同步:
  - `_secev_backing_rows` 的 3-tuple 解包。
  - `_secev_mainline` 的新參數順序。
  - `_secev_config` 的 `for_mainline` 預設。
- 以下修補的邏輯我讀過,方向正確:
  - 核可鏈筆數上限改成超過就丟 `_SecaprTooLong`,不再默默截斷。
  - 驗章逾時走 `_SecevTimeout`,不當成驗章失敗。
  - `approval_backdated` 只拿有效筆當日期基準。
  - 主線鏈「曾經有效」的判定(`ok` 或 `approval_expired`)。
  - 覆蓋證明的數值改成嚴格整數。

**②修補處的正常、錯誤與相鄰呼叫路徑是否仍成立**

- 正常路徑:我沒找到被破壞的。
- 同形狀的鄰近路徑漏修有兩處:
  - 上面的 #1。
  - `_secapr_cmd_verify`、`_secapr_payload_body` 與 `_secapr_add_check` 的相鄰路徑。其中 `_secapr_cmd_verify` 讀主線鏈用的是 `_SecevTree.read`,太大會得到 `None`,於是跳過前綴檢查。閘門主線已改用 `read_status`,這裡沒改。因為鏈檔太大時推送版也讀不到,實際影響很小,所以我沒單列成 finding。
- 兩處值得留意的已知設計取捨,我不算缺陷:
  - 核可鏈上限從 10000 降到 2000,已超過的舊鏈會永久驗不了(帳本只追加,無法縮)。
  - 被判 `approval_backdated` 的 `approvers_revoke` 不生效。

**③新發現的同一案例在修前、修後各是什麼結果**

- #1:修前登記即被擋,修後崩潰。這是從程式推的,沒有跑修前版;修後已實測。
- #2:修前沒有這個機制,修後有靜默退讓。未判定,沒有修前行為可比。

## 資料狀態五問

- **新舊格式互讀**:
  - v1 的 exception 帶 `covers_kinds` 或 `compensating` 仍被當成「未列出的欄位」而擋下,與 v2 區分一致。
  - 閘門端 v1 形狀的 exception 走 `exception_unapproved`,行為一致。
  - 舊核可鏈若曾有亂序的 `approved_on`,現在會被追溯判 `approval_backdated`,見上方「②」。
- **寫一半**:
  - 背書行寫到一半被截斷,仍有 `_truncated` 與 `backing_truncated` 路徑。
  - 型別不對的列現在記入 `malformed`,不採用。
  - 較新的壞列被略過後,會改用較舊的合格列,這個取捨我認為可接受,沒有單獨列出。
- **衍生資料**:`words_notice` 與 `_SECINV_NOTICE` 的字串變動,可能讓 golden 或快照測試受影響。這份差異看不到那些測試,未驗。
- **時間**:
  - `approved_on` 以 UTC 為準。
  - 每次驗章前都查截止時間。
  - 到期後由 `ok` 轉成 `approval_expired`,但 `last_ap` 已先設定,順序正確。
- **不可逆**:
  - `_SECAPR_MAX_ENTRIES` 降到 2000,見上方「②」。
  - 主線鏈只要有過有效筆(含已到期的),就永遠只能追加,這一條是正確的。

未驗範圍:
- patch 的後半(`r2-repair-lumos-b` 之後)和所有測試檔我都沒讀。
- 我沒跑 `python3.14 scripts/test_lumos.py`,所以沒有「測試通過」的證據,不能據此說修好。
- 我沒審 `_secev_mainline_cands` 與 `_secev_mainline_pushed` 的內部邏輯。

最嚴重 severity: minor,blocking 共 0 條。
