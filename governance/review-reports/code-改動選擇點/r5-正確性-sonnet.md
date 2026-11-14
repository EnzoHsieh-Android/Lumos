severity: minor

## c1 照貼的 lint-waive 指令對含控制字元的檔名會指向別的檔(修補外層的 `_kill_esc` 把引號內的原字元換成字面 `\uXXXX`)
severity: minor
blocking: 否 只會讓照貼的指令找不到檔、不會執行別的東西,而且檔名要含 tab、換行或雙向控制字元才碰得到。

- 輸入:不唯一的行所在檔名含 tab、換行或 U+202E。
- 路徑:`_choice_kill_report` 印出 `_kill_esc(_sh_quote(...))`。`_sh_quote` 先加了單引號,`_kill_esc` 再把引號裡的控制字元換成字面 `\u0009` 這類文字。
- 預期:shlex.split 解回來等於 `choice:<原檔名>:12`。實際:解回來是 `choice:a\u0009b.kt:12`,是另一個檔名。
- 我在 83ac95c8 跑了 `_kill_esc(_sh_quote("choice:"+f+":12"))`,四個檔名的結果:
  - `a\tb.kt` 解回來不等於原值(False)。
  - `a\nb.kt` 解回來不等於原值(False)。
  - `x\u202eY.kt` 解回來不等於原值(False)。
  - `中文 檔.kt` 解回來等於原值(True)。
- 新測試 `t_choice_kill_waive_hint_shell_quote` 只涵蓋 `$(…)`、空白、單引號,沒有控制字元案例。
- 這是安全方向的失敗:放行指令回「找不到」,不會誤放行,也不會執行檔名裡的東西。
- 引句:「f"lumos lint-waive {_kill_esc(_sh_quote(_CHOICE_WAIVE_PREFIX + str(x['file']) + ':' + str(x['line'])))} --note \"不適用:<理由>\"")」
- file: `scripts/lumos:78210`
- 歸因:有證據的原有漏查。修前版本(04b21d1ff)的 `_kill_esc(x['file'])` 同樣把控制字元換成字面文字,指令同樣貼不回原檔;修補沒讓它變壞也沒修它。我在修前版本跑了同一支檢查,只對這一點做了兩版比對。

## 三問
**① 原問題的修復效果**:有行為證據。
- 修前 04b21d1ff:檔名 `app/src/main/Foo$(touch PWNED) x.kt`,印出 `lumos lint-waive choice:app/src/main/Foo$(touch PWNED) x.kt:12 ...`,shlex.split 後第二個參數不等於 `choice:<檔>:12`(False)。貼進 shell 會執行 `touch PWNED`,也會被空白切開。
- 修後 83ac95c8:同一輸入解回來等於原值,新測試 3 條斷言全過。
- 把測試放到修前版本跑:`-k choice_kill_waive_hint` 得 2 條紅(`$(touch PWNED)` 與 `It's.kt` 兩條),1 條綠。
- 翻紅釘有效:拿掉 `_sh_quote` 後測試 2 紅 1 綠(一般檔名那條仍綠),與測試說明一致。

**② 修補處的正常、錯誤與相鄰呼叫路徑**:
- 一般 ASCII 檔名 `app/src/main/java/x/Vm.kt`:修前修後都印 `choice:...:12`,解回來等於原值(兩版都是 True)。
- 中文與空白檔名(`中文 檔.kt`):修後解回來等於原值。
- 同族另一處 `scripts/lumos:78791`(`situation-rule --point` 提示)本來就走 `_sh_quote`,沒有改動。
- 同一段選擇點區段裡,檔名組進照貼指令的只有 78210 這一處,我掃過沒有其他漏網。其餘幾處是 `<檔>:<行>` 佔位字樣。

**③ 新發現在修前修後的結果**:c1 修前修後都一樣(都貼不回原檔)。

## 其他兩個 repair 配對案例
- **K2(`_choice_guard` 快取)**:
  - `t_spec_gate_push_choice_guard_cache` 修後綠。
  - 把 `_choice_guard(rr, rng, at_sha, cache=cache)` 的 `cache=cache` 拿掉,測試紅(`_kt_sit_spec_names_calc` 被呼叫 2 次)。
  - 這支測試在修前版本也是綠,因為這一輪沒有改這一處程式,只補了測試。所以它是「現況的回歸釘」,不是修補的證據。
- **K3(`類別.方法` 取最後一段)**:
  - `t_choice_test_blobs_name_shape` 8 條斷言全綠,修前版本也全綠(同樣是只補測試)。
  - 把 `rsplit(".",1)[-1]` 改成 `split(".",1)[0]` 後,新增的 `r4 k1` 兩條紅(`['kotlin-junit', 'QuxTest.zap', '?']`),原本的 FooTest 那條仍綠。
  - 這證明新案例能把「取第一段」分辨出來,舊案例分不出,與測試說明一致。

## 圖譜鏡頭
這次沒附固定席節點(鏡頭計算超時)。修補差異裡的文件只有三處:
- 計劃的〈範圍〉文字。
- `Systems/規格閘` 新增一條 PITFALL,並在兩條既有 PITFALL 補上 `[test:]`。
- `anchor-baseline.json`。

我讀過這幾處,沒有發現與程式不符。

## 未驗範圍
- 真 Android 專案的端到端耗時沒跑(S26 是手動驗收)。
- 這一輪只改了一行 `scripts/lumos`,所以沒有逐 hunk 審前四輪累積的其餘 15k 行。
- 測試只跑了 `-k` 子集,沒跑全套。
- 測試差異裡有 `both =[{` 這個排版小瑕疵(缺空格),屬措辭,不計。

臨時目錄 `/private/tmp/lumos-seat-work/code-改動選擇點/正確性-sonnet/` 底下我建的副本都已刪掉。

最嚴重:minor;blocking 共 0 條
