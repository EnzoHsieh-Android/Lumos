severity: clean

我讀完修補差異裡的程式部分,另外實測了成本和回溯。沒有找到值得擋的問題。

**推送前讀審查帳的成本:已讀,無 finding。**
- `_spec_gate_push_light` 一開頭就判 `if not nogo_skipped: return None`,所以只有「不做清單略過了危險詞」的風險低計劃才會讀帳。其他計劃不多付成本。
- 我拿真實帳(`docs/.canary-log.jsonl`,4.4MB、4329 列)實測:整本讀入、切行、逐行 `json.loads`,一次約 0.05 秒。即使 100 份計劃全都略過了危險詞,最壞也只有約 5 秒。
- `_spec_gate_latest_records` 只在 `_spec_gate_push_scan` 開頭讀一次。輕量審路徑另外對每份計劃各重讀一次帳,這是重複讀,但在單人使用的威脅模型下成本可以接受。

**治理帳:已讀,無 finding。**
- 真實治理帳 `docs/.governance-log.jsonl` 有 20MB。`_append_governance_log` 用 append 模式開檔寫入,不讀整本帳,所以帳大小不影響寫入成本。
- 每份被擋的計劃會呼叫一次它,各多一次 `git rev-parse` 子程序(約數十毫秒),可以忽略。
- 寫入失敗的處理沒有洞。底層自己吞 `OSError` 並在 stderr 警告,新增的 `except (OSError, ValueError)` 又多一層,判定照樣擋、不受寫入結果影響。
- 治理事件標了 `hard: True`,所以每次被擋的推送都會讓這本版控帳多一行,工作樹因此變髒。這是既有閘共用的行為,不算新問題。

**新正則的回溯:已讀,無 finding。**
- 我對 `_NOGO_REF_TOKEN_RE` 試了幾種壞輸入:20 萬個空白接一個左括號、10 萬個連續左括號、`(abc` 後接 20 萬個 `1`、十萬組「左括號加空白」。每種都在 0.01 秒內跑完,是線性的。
- `_NOGO_CLAUSE_SPLIT_RE` 只是單純的選擇字元和詞,沒有巢狀量詞,不會爆。

**寫一半與一致性:已讀,無 finding。**
- `_spec_gate_push_stale` 改成回傳 tuple。全 repo 只有 `_spec_gate_push_one` 一個呼叫者,沒有漏改的地方。
- `_spec_gate_push_light` 做了三件事:檢查帳上最後一筆規格閘留痕的 token 和這次讀到的是否一致;帶輪次的多人審格式回報判不了;沒有 `result_sha256` 時退回讀計劃檔。這些路徑都是 fail-closed。
- 竄改與同秒並列都靠帳的 append 順序處理,不比時間戳。

總結:最高等級 clean,blocking 0 條。
