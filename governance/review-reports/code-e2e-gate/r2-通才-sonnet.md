severity: major

鎖檔 `.warming` 不存在,沒有要處理的鎖。

臨時資料夾和實驗檔已刪。`python3.14 scripts/test_lumos.py -k android_e2e` 跑完是 515 passed、0 failed。這些測試沒有涵蓋下面第 1 條的情境。

## 發現

### 1. 修補讓「在主線採用 E2E 之前就分出去的分支」只改文件也被擋,而且訊息講錯
severity: major
blocking: 是

引句:「if fp == fp_base and same_cfg:」

file: `scripts/lumos:41576`(`_e2e_gate_fps` 的 `same_cfg` 判斷)

**失敗場景**
- 主線後來才加上 e2e 段。
- 有一條更早分出去的分支,被推送提交和分岔點都沒有 e2e 段,只改了 README。
- 兩端指紋一樣,App 沒變,本來應該回「不要求」。
- 修補把 `same_cfg` 定義成「分岔點與被推送提交的 e2e 段都是 dict 且相同」。分岔點沒有 e2e 段,`same_cfg` 就恆為假,於是落到下面那個擋下:「這個提交沒有 e2e 段,App 程式卻跟分岔點不一樣」。
- 這句話是錯的,App 沒有不一樣。使用者只能先把主線合進來,或用 `LUMOS_SKIP_ANDROID_E2E=1`,而這個環境變數會留帳。

**重現**
用 `scripts/test_lumos.py` 的 `_e2eg_proj`,依序:
1. 在 main 上提交「拿掉 e2e」。
2. 從 main 開分支 `old`,只改 README。
3. 回 main,提交「加回 e2e」。
4. 切到 `old`,執行 `lumos android-e2e check`。

| 版本 | 結果 |
|---|---|
| 修前 `0aecbf90` | rc 0,`not-required`,理由「App 程式與驗收素材跟分岔點一樣」 |
| 修後 `ce46398a` | rc 1,`blocked`,理由「這個提交沒有 e2e 段,App 程式卻跟分岔點不一樣…」 |

**歸因:有證據的修復回歸。**
- 修前:`if fp == fp_base:` 直接放行,上面的重現已證實。
- 修後:`same_cfg` 的新條件使放行消失,上面的重現已證實。

### 2. 帳本事件的截斷量的行比實際寫的行短,仍然超過 4096 位元組
severity: minor
blocking: 否

引句:「_gate_event_fit(repo_root, "android-e2e", ev[0], note, extra, "cases", hard=ev[1], head_sha=marker_sha)」

file: `scripts/lumos:66172` 附近(`_codeloop_e2e_step`)。對照 `scripts/lumos:1869` 的 `_gate_event_fit` 說明:「量的跟寫的是同一行」。

**失敗場景**
- `_gate_event_fit` 量長度時沒有傳 `ref`。
- 緊接著的 `_gate_event_or_warn` 卻傳了 `ref=marker_branch`,事件多出 `"ref"` 欄。
- 情境很多的擋下事件被截到「剛好 4096」,實寫時超出,超出量等於 `"ref"` 欄的長度。

**重現**
400 個情境、`head_sha` 為 40 碼。截斷後留 161 筆,實寫長度如下。

| 分支名長度 | 實寫位元組 |
|---|---|
| 10 | 4117 |
| 120 | 4227 |
| 250 | 4357 |

**歸因:未判定。**
- 修前:`_codeloop_e2e_step` 的事件完全沒有截斷,`cases` 無上限。這是我讀碼得到的,沒有實際跑修前版本。
- 修後:截斷有加,但量錯了一個欄位,上面的重現已證實。

### 3. `waive --commit` 的值沒有長度限制,會原樣寫進放行紀錄和治理帳
severity: minor
blocking: 否

引句:「_gate_event_or_warn(root, "android-e2e", "waived", note.strip()[:200], head_sha=commit or head,」

file: `scripts/lumos:41907` 附近(`_e2e_waive_cmd`)

**失敗場景**
- `note` 在事件裡被截成 200 字,但 `--commit` 的值沒有驗證、沒有截斷。
- `_gate_event_build` 把它整串放進 `head_sha` 欄,放行紀錄也存了同一串。
- 一個超長的 `--commit` 會讓版控的治理帳多出一行超長的行。
- 我只讀了碼,沒有實際把超長值寫進去跑。

**歸因:有證據的原有漏查。** 這一段修補沒有碰;修前與修後的 `_e2e_waive_cmd` 是同一行(讀碼確認)。

## 沒成立、已排除的項目
- 修補把鎖換成 `_vault_write_lock`:鎖檔放在 `~/.cache/lumos/vault-lock/`,不會落進紀錄目錄;`WriteBlocked` 已被接住;殘留鎖改成不接手,規則與 `_excl_lock_try` 的說明一致。計劃 WHY 也改成了這個做法,出口 `LUMOS_SKIP_ANDROID_E2E=1` 仍有效。
- 開場掛鉤最壞輸入:500 份各約 2MB 的紀錄(共 900MB),`_e2e_ai_line` 跑 2.4 秒,在可接受範圍內,不列。
- `_confirm_tty_timeout` 把負數、NaN、無限大改成預設 30 秒:其他呼叫者的行為只有「原本會丟 ValueError、現在用預設」這一個變化,沒有壞處。
- 其餘改動沒有找到可重現的錯。
- 風格類警告(連續空行、行長)屬於舊告警,不判。

## 圖譜鏡頭
- 這次沒附固定席節點。我用 `lumos impact --diff 0701350..ce46398a` 自己跑了影響面。
- 最高分的事故筆記是 `Issues/code-loop守衛main-direct盲區.md`(狀態 done)。
- 對應到這次改動的是 `_e2e_check_cmd` 在 main 上補了 upstream 作為起點。`_codeloop_e2e_step` 走 pre-push 傳進來的範圍,不經這個補丁。
- 「這次新增的殘留」:`Systems/android-e2e-acceptance.md` 與計劃裡沒有以「殘留」命名的段落,我只找到一條 WHY 說明殘留鎖不自動接手。這一條的描述與程式一致。
- 以上不是「已逐條對固定席答完」,只是我自己查到的範圍。

## 三問
1. **原問題的修復效果有沒有行為證據?**
   - 只改設定也要驗:`t_android_e2e_gate_reads_mainline_config` 的三種改法都擋,這些測試都通過。
   - 出口順序、`check` 在 main 上的行為、按功能只列效能時不要求紀錄,都有對應測試通過。
   - 跑 `-k android_e2e` 共 515 個測試全過。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - 正常路徑和相鄰路徑成立。
   - 第 1 條是例外:「分岔點沒有 e2e 段」這條相鄰路徑被修補弄壞了。
   - 第 2 條是例外:新加的截斷呼叫量錯了行,仍然超出上限。
3. **新發現在修前、修後各是什麼結果?**
   - 第 1 條:修前放行,修後擋下,兩邊都有實跑。
   - 第 2 條:修前沒有截斷(讀碼推得,沒實跑修前版本);修後截斷但超 4096,已實測。
   - 第 3 條:修前和修後相同。

最高等級 major,擋實作的 1 條(第 1 條)。
