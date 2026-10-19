severity: minor

審查範圍:修補差異 `r3-repair-lumos.patch`(修前 86aa8f40、修後 342cf099),另對照 `r3-repair-tests.patch` 的新測試。這輪沒有 blocker 或 major。

## 發現

**1. `_spec_gate_pick` 同一秒時取先列的,同一本帳內的新留痕會輸給舊留痕**
severity: minor
- blocking: 否
- 輸入:只有治理帳有這條迴圈的留痕,檔內依序是 OLD(紅)、NEW(綠),`ts` 同一秒。呼叫是 `_spec_gate_pick(None, old, new)`,也就是 `_spec_gate_latest_merged` 在本機審查帳沒有這筆時(乾淨 clone)的走法。
- 預期:取同一份帳後寫的 NEW。
- 實際:取到 OLD。
- 兩版查證:我把修前版本存到 `lumos_before` 載入,同一組輸入回 `green`(NEW),修後回 `red`(OLD)。
- 歸因:有證據的修復回歸。
- 影響:改法是要讓本機審查帳那筆在同秒時贏過治理帳。順手把「同一份帳後寫的是新的」這條也拿掉了。程式碼裡沒有分辨「本機審查帳那筆」和「治理帳同一份帳內的列」的機制,只有靠「第一個參數是本機」這個約定。
- 測試缺口:`t_spec_gate_pick_same_second_keeps_local` 只測 `(B, A, B)` 這一組,測不到這個情境。
- 可行性:要在一秒內連寫兩筆同迴圈留痕才會發生,手動重跑做不到,只有自動化迴圈才可能,所以只標 minor。
- 引句:「if best is None or k > bk:       # 同一秒取先列的(本機審查帳那筆;r2 正2:取後列會讓治理帳裡同秒的舊留痕贏)」

**2. 「只要…就」配對只在同一小段內找,最常見的逗號寫法認不出來**
severity: minor
- blocking: 否
- 輸入 `- 只要還沒有登入,就擋`:逗號把「就」切到下一小段,`_ns_neg_cond_paired` 的 tail 看不到,仍回 `[('還沒', 4)]`,等於照現況句唸。
- 輸入 `- 只要還沒有登入就擋`:無逗號,回 `[]`(認得)。
- 新測試 `quiet` 組只有無逗號的寫法,逗號版沒被測到。
- 反方向:`- 等到期後還沒有人處理` 這種現況句會回 `[('還沒', 6)]`,仍會唸,沒被誤吞。
- 影響:只是提醒(note_shape 否定句只有 warn/off),會多唸而不會漏擋。
- 歸因:未判定。修前根本不收「只要」,不能算修補造成的回歸。
- 引句:「return any(h.startswith(w) and any(c in tail for c in pair) for w, pair in _NS_NEG_COND_PAIRED.items())」

**3. `_ref_cmdline_token` 第一個詞是存在的目錄、後面接不像路徑的詞時,缺的路徑會被當成 ok**
severity: minor
- blocking: 否
- 輸入 `src/app v3`:`src/app` 存在,`src/app v3` 不存在,`v3` 不含 `/` 也沒有副檔名。
- 預期:`missing`。
- 實際:函式回 `src/app`,於是核對成 ok。
- 我只直接呼叫了函式,回傳就是 `src/app`。沒有跑完整的 refcheck。
- 範圍:帶空白、無副檔名、最後一段缺的路徑才會這樣;`src/app v2/x.py` 和 `src/app v2.py` 這兩種有被測試守住。
- 歸因:有證據的原有取捨。r1 版本只看旗標,這類輸入本來就不報。
- 引句:「or (exists(words[0]) and not _ref_word_looks_like_path(words[1]))):」

## 已驗無問題

- **`_ref_cmdline_token`**:`scripts/lumos doctor`、`--x`、`的某函式`、`Foo.Bar`、`v1.2`、`doctor.` 都只核對第一個詞。`src/app v2.py`、`foo.bar`、`說明.md` 照整串核對。第一個詞不存在時,只有第二個詞是旗標才截成第一個詞。
- **`_ns_neg_clause_break`**:`前/後` 不算子句記號;`前.`、`前'x'` 算。唯一的副作用是 `前.sh` 這類路徑片段也會當子句記號,屬少見的寫法,我沒有再追。
- **`_excluded_line`**:先數冒號的前置檢查,與 `_EXCLUDED_RE` 本身要求兩個冒號等價,不會放行本來認得的行。
- **`_spec_gate_status_at`**:改用 `_range_base`,`a..b` 與單一 rev 的行為不變,`a...b` 取 merge-base。`startswith("-")` 的早退保留了。
- **`_summary_write_shape_check`**:非 git 目錄回 `False`,git 跑不起來回 `None`。`None` 時 `_drift_fix_shape_err` 拿不到清單而擋下,測試有守。
- **`_drift_fix_shape_err`**:gate 為 off 時只在拿到檔案清單之後才檢查,清單拿不到時不論 off 都擋。這在修前就如此,不是新問題。
- **cochange `--diff ""`**:`is None` 與空字串分開處理,會回 rc2。`--staged` 同時給也一樣。
- **`_dirty_non_bookkeeping`**:簿記檔排除與未追蹤新檔都有測試;`_fix_git_z` 失敗時回空清單,沿用修前行為。
- **S14**:治理帳讀不到時印一句再退回本機帳,不會崩。

## 三問

1. **原問題的修復效果**:G1、G3、G4、G5(只看有無逗號之外的寫法)、G6、G8、`_is_git_worktree`、cochange 都有我自己跑出的行為證據,或對應的新測試。唯一沒守住的是 G7(同一秒)的取捨,見發現 1。
2. **相鄰路徑是否仍成立**:`_spec_gate_pick` 的 `(B, A, B)` 去重正常;`_spec_gate_status_at` 的 `..` 和無範圍路徑沒變;`_excluded_line` 的 lint、判門、推送前重判門共用同一支,行為一致。
3. **新發現在修前、修後的結果**:發現 1 修前取 NEW(`green`)、修後取 OLD(`red`),已實測。發現 2 在修前沒有「只要」前綴,不可比。發現 3 在修前同樣回 `src/app`(旗標以外不截),沒變。

## 未驗範圍

- 我沒有跑全套測試,也沒有對新測試做拿掉實作的翻紅。上面的結論只來自直接呼叫函式與讀 diff。
- `_dirty_non_bookkeeping` 在「整個 `governance/` 目錄都是未追蹤」時,porcelain 收成 `governance/` 單一項,可能不被 `_BOOKKEEPING_DIRS` 的前綴比對排除。我沒有實測。
- `_range_base` 的三點範圍右端若以 `--` 開頭,會原樣傳給 `git merge-base`。我沒有驗證是否可被利用,威脅模型下也不追。

最嚴重 severity:minor,blocking 共 0 條。
