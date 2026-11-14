severity: clean

第 5 輪的修補只有一處程式改動,我沒找到問題。

## 圖譜鏡頭
這次沒附固定席節點(鏡頭計算超時),所以沒有節點可逐條判。我自己讀過改到的節點:
- `Projects/改動選擇點都要有需求守住_計劃.md`:只補了兩句文字,寫明點號名取最後一段、整批掃描關掉忽略規則。程式沒有被這兩句改動,不影響行為。
- `Systems/規格閘.md`:只在既有 PITFALL 行補 `[test:]` 並新增一行 r4 s1 的 PITFALL,不影響合約。
- `docs/.kill-log.jsonl`、`governance/anchor-baseline.json`:屬帳本與簽章,不影響行為。

## 三問的回答

**① 原問題(照貼的 lint-waive 指令,檔名含 shell 特殊字元)的修復效果:已修,有兩版證據。**
- 引句:「f"lumos lint-waive {_kill_esc(_sh_quote(_CHOICE_WAIVE_PREFIX + str(x['file']) + ':' + str(x['line'])))} --note \"不適用:<理由>\"")」
- file: `scripts/lumos:78210`
- 修後(`83ac95c8e`),在臨時副本跑 `python3.14 scripts/test_lumos.py -k choice_kill_waive_hint`:3 passed、0 failed。
- 修前:把 `scripts/lumos` 換成 `04b21d1ff` 版,同一條測試:1 passed、2 failed。
  - 檔名 `Foo$(touch PWNED) x.kt` 印出 `lumos lint-waive choice:app/src/main/Foo$(touch PWNED) x.kt:12 …`,`shlex.split` 解不回原檔名。
  - 檔名 `It's.kt` 同樣紅。
- 歸因:有證據的修復回歸,指的是這個修補讓測試由紅轉綠,不是出了新問題。

**② 修補處的正常、錯誤與相鄰路徑是否仍成立:成立。**
- 一般檔名 `app/src/main/java/x/Vm.kt`:修前修後都綠,指令仍可貼。
- 控制字元檔名:`_sh_quote` 在外、`_kill_esc` 在內,只是顯示被跳脫,貼上後 lint-waive 會因找不到檔而回 rc 2,沒有注入風險。
- 同族掃描:我掃了 `scripts/lumos` 的 77500 到 79000 行,所有印給人貼的 `lumos …` 指令:
  - 把真實檔名組進指令的只有 78210 這處和 78791(`situation-rule` 的 point,原本就有 `_sh_quote`)。
  - 其餘用 `<檔>:<行>` 佔位符,或只印 `_sh_quote(Path(prel).stem)`。
  - 所以新 PITFALL 寫的「只有這一處」成立。

**③ 新發現:沒有新的缺陷。**

## 其他兩組案例

**K2(推送前碰到的計劃只算一次的快取):**
- 程式在修前就有 `cache=cache`,這輪只補測試。
- 引句:「guard, why = _choice_guard(rr, rng, at_sha, cache=cache)」
- file: `scripts/lumos:78571`
- 修後跑 `-k guard_cache`:2 passed。
- 變異驗證:把 `cache=cache` 拿掉(用 Python 取代,只在臨時副本),測試紅,`_kt_sit_spec_names_calc` 被呼叫 2 次,斷言預期 1 次。測試確實能抓到。
- 歸因:未判定修復效果,因為修前沒有程式差異可比。測試守得住,這點成立。

**K3(`QuxTest.zap` 這類點號名取最後一段找測試檔):**
- 程式也是修前就有,這輪只補測試與文件。
- 修後跑 `-k choice_test_blobs_name_shape` 的情況我沒單獨重跑,案例斷言與程式取最後一段的寫法一致。
- 歸因:未判定。

## 沒驗到的範圍
- 沒跑任何不帶 `-k` 的全套。
- 沒重跑 K3 的 `t_choice_test_blobs_name_shape`,也沒實驗「改取第一段會紅」。
- 沒跑 `t_choice_scan_batch_share`、`t_choice_kill_partial_unverified_rc`,它們只是被文件引用。
- 沒驗真 Android 專案的端到端耗時,案例檔也寫為未覆蓋。
- 測試補丁有一處排版小瑕疵(`both =[{`,少一個空格)。我用沒帶專案設定的 ruff 測過,E225 不在預設規則內,所以不報。

臨時副本在 `/tmp/lumos-seat-work/code-改動選擇點/通才-sonnet/`。

最嚴重:clean;blocking 共 0 條
