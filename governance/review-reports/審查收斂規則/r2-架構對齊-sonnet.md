severity: major

我對照了 scripts/lumos,共 4 條不對齊(1 條 major,3 條 minor)。

severity: major
blocking: 是 — S5 要 `pitfalls --diff` 讀圖譜,但現行分級刻意不載圖譜,而且已有另一條放圖譜相關分級調整的路。
引句:「分級升為 high(會派完整代碼審、派工鏡頭會附那條合約)」
對照:``scripts/lumos: `_pitfall_tier` 約 43677-43692`` 的說明寫「★vault-free★,pitfalls 在 pre-push 熱路徑上不載圖譜(代碼審 r1 架構席)」。``scripts/lumos: `cmd_pitfalls` 約 44389`` 註解寫 `Env(vault)` 實測 4.7 秒,不能每輪付。``scripts/lumos: `spec-gate --push-check` 約 9095`` 註解寫「pitfalls/code-loop 都是 vault-free,只有這裡有圖譜」。
判定理由:
- `_pitfall_tier` 只吃 claims、files、repo_root、diff_range,沒有圖譜環境。
- 計劃要它去找「哪個節點的 about_code 含這支檔、該節點有沒有 `[residual:]` 合約行」,這是從 `pitfalls` 往圖譜層直呼。
- 它還會把 4.7 秒的 `Env` 載入放進 pre-push 熱路徑,代碼審 r1 架構席已經挑過同一件事。
- `code-loop check` 與推送閘靠 `pitfalls --diff --json` 的 tier 判定,所以 high 要不要升,影響的是推送閘。
- 既有做法是「要讀圖譜的分級調整放在已經載圖譜的 `spec-gate --push-check`」,light 升降就是這樣做的。
- 計劃應改走同一條路:在 `spec-gate --push-check` 或 `code-loop check` 這類已載圖譜的位置加一步「碰到帶殘留合約,印 high 並要求走代碼審」。
- 若堅持放進 `pitfalls`,至少要寫明另一種做法,例如只在 `--diff` 非 `--no-lint` 時才載圖譜,並說明為何不違反 vault-free 的決定。

severity: minor
blocking: 否 — 「寫入流程」少了鎖與寫後自驗,而這在既有指令是固定範本。
引句:「寫入當下就驗:節點存在、決策存在、沒被標 `valid: false`」
對照:``scripts/lumos: `cmd_guard_audit` 18712-18770`` 外層 `_vault_write_lock(env.vault)`,內層 `_cmd_guard_audit_locked` 用 `env.find`、`load_raw_for_edit`、`_kill_find_contract` 定位合約行,最後 `atomic_write_verify(path, new_lines, key, check)` 寫後自驗。``scripts/lumos: `cmd_guard_bind` 16925`` 與 `cmd_guard_kill_add 17716` 是同一個形狀。
判定理由:
- 計劃只寫了「寫入前驗」的四個條件,沒寫要走這個寫入範本。
- 模組裡有註解說過,決策與守衛的寫入沒鎖會互相覆蓋開頭欄位(代碼審 待決問題改存開頭欄位 r2、r3)。
- 計劃應補一句:`guard residual` 照 `guard audit` 的形狀,外層 `_vault_write_lock`、定位用 `_kill_find_contract`、寫後用 `atomic_write_verify` 比對標記。
- `--remove` 與重複加同一個標記(冪等)也要寫,`guard bind` 有「已綁無需重綁」。
- 決策解析請直接重用 `_dref_parse` 與 `_dref_norm`。它用 `fullmatch((.+?)#(d\d+))`,不必另寫「最後一個 `#`」的切法。

severity: minor
blocking: 否 — 新標記沒說要加進剝除正規式 `INV_TAG_RE`,「一個正規式」只做了一半。
引句:「另立 `[residual:]`;解析「節點#決策」重用既有的決策指標解析」
對照:``scripts/lumos: `AUDIT_REF_RE` 5485 與 `INV_TAG_RE` 5499``。`INV_TAG_RE` 同時剝掉 test、audit、kill、src、git、manual、keeps,註解寫剝除影響 Check T 乾淨宣稱、contracts、lint、guard 分類、guard list、trace、scaffold、kill-add、audit 這 8 類呼叫點。
判定理由:
- 計劃寫了要有 `RESIDUAL_REF_RE`,沒提要把 residual 併進 `INV_TAG_RE`。
- 不剝的話,殘留標記會留在乾淨宣稱文字裡。`guard audit` 與 `kill-add` 的子字串定位 `invariant_substr in INV_TAG_RE.sub(...)` 也可能誤命中標記裡的節點路徑或決策 id。
- 這不是引入第二種做法,是照做不完整。
- 計劃應列出:新增 `RESIDUAL_REF_RE`、併進 `INV_TAG_RE`、補 `invariant_residual_refs` 這類抽取函式,並說明 S2 的保留靠哪個既有的 `AUDIT_REF_RE.search` 分支不碰它。

severity: minor
blocking: 否 — 鏡頭徽章與逃逸帳新欄位的掛接點寫得不夠貼近既有結構。
引句:「跟現在的綁定測試狀態徽章並排,例「⚠帶殘留 2 筆」」
對照:``scripts/lumos: `_LENS_BADGE` 47710`` 與 ``scripts/lumos: `_lens_render_body` 約 48350-48370``。徽章只在 `kind == "INVARIANT" and bidx is not None` 才算,`_LENS_BADGE` 的鍵是 `_classify_one` 的四種狀態(real、dangling、fake、naked)。
判定理由:
- 「帶殘留」跟綁定測試狀態是兩條獨立的軸,不該塞進 `_LENS_BADGE` 的鍵。
- 但現行徽章在 `bidx is None`(平台設定讀不到)時整個不顯示。
- 計劃應寫明殘留徽章不依賴 `bidx`,否則平台設定讀不到時殘留反而看不見。
- `_lens_render_body` 的第 40 行截斷與 INVARIANT 小計也要決定要不要把殘留數併進去。
- 逃逸帳這側:``scripts/lumos: `cmd_loop_escape` 12540`` 的 `_escape_withdraw(... others=(loop_id, stage, severity, desc, defect_ref, ...))` 用一組清單擋「撤回時不准混用其他旗標」。新增 `--residual-ref` 要補進這個 `others` 元組,否則撤回可混用。
- `rec["defect_ref"]` 在 12686 有 `.strip()` 並用 `_esc_clean` 顯示,`residual_ref` 應照同一套,並說明要不要像 `defect_ref` 那樣驗格式。上面的註解說歸因守衛只防實存性,可寫成「只驗 `<節點>#dN` 格式,不驗決策有效」。

不對齊共 4 條,其中 major 1 條。
