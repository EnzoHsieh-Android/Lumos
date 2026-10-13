severity: minor

我跑了修前(ff6565ec)和修後(5242975c)的並排比較,也跑了九組測試子集。九組子集全綠:signoff 23、summary_line 27、guard_ 592、drift 1076、set_ 155、append 215、decision 127、cascade 52、lint 383。

**程序偏差(我自己的):** 我在 repo 根跑過一次 `git checkout --detach 5242975c`,違反派工詞。我隨即 `git switch` 回原分支,`git status` 乾淨、HEAD 仍是 d9c9b820。之後的比較都改用 `git archive` 解出的副本。

1. 簽核 stdout 從 1 行變 2 行,和派工詞鏡頭「輸出逐字與修前相同」不符。
   - 輸入:正常 `lumos signoff S --note ok`。
   - 修前只印 `✓ signoff …` 一行。修後多印 `_cmd_set_locked` 的 `✓ set … signed_off 已改成 …`,走到 `scripts/lumos:9192` 的 `print(set_output, end="")`。
   - 這符合丙規則寫的「成功 stdout 兩行」,所以是規格與鏡頭文字互相矛盾,不是實作錯。
   - 引句:「+    print(set_output, end="")」
   - 歸因:未判定。
severity: minor
   - blocking: 否

2. 清單中間有頂格註解行且註解含 `: `,後面所有合法題目整份被判無法判定。
   - 最小重現:`pending_questions:` 兩題之間夾一行 `# 備註: 下一題`,執行 `_pq_scan`。修前沒報錯,修後報「清單範圍外出現題目的鍵 'text'」。
   - 原因:`_pq_scan` 第一輪不再略過 `#` 開頭的行(修前有 `raw.startswith("#")`)。註解被當成頂格鍵,提前結束清單範圍。後面縮排的題目於是落到「清單外」,被 `_pq_outside_line_problem` 擋下。
   - 影響:不是靜默消失,而是大聲拒讀。工具自己不寫頂格註解,但手寫合法的 YAML 會被誤擋。縮排的註解(`  # 備註: …`)不受影響。
   - file: `scripts/lumos:7321`
   - 引句:「-        if not raw.strip() or raw.startswith("#") or raw[0] in " \t":」
   - 歸因:有證據的修復回歸。兩版都用 `_pq_scan` 跑同一份 fm 驗證過。
severity: minor
   - blocking: 否

3. 開頭欄位的巨型 `- - - …` 行造成二次方時間,修前不會。
   - 輸入:`aliases:` 底下一行 `  - ` 加 10 萬個 `- ` 再加 `x`,放在含 pending_questions 的筆記裡。
   - 修前 0.0 秒。修後 25k 個 0.09 秒、50k 個 1.06 秒、100k 個 3.02 秒。另一組是 50 行、每行 5 萬個 `- ` 再接 `text: a`,共 15.4 秒。
   - 原因:`_pq_questionish_key`(`scripts/lumos:7141`,`while t.startswith("- ")`)與 `_pq_line_mapping`(`scripts/lumos:7201`,`text[2:].lstrip`)每剝一個 `- ` 就複製整串字串。同一行還會被這類函式各剝一次。
   - 影響:需要刻意構造的筆記;依觀察到的增長趨勢,更長的行會繼續變慢。
   - 引句:「+        text, prefixes = text[2:].lstrip(" "), prefixes + 1」
   - 歸因:有證據的修復回歸。
severity: minor
   - blocking: 否

4. 硬連結規則擴到所有寫入原語,`guard plan` 因此留下半完成狀態。
   - 輸入:`guard plan S …`,功能筆記是硬連結。修前 rc0 完整成功。修後 rc2,守衛節點 `Verification/<日期>_短名.md` 已建好,功能筆記沒寫標記,只印「不回滾;手動補上這一行」。
   - 原因:`guard plan` 先建守衛節點、再走 `atomic_write_verify`;`atomic_write_verify` 現在對 `nlink>1` 也拒寫。符號連結的筆記修前就是這個半完成結果,硬連結是新增的受影響面。
   - 同族:所有一般寫入指令(set、append、remove、summary-line、updated-sync、self-audit、decision-add、decision-reindex、signoff)對硬連結筆記從 rc0 變 rc2,這符合丙規則。
   - 另一個誤導訊息:`decision-reindex --all` 遇到硬連結時,摘要寫「0 處理 / 2 拒絕(格式不合)」,標籤不準。
   - 引句:「+        if path.exists() and path.stat().st_nlink > 1:」
   - 歸因:有證據的修復回歸。
severity: minor
   - blocking: 否

5. 簽核帳檔是目錄時,誤報成硬連結。
   - 輸入:`.signoff-log.jsonl` 是目錄。修後訊息「有多個硬連結(nlink>1)」,實際原因是目錄的 `st_nlink` 本來就大於 1。修前訊息是 `Is a directory`。
   - 影響:只是診斷訊息錯,檔案狀態與還原行為正確(筆記已還原)。
   - file: `scripts/lumos:9081`
   - 引句:「+            return f"寫入目標 {path.name} 有多個硬連結(nlink>1);換檔或追加會讓內容分岔,這次不寫"」
   - 歸因:有證據的修復回歸。
severity: minor
   - blocking: 否

6. 「WriteBlocked 只由 main 最外層接、訊息先 `_esc_clean`」不完全成立。
   - 指令函式內部仍有大量 `except (ValueError, RuntimeError)`(例如 `scripts/lumos:16010`、16035、17770)會先接住 WriteBlocked,用原始 `{ex}` 直接印。
   - 新的符號連結與硬連結訊息含 `path.name`,沒有清洗,修前的符號連結訊息沒有檔名。
   - 實測:筆記檔名含 `\x1b[31m`、符號連結或硬連結的 `guard plan`,stderr 修後帶出原始 ESC,修前沒有。
   - 影響:有限,因為成功路徑的 stdout 修前就會原樣印檔名。
   - 引句:「+        print(f"擋下:{_esc_clean(str(exc), 1000)}", file=sys.stderr)」
   - 歸因:有證據的修復回歸。
severity: minor
   - blocking: 否

7. ⚠ 兩個 Unicode 邊界,是規格寫法本身的取捨。
   - 軟連字號夾在兩個漢字之間會放行(`中\u00ad文` 通過),因為規格寫「夾在兩個字母間」且漢字是 L 類。額度上限 8 個。
   - 非 emoji 看不見字元上限最多 8 個,對一整段高 ZWNJ 密度的波斯文可能誤擋。我的 80 字、24 個 ZWNJ 測資過於極端,現實密度我沒量到。
   - 引句:「+        elif c == "\u00ad" or c in "\u180b\u180c\u180d\u180f":」
   - 歸因:未判定。
severity: minor
   - blocking: 否

8. ⚠ `decision-add --decided "2026-10-01\n"`(尾端換行)會通過。
   - 原因:`DATE_RE` 用 `$`,尾端換行也算符合,結果在決策項中間寫進一個空行。修前修後結果相同,`_fmt_decision_value` 的新換行檢查沒涵蓋 `decided` 欄位。
   - 引句:「+        raise ValueError("決策開頭欄位的自由文字不能含換行類字元,檔案沒動")」
   - 歸因:有證據的原有漏查。
severity: minor
   - blocking: 否

**鏡頭其餘結論:**
- 工具寫出的筆記照常讀得懂。我依序跑 question-add(含波斯文與 emoji)、decision-add(內容含 `status:`、`text:`、`- id:`)、append、self-audit、signoff、updated-sync、summary-line、decision-supersede,最後再 question-add 仍成功。
- repo docs 855 篇筆記,`parse_frontmatter`、`parse_decisions`、`fm_structure` 修前修後 0 差異。
- 讀取不再拒符號連結後,我沒找到繞過 `_write_refusal_reason` 寫出庫外的寫入路徑。
  - 驗證方式:對指向庫內與庫外的符號連結,各跑 set、append、remove、summary-line、updated-sync、self-audit、decision-add、decision-reindex(含 --all)、question-add、guard bind、decision-supersede、signoff。目標檔位元不變,連結仍在。
  - 方向修正:`guard bind` 對已綁的 no-op 從 rc2 變 rc0(合乎測試 ①b)。`decision-supersede` 在驗證階段先報另一個錯,仍沒寫。
- 擋下訊息沒有重複印兩次。
- `guard kill` 對 BOM 筆記:修前「開頭沒有欄位區塊」,修後 BOM 訊息。對非 UTF-8 檔我只觀察到兩版都是 rc2、訊息相同,沒重現派工詞說的 rc1。
- 簽核的帳寫失敗路徑:符號連結帳、硬連結帳、唯讀帳都是 rc2,筆記還原,庫外檔不變。
- 乙規則(Unicode)的 40 多個變形抽樣符合規格。拉丁、漢字、框線的 ZWJ 被擋;波斯、馬拉雅拉姆、梵文放行;emoji、鍵帽、旗幟、膚色放行;DICP 超過 16 個與 NFC 錯誤被擋。
- 圖譜四篇我只 grep 了符號連結、硬連結與 WriteBlocked 相關句,沒有逐篇完整對照。`lumos-cli-write.md:118` 的「只由 main 最外層接」與第 6 條同一處對不上。
- 沒做:鎖被占住的情境(鎖實作本輪未動,等待上限 60 秒);drift fix 的完整正常與錯誤呼叫,只確認它走 `_write_refusal_reason`。

**三問:**
- ① 原問題的修復效果:三條規則的主要行為都有證據。清單外題目鍵、流式與引號鍵、anchor 皆被拒;看不見字元的位置、容量規則生效;符號連結與硬連結只在寫入前拒;簽核帳失敗會截回並還原筆記。
- ② 正常、錯誤與相鄰路徑:基本都成立。例外是第 1 條(stdout 變 2 行)、第 2 條(頂格註解)、第 4 條(硬連結改 rc2)、第 5 條與第 6 條(訊息)。
- ③ 新發現案例在修前與修後:
  - 第 2 條:修前讀得懂,修後整份拒讀。
  - 第 3 條:修前 0.0 秒,修後 3.02 秒。
  - 第 4 條:修前 rc0,修後 rc2 且守衛節點已建。
  - 第 5 條:修前顯示 `Is a directory`,修後顯示硬連結訊息。
  - 第 6 條:修前 stderr 沒有 ESC,修後有。
  - 第 7、8 條:兩版相同。

整體只有輕微問題,沒有會擋合併的項目;最值得修的是第 2 條頂格註解被誤擋和第 3 條二次方耗時。

我的實驗檔放在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-通才回歸-sonnet/`,收貨後可刪。
