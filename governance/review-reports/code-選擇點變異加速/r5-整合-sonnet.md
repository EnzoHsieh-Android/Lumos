severity: minor

派工詞要我檢查的那把鎖(`...9715c2af...json.warming`)已經不在 dispatch-lens 目錄裡,我沒有刪任何鎖。

## 已驗主張

我在修後版 f14bd5881 開了 worktree,對照程式與兩篇筆記逐項核對。

**1. 筆記說「on_row 與 result_out 照欄位白名單另組列,只有 --json 整列吐出」,對程式成立。**
- `result_out["rows"]` 是固定幾個欄位另組出來的字典,沒有 `judged`。
- `_KillHooks.flush` 交給 `on_row` 的字典同樣是固定欄位。
- `--json` 是把 `results` 的每一列去掉私有鍵後整列輸出,所以結果列上只要多了 `judged`,就會出現在 `--json`。
- file: `scripts/lumos:28590`、`scripts/lumos:28610`、`scripts/lumos:28696`
- 引句:「(on_row 與 result_out 照欄位白名單另組列,只有 --json 會整列吐出,測試看 --json)」

**2. 測試 docstring 說的「翻紅釘」是真的會翻紅。** 我在自己的 after worktree 各改壞一次:
- 拿掉合併基準那處 `max(mg.remaining(), 1.0)`,「r4 邊界 #2」那條紅,收到 `[-5.0]`。
- 在 `_kill_merge_emit` 的 survived 列加上 `"judged": "merged"`,「r4 整合 #1」那條紅。
- 兩處改完都已 `git checkout scripts/lumos` 還原,worktree 也已移除。
- 引句:「合併基準拿掉 max(…, 1) → 情境二收到 -5 而紅;合併交出的結果列加帶 judged → 情境一 --json 那條紅。」

**3. 新測試在修後版都綠。** `-k choice_kill_merge_cap_wiring` 是 5 passed、`-k choice_kill_merge_budget_edge` 是 6 passed。我只跑了修後版,沒有跑修前版對照。

**4. lint 與 spec-trace 都過。**
- guard-kill 與計劃兩篇 `lumos lint` 都是 0 問題。
- `spec-trace` 結果是 24 條款、綁了 21、靠人 3、懸空 0、壞名 0。S12、S22、S23 的 [test:] 都解得出來。
- guard-kill PITFALL 新增的出處(r4 通才 #1、邊界 #1 #3、整合 #1)與 `[test:t_choice_kill_merge_cap_wiring]` 在 lint 下沒有問題。

## Findings

**1. 計劃條款與驗收表沒收進 r4 補的新行為**

severity: minor
blocking: 否

引句:「check("r4 邊界 #3 剩下時限 -5 秒 → 第一支單支基準收到的上限是保底 1 秒」

file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:190`,`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:219`,`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:220`

失敗場景有三處:
- S22 的字面雖然寫了 `max(R, 1)`,驗收表第 219 列的案例卻只有「下限 300、總時限 60」,沒有「剩下時限為負數」那案。新測試「情境二」守的就是這案。
- S23 的驗收表只列了 1、3、1 秒的案例,新的 1、5、1 秒(分得出平均、最小值、第一支)與「單支基準上限保底 1 秒」都沒進表,字面也沒寫。
- 單支基準上限保底 1 秒(`scripts/lumos:28986` 的 `cap = min(full, max(mg.remaining(), 1.0))`)沒有任何一條計劃條款描述,guard-kill 的 PITFALL 修法也沒提。
- 這三處都沒有讓測試或推送被擋下,只是條款與驗收表落後於已綁定的測試行為。

重現:`grep -n "保底" docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md`,在修後版沒有任何輸出。

歸因:有證據的原有漏查。第三輪就有的條款沒涵蓋到負數剩餘,r4 才補了測試與程式;修前我沒有跑。

**2. 合併開著時 `--json` 不帶 judged 這件事,在計劃裡沒有任何一條條款綁測試**

severity: minor
blocking: 否

引句:「check("r4 整合 #1 合併開著時 --json 輸出的存活列不帶 judged(判法只在收尾算一份)",」

file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:180`,`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:123`

- S12 的字面限定「沒傳 `merge` 時」,綁的是 `t_choice_guard_kill_new_params`。
- 守「合併開著時 --json 沒有 judged」的是 `t_choice_kill_merge_cap_wiring`,它只被 S22 綁。
- 計劃第 123 行的合約句講的是這件事,卻沒有對應條款。以後若有人調整 S22,這條守衛會變成沒有條款對應的孤兒測試。
- 這個鬆綁沒有造成現在的行為出錯,只是條款對應不完整。

歸因:有證據的原有漏查。計劃第 123 行早就有那句合約,r4 才補測試。

## 未驗範圍

- 沒有跑修前版 100d3851c 的任何測試,所以沒有修前結果可比。
- 沒有在真實 Android 專案或真 Gradle 上跑。
- 沒有審 S12、S22、S23 以外的條款字面。

## 三問

1. 原問題的修復效果:r4 整合 #1(`judged` 重複算)與邊界 #2、#3(負數剩餘保底)已有同一案例證據,即上面的改壞後翻紅與修後綠燈。
2. 修補處的正常、錯誤與相鄰路徑:已驗路徑仍成立,即合併基準與兩個快篩的逾時都不超過剩下時限、1、5、1 秒的重估、單支基準保底。相鄰的 `--no-merge` 路徑沒有跑。
3. 同一案例在修前、修後各自的結果:修前未判定,因為沒有跑修前版。

總結:最高嚴重度 minor
