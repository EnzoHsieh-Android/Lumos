severity: minor

## b1 推送前碰到計劃改用快取,沒有測試釘住「一定命中」
severity: minor
blocking: 否。拿掉快取只讓重算多花時間,判定結果不變,實測成本小。

這一輪拿掉了 `_CHOICE_GUARD_FLOOR`(時限底線),把「碰到的計劃一定命中判要不要求時的快取」當作時限保證。這個保證現在沒有任何測試守著。

引句:「guard, why = _choice_guard(rr, rng, at_sha, cache=cache)   # 碰到的計劃吃判要不要求時的快取(_choice_push_scan)」

- file: `scripts/lumos:78571`
- 我把這行改成 `cache=None`,再跑 `python3.14 scripts/test_lumos.py -k spec_gate_push_choice`,結果是 `42 passed, 0 failed`,測試照綠。`-k choice_scan_batch_budget` 也是 2 passed。
- 沒有測試引用 `_choice_spec_calc` 或 r3 g1。改成 `cache=None` 後,`_choice_guard` 以 `deadline=None` 重算,不再受推送時限約束。
- 實測影響:在 2 萬檔的 repo 上,不經快取算一次 `_choice_spec_calc` 約 0.7 秒。
- 現況成立:`_choice_requirement` 在回傳 True 之前一定先呼叫 `_choice_spec_calc`,而且快取鍵 `("spec", rng, at_sha)` 與 guard 用的相同,所以目前一定命中。
- 歸因:未判定。修前版本靠 `_CHOICE_GUARD_FLOOR` 保底,修後改為依賴快取,這個缺口是修補換機制後出現的。我沒有在修前版本跑同一個改壞,所以不能判定是回歸。

## 三問

**① 原問題的修復效果(兩版證據)**

**整批掃描靜默零命中(r3 c1 b1)**
- 做法:暫存目錄放在 `.gitignore` 寫 `*.kt` 的 git repo 底下,檔名用中文(`app/測試/檔N.kt`,內含 emoji 與中文字串),直接呼叫兩版的 `_choice_scan`。
- 修前(`dbdc0386`):1 檔得 1 命中;2 檔得 0 命中;3000 檔得 0 命中。`bad` 為空,也就是靜默漏掉。
- 修後(`24ec7896`):1 檔得 1;2 檔得 2;3000 檔得 3000,共 0.7 秒。
- 底層用 `ast-grep 0.51.2` 指令確認:同一個目錄不帶 `--no-ignore` 得 0 行,帶六種得 2 行;單點名檔案本來就能掃到 1 行。
- 另試目錄名以點開頭、且有 `.ignore` 寫 `*` 的情況:修前 0 行,修後 2 行。

**測試名寫成 `類別.方法`(r3 a1)**
- 做法:自建 repo,對兩版呼叫 `_choice_test_blobs`。
- 修前:`FooTest.bar` 得到 `?`(不明標記);`FooTest.nothere`、`FooTest.解析`、`a.b.c` 也得 `?`。
- 修後:`FooTest.bar` 得到真的物件編號,`bar` 與反引號句子名 `解析 1.5 值`、`bar handles empty` 的結果與修前相同。
- 驗過的 preserve:`FooTest.nothere` 仍是 `?`(找不到所在檔就多跑,符合設計)。
- `git grep -o` 有多個 `-e` 時取最長匹配(實測 `bar` 與 `bar handles empty` 同行,只回長的),所以點號名取最後一段後,不會把句子名吃掉。
- 修後的新測試 `t_choice_test_blobs_name_shape`、`t_choice_scan_batch_no_ignore`、`t_choice_scan_batch_share`、`t_choice_kill_partial_unverified_rc` 在修後都綠(`-k` 子集)。

**② 修補處的正常、錯誤與相鄰呼叫路徑**
- 單檔路徑(`len(names) <= 1` 不走整批):修後 1 檔仍得 1 命中。
- 逐檔退回路徑(`_choice_scan_one`):不帶 `--no-ignore` 也掃得到被忽略的檔(上面指令實測),退回路徑不受影響。
- 整批卡住時只用掃描時限的一半,其餘留給逐檔:`t_choice_scan_batch_share` 綠。
- 拿掉 `_CHOICE_GUARD_FLOOR` 後仍有引用的地方:全 repo `grep` 該符號,程式與筆記都沒有殘留。
- `_choice_push_scan` 回傳值從三元組改成二元組,呼叫端與測試都已同步。

**③ 新發現在修前、修後各是什麼**
- 只有 b1。修後 `cache=None` 的改壞測試仍綠。我沒有在修前版本重跑,這條歸因未判定。

## 其他已驗的邊界(正向主張)
- 回報上限邊界:讀了 `_choice_cap_pick`。`len(keys) <= cap` 時全收,等於上限時不抽樣,沒看到邊界錯誤。
- 回報上限邊界的未驗範圍:`cap=0` 的組合我只讀碼,沒有造輸入實跑。
- J4 兩項(rc 2 與 doctor 另列):這輪只新增測試,程式本來就有。`scripts/lumos:78223` 的 rc 運算式含 `res.get("unverified")`。`_lint_waivers_doctor_bits` 把選擇點放行另列成「另有選擇點放行 N 條」。兩個測試修後都綠。

## 圖譜鏡頭
這次沒附固定席節點(hook 回報計算超時)。我只確認修補改到的 `規格閘.md` 兩筆 PITFALL 與計劃文字,都沒有指到已刪的符號,引用的測試名都存在。

## 未驗範圍
- ast-grep 版本太舊、不認得 `--no-ignore global` 等值時的行為:整批會回 rc 2 並退回逐檔,行為上能退,但我沒用舊版實測。
- 非 ASCII 的 `類別.方法`(例如 `FooTest.解析`):`_dotted_ident` 只認 ASCII 識別字,所以永遠是 `?`、存活的行每次重跑。這是修前就有的行為,只多跑不漏,不算 finding。
- 全程用臨時 clone 實驗,已刪除,沒有改 repo。

最嚴重:minor;blocking 共 0 條
