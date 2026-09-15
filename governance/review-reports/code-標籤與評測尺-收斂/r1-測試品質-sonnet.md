severity: minor

# r1「標籤與評測尺收斂」測試品質審查

審查範圍:`scripts/test_lumos.py` 新增/改過的 +282 行測試,對應 `governance/eval/retrieval_eval.py`(`_macro_on`/`_touched_edit`/`_edit_orders`/`_switch_equal`/`collect_unjudged`/`report_goldset`)與 `scripts/lumos`(`SYMBOL_NAMES`/`SYMBOL_RE`/`SYMBOLISH_RE`)的改動。方法:在 `/tmp/lumos-mut`(rsync 複本,不碰 repo)逐項拆掉修法、清 `__pycache__`、跑對應測試觀察是否翻紅,再還原確認轉綠。收工前用 `diff -q` 核對三支被動過的檔與 repo 內原檔位元相同。

## 一句話總結

六類新測試裡,五類的變異測試結果與測試自己的宣稱(翻紅釘、通過/不通過的條件)完全吻合,是真的能咬人的守衛;有兩支測試的說明文字宣稱「拆某段會讓第幾條斷言翻紅」,實測翻紅的條數跟宣稱的不一樣——測試本身仍然守得住(拆了修法照樣翻紅),只是那句話拿去對照原始碼會找錯地方,屬於文件精確度問題,不影響這批改動的殺傷力。

## 逐支結論

**1. 恆等斷言不得靠「沒資料」放行**(`t_eval_switch_equal_no_data_is_not_equal`、`t_eval_switch_equal_same_question_set`):守得住。把 `_switch_equal` 對兩側皆 `None` 的分支改回單純 `continue`(不記差異),五項指標的斷言裡有 3 項照宣稱的位置翻紅,還原後轉綠;`_macro_on` 本身的篩選邏輯拿掉 gate_key 條件也會讓對應斷言直接翻紅,證明不是空跑。

**2. 限縮平均要接上報告流程,不能只有函式本身會算**(`t_eval_eq_keys_are_wired_in`):守得住。把 `report_goldset` 裡五處 `_macro_on(...)` 全部改回 `_macro(...)`(維持 `_macro_on` 函式本體不動),斷言直接抓到 `verdict["_rn_eq"]` 變回全題平均 0.5667,而不是限縮值 0.8——這正是這支測試存在的理由(舊測試群只驗函式能不能算,不驗有沒有接線)。

**3. 排序鍵單一來源+缺 score 要拋錯**(`t_eval_edit_orders_single_source`、`t_eval_touched_edit_covers_all_arms`):守得住。無論是讓 `_touched_edit` 的三臂退化回單一 `free[:k]`(未涵蓋 bm25/graph 各自前 k),還是讓 `_touched_edit` 只有 fusion 臂沿用未排序的上游順序,都會如期翻紅;把 `_edit_orders` 的 fusion 排序鍵從 `x["score"]` 改回 `x.get("score", 0.0)`,「缺 score 要拋錯」那條斷言也如期翻紅(`KeyError` 不再發生)。

**4. 未標檢查要吃 CLI 的 `-k`**(`t_eval_unjudged_check_honours_cli_k`):守衛本身守得住,但文件裡宣稱的翻紅條號是錯的(見下方發現一)。把 `main()` 裡兩處 `k=args.k` 都拿掉,測試仍然翻紅、觀察到 `k=[8, 8]`;把 `LUMOS_EVAL_HISTORY` 導向那行拿掉,測試在跑到 `main()` 之前就被自帶的 `assert` 擋下並丟例外,正式的 `governance/eval/retrieval-eval-history.jsonl` 位元組經 md5 核對前後一致——這道「先擋後跑」的順序是真的,不是擋在損害之後。

**5. 摘要符號詞彙表單一來源+抓錯字正則吃得到連字號**(`t_symbol_vocab_single_source_and_reach`):守衛本身守得住,但文件裡宣稱的翻紅條號是錯的(見下方發現二)。把 `SYMBOL_RE` 改回獨立寫死的九值(不含 `PRIOR-ART`/`REVISIT`),測試如期翻紅;把 `SYMBOLISH_RE` 改回 `^([A-Z]{2,}):`(不吃連字號),測試也如期翻紅——而且這支測試驗的是「詞彙表裡每個值,正則真的認得出來」的實際比對行為,不是掃原始碼文字,能擋住「表面還寫著、推導時偷偷漏一個值」這種變異(已用第一個變異驗證過:只改 `SYMBOL_RE` 不改 `SYMBOL_NAMES`,測試立刻抓到兩者不一致)。

**6. 觸及集上下界**(`t_eval_touched_universe_bounds`):守得住。除了測試自己驗過的形狀外,額外補做兩個變異:退化回單臂(free 側只剩 8 個)讓下界與 bm25/graph 前 8 檢查翻紅;拿掉 `[:k]` 截斷(free 側暴增到 40 個)讓上界檢查翻紅。上界寫成「至多 3 條窗×k」、下界寫成「必多於單臂的 8 個」,兩端都有鑑別力,不是恆真斷言。

## 發現

### 發現一:CLI k 未接線測試的翻紅釘條號寫錯

測試 `t_eval_unjudged_check_honours_cli_k` 的說明宣稱拆掉 `k=args.k` 會讓「第 2 條」斷言翻紅,但這支測試共 4 條斷言,實際拆除後翻紅的是第 4 條(「★每一次未標判定拿到的視窗都是 CLI 給的 12,不是預設 8★」),第 1–3 條(正式帳未變動 / fixture 帳有寫到 / main 有呼叫到未標判定)仍然照樣通過。測試本身的判定邏輯沒有問題——它確實會在 bug 重現時翻紅——只是這句對照原始碼位置的說明文字會讓人找錯斷言。

severity: minor
blocking: 否——測試的殺傷力不受影響(拆修法照樣翻紅、還原照樣轉綠),只是註解裡的斷言編號需要更正,不影響這批改動能否合併。
引句:「翻紅釘:①把那兩處的 k=args.k 拿掉 → 第 2 條翻紅(觀察到的 k 出現 8)」

### 發現二:符號詞彙表連字號正則測試的翻紅釘條號寫錯

測試 `t_symbol_vocab_single_source_and_reach` 的說明宣稱把 `SYMBOLISH_RE` 改回 `^([A-Z]{2,}):`(拿掉連字號支援)會讓「第 3 條」翻紅,但這支測試共 9 條斷言,第 3 條是「② 詞彙表含 PRIOR-ART 與 REVISIT」——這條只檢查 `SYMBOL_NAMES` 集合本身,跟 `SYMBOLISH_RE` 完全無關,實測依然通過。真正翻紅的是第 5、6 條(「★正則伸得到含連字號的前綴★」與「★不空過:打錯字的含連字號變體仍被抓到★」)。同一支測試裡的第一個變異(`SYMBOL_NAMES` 改回獨立字面集合)宣稱的「第 1 條」翻紅則完全準確。

severity: minor
blocking: 否——測試邏輯本身正確且有鑑別力(該翻紅時真的翻紅),純粹是說明文字的斷言編號對不上,修正一下註解即可,不需要動測試邏輯或阻擋這次改動。
引句:「②把 SYMBOLISH_RE 改回 ^([A-Z]{2,}): → 第 3 條翻紅"""」

## 變異測試結果表

| 測試 | 植入什麼 | 跑哪支 | 實際輸出 | 判定 |
|---|---|---|---|---|
| `t_eval_switch_equal_same_question_set` | `_macro_on` 拿掉 `gate_key` 篩選(退化成 `_macro`) | 同名測試 | `★_macro_on 只算新尺也認可的題★  0.5667`(預期 0.8)翻紅,其餘 4 條綠;還原後 5 條全綠 | 守得住 |
| `t_eval_switch_equal_no_data_is_not_equal` | `_switch_equal` 對兩側皆 `None` 的分支改回單純 `continue` | 同名測試 | 第 1、3、4 條翻紅(與說明宣稱一致),第 2、5 條仍綠;還原後 5 條全綠 | 守得住 |
| `t_eval_eq_keys_are_wired_in` | `report_goldset` 五處 `_macro_on(...)` 全改回 `_macro(...)` | 同名測試 | 第 2、3、4 條翻紅(與說明宣稱一致:`_rn_eq`=0.5667≠0.8、`_ln_eq`=0.5≠0.7、舊鍵與壞掉的限縮鍵變相等);還原後 4 條全綠 | 守得住 |
| `t_eval_touched_edit_covers_all_arms` | `_touched_edit` 退化回 `free[:k]`(單臂,`free` 用原始未排序順序) | 同名測試 | 第 2、3 條翻紅(與說明宣稱一致:只比文字/只比圖的前 2 名不在觸及集);還原後 5 條全綠 | 守得住 |
| `t_eval_edit_orders_single_source` | 讓 `_touched_edit` 的 fusion 臂改回沿用未排序上游順序(bm25/graph 仍走 `_edit_orders`) | 同名測試 | 第 2 條翻紅(k=1 fusion 檢查漏掉 A.md,與說明宣稱一致);還原後 11 條全綠 | 守得住 |
| `t_eval_edit_orders_single_source` | `_edit_orders` 的 fusion 排序鍵改回 `x.get("score", 0.0)` | 同名測試 | 最後一條(缺 score 應拋錯)翻紅,`KeyError` 不再發生;還原後 11 條全綠 | 守得住 |
| `t_eval_unjudged_check_honours_cli_k` | `main()` 兩處 `collect_unjudged(..., k=args.k)` 都拿掉 `k=args.k` | 同名測試 | 第 4 條翻紅(觀察到 `k=[8, 8]`),第 1–3 條仍綠;還原後 4 條全綠(說明文字宣稱是第 2 條,實測是第 4 條——見發現一) | 守得住(文件編號有誤) |
| `t_eval_unjudged_check_honours_cli_k` | 拿掉 `os.environ["LUMOS_EVAL_HISTORY"] = str(_hist)` 這行導向 | 同名測試 | 測試在跑到 `main()` 前就因自帶 `assert` 丟出例外(`拒跑:評測歷史帳沒導向 fixture...`),`retrieval-eval-history.jsonl` md5 前後一致、未被寫髒;還原後 4 條全綠 | 守得住(擋在損害之前) |
| `t_symbol_vocab_single_source_and_reach` | `SYMBOL_RE` 改回獨立字面九值(不含 `PRIOR-ART`/`REVISIT`),`SYMBOL_NAMES` 不動 | 同名測試 | 第 1 條翻紅(與說明宣稱一致:認不出來的 `['PRIOR-ART', 'REVISIT']`);還原後 9 條全綠 | 守得住 |
| `t_symbol_vocab_single_source_and_reach` | `SYMBOLISH_RE` 改回 `^([A-Z]{2,}):`(不吃連字號) | 同名測試 | 第 5、6 條翻紅,第 3、4 條仍綠;還原後 9 條全綠(說明文字宣稱是第 3 條,實測是第 5、6 條——見發現二) | 守得住(文件編號有誤) |
| `t_eval_touched_universe_bounds` | `_touched_edit` 退化回單臂 `free[:k]` | 同名測試 | 下界檢查(「必多於單臂的 8 個」)與 bm25/graph 前 8 檢查共 3 條翻紅;還原後 9 條全綠 | 守得住 |
| `t_eval_touched_universe_bounds` | `_touched_edit` 三臂迴圈拿掉 `[:k]` 截斷 | 同名測試 | 上界檢查(「至多 3 條窗×k」)翻紅(實測 40 個);還原後 9 條全綠 | 守得住 |

## 補充查證

- `_edit_orders` 確實是排序鍵的唯一來源:`grep -n 'sorted(free'` 在 `governance/eval/retrieval_eval.py` 全檔只命中 `_edit_orders` 內的三行(`fusion`/`bm25`/`graph`),`eval_edit` 與 `_touched_edit` 都改成呼叫它,沒有第二份手寫排序鍵殘留。file: `governance/eval/retrieval_eval.py:466`、`governance/eval/retrieval_eval.py:200`、`governance/eval/retrieval_eval.py:493`。
- `collect_unjudged` 內部呼叫 `_touched_edit(res, k)` 時的 `k` 確實一路從 `main()` 的兩處呼叫點傳入,鏈路完整,不是巧合放行。file: `governance/eval/retrieval_eval.py:275`。
- 三支被拿去做變異測試的檔案(`governance/eval/retrieval_eval.py`、`scripts/lumos`、`scripts/test_lumos.py`)收工前用 `diff -q` 核對,與 repo 內原檔逐位元組相同,沒有殘留改動。

全篇最高等級為輕微,阻塞項為零條。
