severity: clean

本輪沒有 finding。查證用的臨時副本(修前、修後各一份)已刪。

## 三問

**①原問題的修復效果**

- 原問題是 choice-kill 對「不唯一」的行印出照貼的 `lint-waive` 指令,檔名含 `$(…)`、空白或單引號時貼進 shell 會被展開或切開。
- 修後版(83ac95c8e)已修好。`scripts/lumos` 第 78210 行改成整個 `choice:<檔>:<行>` 參數先過 `_sh_quote`,再過 `_kill_esc`。
- 修後跑 `python3.14 scripts/test_lumos.py -k t_choice_kill_waive_hint_shell_quote`,3 條斷言全過。
- 修前版 04b21d1ff 套上新測試檔後跑同一條指令,2 條紅,印出 `lumos lint-waive choice:app/src/main/Foo$(touch PWNED) x.kt:12 --note …`。
- 我在修後版把 `_sh_quote` 拿掉再跑,同樣紅 2 條(`$(touch PWNED)` 與 `It's.kt`),所以這條測試確實釘住這個修補。
- 同族掃描:`scripts/lumos` 77640–79200 行裡,把真實檔名組進指令的只有第 78210 與 78791 兩處。78791(`situation-rule --point`)本來就走 `_sh_quote`。其餘 78222、78324–78326 只印 `<檔>` 占位字,78046、78668 是訊息不是指令,不用處理。

**②修補處的正常、錯誤與相鄰呼叫路徑**

- 一般 ASCII 檔名:`app/src/main/java/x/Vm.kt` 的 `shlex.split` 結果仍是 `["lumos", "lint-waive", "choice:<檔>:12", "--note", "不適用:<理由>"]`,放行鍵格式不變。
- `t_choice_kill_waive_hint_shell_quote` 的 3 條斷言全過。
- 檔名含控制字元時,`_kill_esc` 會把它換成可見的 `\uXXXX`,貼上去後鍵對不上,`lint-waive` 會拒絕。這是安全失敗,不是新洞。

**推送前快取(K2)**

- `_choice_push_round`(`scripts/lumos`)把 `cache=cache` 傳給 `_choice_guard`。
- 修後版跑 `-k t_spec_gate_push_choice_guard_cache`,2 條過。
- 我把 `cache=cache` 拿掉再跑,紅在「計劃只算 1 次」,`calls` 有 2 筆。
- 修前版這條測試也是綠的,所以 K2 是補測試,不是改行為;preserve 沒有被動到。

**點號名取最後一段(K3)**

- `_choice_test_blobs` 用 `n.rsplit(".", 1)[-1] if _dotted_ident(n)` 取最後一段。
- 修後版 `-k t_choice_test_blobs_name_shape` 共 8 條過。
- 我把最後一段改成第一段再跑,紅 2 條:`QuxTest.zap` 找不到 Other.kt,雜湊停在 `?`。
- 修前版這條測試也綠,所以 K3 同樣是補測試,不是改行為。

**③新發現**

沒有新發現,所以沒有同案例的修前、修後對照。

## 鏡頭 1:文件對照 `scripts/lumos`

- **計劃〈範圍〉兩句新增**
  - 「點號名只拿最後一段」與 `_choice_test_blobs` 的實作一致。
  - 「整批掃描關掉忽略規則(`--no-ignore` 六種)」與 `_CHOICE_SG_NO_IGNORE`(`scripts/lumos` 第 77035 行,hidden、dot、exclude、global、parent、vcs 共六個)一致。
- **Systems/規格閘 新 PITFALL**
  - 引用的 `_sh_quote`、`_kill_esc` 和修法都跟程式一致。
  - 兩支測試引用都存在:`t_choice_scan_batch_share`(`scripts/test_lumos.py:145701`)、`t_choice_kill_partial_unverified_rc`(`:145718`)。
  - 新 PITFALL 引用的 `t_choice_kill_waive_hint_shell_quote` 也存在。
- 計劃〈存活的處置〉沒有寫照貼指令的引號形狀,所以沒有文字跟不上。

## 鏡頭 2:合約

- Systems/guard-kill 兩條 ★INVARIANT★,修補差異完全沒碰 `cmd_guard_kill`。我在修後版跑綁定測試:
  - `t_guard_kill_rc_precedence`:4 條過。
  - `t_guard_kill_json_purity`:6 條過。
- 本輪改到的筆記裡沒有合約行被動到:計劃與規格閘只加了 PITFALL 與範圍說明。

## 圖譜鏡頭

- 派工尾端沒附固定席節點(鏡頭計算超時),所以沒有逐條判定可寫。
- 就我讀到的差異,本輪實際動到的程式只有 `_choice_kill_report` 的一行。它不影響 guard-kill 的 rc 優先序與 JSON 純淨度,上面兩支測試也驗過。

## 未驗範圍

- 沒跑不帶 `-k` 的全套,也沒驗真 Android 專案的端到端。
- 控制字元檔名下 `_kill_esc` 疊在引號外的行為只用推理判斷,沒實測。
- 修後版 `scripts/test_lumos.py` 裡有一處排版 `both =[{`(等號後少空格);我沒找到會造成失敗的場景,所以沒列 finding。

最嚴重:clean;blocking 共 0 條
