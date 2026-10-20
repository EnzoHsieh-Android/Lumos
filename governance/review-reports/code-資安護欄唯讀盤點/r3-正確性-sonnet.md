severity: minor

# 代碼審查席報告:正確性鏡頭(第 3 輪,末輪)

我沒找到 blocker 或 major。r2 修補的原問題都修好了,正常路徑也都還成立。有兩處測試擋不住回歸,各列一條 minor。

兩版程式我都實跑了:修前 aadf6b07、修後 84a58aee,臨時目錄在 `/tmp/lumos-seat-work/code-資安護欄唯讀盤點/`。修後的 `-k seclist` 全過(326 passed, 0 failed)。我另外在臨時副本做了翻紅實驗(把修補處改回去,看測試紅不紅)。

## Finding 1:錯誤超過每篇上限後,「引用是否有效」沒有測試守
引句:「    r["references_valid"] = errors.attempted(_SECINV_REF_ERROR_KINDS) == n0」
severity: minor
blocking: 否

- **失敗場景**:同一篇有 60 條控制項,來源決策引用都指向不存在的 `Systems/Nope#d1`。
- **預期**:60 條都是 `references_valid=false`,入口 `S-pay` 是 `unmapped`。
- **修後實際**:正確,10 筆錯誤被併進 `errors_truncated`,入口是 `unmapped`。
- **翻紅實驗**:把 `_secinv_check_row` 改回舊寫法,即 `n0 = len(errors)` 加 `errors[n0:]` 的掃描。
  - 結果:有 10 條被誤判為有效,入口變成 `mapped`。
  - 這正是「缺口被藏成已覆蓋」的舊症狀。
  - `-k error_cap` 通過(4 passed),`-k seclist_g3` 通過(11 passed),兩支都沒紅。
- **缺口**:`t_seclist_r2_error_cap` 只檢查筆數與彙總,不看 `references_valid` 和入口狀態。r2 配對表把它列為這處修補的守護測試,實際沒守到。
- 歸因:有證據的修復回歸不成立。這是新機制(`attempted`)沒有配套測試,不是程式壞了。
- 建議:補一支測試,造超過上限的引用錯誤,斷言每條的 `references_valid` 為 false 且入口不是 mapped。

## Finding 2:決策作廢旗標不分大小寫的比對沒有測試守
引句:「by_id[str(d.get("id", "")).strip()].append(str(d.get("valid", "true")).strip().lower())」
severity: minor
blocking: 否

- **失敗場景**:決策寫 `valid: False`(大寫 F),控制項來源引用它。
- **預期**:`決策已作廢(valid:false)` 的 reference_error。
- **修後實際**:正確,也與修前逐位元組相同。
- **翻紅實驗**:拿掉 `.lower()` 後,作廢決策被當成有效,錯誤消失。`-k seclist` 全 326 項仍過(326 passed, 0 failed)。
- **缺口**:決策表快取是 R4 新寫的,大小寫這一步沒有任何斷言。
- 歸因:有證據的原有漏查。修前舊寫法也沒有測試,但這次重寫了這行,應順手補。

## 三問回答

**① 原問題的修復效果**

| 組 | 同一案例 | 修前 | 修後 |
|---|---|---|---|
| R3 | 證據指到 `Systems/Pay`(非 Verification 節點)的控制項 C1 | rc0,`references_valid=true` | rc2,記一筆 `reference_error`,`references_valid=false`;不受影響的 C2 仍是 `declared_only` |
| R4 | 同篇 60 條壞決策引用 | 錯誤 60 筆 | 51 筆,含 `errors_truncated(omitted=10)`;`references_valid` 仍 0/60 有效,入口 `unmapped` |
| R2 | `docs` 是捷徑指向 repo 外(自動找與 `--vault` 兩條路) | 兩條都讀到 repo 外,rc0 | 兩條都擋下(rc2),訊息指出是哪一層 |
| R2 | `docs` 是捷徑但指向 repo 內 | rc0 | rc2;和計劃文件「不跟任何捷徑」一致 |
| R2 | 圖譜目錄本身是捷徑 | rc2 | rc2,維持 |
| R4 | 決策引用 15 種寫法(大小寫、`.md`、`#d` 缺漏、重複編號、作廢、同名不同大小寫兩篇),含例外的決策引用 | — | 修前修後的完整 JSON 相同(扣掉 observed_at) |

**② 修補處的正常、錯誤與相鄰呼叫路徑**
- **圖譜選擇**:相對 `--vault`、從子目錄自動找、macOS 的 `/tmp` 到 `/private/tmp`(repo 根以上的捷徑不查)都正常。
- **輸出內容**:零登記、無 inventory、重複 ID 與同來源雙 ID、證據 stale/pending/abandoned/未知狀態、零控制項,修前修後輸出相同。
- **`_visible_lines`**:拿 ec4c6307 的舊版與修後版做差分,2 萬組隨機圍欄輸入、keep_fenced 兩種模式,差異 0。`_fence_regions` 抽出後行為完全不變。
- **`_read_fd_capped`**:現在只讀到 limit+1 位元組,不再多讀。這不影響 `_retro_read_bytes` 的判斷,只讓超限訊息的位元組數更精準。
- **`_regular_own_fd(dir_fd=…)`**:`dir_fd` 預設 None,既有呼叫端走原路徑,行為不變。

**③ 新發現的同一案例修前修後**
- Finding 1:修前 `len(errors)` 版本在 `mapped` 這一點與修後不同,是我造的回退實驗,不是原始差異。
- Finding 2:修前修後行為相同,只有測試缺口。

## 未驗範圍與觀察
- **疑似死碼**:`_secinv_build` 的 `errors_truncated` 加 `omitted_by_kind & _SECINV_READ_KINDS` 分支。讀取類錯誤每篇不會超過 50 筆,所以我沒造出會走到它的輸入。我已把這個分支拿掉,`-k seclist` 全過,但沒找到會走到它的輸入,所以不確定它是不是死碼。
- **`changed_during_read` 去重改成只看節點**:同一節點先有別種讀取錯誤,就不再補 `changed_during_read`。因為所有讀取類錯誤都會讓 `read_complete` 為 false,不影響完整性判斷。
- **文字與 JSON 的差別**:文字輸出看不到 `scope.limits`。這不是 r2 修補造成的,我沒當 finding。
- **未跑**:大型與深層巢狀輸入的效能,留給資源席。

最嚴重 severity:minor,blocking 共 0 條
