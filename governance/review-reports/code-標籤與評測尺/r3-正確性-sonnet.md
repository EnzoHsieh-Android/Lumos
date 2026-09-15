severity: blocker

（審查方法：把 e75b883c 三支相關檔案複製到 /tmp 沙盒、依相對路徑重建成與正式 repo 一致的結構，`patch -p1` 套上 r3-final.patch 裡 `governance/eval/retrieval_eval.py`／`scripts/lumos`／`scripts/test_lumos.py` 三段 diff，全部乾淨套用；正式 repo 全程未被 git 操作，只讀 `r3-final.patch`。變異測試改的是 /tmp 沙盒複本，改完清 `__pycache__` 再跑。）

## 發現一：新增的守護測試會把假資料寫進真正的治理帳本檔（第一優先，最後折進去的那個修正自己帶的新問題）

`t_eval_unjudged_check_honours_cli_k` 是這輪新增、專門守「`collect_unjudged` 要吃 `args.k` 不能用預設 8」這個修正的測試。它直接呼叫 `m.main()`：

引句:「sys.argv = ["retrieval_eval", "--goldset", str(p), "-k", "12"]」

但 `main()` 跑到底一定會把這輪結果寫進歷史帳：

引句:「LUMOS_EVAL_HISTORY:測試導向 fixture 帳,避免 e2e 測試污染真 history(code-r1 修)」

——這行註解講得很清楚：本檔已經知道「直接呼叫 `main()` 會污染真 history」這個坑，並且準備了 `LUMOS_EVAL_HISTORY` 環境變數當逃生門（另一支 e2e 測試 `t_refresh_full_chain_and_eval_e2e` 有設這個環境變數）。但這支新測試從頭到尾沒有設 `LUMOS_EVAL_HISTORY`，也沒有把 `hist` 的寫入目標導向任何隔離路徑。

`main()` 裡真正決定寫去哪的邏輯是：

`hist = Path(os.environ.get("LUMOS_EVAL_HISTORY") or Path(__file__).parent / "retrieval-eval-history.jsonl")`

而載入這支模組的 `_load_retrieval_eval()` 是用 `importlib.util.spec_from_file_location(..., repo / "governance" / "eval" / "retrieval_eval.py")` 直接指向**正式 repo 裡的真檔案**（只是把 `m.ROOT`／`m.VAULT` 兩個變數重新指到 fixture 目錄，模組本身的 `__file__` 完全沒變）。所以 `Path(__file__).parent` 解析出來的，不是任何 fixture 或臨時目錄，就是正式 repo 的 `governance/eval/` 目錄，也就是這支測試沒設環境變數時，寫入目標=真正的 `governance/eval/retrieval-eval-history.jsonl`。

**我做了實測驗證**（不是臆測）：把 e75b883c 版的三支檔案原封不動複製到 `/tmp` 沙盒，保留完全相同的相對路徑結構（`scripts/test_lumos.py`、`scripts/lumos`、`governance/eval/retrieval_eval.py` 三者的相對位置與正式 repo 一模一樣），套上 r3-final.patch，跑 `python3 scripts/test_lumos.py -k t_eval_unjudged_check_honours_cli_k`。測試綠燈通過的同時，沙盒裡的 `governance/eval/retrieval-eval-history.jsonl` 從不存在變成新增一行 JSON，內容帶著 fixture 產生的假 `goldset_rev`（如 `34c71678e723`）、假 `eval_head`（fixture 臨時 git repo 的 HEAD 短碼）、以及 `"k": 12` 等與真評測完全無關的資料。這條路徑解析邏輯（`Path(__file__).parent`）在正式 repo 裡跑起來完全相同，因為它不看 cwd、只看模組檔案物理位置——這就是正式 repo 執行這支測試時會發生的事，不是沙盒才有的假象。

`governance/eval/retrieval-eval-history.jsonl` 是 git 追蹤、有真實提交歷史的治理帳本（`git log` 可查到多筆提交只動這個檔），本分支自己的 diff 裡也對它做過正式的資料修改（`diff --git a/governance/eval/retrieval-eval-history.jsonl`）。這支測試會被 `scripts/test_lumos.py` 的全域掃描自動收進完整測試集（`[k for k in globals() if k.startswith("t_")]`），也就是每次推送前的全套跑（CLAUDE.md 講的「全套留給推送前的閘」）跟 CI 都會執行到它——等於**每次推送前跑全套，工作樹就會多一筆髒改動**，如果沒人注意到就手滑一起提交，這本「帳本連續」的治理帳就永久混進一筆假資料。更壞的可能：`_history_metric_rev` 是靠「history 任一列帶 `metric_rev` 即已切換」的 sticky 判定；雖然本次實測這支測試寫入的紀錄沒有帶 `metric_rev`（因為 fixture 資料的未標數不是 0，沒有觸發切換分支），但那是這次 fixture 湊巧的行為，不是任何機制擋著——如果日後 fixture 或執行環境變動使得 fixture 資料剛好未標=0 且恆等斷言剛好過，這支測試就會把「尺切換已完成」這個★切了不回頭★的旗標，寫進正式治理帳，而且是用假資料觸發的。

修法很直接：仿照同檔案已有的 `t_refresh_full_chain_and_eval_e2e`，在呼叫 `m.main()` 前後用 `os.environ["LUMOS_EVAL_HISTORY"]` 指到 `root` 底下的臨時檔案即可，不需要新機制。

severity: blocker
blocking: 是——每次執行全套測試（推送前的閘、CI）都會真的寫一行假資料進正式治理帳本檔 `governance/eval/retrieval-eval-history.jsonl`，已用 /tmp 沙盒實測重現；不是理論風險。

## 發現二：`k=args.k` 這個修法本身是對的，沒有改出反向錯

比對三個呼叫點：`ablation_blocked` 內部呼叫（本來就對）用 `k=args.k`；計分視窗 `report_goldset(gs, sp, k_edit=args.k)`（本來就對，未被這輪動到）；這輪改的兩處——尺切換判定與 held 未標率印出——原本完全沒傳 `k`（等於恆用 `collect_unjudged` 自己的預設值 8），改成把 `args.k` 傳進去。三處現在口徑一致，沒有發現任何本該維持 8、卻被誤改成 `args.k` 的位置：`-k` 這個 CLI 旗標的語意本來就是「edit 面算分要看前幾名」，未標檢查理應同界，不存在「這裡本來就該用 8」的正當理由。

引句:「★視窗要跟計分同界★(2026-09-15 code-r3):不傳 k 會永遠用預設 8,」

**變異測試**（在 /tmp 沙盒進行，正式 repo 未被觸碰）：

| 植入什麼 | 跑哪支 | 輸出是什麼 |
|---|---|---|
| 無（照 r3-final.patch 原樣套用） | `t_eval_unjudged_check_honours_cli_k` | `2 passed, 0 failed` |
| 把 `governance/eval/retrieval_eval.py` 裡兩處 `collect_unjudged(gs, args.split, k=args.k)` / `collect_unjudged(gs, k=args.k)` 改回不傳 `k`（等同修法被拆掉），另一處 `unj = collect_unjudged(gs, "held", k=args.k)` 也改回不傳 `k` | `t_eval_unjudged_check_honours_cli_k` | 第 2 條斷言翻紅：`★每一次未標判定拿到的視窗都是 CLI 給的 12,不是預設 8★  觀察到的 k=[8, 8]——有 8 就是沒把 args.k 傳下去`；第 1 條（有呼叫到）仍過；`1 passed, 1 failed` |
| 還原修法、清 `__pycache__` | 同上 | 回到 `2 passed, 0 failed` |

這支測試不是空過：它會真的因為修法被拆掉而翻紅，而且翻紅訊息點出的正是被拆掉的那兩個呼叫點（`seen=[8, 8]`，剛好兩次呼叫都退回預設值）。第一條斷言（`len(seen) >= 1`）也守住了「被測路徑根本沒跑到」這種空過——若 spy 一次都沒被呼叫到就會先在這條掛掉，不會誤判成通過。

severity: clean
blocking: 否——修法正確、變異測試證實有效攔截，沒有找到反向錯或空過。

## 發現三：`_edit_orders` 唯一實作沒有漏掉呼叫路徑；`_switch_equal` 沒找到會誤放行的路徑

全檔搜尋排序鍵的建構點（`sorted(free`／`sorted(_f`／`_graph_score(x)`／`x.get("L"`），只剩 `_edit_orders` 一處定義；`_touched_edit`（呼叫 `_edit_orders(_f).values()`）與 `eval_edit`（呼叫 `orders = _edit_orders(free)`）都改吃它，`collect_unjudged`／`ablation_blocked` 只透過 `_touched_edit` 間接使用，沒有第三份手寫排序鍵。`_macro_on` 的兩個過濾鍵（`_rn_eq` 用 `c_ranked_ndcg`、`_ln_eq` 用 `c_legacy_ndcg`）雖然各自獨立，但因為 `_switch_equal` 是逐指標比對（`_rn_eq` 只跟 `cs.get("ndcg")` 比、`_ln_eq` 只跟 `cs.get("ndcg_legacy")` 比），每一組比較用的都是同一個過濾鍵圈出來的同一批題，不會出現「用甲指標的有效題子集去跟乙指標的全題平均比」這種混用；兩邊同時 `None` 的分支也已經是「列成差異、擋下切換」而非放行，只有讓判定變更嚴，沒有找到讓它變寬鬆、誤放行的路徑。

引句:「改這裡就是同時改兩邊;有測試斷言兩邊前 k 一致(t_eval_edit_orders_single_source)」

severity: clean
blocking: 否——排查沒有發現漏接的呼叫路徑或會誤放行的恆等判定路徑。

## 發現四（觀察，非阻塞）：`_edit_orders` 的 fusion 排序鍵從硬性索引改成防禦式預設值

抽成 `_edit_orders` 時，fusion 那條的排序鍵從 `x["score"]`（缺欄位就丟 `KeyError`）改成 `x.get("score", 0.0)`（缺欄位靜默當 0 分排到榜尾）：

引句:「"fusion": sorted(free, key=lambda x: (-x.get("score", 0.0), x["node"])),」

理論上這會讓「上游 `impact --ranked` 回傳的候選漏了 `score` 欄位」這種資料異常，從原本會讓程式當場炸掉、逼人注意到，變成悄悄把該候選排到最後、繼續往下跑。查過 `scripts/lumos` 的 `impact` 輸出路徑（`pins + free + rescued` 組裝前，每個候選都在同一輪打分邏輯裡被賦值 `score`），目前沒有找到任何真實輸出會缺這個欄位的分支，這點跟本分支既有的（r2 已核過）「實測真實輸出全部帶該欄位」結論一致，我沒有找到能推翻它的新路徑。列出來是因為這是本次抽取單一實作時，一併悄悄放寬的防呆邊界，值得留意，不是本輪要處理的缺陷。

file: `scripts/lumos:23329`（候選组裝點 `final = pins + free + rescued`，往上追每個來源都在賦值 `score` 之後才加入清單）

severity: minor
blocking: 否——目前所有已知生產路徑的候選都帶 `score` 欄位，不會觸發；只是把原本會讓資料異常提早曝光的硬斷言換成靜默容錯，日後若上游輸出格式漂移會更晚才被發現。

## 總結

發現一是本次「最後折進去的修正」自己帶的新問題：它要驗證的核心邏輯（`collect_unjudged` 該不該吃 `args.k`）修得對、測試本身也真的守得住（變異測試證實），但驗證手法本身（直接呼叫 `main()` 又沒隔離歷史帳寫入路徑）會在每次全套測試時把假資料寫進正式治理帳本檔 `governance/eval/retrieval-eval-history.jsonl`，已用沙盒實測重現，不是理論推測。建議在提交前補上 `LUMOS_EVAL_HISTORY` 隔離（比照同檔案的 `t_refresh_full_chain_and_eval_e2e`），一行環境變數即可解決。

全篇最高等級是阻塞級,阻塞項 1 條(發現一)。

## 驗收(2026-09-15)

方法:先比對 `r3-final.prev.patch`(我上次審的版本)與 `r3-final.patch`(這次的凍結版本),逐檔比對兩份 patch 裡每一支檔案的 diff 內容,確認只有三支檔案不同:`scripts/test_lumos.py`、`governance/eval/retrieval-eval-history.jsonl`、`docs/lumos-toolchain-knowledge/Issues/尺切換恆等斷言反覆不過.md`;`governance/eval/retrieval_eval.py` 與 `scripts/lumos` 兩版逐位元組相同,跟你說的一致。所有實驗都在自己的 `/tmp` 沙盒裡、對 e75b883c 基準套上 patch 後進行,沒有對 repo 根跑任何 git 寫入指令,也沒有跑到任何會寫進真歷史帳的東西。

### 逐塊查證

**① 導向 fixture、跑完還原**:讀了新版 `t_eval_unjudged_check_honours_cli_k`,它把 `LUMOS_EVAL_HISTORY` 導到 `root / "fixture-history.jsonl"`,並在 `finally` 用 `_env_old` 分兩種情況還原(原本沒設就 `pop` 掉、原本有設就設回原值)。我在同一個 Python process 裡各自驗證兩個分支:先塞一個 sentinel 字串進 `LUMOS_EVAL_HISTORY` 再跑這支測試,跑完環境變數精確變回那個 sentinel;另外清空這個環境變數再跑一次,跑完環境變數精確變回未設定。兩種情況都對。

**② 硬前置 assert**:只拿掉 `os.environ["LUMOS_EVAL_HISTORY"] = str(_hist)` 這一行、`assert` 那行原樣保留,在沙盒重新跑這支測試,得到:

```
✗ t_eval_unjudged_check_honours_cli_k EXCEPTION: 拒跑:評測歷史帳沒導向 fixture,跑下去會寫進正式帳
```

跑之前我在沙盒的「正式帳」位置預先塞了兩筆假的既有紀錄,跑完前後檔案 md5 完全一致(`0df338b316d5ce6fb56f4c852c266f3a`)——確認 assert 真的擋在 `m.main()` 之前執行,一個位元都沒被動到。這是我自己獨立重跑出來的結果,不是採信你的說法;跟你描述的「拒跑」訊息與「一個位元沒動」吻合。

**③ 事後斷言**:讀了程式碼,兩條斷言分別驗「正式帳前後 bytes 相同」與「fixture 帳確實存在」。為了確認這兩條斷言本身有沒有殺傷力(不是裝飾),我另外做了一個更壞情境的變異:把導向那行「和」assert 那行一起拿掉(等於假設前置守衛整組失效)。結果 `main()` 真的跑下去,往沙盒裡的「正式帳」多寫了一筆假紀錄,這兩條事後斷言雙雙翻紅,訊息正確指出「這支測試呼叫了 main(),沒導向 fixture 就會往受版控的真帳 append 假紀錄」與「導向了卻沒產生 fixture 帳」。證明這兩條真的會抓到「導向失效」這件事,不是恆真的裝飾斷言。

把修法還原、重跑正常路徑,四條斷言全綠;沙盒裡預先塞的兩筆「正式帳」假既有紀錄原封不動,新增的 fixture 帳也確實被寫進 fixture 目錄(證明導向不是沒被走到)。

### 對照真實 repo 現況

拿 e75b883c 版的 `governance/eval/retrieval-eval-history.jsonl` 分別套上 `r3-final.prev.patch` 與 `r3-final.patch` 裡這支檔案的 diff,重建出兩個完整版本:base 100 行、prev 版 109 行(比 base 多 9 筆)、final 版 105 行(比 base 多 5 筆,而且逐筆核對都能對到這個 repo 裡真實存在的 commit)。重建出來的 final 版與現在 repo 裡實際的 `governance/eval/retrieval-eval-history.jsonl` 逐位元組相同。prev 版裡多出、final 版裡沒有的那 4 筆全部帶著同一個指紋:`goldset_rev: "34c71678e723"`、`k: 12`、`goldset_snapshot: null`,`eval_head` 分別是 `1fbf35f`/`621f157`/`d8f28c8`/`c6d831e` 四個短碼,拿 `git cat-file -t` 逐個查全部回「不是合法物件」——不是真評測留下的,是夾具跑出來的假紀錄,現在的 final 版裡確實一筆不剩。值得一提:這 4 筆全部都帶著 `"metric_rev": "condensed-v1"`,也就是這個 bug 曾經真的把「尺切換已完成」這個不可逆的旗標寫進過正式帳一次——我原報告裡講的「最壞情況」不是純理論,是真的發生過,現在已經清乾淨了。

有一點要更正:你的訊息與新知識圖譜筆記裡都寫「清出 5 筆」,但我直接拿 base+patch 重建、逐筆核對指紋算出來的數字是 **4 筆**——105 比 100 多的那 5 筆是「淨增加的合法紀錄」,不是「被清掉的假紀錄」;109 比 105 多的 4 筆才是真正被清掉的假紀錄。這不影響這條的驗收結論,但你要求獨立查證、不要採信說法,這個對不上的數字我如實列出來。

### 結論

三塊修法(導向 fixture、跑完還原環境值、硬前置 assert 拒跑、事後雙重斷言)都如描述運作,逐塊經我自己獨立的變異測試驗證有效,不是採信你的說法;現在 repo 裡的正式歷史帳與從 base+patch 重建出來的結果逐位元組一致,105 筆均可對應到真實 commit,先前混入的假紀錄已確認清除乾淨(僅「清出幾筆」這個數字對不上,實際是 4 筆不是 5 筆)。這條算修好。

## 第四條折入驗收(2026-09-15)

方法:比對 `r3-final.prev3.patch`(我上一輪確認的版本)與 `r3-final.patch`(這次的凍結版本),逐檔比對每一支檔案的完整 diff 內容。兩版檔案清單一樣(都是 46 支),只有三支內容不同:`governance/eval/retrieval_eval.py`、`scripts/test_lumos.py`、`docs/lumos-toolchain-knowledge/Issues/尺切換恆等斷言反覆不過.md`,跟你說的一致。所有實驗都在自己開的 `/tmp` 沙盒對 e75b883c 基準套上 patch 後進行,沒有對 repo 根跑任何 git 寫入指令,也沒有跑到任何會寫進真評測歷史帳的東西。

### ① 恢復硬性取值會不會打到真實路徑

沒有直接採信你的「43/43」數字,自己重新做了兩層查證:

- **靜態追蹤**:讀了 `scripts/lumos` 裡 `cmd_impact` 組裝 `results`/`lane_raw` 的每一個位置——事故固定席、direct(不論 pinned 與否)、indirect 固定席、indirect 參考道、indirect 自由席、`rescued`(複製自既有 direct 項)、`_impact_mark_home` 新增的 home 項——逐一確認:凡是最後會落在「非 pinned、無 lane 欄位」(也就是會被 `split_buckets` 分進 `free`、進而餵給 `_edit_orders`)的項目,建構當下**一律**在同一行字面就寫了 `"score": ...`;唯一不帶 `score` 字面的新增分支(`_impact_mark_home` 裡「還不是候選、直接新增一筆 home 項」那條,雖然它其實有寫 `"score": 0.0`)本身 `"pinned": True`,不會落進 `free`,跟這次改動無關。沒有找到任何一條會產生「非 pinned、無 lane、缺 score」項目的路徑。
- **實測補一刀**:另外自己對真實 repo 跑了幾個不同檔案的 `python3 scripts/lumos impact --file <檔> --ranked --top 50 --json`(唯讀,不寫任何檔),逐一檢查 `free` 桶裡有沒有缺 `score` 的項:

  | 檔案 | 總候選數 | free 桶大小 | free 桶缺 score 數 |
  |---|---|---|---|
  | `scripts/lumos` | 43 | 10 | 0 |
  | `governance/eval/retrieval_eval.py` | 15 | 10 | 0 |
  | `scripts/test_lumos.py` | 35 | 10 | 0 |
  | `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md` | 0 | 0 | 0 |
  | `README.en.md` | 10 | 6 | 0 |

  `scripts/lumos`那筆的「43」跟你說的「43/43」剛好對上,不是巧合——這是同一份真實輸出。

兩層查證(讀程式碼找出每一條會進 free 的路徑、實跑多個真實檔案取樣)都沒找到反例,結論跟你的一致:恢復硬性取值不會打到目前任何已知的真實呼叫路徑。

### ② 新的守衛斷言守不守得住

在沙盒套上 `r3-final.patch` 後,先跑一次乾淨版本:

```
python3 scripts/test_lumos.py -k t_eval_edit_orders_single_source
→ 11 passed, 0 failed(含新增那條「★自由候選缺 score 時排序要直接炸,不得靜默當 0★」)
```

接著自己做變異(不採信你的說法、獨立重跑):把 `_edit_orders` 裡 fusion 那條排序鍵從 `x["score"]` 改回 `x.get("score", 0.0)`,清掉 `__pycache__` 重跑,得到:

```
✗ ★自由候選缺 score 時排序要直接炸,不得靜默當 0★  給了預設值=上游格式漂移會悄悄走樣,而這個視窗餵的是不可逆的尺切換判定
✗ FAILED t_eval_edit_orders_single_source(1 條斷言)
→ 10 passed, 1 failed
```

跟你說的「守衛斷言翻紅」吻合。還原修法、重跑,回到 `11 passed, 0 failed`。

有沒有空過的可能,額外查了兩點:①這條斷言餵的 `_bad = [{"node": "Z.md", "L": 0.1, "kind": "direct"}]` 只有一個元素、且真的缺 `score`——不是空列表(空列表餵給 `sorted()` 時 key function 根本不會被呼叫,就算程式碼是硬性取值也不會拋錯,那樣寫才會是空過;這裡不是這個形狀)。②單獨呼叫 `m._edit_orders(_bad)` 直接印例外,確認拋出的正是 `KeyError: 'score'`,跟測試 `except KeyError:` 抓的型別一致,不是抓到不該抓的例外把它悄悄吃掉。這條斷言是真的會抓到「排序鍵被改回防禦式預設值」這件事,不是裝飾。

### ③ 這次改動有沒有夾帶別的東西

三支檔案逐一核對:

- `governance/eval/retrieval_eval.py`:diff 只有 fusion 那一行從 `x.get("score", 0.0)` 改回 `x["score"]`,加五行說明註解;其餘所有 hunk 內容逐字相同,只有行號因為插入註解而位移。沒有夾帶其他邏輯改動。
- `scripts/test_lumos.py`:diff 只在 `t_eval_edit_orders_single_source` 函式尾端插入這條新守衛斷言(連同三行說明註解);函式其餘內容、以及檔案其他部分逐字相同。沒有新增其他測試或改動既有斷言。
- 知識圖譜筆記:只有一行 KEY 從「r3 有一條 minor ★接受不改★……」改寫成「r3 還有一條 minor ★已折★……」,把折的理由與變異驗證結果寫進去;順帶把我上一輪追蹤的「4 筆 vs 5 筆」數字差異也在另一行 KEY 裡做了訂正說明(標成「驗收席據此訂正」)。沒有夾帶其他內容變動。

另外跑了一次更大範圍的迴歸,`python3 scripts/test_lumos.py -k eval`(沙盒版):修法套用後 111 passed、3 failed;把 fusion 那行改回防禦式預設值後也是同樣那 3 支測試失敗、外加新守衛那 1 條。用 `diff` 核對這 3 支失敗測試在兩種狀態下的錯誤訊息逐字相同(缺 `hist.jsonl`/`dc.json`、about-comparison 差異),判斷是我自己這個精簡沙盒沒帶完整知識庫語料所致,跟這次的排序鍵改動無關,不是這次改動引入的回歸。

### 結論

三點都查完:恢復硬性取值目前沒有任何已知真實路徑會踩到(自己讀程式碼逐路徑核對過,也實跑多個真實檔案取樣,沒有找到反例);新守衛斷言真的守得住,變異測試證實會翻紅,也排除了空過與例外型別對不上這兩種可能;三支改動檔逐一核對過,除了折這條之外沒有夾帶其他東西。這條折入算驗收通過。
