severity: major

我把 diff 逐 hunk 走過,在臨時目錄 `/tmp/rvC.onx3` 用 `scripts/test_lumos.py` 的測試輔助函式做了實驗。repo 本身沒動。發現 2 條:C1 是上輪「借舊行的債」漏洞的另兩種形狀,C2 是申訴範圍放寬後蓋掉整行判定。

**C1 「現況描述沒寫來源」以外的整行規則,括號裡的新內容還是能借舊行的債過關(題:SEE 只放連結、條件標記)**
severity: major
blocking: 是 — 上輪 r1 通才席點名的同一種漏洞,只修了一條規則名,同形狀的另外幾條仍可繞過第一層
引句:「        if k == ("現況描述沒寫來源",):」
- 輸入一(SEE):起點版本摘要有一行 `SEE:[[Systems/Pay]] 付款說明在這裡`。它夾了句子,所以本來就犯「SEE 只放連結」。這次只在句尾補 `(現況:線上已全量切換新閘道)`。
- 走到的行:`_ns_append_subtract` 裡 `_ns_viol_key("SEE 只放連結", …)` 的鍵只有規則名。舊行的計數是 1,新行的違規也是 1,所以被扣掉。
- 繞過的原因:`_ns_check_line` 的 `SEE` 分支是 `if … elif m and not skip`。SEE 行永遠不會進「現況描述沒寫來源」那條,括號裡沒帶來源的現況句就沒有任何一道在查。
- 第二層只判尾巴是 CONTEXT 還是 CODE,不管有沒有來源,所以也不會擋。
- 預期:跟新行整行寫同一句一樣被擋。
- 實際:提交前 `note-shape --staged` 回 rc 0、沒有任何輸出。
- 對照:同一句整行新寫 `SEE:[[Systems/Pay]] 付款說明在這裡(現況:線上已全量切換新閘道)`,回 rc 1 並報「SEE 只放連結」。
- 輸入二(條件標記):起點有表格列 `| 付款 | 舊閘道還在用 [when-file:src/x.py] |`,已犯「條件寫在不評估的地方」。這次補 `(另見 [when-file:src/y.py])`,回 rc 0。
- 對照:另起一列寫新標記,回 rc 1。
- 輸入二的影響較小,因為這個位置的條件標記本來就不會被評估,但形狀跟輸入一相同。
- 範圍:其他規則名不受影響。「程式行號引用」和「釘版本不合法」用片段當鍵,同一個引用寫兩次會多算一條。「回頭條件格式不合」只看行首,括號補不出新違規。
- 重現:
  - 在 `/tmp/rvC.onx3` 的 `scripts/test_lumos.py` 加測試。
  - `root=_tail_repo(summary="SEE:[[Systems/Pay]] 付款說明在這裡")`
  - `_ns_note(root, summary="SEE:[[Systems/Pay]] 付款說明在這裡(現況:線上已全量切換新閘道)")`
  - `_ns_stage(root)`
  - `_ns(root)` 回 `(0, '')`。
  - 跑法:`python3.14 scripts/test_lumos.py -k t_zz_probe`。
- 修法:`_ns_append_subtract` 只扣有片段鍵或條件鍵的規則,只用規則名當鍵的(`SEE 只放連結`、`條件寫在不評估的地方`)一律不扣。這跟「現況描述沒寫來源」永遠不扣是同一條原則。

**C2 申訴不分範圍後,只判句尾的申訴會把同編號的整行 CODE 判定也蓋成 CONTEXT(題:申訴只指名其中一份)**
severity: minor
blocking: 否 — 要先走完一輪申訴、而且同一句日後在別處再整行出現才會漏;依賴發生順序,但結果是 CODE 判定被洗掉
引句:「            c = disputes.get((name, r["id"]), c)」
- 輸入:判定檔 `v1.json` 有一列 `{id: I, class: CODE}`,是整行判定。申訴檔 `v2.json` 的 `disputes` 指向 `v1.json`,列是 `{id: I, class: CONTEXT, tail: T}`,是只判句尾的申訴。
- 走到的行:`_note_audit_dispute_map` 的鍵不再含 tail,`_note_audit_fold_scoped` 照鍵 `(name, id)` 取代。`v1.json` 裡鍵 `(I, None)` 的整行 CODE 被換成 CONTEXT。
- 預期:只判句尾的申訴只換掉句尾範圍的判定,整行 CODE 保留。
- 實際:`_note_audit_class_for(fold, {"id": I, "tail": None})` 回 `CONTEXT`,`best == {(I, None): 'CONTEXT'}`。
- 影響:同一句話日後在別的筆記整行新寫(例如整句複製),整行項目直接算 CONTEXT 放行。
- `v2.json` 裡 tail 範圍那一列自己根本沒進 `best`,因為 `kind` 是申訴,不走判定迴圈。
- 重現:`/tmp/rvC.onx3` 的 `t_zz_probe5` 輸出 `whole-line item class: CONTEXT | scoped: {('abab…', None): 'CONTEXT'}`。
- 修法:申訴列自帶 `tail` 時,只換 `v1.json` 裡 `tail` 欄相同(或兩邊都是 None)的列;被指名那份沒有同範圍的列時,不要替整行 CODE 背書。

**已逐項走過、結果沒問題的題目(不是 finding)**
- `_gate_event_fit` 二分:拿 300 組隨機輸入對照舊的逐筆丟,結果完全一致。輸入涵蓋 0、1、2、3、5、40、200 筆,`check` 欄塞到 3900 到 5000 位元組,`nodes` 有無、`nodes_cap` 有無都含。旗標讓 0 筆也裝不下時,行為跟舊的相同。
- `_ns_deleted_summary_lines` 改走共用讀法:拿 10 種合成 diff 對照舊實作,結果完全一致。種類有空 diff、刪整檔、非 UTF-8 位元組、`\ No newline`、CRLF、兩個 hunk、二進位檔、`---` 開頭的續行、改名、結尾無換行。內容是 `-- x` 的被刪行被當檔頭是預期中的修正。
- NFC/NFD 撞名:有違規的篇一定在 diff 裡,而 `table` 只由 diff 建出來,所以一篇在 diff、一篇沒改的情形不會誤配。撞名偵測只看 diff 夠用。
- 起點與終點批次讀:候選要求 `a == b` 兩邊都存在,所以暫存區沒有那篇不會發生。終點是 `index` 時 `:路徑` 的寫法正確。終點非 `index` 時走 `<sha>:路徑`,正確。路徑含換行本來就先被排除。
- skip 改用 `_note_audit_class_for`:`heavy` 仍用不比範圍的 `_note_audit_fold` 先排除,判了 CODE 或 MIXED 的不會被略過。被別的範圍判成 CONTEXT 的整行項目變得可略過,略過後 check 也算涵蓋(SKIP),口徑一致。
- `_ns_relaxed_seen`:推送編號是 `date-$$`,實際不會重用。`--absolute-git-dir` 在 worktree 各自獨立,不會互相吞帳。寫記號失敗回 False,照記帳,偏安全。
- 固定席節點:guard-kill、bound-tests-gate、lumos-cli-read、授權與歸屬、測試假綠形態、design-loop 處置閘、reversibility-governance-ledger、pitfalls-code-loop,diff 都沒碰到它們宣稱的行為或合約。diff 沒動 `search`、guard kill、`_VENDORED_TOOLKIT`、`scripts/lumos` 檔頭的授權行,也沒動處置閘。
- 角色卡:`be-api-compat` 方面,判定檔 `tail` 欄收緊成 16 碼十六進位,只影響自家判定檔格式,diff 內沒有舊格式資料。⚠ 若 6c22a561 已推出、別的專案已提交過其他格式的 `tail`,整份判定檔會被當成壞檔,這點我沒查證。`be-authz` 沒有新增端點,不適用。

最高嚴重度 major,blocking 1 條
