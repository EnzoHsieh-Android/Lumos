severity: clean

## 問 1 分層與依賴方向:對齊

- **位置**:新碼放在 `cmd_decisions` 正後方(`scripts/lumos:18132`、`:18149` 之後),前面是 `parse_decisions`、`fmt_decision`,後面是 `_conds`。這和鄰居一樣是「讀取指令緊接決策解析」。
- **共用收集函式**:`_superseded_decisions`(`:18135` 一帶)是從 `cmd_decisions --superseded` 原樣抽出,兩邊都呼叫它。測試 `t_decisions_superseded_output_unchanged`(`scripts/test_lumos.py:76544`)釘住輸出不變。
- **規格閘端**:`_spec_gate_print_rejections`(`:7275`)緊貼 `_spec_gate_print_door`(`:7286`),在 `_spec_gate_front` 裡於它之後呼叫(`:7703`)。這和閘裡其他印行函式的做法一致。
- **跨功能區借用**:`_drift_mask_quotes`(`:35378`)、`_NS_NEG_SEG_CUT_RE`(`:31271`)、`SYMBOL_RE`(`:3835`)、`_STATUS_ENUM`(`:18448`)、`_visible_lines`(`:4871`)、`_slot_summary_entries`(`:4041`)都是模組層共用件,沒有人複製一份。專案裡本來就大量跨區借用,所以我不判這是跨層直呼:
  - 一般讀取函式借 drift 區:`:1446`、`:2519` 呼叫 `_drift_jsonl_iter`,`:2746` 借 `_drift_str`。
  - 一般函式借 ns 區:`:4032` 呼叫 `_ns_summary_logical`,`:4092`、`:4283`、`:4343` 呼叫 `_ns_superseded`。
  - 常數借用:`_ISSUE_CLOSED_STATUSES` 與 `_DRIFT_C3_STATUSES`(`:37842`)都從 `_STATUS_ENUM` 派生。
  - 唯一小差別:`_drift_mask_quotes` 之前只有 drift 區自己用(`:35394`),這次是第一次被區外呼叫。但 `_drift_*` 其他函式區外借用已有先例,所以不算新做法。
- **同檔往後引用**:`_rejections_collect` 在 `:18216`,規格閘在 `:7278` 就呼叫它。模組內往後引用在這個檔很普遍,不是問題。

## 問 2 命名與錯誤處理:對齊

- **命名**:
  - `cmd_rejections(env, as_json=False)` 對 `cmd_query(..., as_json=...)`。
  - argparse 的 `dest="rej_json"` 對 `q_json`、`gk_json`、`ctx_json`。
  - 私有函式的前綴 `_rejections_*`、常數的前綴 `_REJ_*` 都是功能名前綴,和 `_drift_`、`_NS_NEG_` 同一種風格。
  - `HELP_WHEN` 有登記(`:49413`),`main()` 的子指令與分派段也放在 `decisions` 旁(`:50001`、`:50954`),和 `contracts`、`query` 的註冊方式一樣。
- **`--json` 形狀**:`{"total", "results"}`,其中每條有 `node`(帶 `.md`)、`kind`、`content`、`context`。
  - 對照 `cmd_query` 的 `{"results":[{"node",...}], "hidden_superseded"}`(`:18504`)和搜尋的 `results`,以及 `:26030` 的 `total`,頂層叫 `results`、單條叫 `node` 是一致的。
  - 空結果 `{"total":0,"results":[]}` 也跟 `query` 一樣是空陣列,不是 null。
- **空結果訊息**:`無舊否決(共 0 筆)`。鄰居是 `無被推翻的決策`、`無節點符合條件`,同屬「無…」開頭的短句。括號多了筆數,是這支指令自己的測試要求,我不算不一致。
- **例外處理**:`_spec_gate_print_rejections` 刻意 `except Exception`、只印略過原因、不改回傳碼。這和 `_gist` 的 fail-open、`:64838` 測試用 `side_effect=ValueError("壞掉")` 的同型做法一致。輸出走 stdout,對上同閘內 `[spec-gate] 跑: —(略過:...)` 這種「—(略過…)」寫法;只有真正的寫帳失敗(`:7270`)才走 stderr,那是另一類。
- **輸出用語**:行首 `[spec-gate] 舊否決:` 對 `[spec-gate] 計劃風險:`、`條款綁定:`,格式一致。

## 問 3 第二種做法:沒有

- **決策與正文辨識**:
  - 正文 WHY 辨識用 `SYMBOL_RE.match`,摘要的 WHY 用 `_slot_summary_entries`,圍欄用「全檔唯一」的 `_visible_lines`(`:4871`)。
  - 欄位解析走 `slot_parse` 加 `_slot_vals`;一句話走 `_gist`;全文讀取走 `env_text`;決策解析走 `parse_decisions`。這些都用既有件,沒有新寫一套。
  - 單行 WHY 去掉列表記號 `- ` 的那兩行是新寫的,但註解已說明原因,而且仍交給 `SYMBOL_RE`,不算另立辨識。
- **「推翻」判法**:專案裡沒有現成的「決定不做」偵測器。`_NS_NEG_*` 管的是「還沒做、缺」的缺口詞,語意不同。所以 `_REJ_NOGO_RE` 和 `_REJ_REVERSAL_RE` 是這個功能自己要寫的,不是重造輪子。引號遮蔽與子句切點也都是借用。
- **作廢狀態表**:`_REJ_RETIRED` 是手寫字面表。同一個檔裡 `_DRIFT_CLOSED = ("done", "superseded")`(`:35125`)也是手寫字面;而且它在 `_STATUS_ENUM` 定義之前出現(`:18169` 對 `:18448`),無法派生。再加上測試 `t_rejections_retired_statuses_in_enum`(`scripts/test_lumos.py:76536`)釘住值域,所以不判為第二份詞彙。
- **測試佈景**:用既有的 `mkvault`、`write`、`run`、`_mk_spec_gate_repo`、`_sg_plan2`、`_load_lumos_inproc`,以及 `patch.object(m, ..., side_effect=...)` 加 `patch.object(m.sys, "stdout", ...)`。這些和 `scripts/test_lumos.py:39590`、`:64838` 的做法一樣。`_rej_vault` 是新增的佈景函式,但它是這組測試專屬的資料,沒有取代任何既有 helper。

## 交編排者的不確定點

⚠ 一個判不準、沒有先例可比的地方,我不硬判成不對齊。`_rejections_collect` 用 `_slot_summary_entries(env, ("WHY",))`(`:18220`)收摘要 WHY,沒有過濾已標 `[status:superseded]` 的行。鄰居 `:4092`(只收作廢行)、`:4283`、`:4343` 都用 `_ns_superseded` 做過濾,但那些是別種前綴的規則。WHY 行目前沒有任何先例。「已作廢的 WHY 裡的不選,該不該仍當舊否決列出」是語意題,請依計劃〈範圍〉裁定。

不對齊共 0 條,其中 major 0 條
