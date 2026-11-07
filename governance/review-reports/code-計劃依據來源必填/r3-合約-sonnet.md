severity: major

審查摘要:我對 `_plan_sources_uncomment`、樹清單解析、`_plan_src_path_ok`、首次加入日、生效日比較等分支共做 45 道改壞實驗,只跑完 34 道,另有 1 道因為要改的那段文字出現 7 次而略過。r2 的 F2、F3 照上次的方式重做,現在都會翻紅。其餘多數翻紅,但有 8 道仍全綠,見 F2 到 F5。實驗複本已用字面絕對路徑刪除,沒有改 repo。

r2 前輪核對:
- F1(規格閘舊 PITFALL):`Systems/規格閘` 的 PITFALL 已改成 `_plan_first_days` 整個 repo 一次 `git log`。綁的 `t_high_risk_evidence_since` 守得住:複製不跟、改名接舊日期都有斷言。
- F2:已修好。把圍欄跳過那段拿掉後 `-k psrc` 為 119 過 1 敗,翻紅。
- F3:已修好。`c > since` 與 `day > since` 兩種改壞都翻紅。
- F4:翻紅釘說明已改正,`t_psrc_first_day_nfd_rename` 已補上。我沒有重做 NFC 的改壞實驗。
- F5:五種應擋在 S1 條款、預期值表、`t_spec_gate_sources_section` 三方對得上,標籤逐一相符。但目錄 `scripts/` 應擋仍沒有進預期值表,條款裡有。

F1
severity: major
blocking: 是
引句:「(2026-11-07 標註:這一點與開頭欄位決策 d12 寫的「逐跳 `diff-tree -M` 追改名、每次 git 逾時 20 秒」已被 `_plan_first_days` 取代」
`Projects/高風險測試證據加嚴_計劃` 加了正文標註,但結構化的 `decisions:` 欄位沒改。`docs/lumos-toolchain-knowledge/Projects/高風險測試證據加嚴_計劃.md:99-100` 的 d12 仍是 `valid: true`,內容寫「diff-tree -M 看它是不是從別的檔改名過來,是就換舊路徑再找」。專案 CLAUDE.md 規定 `decisions:` 紀錄有挑戰程式碼的效力。下一個 session 讀到 d12 會判程式違反決策,反過來可能照 d12 去「修」成逐跳追蹤。
標註沒有說清楚的地方:
- 它不在決策欄裡。d11 被 d12 取代時是用 `valid: false` 加 `superseded_by` 處理的,這次沒照做。
- 內文第 161 行仍寫「每次 git 逾時 20 秒」,現在是 60 秒。
建議:用 `lumos decision-add` 補 d13 並把 d12 標 superseded。

F2
severity: major
blocking: 是
引句:「            out[i] = "".join(keep) + ln[pos:j]」
`_plan_sources_uncomment` 的「行中 `<!--` 在後面幾行才閉合」這一整支分支沒有任何測試。`t_psrc_uncomment_inline_open` 與其他測試都只有「同一行閉合」或「沒閉合」。
- 實驗(`-k psrc`,三道都是 120 過 0 敗):
  - 把上面這行改成 `out[i] = ""`,仍綠。
  - 把 `for z in range(i + 1, q):` 改成 `range(i + 1, q - 1)`,仍綠。
  - 把跨行閉合後的 `no_close` 重設從 `False` 改成 `True`,仍綠。
- 失敗場景:
  - 少換空一行:被註解藏起來的表格列還算數,藏起來的依據被當成有效出處而放行。
  - 開頭行被整行清掉:行首文字消失。
- 這是 r2 修法的「行中」那條規則,正是 CommonMark 區塊與行內分開判的另一半。

F3
severity: minor
blocking: 否
引句:「    return n is not None and 1 <= lo <= hi <= n」
行號範圍的下界與順序沒有測試,只測了超出檔尾。
- 實驗(`-k psrc`,皆為 120 過 0 敗):改成 `lo <= hi <= n`(`:0` 會放行)、改成 `1 <= lo and hi <= n`(`:5-2` 倒序會放行)、改成 `1 <= lo <= n`(`hi` 超界會放行)。
- 失敗場景:出處寫 `` `scripts/a.py:0` `` 或 `` `scripts/a.py:3-1` `` 時被判合格。
- `t_psrc_tree_git_calls_bounded` 只用 `:1`、`:1-1`,`scripts/a.py:999` 也只測了上界。

F4
severity: minor
blocking: 否
引句:「        val = t.count("\n") + (1 if t and not t.endswith("\n") else 0)」
`_plan_blob` 算行數時「結尾沒換行要多算一行」沒有測試。
- 實驗:改成 `val = t.count("\n")`,`-k psrc` 仍為 120 過 0 敗。
- 失敗場景:最後一行沒有結尾換行的檔,寫該行行號會被誤擋。測試用的 `a.py` 都以換行結尾。
- 另一道 `always +1` 改壞有翻紅,所以只有這一側漏掉。

F5
severity: minor
blocking: 否
引句:「    path = nfc(path.strip())」
出處路徑轉 NFC 沒有測試。
- 實驗:改成 `path = path.strip()`,`-k psrc` 仍為 120 過 0 敗。
- 失敗場景:計劃裡寫 NFD 形式的路徑(例如從 macOS 檔案名稱複製),樹清單的鍵是 NFC,會被誤擋。
- `t_psrc_first_day_nfd_rename` 只守首次加入日這一側。

F6
severity: minor
blocking: 否
引句:「②repo 內存在的檔案:反引號包住的路徑(可帶尾端 `:行號`),交給既有的 `_validate_repo_ref` 對 HEAD 的版控樹判」
計劃〈用詞〉的出處合格定義(`Projects/計劃依據來源必填_計劃.md:34`)仍寫「交給 `_validate_repo_ref` 判、只認它回 ok」。程式現在改在 `_plan_tree`、`_plan_tree_resolve` 裡查,只共用 `_repo_ref_token_unsafe` 的消毒。同檔第 83 行的〈依據來源〉列已經改對,〈用詞〉這句沒跟上,同檔兩處說法不一致。結果行為相近,但這是下一個 session 會照著找函式的那一句。

未跑完的實驗(以下為預期,未驗證):
- 剩下 11 道沒跑:
  - `tree nfc off`、`shallow tree none`、`blob cache key`、`plan_is_plan slash`、`plan_is_plan suffix`、`nfc rename old`、`rename new in seen`、`cache max`、`type other notice`、`fp drop probs`、`fp drop cells`。
  - `lines CR off` 因要改的那段文字出現 7 次而略過。
- 我預期 `plan_is_plan slash`、`plan_is_plan suffix`、`type other notice`、`fp drop probs`、`fp drop cells`、`rename new in seen` 會翻紅,因為各有對應測試。
- 預期 `shallow tree none` 與 `tree nfc off` 可能仍綠,理由是我沒看到淺複製加判路徑,以及 NFD 樹的測試。
- `hops 9` 預期綠但屬等價改動,不算 finding。

已確認翻紅的主要實驗(`-k psrc`):
- 圍欄跳過拿掉、`c > since`、`day > since`。
- 區塊永不結束、區塊首行永不結束、單行區塊也開啟。
- `stops` 去掉空白行、標題、圍欄三種。
- `<!-->` 與 `<!--->` 短寫、行首縮排放寬到任意空白、行內程式碼跳過關掉。
- 跳數上限改 1、不檢查 blob 類型、不檢查正規化、`dirname` 接路徑、不接剩餘段。
- 行號上界、行數永遠加一、`./` 前綴、`.git` 例外。

另有一個我沒有標成 finding 的觀察:`_plan_sources_uncomment` 對一段 8000 行、每行都有未閉合 `<!--` 的輸入要約 7.9 秒(2000 行約 0.5 秒),這是平方級成長,實際計劃不太會出現。

總結:最嚴重是 d12 決策紀錄仍寫逐跳追改名而未標已取代、以及「行中註解跨行閉合」整支分支無測試,會擋 2 條(另 4 條 minor 不擋)。
