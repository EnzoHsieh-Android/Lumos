severity: major

審查範圍:/tmp/code-revB-r2.patch 全部 hunk(計劃、scripts/lumos、scripts/test_lumos.py)。在 rw 工作樹實跑 `python3.14 scripts/test_lumos.py -k when_gone`(35 條全綠),另在副本做翻紅實驗與輸入實測。

**C1 字串含 `[` 被擋了,同一個「標記在第一個 `]` 結束」的截斷,路徑含 `[` 卻放行,RULE 撤除條件因此永遠誤成立**
severity: major
blocking: 是 — 修法只補了字串、沒掃同根因的路徑那一段;RULE 撤除條件寫 `app/[id]/page.tsx` 這類路徑會被默默截成不存在的路徑,推送時對一支還在的檔喊「撤除條件成立」。
引句:「when-gone 的字串不能含方括號(標記在第一個 ] 結束,後面會被截掉)」
file: `scripts/lumos:31951-31958`(`_probe_gone_err` 的 `[` 檢查只對 `text`,不對 `path`)
file: `scripts/lumos:32073-32080`(`_retire_lines` 把撤除條件改寫成 `"[" + vals[0] + "]"` 再交給 `_probe_parse`,`_PROBE_TOKEN_RE` 的值部分是 `[^\]\n]*`)
1. 輸入:`RULE:頁面要人簽 [依據:人] [since:2026-09-01] [retire:when-gone:app/[id]/page.tsx]`(Next.js 動態路由,路徑本身有方括號)。
2. `slot_parse` 把撤除條件值切成 `when-gone:app/[id]/page.tsx`;`_slot_retire_err` 走 `_probe_check_value` → `_probe_gone_err`:只檢查 `text`(空字串),路徑 `app/[id]/page.tsx` 不含 `..` 就過 → 回 None,提交時不擋。
3. 實測 `_retire_lines(txt)` 解析結果為 `conds: [('gone', 'app/[id')]`、`errs: []`、`bad: False`:路徑被截成 `app/[id`,樹上永遠沒有這個路徑,`present` 回 False、`gone` 回 True,所以推送時只要這一行是候選就點名「撤除條件成立」,而 `app/[id]/page.tsx` 其實還在。
4. 同形狀在 REVISIT 行:`REVISIT:[by:2099-01-01][when-gone:app/[id]/page.tsx] x` 單看 `_probe_parse` 回 `conds=[('gone','app/[id')]`、`errs=[]`(提交時剛好被另一條「第一個位置要是日期」規則擋下,但原因講錯);條件在前、期限在後時錯誤訊息是「沒帶期限」,也不是真因。
5. 最小重現(指令):
   `python3.14 - <<'E'`
   `…載入 scripts/lumos 為 m…`
   `print(m._slot_retire_err("when-gone:app/[id]/page.tsx"))` → 輸出 `None`(應報錯)
   `print(m._probe_check_value("gone","app/[id"))` → 輸出 `('app/[id', None)`。
6. 這是上輪「字串含 [」那條的同根因再發一次(「同族一次掃完」):根因是標記值不能含 `]`、也就不能含會讓人誤以為成對的 `[`,應該對整個值(路徑加字串)擋 `[`,或乾脆擋 `[`/`]` 在 `_probe_check_value` 對 `gone` 的整串。天花板 4 也只寫「字串不能含 `[`」,路徑沒寫。

**C2 反引號檢查仍會把「說明文字裡單獨提到 `[when-gone:`」當成標記,誤擋合法的條件式回頭條件**
severity: minor
blocking: 否 — 只在提交時多擋、改寫說明文字即可繞開,但訊息(「字串不能含反引號」)指向不存在的字串,而且計劃明寫「說明文字裡提到 when-gone: 不算」。
引句:「回頭條件行原文:只看真正的 [when-gone: 標記、到同一個標記的 ] 為止」
file: `scripts/lumos:31962-31973`(`_probe_gone_backtick_err`)、`scripts/lumos:27970`(呼叫端 `_ns_revisit_cond_viol`)
1. 「真標記」的判準只剩「`[when-gone:` 之後找得到任何 `]`」。說明文字裡寫 `` `[when-gone:` ``(只提鍵名、沒有閉合),後面只要同一行還有任何 `]`(別的標記、`[[節點連結]]`、`[by:…]`),就把「從 `[when-gone:` 到那個 `]` 之間」整段當標記值,中間含反引號就報錯。
2. 實測:`REVISIT:[when-file:src/a.py][by:2099-01-01] 把 `` `[when-gone:` `` 那段 [[Projects/x]] 改掉` → `_ns_revisit_violations` 回「條件寫錯:when-gone 的字串不能含反引號…」;`REVISIT:[when-file:src/a.py][by:2099-01-01] 把文件裡寫 `` `[when-gone:` `` 的地方改掉,見 `` `[when-file:x]` `` 那種` 同樣被擋。同一行改成日期型(`REVISIT:2099-01-01 …`)則不擋,可見只擋條件式。
3. 與上輪第一條同一類(用原文正則猜標記範圍),修法把「有閉合的說明文字」放行,「沒閉合的說明文字」仍誤擋。比較穩的做法是只檢查 `_PROBE_TOKEN_RE` 在剝過反引號的文字裡真的解析出的 `when-gone` 標記,再回原文對位。

**C3 工作目錄模式「每支檔看預算」那段新增的檢查,沒有任何測試咬得到**
severity: minor
blocking: 否 — 行為不會錯,是補測試的缺口;計劃審計紀錄把「工作目錄模式每支檔看預算」列為已折入的修正,但還原它測試全綠。
引句:「if self._over():」
file: `scripts/lumos:32370-32376`(`_read_raw` 工作目錄分支迴圈內的 `_over()`)
file: `scripts/test_lumos.py`(新增測試 ⑥,約 55970 行起)
1. 測試 ⑥ 把 `tr.deadline = _time.monotonic() - 1` 設成一開始就逾時,`_read_raw` 開頭那個 `if self._over(): return False`(diff 前就有)就先回 False,迴圈從未進入。
2. 翻紅實驗:在副本 mut1 刪掉迴圈內那兩行 `if self._over(): return False`,`python3.14 scripts/test_lumos.py -k when_gone_review` 結果 `9 passed, 0 failed`(沒有任何一條翻紅)。
3. 沒有前置斷言證明「預算在迴圈中途到期」這條路真的走到(要在第二支檔之前讓 `deadline` 到期,例如對兩支檔的條件、用 monkeypatch 讓第一次 `stat` 之後 `_over` 變 True)。

沒問題的項目(逐 hunk 走過,判定成立):
- `_drift_cond_split(v, k)` 鍵參數改必填:`scripts/lumos` 與 `scripts/test_lumos.py` 全部 13 處呼叫都帶第二個參數,沒有漏的舊式單參數呼叫。
- `is_dir` 共用:`path.rstrip("/")` 對 `_posix_norm` 後的值無影響(正規化已去尾斜線);when-file 提示由「只看一般檔前綴」改為「看全部條目前綴」,只多涵蓋連結檔與子模組,測試 ⑦ 兩個方向都釘住。
- `_read_raw` git 模式改走 `_nodehome_cat_blobs_capped`:用列檔時的內容編號當 spec,路徑含換行不會再讓整批失敗;> 2 MB 的檔回 None、不進記憶體(測試 ③ 在還原成整份讀時會因 `held` 是 3 MB bytes 而紅);超過上限與讀不出合併成同一則原因「讀不出或超過 2 MB」,訊息與 `_drift_gone_text` 一致。
- 反引號檢查的 `startswith("when-gone:")` 分支:`_slot_retire_err` 的 `v` 已去頭尾空白,撤除條件值內有反引號仍報;REVISIT 行原文不會以 `when-gone:` 開頭,兩分支不互相干擾。
- `[` 檢查在 `_slot_retire_err` 與 `_probe_parse` 兩條路都生效(字串部分),`slot_parse` 能容巢狀括號而 `_retire_lines` 改寫後會被截斷,所以撤除條件那條路也必須擋(字串部分已擋,見 C1 的路徑部分缺口)。
- 計劃〈驗收條款〉S1~S5 的測試名稱仍存在且綠;S3 沒列 `[` 的規則,新測試 `t_drift_when_gone_review_r1` 未綁進任何 [S?](不影響行為,只是新增行為沒有條款綁定)。

固定席節點(逐條判這份 diff 會不會破壞其宣稱的行為或合約):
- Systems/bound-tests-gate [家]:★INVARIANT★ 是 code-loop check 對固定席合約綁的測試逐支真跑。本 diff 沒有改閘的實作,只新增一支測試函式 `t_drift_when_gone_review_r1`(未綁合約、不影響該合約)。判不影響。
- Systems/guard-kill:兩條 ★INVARIANT★ 談 guard kill 的 rc 優先序與 `--json` 純淨度。本 diff 不碰 guard kill 的程式路徑。判不影響。
- Systems/授權與歸屬:授權檔不得進 `_VENDORED_TOOLKIT`、主程式檔頭需帶 SPDX 與 MIT 全文。本 diff 只動 `scripts/lumos` 函式本體,不碰檔頭與白名單。判不影響。
- Systems/測試假綠形態:★INVARIANT★ 要求「還原翻紅釘」配前置斷言證明被測路徑走到。本 diff 的新測試多數符合(③ 的 `held` 與 `gone_why` 斷言、⑤ 的 monkeypatch、⑦ 兩方向),唯一不符合的是 ⑥ 對迴圈內預算檢查(見 C3)。就這條合約而言,C3 是對它的一處未遵守。
- Systems/lumos-cli-read:search 預設排除 superseded 的合約。本 diff 不碰 search。判不影響。
- Systems/pitfalls-code-loop [家] ★RISK★:談 pitfalls 與代碼審流程。本 diff 不改分級邏輯,只動 drift 條件評估。判不影響。
- Systems/lumos-cli-lifecycle:re-inject 只覆蓋 sentinel 之間 body。本 diff 沒有再改紀律範本與注入程式(範本與注入區塊在前一輪已處理)。判不影響。
- Systems/design-loop:處置閘第五步要求設計審材料為 .md 計劃並檢查條款綁測試。本 diff 修改的計劃檔是 .md,條款 [S1]~[S5] 與其綁定測試未變。判不影響。
- 其餘「超出上限,只列名」的 14 個節點(loop-convergence-recording、reversibility-governance-ledger、lumos-deinit、節點範圍與索引守衛、check-t-sentinel、cochange-guard、check-r-guard、doctor-irreversible-hint、lumos-refcheck、canary-audit、slim-get/slim-install/slim-uninstall、雙向門放行、規格落成可驗收條件、逃逸自動記、core-invariant-baseline、judge-severity-gate):只列名、未給內容,從 diff 看不出牽連它們宣稱行為的具體路徑,不臆測。

最高 severity:major
