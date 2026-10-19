severity: major

鏡頭:合約與圖譜一致/知識同步,範圍是修補差異的文件那半(r2-repair-docs.patch)。

**推送前兩道檢查,在 HEAD 86aa8f40 實跑**
- `python3.14 scripts/lumos doctor --ci` 的 rc 是 0,結果是「圖譜健康 — 0 issues (894 篇)」。另有 29 段、367 條提醒沒算進去。
- `python3.14 scripts/lumos note-shape --diff 0beb6d7d…..HEAD` 的 rc 是 0。
- 但 note-shape 最後印了「筆記測試綁定:這組的 20 秒用完了,剩下的名稱這次不查」,所以測試綁定那一組沒查完。這一點我沒驗,列入未驗範圍。
- HEAD 比 b76b570e 多的只有審查材料,`scripts/lumos` 沒變。
- 兩篇被改的節點(規格閘、計劃)`lumos lint` 都是 0 問題。
- 新寫的 WHY 行綁的 `t_prepush_spec_gate_done_stale_still_checks_nogo` 存在於 `scripts/test_lumos.py`。

**1. 決策 d3 與 B2 沒跟著寬待收窄一起改,和修後程式不一致**
severity: major
blocking: 是
- **哪一段**:修補把 S27、規格閘 KEY/WHY、雙向門放行的「部分翻案」標註都改成「起點已 done 才寬待、不做清單照查」。決策 d3 本身(計劃節點 decisions 欄)和〈做法〉10 B2 兩處都沒動。
- **d3 現在寫的**:「推送閘對這次推送改到計劃檔本身的 done 風險低計劃也跑留痕裡的測試(紅了擋);留痕指紋對不上或測試找不到時只提醒不擋」。B2 同樣沒講起點條件和不做清單照查。
- **程式實際做的**:`_spec_gate_push_scan` 的 `done` 要求 `_spec_gate_status_at(...)=="done"`。
  - 輸入一:這次推送才把狀態改成 done,而且留痕指紋對不上。程式回 `stale` 擋下(`if stale and not done: return stale, None`),和 d3 寫的「只提醒不擋」相反。
  - 輸入二:起點已 done,留痕指紋對不上。程式仍呼叫 `_spec_gate_push_nogo_only`,輕量審沒過就擋,也不是「只提醒不擋」。
- **為什麼算 major**:專案規定決策有挑戰程式的效力。三個月後的人讀 d3,會以為程式把「改成 done 的指紋過期」放行了。規格閘 KEY 和雙向門放行都指向 d3 當出處,讀者會讀到過期的版本。
- **佐證**:`scripts/lumos:10017`(`# 寬待只給「推送範圍起點就已經是 done」…`)、`scripts/lumos:9912-9927`。決策欄文字見 `docs/lumos-toolchain-knowledge/Projects/筆記指令健檢與規格閘小修_計劃.md` 的 `id: d3`。
- **歸因**:有證據的修復造成的文件分叉。修前程式讀起點之前,d3 與程式大致相符;修後程式行為變了,d3 沒跟。修前版本 55da596f 沒有 `_spec_gate_status_at`。
- 同源的小處:〈實務隱患〉(c)「指紋對不上與測試找不到兩種沒出路的情形只提醒不擋」也沒補不做清單照查。
- 引句:「推送閘對這次推送改到計劃檔本身的 done 風險低計劃也跑留痕裡的測試(紅了擋);留痕指紋對不上或測試找不到時只提醒不擋;沒被改到的 done 計劃照舊不查」

**2. refcheck 和 doctor P 段:沒有旗標的「路徑加子指令」現在被判 missing,是修補造成的回歸,S18 和 refcheck 的 WHY 也還寫「路徑加參數」**
severity: major
blocking: 是
- **哪一段**:`_ref_cmdline_token` 改成只在第一個詞之後有 `-` 開頭的詞時才截斷;S18 和 `Systems/lumos-refcheck.md` 的 WHY 都還寫「路徑加參數的一行指令只核對第一個詞」。
- **重現一:函式直接呼叫**,修後輸出:
  - `scripts/lumos doctor` → `'scripts/lumos doctor'`(沒截,修前會截成 `scripts/lumos`)
  - `scripts/lumos doctor --ci` → `'scripts/lumos'`
  - `scripts/lumos summary-add x` → 沒截
- **重現二:refcheck**,輸入 `跑 \`scripts/lumos doctor\` 看健檢`:
  - 修後(`scripts/lumos`)輸出 `✗ missing scripts/lumos doctor`。
  - 修前(`git show 55da596f:scripts/lumos`)輸出 `✓ ok scripts/lumos`。
- **重現三:doctor P 段實跑**,修後多出兩處假的「已不存在」,修前沒有:
  - `Projects/最低Python版本改3.14_計劃.md → scripts/lumos python-path(已不存在)`
  - `Projects/派工鏡頭可指定目標repo_計劃.md → scripts/lumos dispatch-lens(已不存在)`
- **測試缺口**:`t_ref_path_first_word_of_command` 只用 `scripts/e2e.sh --cleanup` 這種帶旗標的寫法,抓不到這個回歸。
- **歸因**:有證據的修復回歸。修前一律截第一個詞,修後要求帶旗標。
- **說明**:作者要擋的是 `src/app v2/x.py` 這種帶空白路徑的缺檔被截成存在的前綴,這個目的合理。但現在沒帶旗標的子指令全被打回整串核對。
- 引句:「路徑加參數的一行指令只核對第一個詞(_node_code_ref_tokens 的 cmdline 選項,預設關、推筆記與每支檔有家不受影響)」

**3. cochange 預設改成 `--staged` 後,說明和程式的 docstring 還寫「皆缺 rc 2」**
severity: minor
blocking: 否
- **程式**:`cmd_cochange_check` 沒帶範圍已改成印「沒帶範圍,照 --staged 查這次要提交的內容」並照常查。實跑 `lumos cochange check` 確認如此。
- **過期的兩處**:
  - `Systems/cochange-guard.md:42` 寫「皆缺 rc 2、同給 `--diff` 優先」。
  - 同函式 docstring 寫「皆缺 --staged/--diff 或 git 失敗=2」。
- **另一處不一致**:計劃〈做法〉9 B9 與 S22 只說 `home check` 與 `note-shape` 兩支,實際連 cochange 共三支(程式註解寫代碼審 r1 架2)。S22 的條款和說明沒補。
- **歸因**:有證據的修復造成的文件漂移(行為是 r1 折入,同步漏了 cochange-guard)。
- 引句:「`lumos cochange check [--staged|--diff <A..B>] [--repo] [--json]` — 皆缺 rc 2、同給 `--diff` 優先」

**4. 計劃〈做法〉1.4 沒跟「summary-line 在非 git 跳過」、「總開關 off」同步**
severity: minor
blocking: 否
- **計劃寫的**:「不是 git 專案…summary-add 同樣 rc2 不寫…不另寫跳過分支」,格子開關只提 `_ns_slots_mode`、「off 不看」。
- **程式實際的**:`_summary_write_shape_check` 在非 git 時,`summary-line`(`nongit_ok=True`)跳過檢查照寫,`summary-add` 才擋。`note_shape.gate` 為 `off` 時兩道檢查都不跑,warn 只提醒。
- **佐證**:`scripts/lumos` 的 `_summary_write_shape_check` 第 2 段;審計紀錄寫了「summary-line 在非 git 退步」已折入,但〈做法〉本文沒改。
- 引句:「不另寫跳過分支(圖譜本來就在 git 專案裡、提交前掛鉤也要 git,單人使用不值得多一條路;跟 `drift fix` 同一個擋法)」

**5. 計劃〈實務隱患〉效能那條和 PRIOR-ART 與〈做法〉本文不一致**
severity: minor
blocking: 否
- **效能那條寫的**:「索引清單整次執行只讀一次」和「doctor P 段多一次 `git check-ignore --stdin`」。
- **實際**:S32 已改成「工作目錄的路徑樹只列一次」;〈做法〉8 與程式 `_git_ignored` 是用 `_lens_git` 把路徑當參數,不走標準輸入。
- **PRIOR-ART** 那行同樣寫 `git check-ignore --stdin`。

**6. 決策 d2 文字沒反映新檔改走空殼**
severity: minor
blocking: 否
- **d2 寫的**:「教人把實作檔暫時換回實作前的版本」。
- **程式訊息(`scripts/lumos:9231`)和 S25**:實作是新檔時要換成只留介面的空殼,不要移走。
- 方向沒翻案,所以只列 minor。

**刪掉的 FLOW 行(test-profile-multiplatform):沒有帶走程式碼推不出的資訊**
- 被刪那行只寫 `load_platforms → resolve_test_refs → _platform_test_index → Check T/classify_invariants/cmd_archive` 的呼叫流向和判 real/fake/dangling,用 grep 都查得到。
- 行本身沒有 `[來源:]`,依專案規則本來就不該留。
- 其餘 KEY 行只加了反引號,沒丟內容。這一項沒問題。

**其他已核對、一致的**
- 寫入原語數字:`lumos-cli-write.md` 表頭已不寫死數字,指到 `lumos --help`;`lumos-cli-read.md` 也改成連結。
- `docs/指令參考.md` 和 `docs/command-reference.md` 已補 summary-add。
- 摘要行分類和必有鍵:新 WHY 帶 `[出處:]` `[因:]` `[test:]`,lint 0 問題。
- summary-add 在非 git 擋、summary-line 在非 git 跳過,和 `_summary_write_shape_check` 一致。
- refcheck 的帶空白路徑缺檔不再被誤判存在,見上面第 2 項。

**回答三問**
1. **原問題的修復效果**:有行為證據的只有兩項。起點已 done 的寬待與不做清單照查,有 `_spec_gate_push_one` 的程式路徑,我跑了 `t_prepush_spec_gate_done_stale_still_checks_nogo` 之外的路徑閱讀,沒另跑該測試(`timeout` 指令不存在,沒跑成,未判定)。`src/app v2/x.py` 這類帶空白缺檔,修後走整串核對,我只靠讀碼確認,沒另造輸入。
2. **修補處的相鄰路徑**:兩個壞掉的相鄰路徑是第 1、2 項。第 2 項是修復回歸,修前修後兩版我都實跑過。
3. **新發現的同一案例修前修後**:
   - 第 2 項:`scripts/lumos doctor` 的 refcheck 結果,修前 ok、修後 missing。
   - 第 1 項:d3 與程式之間,修前大致一致、修後分叉。

**未驗範圍**
- 沒跑全套測試,也沒另跑 `-k prepush_spec_gate_done` 子集。
- note-shape 的測試綁定那組沒查完(上面提過的 20 秒用完)。
- 沒逐個核對 `t_docs_command_count` 等守衛的數字。
- 沒驗 S10 的 `[[Systems/x]]` 反引號是否只是排版。

最嚴重 severity:major,blocking 共 2 條(第 1、2 項)。

我的臨時目錄 `/private/tmp/lumos-seat-work/code-筆記指令健檢與規格閘小修/整合-sonnet` 已用字面絕對路徑刪除。
