severity: minor

## 結論

合約與圖譜一致性這個鏡頭,我沒找到會擋推送的問題。圖譜讀完、命令實跑之後,只有一條 minor。

我在 84a58aee(修後)和 aadf6b07(修前)各開一個暫存 worktree 比對。用完已按字面路徑移除,`git worktree list` 沒有殘留。

### 實測結果

- `python3.14 scripts/lumos doctor --ci`:rc=0,「圖譜健康 — 0 issues (907 篇)」。
- `lumos note-shape --diff ec4c6307..84a58aee --slots`:rc=0。
- `lumos lint` 跑在子計劃和母計劃:各 0 問題。
- `lumos spec-gate Projects/資安護欄唯讀盤點_計劃`:S1 到 S13 共 13 條全綁、全綠,相依回歸 `t_search_forget_superseded` 綠。
- `python3.14 scripts/test_lumos.py -k seclist`:326 passed、0 failed。
- `-k search_forget` 19 passed、`-k fence` 49 passed、`-k no_duplicate_defs` 1 passed。
- 圖譜自己的 doctor 輸出裡有「數字宣稱與實測不符」11 筆(提醒、不擋),都在這次沒碰的筆記,不是這批改動造成。

### 子計劃 d1 七處保守做法與程式對照

七處我實跑了六處,都和 d1 一致;「錯誤種類名照實作命名」由下面的種類對照覆蓋,不單獨實跑。

- 零登記:rc=0、registration_complete=false。
- 只有候選的入口:同時出現在 unmapped 和 candidate_only。
- 圖譜內任何捷徑(含非 .md、子目錄、點開頭目錄):一律 `symlink_rejected`、rc=2。
- 例外過期:列 issue `exception_expired`、rc=0。
- 例外引用的決策已作廢(d2 valid:false):`reference_error`、rc=2。
- 決策引用大小寫不同(`systems/slpay#d1`):照樣通過,與「路徑不分大小寫再比一次」相符。

### 其他逐處核對

- **輸出頂層鍵**:多份 inventory 列 `inventory_error` 且 coverage 為 unknown,重複來源列 `duplicate_source`,Systems 以外出現圍欄列 `misplaced_block`,一篇多塊列 `multiple_blocks`。頂層鍵涵蓋子計劃〈輸出契約〉列的全部欄位(另有 notice、scope、limitations、today_utc 等額外鍵)。
- **多圖譜**:同層找到兩個圖譜,`security list` 報錯、不猜。
- **子命令**:只有 `--json`,與「首版無篩選旗標」一致。
- **`lumos-cli-read` 錯誤種類表**:表內 23 種全部能在 `scripts/lumos` 找到字面,沒有查到不在表內的 errors 種類。
- **上限常數**:`scripts/lumos` 的 `_VAULT_SAFE_*_MAX` 與 `_SECINV_ERRORS_PER_NODE`、`_SECINV_TEXT_CAP` 的值,與子計劃〈實務隱患〉的 2MiB、64MiB、10000、50000、50、2000 一致。
- **test 綁定**:S1 到 S13、r2、g1 到 g8 等 `[test:]` 指到的函式都存在,Verification 筆記提到的測試名也都存在。
- **d4 例外**:`_trusted_private_dir` docstring 真有「REVISIT:2026-12-07」和「已知例外」段,`scripts/lumos:631` 的註解指得到。
- **NFC 碰撞 PITFALL**:`Env.from_texts` 確實用 `nfc(r)` 當字典鍵。
- **Verification 的實跑數字**:我用 `security list --json` 對本 repo 圖譜量到待分類合約 35 條,和筆記一致;未登記節點是 2 篇,與筆記一致。
- **每支檔有家與 lands_in**:`scripts/lumos`、`scripts/test_lumos.py` 的家是 `lumos-cli-read`,`lands_in` 指到 `Systems/lumos-cli-read`。
- **`lumos-cli-read` 的 search 合約**:`t_search_forget_superseded` 綠,沒被破壞。
- **母計劃 d8、d9、Q3/Q4**:d8 和 d9 的 Q 狀態與正文引用互相對得上。Q1、Q2 已決指 d1,Q3 指 d8,Q4 指 d9,正文裡「仍待」的說法都改成「已依 dN 決定」。「P1 執行更新」只引用 order-demo 的 Verification 路徑,我沒有跨 vault 去查。

## 修補鏡頭(before aadf6b07 → after 84a58aee)

1. **原問題的修復效果**:在 `ds/repo/docs -> ../real`(`docs` 這層是指向 repo 外的捷徑)這個 case 上,修前和修後結果不同。
   - 修前:rc=0、read_complete=True、讀進 1 檔,等於跟著捷徑讀到 repo 外。
   - 修後:rc=2、`vault_selection_failed`、stderr 是「圖譜路徑上的 …/docs 是捷徑,不跟隨」,files=0。
   - case_source:本席自建的輸入。`tmp/…/ds/real/x-knowledge/Systems/leak.md` 放在 repo 外,內容是哨兵字串。
   - 命令:兩版都跑 `lumos security list --json`,工作目錄在 `ds/repo`。
2. **修補處的正常路徑**:`mk()` 建的不在 git repo 內的隔離圖譜(`--vault` 指定)修後 rc=0,控制項照列。本 repo 的真實圖譜修後 rc=0、read_complete=True、907 檔,沒有誤擋。
3. **新發現的同一案例修前修後**:沒有新發現。

這一輪沒有 repair 或 preserve 的回歸證據。

## Finding

**母計劃已決問題 Q3、Q4 的 `text` 欄還是未決時的原文**

severity: minor
blocking: 否

引句:「正式交付必擋清單、閘門接線位置、例外核可者與期限仍待使用者裁定。此題阻塞正式接線,不阻塞唯讀盤點設計。未裁定不得改CI或push行為。」

file: `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:37`(此行未被這次 diff 改動)。

這一段是 Q4 的 `text`,但同一個 frontmatter 裡 Q4 已標 `status: 已決`、`decision: "#d9"`。Q3 的 `text`(第 30 行)同樣還寫「下一個故障執行前仍需確認隔離副本與預算」。

三個月後接手的人只讀 frontmatter 會誤判兩題仍在擋。正文已經寫「Q4已依d9決定」,所以 frontmatter 和正文互相矛盾。

失敗場景:
- 輸入:讀母計劃 frontmatter 的 Q3、Q4。
- 預期:`text` 反映已決狀態,或明標「(原題文,已依 dN 決定)」。
- 實際:`text` 仍是未決時的文字,和 `status: 已決` 矛盾。

歸因:未判定。這兩題的 `text` 在修前就是這樣,r2 只改了 `status` 和 `decision`,不是 r3 修補引入的回歸。我沒有把修前版和修後版的 `text` 欄逐一比對。

## 未驗範圍

- 沒跨 vault 查 order-demo 的證據(依派工詞只核對引用方式)。
- 沒重跑 Verification 筆記裡「26 種變體翻紅」「32 種變體翻紅」的破壞測試,只確認測試函式存在且現況全綠。
- 非 macOS 與沒有 `dir_fd` 的平台,沿用 Verification 〈未驗〉段,我沒補驗。

最嚴重 severity: minor,blocking 共 0 條。
