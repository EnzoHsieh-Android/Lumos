# 第 3 輪審查報告(code-dloop-redesign r3 s3)

審查對象:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/907f3c42-1246-4d5f-a854-ed66bb17b77e/scratchpad/codeloop/code-dloop-redesign-r3-s3.patch`
比對基準:`/Users/enzo/harness/lumos-toolchain` 實際工作樹(`git diff -U10`)

## 方法論說明(先講,因為 finding 1 就是靠這個抓到的)

逐段核對前,先把 patch 檔與 `git diff -U10 -- governance/eval/canary_calibration.py scripts/lumos scripts/test_lumos.py` 的實際輸出做逐位元組 diff。結果:`governance/eval/canary_calibration.py` 與 `scripts/test_lumos.py` 兩檔完全一致;`scripts/lumos` 只有**一處**不一致——見 finding 1。其餘所有 hunk(★收斂判定與 hash 鏈★主鏡頭涉及的 round-less 分組、留痕全席重驗、`_vault_repo_root`、badlines 行號、round-id 非連續重現守衛)在實際工作樹逐字存在,已對照真代碼確認語意。

三支新測試(`t_disposal_gate_r1_panel_hardening`、`t_disposal_gate_r2_panel_hardening`、`t_calibration_readback_hardening`)與既有 `t_quote_check_nested_quotes_and_min_length` 皆已用 `python3 scripts/test_lumos.py -k <關鍵字>` 實跑,全綠(合計 24 案例 0 fail)。

---

## Finding 1(嚴重,主鏡頭①:G3 hash 鏈)

**diff 檔宣稱的修法未落地到真代碼,且該修法本身若真的套用會是錯的。**

引句(diff 檔逐字複製):「for grp in (rounds_list[:-1] or rounds_list):   # dsp_chain_tail: 窗末輪交由下方 result==當前檔 單獨驗,不重複入鏈」

- 這段 hunk 出現在 patch 檔的 `_hash_chain_check`(對應舊檔行號 `@@ -3266,9 +3300,9 @@`),但 `/Users/enzo/harness/lumos-toolchain/scripts/lumos:3300` 現在仍是修改前的原文:`for grp in rounds_list:`(已用 `git diff -U10` 與 `grep -n "dsp_chain_tail\|rounds_list\[:-1\]"` 兩種方式確認整個 repo 找不到這段文字,`git stash list` 也查過、無關)。scripts/lumos 檔的 mtime(17:10:44)早於 patch 檔 mtime(17:15),但內容對不上——patch 檔描述的這一刀沒有真的留在工作樹裡。
- **這不只是文件落差**:若這段真的套用到 `_hash_chain_check`,會壞掉它在多輪視窗場景下的邏輯。`_hash_chain_check` 有兩種呼叫型態:①disposal/light 只傳 `[latest]`(單輪,`rounds_list[:-1]` 是空 list、`or` 會 fallback 回 `rounds_list`,這條分支下無影響)②legacy `--gate` 路徑在 `scripts/lumos:3777` 用 `_hash_chain_check([[r] for r in tail], spec)` 傳「收斂窗 tail need 筆」的**多輪**清單。對②而言,`rounds_list[:-1]` 會把窗末那一輪整個踢出 `per_round` 計算:(a)`per_round` 少一個元素,窗末輪與倒數第二輪之間的鏈續性檢查(`per_round[k+1][0] != per_round[k][1]`)永遠不會跑到;(b)最後拿去跟「當前檔 sha256」比對的 `per_round[-1][1]` 會變成**倒數第二輪**的 result_sha256,而不是窗末真正最後一輪的——等於驗證器在跟錯的一輪比對,窗末輪的雙 hash 完全逃過鏈驗。這正好是 G3 這條合約要防的事(「spec 於審計後被改動」)。
- 建議:先確認這段 hunk 是不是應該存在(是被中途手動 revert 掉、還是 patch 產出流程出錯多包進一份沒真的寫入的內容);如果原意是要處理某個「窗末輪重複驗」的疑慮,需要重新設計(至少不能整輪從 `per_round` 抽掉),並補一支能翻紅這個錯誤配對的測試(構造窗內 ≥2 輪、窗末輪 result_sha256 ≠ 當前檔但倒數第二輪 result_sha256 == 當前檔的案例)。

---

## Finding 2(中等,主鏡頭①:round-less 分組)

**round-less 記錄的合成鍵 `__seq{N}` 與使用者可自訂的 `--round` 值同一個命名空間,撞名會把兩筆邏輯上不相干的記錄併成同一個「判定輪」。**

引句(diff 檔逐字複製):「groups[f"__seq{len(groups)}"] = [r]」

- 位置:`scripts/lumos` 的 `_loop_status_disposal`(patch 內對應「round-less 逐筆自成一輪」那段)。目前邏輯是:round-less 記錄(`r.get("round") is None`)一律用 `f"__seq{len(groups)}"` 當 key 自成一輪;有 round 欄的記錄則用 `rid_ in groups` 判斷是否为「非連續重現」。但這兩條路徑共用同一個 `groups` dict 的 key 空間——如果某筆記錄的 `--round` 剛好打進去一個跟合成鍵格式相同的字串(例如 `--round __seq0`),`rid_ in groups` 會判定「已存在」,且因為它剛好是 groups 裡最後一個 key(`next(reversed(groups)) == rid_`),不會觸發「非連續重現」錯誤,而是直接 `groups.setdefault(rid_, []).append(r)` 併進前一筆 round-less 記錄的組裡。
- **已用真代碼實測重現**(非臆測):先記一筆 round-less 的 `caught`(無 `--round`),再記一筆 `--round __seq0` 且帶 `--findings-set/--report/--snapshot/--spec/--reviewed` 的完整 carrier 記錄,`loop status --disposal` 印出:
  ```
  __seq0.1	caught	minor	s1
  __seq0.2	caught	minor	s2
  ⛔ DISPOSAL GATE FAIL (collideL 輪 __seq0: G3/留痕/留痕)
  ```
  兩筆記錄被判成同一輪 `__seq0`(`.1` 是無 round 的舊記錄、`.2` 是刻意撞名的 carrier),因為前者沒有 hash/report/snapshot,'"處置集合"' 雖然因 carrier 只有一筆而過關,但 G3(半帶 hash)與「留痕全席重驗」都被前者拖累而 FAIL——即使 carrier 那一筆本身完全合規。反過來想,若第一筆 round-less 記錄剛好也帶了合法的 report/snapshot/hash(單純巧合或惡意構造),也可能讓兩筆不相干的記錄被誤判「合起來過關」。
- 這個設計本身就是這次 disposal 閘一路在堵的那類問題(「不信寫側單席視角」「append-only 帳次序損壞」)的同型漏洞,只是這次撞在 round-less/round-ful 兩種命名空間的交界上。
- 建議:合成鍵改用使用者不可能透過 `--round` 打進去的形式(例如 CLI 對 `--round` 加白名單校驗、拒絕 `__` 開頭;或合成鍵改存在獨立集合而非借用 `groups` 的 key 空間,例如用 `(None, i)` tuple 當 key 而不是字串)。

---

## 其餘各段核對結果(無新增 finding)

- **`_vault_repo_root`(向上找 `.git`)**:寫側(`cmd_canary` 落帳)與讀側(`cmd_loop_status` 呼叫 `_loop_status_disposal`)都呼叫同一份函式、傳入同一個 `env`,語意對稱;`.exists()` 對 worktree 的 `.git` 檔案(非目錄)一樣成立,不受 worktree 影響。已用測試 ③(`t_disposal_gate_r2_panel_hardening`)構造 `docs/<slug>-knowledge` 兩層布局實測,`record` 存相對路徑、換 cwd 後 `--disposal` 仍能同根解回,綠燈。
- **判定輪缺留痕欄席 FAIL(全席重驗)**:內層 `continue` 只跳過同一筆記錄的另一個欄位檢查,不會誤跳過整筆記錄;`n_files`/`ok` 累積邏輯正確。已用測試 ②(missed 席定錨前合法缺留痕、carrier 席帶留痕)驗證會正確 FAIL 並標出是哪一席缺欄。
- **badlines rc2 訊息附行號**:`enumerate(..., 1)` 在 `line.strip()` 覆寫前取值,行號對應原始檔案位置正確;`bad_linenos` 只在 `disposal`/`settle` 用於 fail-closed,`panel`/`light`/legacy 路徑不受影響,與註解「legacy/panel 維持容忍(行為不變)」一致。
- **校準帳 run_id 全檔掃描 + 半行補換行**:半行偵測(`old and not old.endswith("\n")`)只補在「本次寫入前」,不會動到既有半行本身(那一行本來就是壞的,補完後獨立成一行不影響新寫入的完整行);讀回改用 run_id 唯一鍵全檔容錯掃描,不再依賴「最後一行」。已用新測試(帳尾人工塞半行 `{"half":`)實測:寫入成功、無 traceback、能讀回自己的 run_id。
- **三支新測試**:皆有「★前置★ 現場成立」斷言把現場條件釘死(而非只驗最終 rc),核對後與程式碼實際行為相符,不是湊數測試。已全數實跑通過。
- **quote-check 巢狀引號 + 下限**(雖非本輪新增六項之一,但落在同一 hunk 群裡,一併核對):正則 `引句[：:]\s*(?:「([^」]+)」|『([^』]+)』)` 正確地讓「…」內容可含『』而不誤截斷;`_QUOTE_MIN_NORM_LEN=10` 門檻只在正規化後長度計算,實測含巢狀引號與 1 字短引句兩案例皆如預期。

## 附註

全量測試(`python3 scripts/test_lumos.py`)已在審查期間背景跑完:**2298 passed, 0 failed**。加上針對本輪改動範圍用 `-k` 篩選跑過的相關測試群(`disposal_gate_r`、`calibration_readback`、`quote_check_nested`,共 24 案例全綠),可以確認:除了 finding 1 描述的那個「patch 檔多出一段沒有真的落地的 hunk」以外,patch 檔其餘內容與 `git diff -U10` 實際輸出逐字一致,且全量測試在該實際狀態下全綠——finding 1 講的是「diff 檔本身的完整性問題(有一刀沒真的下)」,不是「現有代碼跑不過測試」。
