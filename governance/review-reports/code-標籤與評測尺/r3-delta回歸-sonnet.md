severity: minor

（來源：代碼審 r3 delta 回歸審查席，sonnet，2026-09-15；方法＝逐條核對 r2 提出的四條修正＋對關鍵翻紅釘預測做實際變異測試、臨時複本操作、正式 repo 全程未觸碰、跑完清 `__pycache__`）

## 第一優先：四條修正有沒有把原本對的東西改壞

逐條核對 r3-delta.patch 對 r2 四個 minor 發現（原報告編號 6–9）的修法：

- 對應第 6 條（`_touched_edit` docstring 留著失效舊指示）：舊句「三條排法要跟 eval_edit 的 orders 用同一組排序鍵,改一邊要改兩邊」已換成新句,與程式現況一致：`eval_edit`（`orders = _edit_orders(free)`）與 `_touched_edit`（`_edit_orders(_f).values()`）現在確實共用同一個函式，舊指示的前提已不成立，換掉是對的，沒有把邏輯改壞。
  引句:「★2026-09-15 起排序鍵已抽成 _edit_orders 唯一實作,兩邊共用——這句舊指示作廢★」
- 對應第 7 條（`t_eval_switch_equal_no_data_is_not_equal` 翻紅釘數字錯）：新文字把翻紅條數改成 1、3、4 條(實測 3 條)。我把 `_switch_equal` 的 both-None 分支複製到 /tmp 獨立副本改回純 `continue` 後實跑，結果確實是「★五個指標全無資料→不得判恆等★」「五個指標一條都不漏」「★部分指標無資料也不得判恆等★」三條斷言翻紅，其餘兩條(含反向對照)仍過——與新文字完全吻合。
  引句:「翻紅釘:把 _switch_equal 對兩側皆 None 的處理改回 continue → 第 1、3、4 條翻紅(實測 3 條)。」
- 對應第 8 條（`t_eval_eq_keys_are_wired_in` 翻紅釘數字錯）：新文字把翻紅條數改成 2、3、4 條(實測 3 條)。我把五處 `_macro_on(...)` 賦值改回 `_macro(...)` 實跑,結果是「★_rn_eq 是限縮值 0.8...★」「★_ln_eq 同理是 0.7...★」「舊鍵仍是全題平均(...)」三條翻紅、第一條「前置」仍過——與新文字完全吻合。
  引句:「翻紅釘:把 report_goldset 裡五處 _macro_on 改回 _macro → 第 2、3、4 條翻紅」
- 對應第 9 條（符號詞彙表測試留著沒人用的 import）：`import re as _re` 與 `src = Path(GRAPHCTL).read_text(...)` 兩行已整段刪除,改成驗實際辨識行為,讀過整支 `t_symbol_vocab_single_source_and_reach` 確認函式體內再無 `_re`／`src` 的殘留引用,不是刪一半留另一半的半調子清理。
  引句:「① 單一來源——★驗實際辨識行為,不掃原始碼文字★(code-r1 測試品質席:文字掃描擋不住」

四條修正的「說明文字」都跟程式實際行為對得上,沒有發現新寫的說明反而跟行為不符的情況。

## 第二優先：這四條修正自己有沒有新問題

實際跑了以下測試子集,均為綠燈,沒有因這批修正引入回歸：

```
python3 scripts/test_lumos.py -k eval_edit_orders          # 10 passed
python3 scripts/test_lumos.py -k switch_equal_no_data      # 5 passed
python3 scripts/test_lumos.py -k eq_keys_are_wired          # 4 passed
python3 scripts/test_lumos.py -k touched_edit_covers        # 5 passed
python3 scripts/test_lumos.py -k touched_universe_bounds    # 9 passed
python3 scripts/test_lumos.py -k symbol_vocab                # 9 passed
python3 scripts/test_lumos.py -k eval                        # 111 passed（governance/eval 全部相關測試）
```

沒有發現這四條修正自己帶新問題。

## 第三：整條分支殘留缺陷排查

### 1. 尺切換的未標門檻在 `-k` 非預設值時可能誤放行

`main()` 裡有兩個地方會把 CLI 的 `-k`（`args.k`，預設 8）餵進 `collect_unjudged` 判斷未標:第 234 行 `ablation_blocked` 正確地把 `k` 轉傳給 `collect_unjudged(gs, split, k=k)`；但驅動「尺切換」判定的那一段（第 833 行 `_unj_all = collect_unjudged(gs, args.split) if args.split else collect_unjudged(gs)`）完全沒帶 `k=args.k`，等於永遠用 `collect_unjudged` 自己的預設值 `k=8`。而同一輪的實際計分視窗（`report_goldset(gs, sp, k_edit=args.k)`，第 822 行）是照 `args.k` 走的。

如果有人跑 `retrieval_eval.py --goldset ... -k 12`（`-k` 是公開、有效的旗標,不是只給 `--auto` 模式用),三條排法各自的計分視窗會擴到前 12 名,但「尺切換」用來判斷「未標=0 才准切換」的觸及集仍只看前 8 名。這代表:如果第 9–12 名裡剛好有未標候選,未標門檻(`_unj_all["count"] == 0`)可能顯示為 0(因為它只掃了前 8 名)而放行切換,但那些未標節點其實正在被算進第 9–12 名的分數裡——恰好就是這條分支想杜絕的那類「檢查看不到、但分數被未標拖累」的漏洞的鏡像版本。

這不是本輪 r3-delta 或更早的四條修正引入的——`main()` 這一段完全不在 r3-snapshot.patch(整條分支 e75b883c..HEAD)的 diff 範圍內,是分支開始之前就有的舊碼；目前唯一的生產呼叫點 `governance/autonomous-loop.sh:327` 從不帶 `-k`,恆等於預設值 8,所以現況下不會觸發。列在這裡是因為它剛好命中本題「恆等判定在什麼情況下會誤放行」的問法。

severity: minor
blocking: 否——不是本分支引入、也不在本輪 diff 範圍內,且目前唯一的生產呼叫路徑（autonomous-loop.sh）從不傳非預設 `-k`,現況不可觸發；只在有人手動帶 `-k` 跑 goldset 模式時才會露出。
file: `governance/eval/retrieval_eval.py:833`（對照正確寫法 `governance/eval/retrieval_eval.py:234`）

### 排查過、判斷乾淨、不列 finding

- `_edit_orders` 有沒有漏掉某條呼叫路徑:全檔搜尋只有 `_touched_edit`（第 204 行）與 `eval_edit`（第 488 行）兩處建構三條排法,兩處都改吃 `_edit_orders`；`collect_unjudged`／`ablation_blocked` 只呼叫 `_touched_edit`,沒有第三份手寫排序鍵。`refresh_labels.py`／`retrieval_eval_multiword.py` 都不涉及 fusion/bm25/graph 這三條排法,不是漏掉的呼叫路徑。
- `_switch_equal` 新的「兩邊皆 None → 不算恆等」分支只會讓判定變得更嚴(以前是靜默放行,現在是列成差異擋下),沒有找到會讓它反而變寬鬆、誤放行的路徑。
- `_edit_orders` 的 fusion 鍵從 `x["score"]` 放寬成 `x.get("score", 0.0)`,理論上會讓缺 `score` 欄位的候選靜默排到最後而不是丟例外；這點 r2 已核過「實測真實輸出 43 筆全部帶該欄位」,本輪沒有新資訊推翻這個結論,不重覆列。

## 總結

全篇最高 severity 為 minor；blocking 共 0 條。r2 提出的四條修正（原報告編號 6–9）本身修得正確,兩條翻紅釘數字都經過實際變異測試核對、與新文案完全吻合,沒有引入回歸。額外在分支既有程式碼裡發現一處與本題精神相關但非本分支引入、現況不可觸發的未標門檻 `k` 值未同步問題,列為 minor、不阻塞。
