severity: major

角色:架構對齊審查員。只判這份 r2→r3 修正差異有沒有「跟本專案既有做法不一樣」,不找一般 bug、不評風格。三問逐問答,每問附對照的既有做法 file:line。

## 問一:分層與依賴方向

對照:`Env`(scripts/lumos:407 起)是全專案共用的核心物件,只在 `__init__`/`from_texts` 裡設自己的欄位;各 domain(note-shape、note-audit、guard、drift)一律用回傳值或呼叫端自己的資料結構帶 domain 資訊,沒有別的 domain 在建好 `Env` 之後從外面直接塞私有屬性的先例(唯一例外就是這份 diff 在管的 `undecodable`)。

## F1 Env.undecodable 是 drift 專屬概念,靠外部賦值掛在共用核心類別上,且與既有的 Note.lint 管道重複

severity: minor
blocking: 否 — 目前 `lumos drift scan` 兩種模式(有無 `--at`)剛好只有其中一個管道會非空,尚未證出會誤判的具體輸入,但這是同一概念的第二套表示法
引句:「bad = sorted(set(tenv.undecodable) | {r for r, n in tenv.notes.items() if any("讀檔失敗" in x for x in n.lint)})」

1. `Env.__init__`/`Env.from_texts`(scripts/lumos:407-431)這次補上 `self.undecodable = []`,但這個欄位只有 `_drift_tree_env`(scripts/lumos:25389-25412,r3 未改動)一支函式會填,其餘呼叫端(disk 版 `Env(vault)`)永遠是空清單。
2. 全檔唯一一處在建構完之後直接對 Env 實例外部賦值的地方是 `env.undecodable = bad`(scripts/lumos:25411),不是透過建構參數或回傳值——跟核心類別「欄位只在自己的 `__init__`/工廠方法裡設」的既有寫法不一樣。
3. 「這篇筆記讀不進來」這個概念,本專案已經有現成管道:`load_vault` 讀檔失敗時把 `Note.lint` 設成 `[f"讀檔失敗: {e}"]`(scripts/lumos:327-331),供其他程式查詢(例如 scripts/lumos:13022 的註解就是在講這個管道)。這次新加的 `cmd_drift_scan` 判不了清單(scripts/lumos:25717,r3 新增,見上面引句)沒有沿用這條既有管道,而是另開 `Env.undecodable` 一條平行清單,兩邊靠字串比對 `"讀檔失敗"`(無共用常數,`load_vault` 那邊寫 `f"讀檔失敗: {e}"`,這邊用子字串比對)手動 union 起來。
4. 用 `python3 -c` 驗證:`Env(vault)`(disk 版,`lumos drift scan` 不帶 `--at` 時用的就是這個)建構後 `.undecodable` 恆為 `[]`;`_drift_tree_env` 建的 `tenv`(`--at` 版)的筆記則永遠不會在 `.lint` 裡出現 `"讀檔失敗"`(因為 `_note_from_text` 從沒寫過這個字串,只有 `load_vault` 會寫)。也就是說這行 union 目前「湊巧」在兩種模式下各自只有一半在起作用,沒有測試同時覆蓋「disk 模式 + 不是 UTF-8 的檔」這個組合(新測試 ⑨ 只測了 `--at HEAD` 那條路,scripts/test_lumos.py:656-660)。
5. ⚠ 判不準:目前找不到會讓這行輸出錯誤結果的具體輸入,所以只列 minor,不當 major——但這確實是同一件事「筆記讀不進來」被寫成兩套表示法,而不是把 `_drift_tree_env` 的解碼失敗也寫回 `Note.lint`(跟 `load_vault` 一致)後只查一個管道。

其餘 `Env`/`_drift_tree_env` 相關改動(`from_texts` 的排序註解、`getattr(tenv, "undecodable", [])` 簡化成 `tenv.undecodable`)已看,無 finding——這兩處都是把既有欄位存取寫法收斂成單一形式,方向是對的。

## 問二:命名與錯誤處理

對照:`_note_audit_doctor_lines(repo_root, vault, ci=False)`(scripts/lumos:26163)兩個參數都在函式體內用到(`ci` 在 26192 做提前返回、`vault` 在 26204-26207 算 `vault_rel`);`_guard_planned_line` 的三種失敗一律用「回 `(None,None,None,err字串)`、呼叫端只認 `lines is None` 就統一擋下」的形狀(既有呼叫點 scripts/lumos:12023-12026、12123-12126)。

## F2 _drift_gate_doctor_lines 新增的 vault/ci 兩個參數整支函式沒用到

severity: minor
blocking: 否 — 不影響行為,是死參數,但跟它比照的鄰居 `_note_audit_doctor_lines` 不一樣(那邊兩個參數都真的用得到)
引句:「def _drift_gate_doctor_lines(repo_root, vault=None, ci=False):」

1. r3 把呼叫端(scripts/lumos:1049,原文引句同段:「for _ln in _drift_gate_doctor_lines(_vault_repo_root(env), env.vault, ci=ci):」)與函式簽章一起從 `_drift_gate_doctor_lines(repo_root)` 改成 `_drift_gate_doctor_lines(repo_root, vault=None, ci=False)`,理由是「doctor 閘提醒照鄰居的設定檔防護與參數形狀」(存量漂移守衛.md 摘要行)。
2. 但實際比對函式體(scripts/lumos:25761-25787,`sed -n '25761,25787p' | grep -n "vault\|ci"` 只在 def 那一行命中),`vault` 與 `ci` 兩個參數在整支函式裡完全沒被讀取——真正被搬過來的只有「.lumos 資料夾捷徑不跟」那段防護邏輯(scripts/lumos:25768-25772),不需要這兩個參數也做得到。
3. 對照鄰居 `_note_audit_doctor_lines`(scripts/lumos:26163-26207),`ci` 用在 26192 的提前返回、`vault` 用在 26206 算 `vault_rel` 供後面刪除次數統計用——是真的需要這兩個參數。`_drift_gate_doctor_lines` 只是抄了參數表的「形狀」,沒有抄對應的用途,容易誤導之後的人以為這支函式也會依 `vault`/`ci` 分流。

## F3 _guard_settle_home 用子字串比對 _guard_planned_line 的自由文字錯誤訊息來分岔,是這個函式唯一一處這樣用

severity: minor
blocking: 否 — 目前唯一會命中「找不到預告行」字樣的情境是設計要放行的那條分支,行為正確,但耦合脆弱
引句:「if lines is None and "找不到預告行" not in (_err or ""):」

1. `_guard_planned_line`(scripts/lumos:11735-11762)回傳 `(lines, idx, e, err)`,`err` 是三種失敗各自寫死的中文句子(檔打不開 11746、重複命中 11757-11758、找不到 11761),函式本身沒有提供結構化的失敗種類。
2. 這支函式在本檔另外兩處呼叫點(scripts/lumos:12023-12026、12123-12126)都只用 `if lines is None:` 統一當失敗處理,不區分是哪一種原因。
3. r3 新增的這一段(scripts/lumos:11999-12003,程式碼審查在管的「已有正式行、要換測試」情境的下一步)第一次對同一支函式的 `_err` 做子字串比對——`"找不到預告行" not in (_err or "")`——藉此把「找不到預告行(視為已經轉正過,放行)」跟「檔打不開/重複命中(視為錯誤,擋下)」分開。這是專案裡目前唯一一處靠比對錯誤訊息文字內容來分岔控制流程的地方(全檔搜尋 `in (_err`/`in _err` 只有這一處命中)。
4. 這條耦合沒有共用常數銜接:`_guard_planned_line` 寫死「找不到預告行」(scripts/lumos:11761),呼叫端寫死同一個四字詞(scripts/lumos:12006)。往後如果有人只改其中一邊的措辭(例如把訊息改成「沒找到預告句」),這個分岔會悄悄失效——這是一種未來重現而不是現在能翻紅的重現,故只標 minor、不升 major。

## 問三:第二種做法(有沒有另開一套已有的工具)

對照:`INV_TAG_RE = re.compile(r"\[(?:(?:test|audit|kill|src|git):\s*[^\]]+|manual:\s*[^\]]*|keeps)\]")`(scripts/lumos:3884)是全檔既有、且明確寫在註解裡「抽乾淨宣稱文字時 test/audit/kill 與 regen 證據指針(src/git)都要剝掉」的共用「剝掉 ★INVARIANT★ 行尾工具標記」機制,連 guard 家族自己的 `cmd_guard_kill_add` 都在用它(scripts/lumos:12290:`INV_TAG_RE.sub("", lines[i])`)。

## F4 _GUARD_TAIL_MARKS_RE 是 INV_TAG_RE 的第二套實作,標記字彙較窄,已證出跟 guard 家族既有用法不一致的行為差異

severity: major
blocking: 是 — 帶 `[src:]`/`[git:]` 尾標的合約行,`guard settle` 判不出既有正式行,重複判定會分岔(見下方重現)
引句:「_GUARD_TAIL_MARKS_RE = re.compile(r"(?:\s*\[(?:test|audit|kill):[^\]]*\])*\s*")」

1. r3 把 `_GUARD_TAIL_MARKS_RE` 從「認任何 `[鍵:值]`」收窄成「只認 `test|audit|kill`」(scripts/lumos:11805-11807),理由是代碼審 r2 正確性席抓到的「合約原文自己帶 `[scope:…]` 被誤剝」問題,這個修正方向本身是對的。
2. 但本專案已經有一支專門管「★INVARIANT★ 行尾工具標記家族」的共用正則 `INV_TAG_RE`(scripts/lumos:3884),而且明文寫著這個家族包含 `test|audit|kill|src|git|manual|keeps`;連 `guard kill-add` 這個跟 `_guard_formal_line`/`_guard_settle_home` 同屬 guard 家族、操作同一種 `KEY:★INVARIANT★` 行的指令,都是靠 `INV_TAG_RE.sub("", lines[i])` 剝標記後比對(scripts/lumos:12290,函式 `cmd_guard_kill_add`)。`_GUARD_TAIL_MARKS_RE` 沒有沿用或擴充這支既有正則,而是另外手寫一份字彙較窄的版本,只解決了「不要剝掉非工具標記」這一半,沒有覆蓋 `INV_TAG_RE` 家族裡的 `src`/`git`/`manual`/`keeps`。
3. 重現(inproc 載入 scripts/lumos,不改任何檔):
   ```
   ls = ["---", "summary: |-",
         "  KEY:★INVARIANT★ 大額退費要人工核可 [test:t_refund] [src:committed] [git:abcd123]",
         "---"]
   m._guard_formal_line(ls, 3, "大額退費要人工核可", "t_refund")
   ```
   輸出 `None`——這一行明明是合法的正式合約行(宣稱文字 + `[test:t_refund]` + 兩個 regen 證據指針),`_guard_formal_line` 卻判成「找不到正式行」。對照 `m.INV_TAG_RE.sub("", "大額退費要人工核可 [test:t_refund] [src:committed] [git:abcd123]").strip()` 正確剝出 `'大額退費要人工核可'`。
4. 後果串到 `_guard_settle_home`(scripts/lumos:11991):r3 新加的「已有正式行、綁別的測試就擋下」那段(scripts/lumos:11999-12003)靠 `_guard_formal_line` 兩次呼叫的結果分岔——如果家筆記的正式行剛好帶 `[src:]`/`[git:]` 尾標,兩次呼叫都會判成 `None`(不存在正式行),`_guard_settle_home` 會照「還沒轉正」那條路徑重新寫一條新的正式行(scripts/lumos:12027-12031),跟已經存在、只是判不出來的那條正式行重複——這正是這份 diff 自己在防的「寫出第二條同文字的正式行」問題,只是換了一種尾標組合就繞回去了。
5. `[src:]`/`[git:]` 不是我臆測出來的無關標記:同一支檔案裡明寫它們是「跟 test/audit 一起被 INV_TAG_RE 剝掉」的同一家族(scripts/lumos:3876、3880-3883),且該擴充明確列了「guard 分類·list·trace/scaffold/kill-add/audit」都受影響(scripts/lumos:3881-3883)——`_guard_formal_line`/`_guard_settle_home`(guard settle/bind 用)沒被列進那份影響清單,這次的收窄又進一步讓它跟同家族其他指令的行為分岔。

已看,無 finding 的部分:
- `_notes_status_flipped`/`_note_status_seq`/`_git_log_sha_paths`/`_note_base_status` 的拆分與 `_nodehome_cat_blobs` 失敗語意(`is None` 才算判不了,不拿 `or []` 悄悄轉成「沒有」)跟既有合併邏輯的寫法一致(對照 scripts/lumos:23041-23050 對 `blobs is None` 的處理),沒有另開一套。
- `deadline`/`_left()` 這種「呼叫端傳絕對期限、每步開始前用 `_t.monotonic() > deadline` 檢查」的寫法,是全檔已經在多處(note-audit 判定 `_lint_new_verdict`、`_dispositions_verdict`、`_delguard` 等)使用的既有慣例,這次在 `_notes_status_flipped`/`_drift_range_events`/`_note_status_seq` 加的檢查跟既有慣例一致,不是新形狀。
- `.lumos/config.json` 讀取時「符號連結/捷徑不跟」那段防護,本來就是全檔每個消費端各自內嵌一份(note-shape lint、note-audit、symbol_profile、test_profile 等至少 4 處都各自重複同一段邏輯,從沒抽成共用函式),`_drift_gate_doctor_lines` 這次補的是「跟其他消費端補齊到一致」,不是新增一種寫法。
- `_drift_c3_hit` 改成比對 `len(got)`(fwd 索引的原始項目數,一種寫法一項)而不是 `len(plans)`(去重後的篇數),以及 `_drift_plan_followups` 補 `sn is not None` 檢查——這兩處是邏輯修正,不涉及跟既有分層/命名/重複做法的落差。

總結:最嚴重等級為架構分層與重複實作類的 major(F4:`_GUARD_TAIL_MARKS_RE` 重新發明 `INV_TAG_RE` 已有的標記家族,且證出行為分岔),blocking 共 1 條;另有 3 條 minor(F1 Env.undecodable 與既有 Note.lint 管道重複、F2 死參數、F3 錯誤訊息子字串耦合)。
