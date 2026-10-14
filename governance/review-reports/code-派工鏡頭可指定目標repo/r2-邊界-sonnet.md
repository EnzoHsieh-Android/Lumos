severity: major

這輪修補的路徑邊界大致站得住。我實測了 `..`、`.`、雙斜線、結尾斜線、`.GIT` 大小寫、`--out` 指向 repo 根或其絕對路徑、`Systems/..`、`Systems/./a`、`Systems//a`,都照預期擋下或放行。但有一處回歸會讓既有測試變紅,另有三處較輕的問題。

severity: major
blocking: 是 — `_dispositions_verdict` 的 `deadline` 預設是 `None`,這次拿掉了 `None` 判斷,只要呼叫端沒傳 `deadline`、又走到逐題核對迴圈就拋 TypeError,而且既有測試現在就是紅的
引句:「if _time.monotonic() > deadline:」
問題:這一刀(`deadline is not None and` 被刪掉)跟派工鏡頭無關,是順手改的,卻動到表態閘。函式簽章仍是 `deadline=None`。`_disp_record_for` 對 `None` 也原樣回傳 `None`(`deadline = None if deadline is None else ...`)。
具體失敗情境:
- 呼叫端不帶 `deadline`,記錄有效、有適用題,執行到迴圈第一題就拋 `TypeError`。
- 我實跑 `python3.14 scripts/test_lumos.py -k t_contract_evidence_warn_only`,結果是 `✗ ... EXCEPTION: '>' not supported between instances of 'float' and 'NoneType'`,0 passed 1 failed。
- 同檔的 `t_contract_backing_marked_questions` 用同樣的呼叫形狀,應該也紅(我沒單跑)。
- 目前唯一的正式呼叫端有傳 `deadline`,所以線上暫時不會爆。但那一處外層是 `except Exception` 然後 fail-open,將來有人漏傳時,表態閘會悄悄放行。
- 這批改動會讓推送前的閘紅,而且改動範圍沒有提到這一段。
佐證:`scripts/lumos`(post-patch)`:51464`、`:51579`、`:51458`;測試在 `scripts/test_lumos.py:78756`、`:76848`。

severity: minor
blocking: 否 — 這個守衛的測試沒釘大小寫,但程式現在是對的
引句:「if not segs or any(sg.lower() == ".git" for sg in segs):」
問題:`--out` 的 `.git` 擋判斷,測試只覆蓋小寫 `.git/info/attributes`。
具體失敗情境:我在複製的樹上把 `sg.lower() == ".git"` 改成 `sg == ".git"`,清掉 `__pycache__` 後跑 `-k spec_freeze_out_must`,結果 6 passed 0 failed,改壞沒有紅。macOS 與 Windows 預設不分大小寫,`.GIT/info/attributes` 會寫進真的 `.git`,這正是這條守衛要擋的情境。測試只缺 `.GIT`、`a/.Git/x` 這類案例。
佐證:``scripts/test_lumos.py: `t_spec_freeze_out_must_stay_in_repo`(patch 的 tests.patch:381-406)``,程式在 `scripts/lumos`(post-patch)`:795`。

severity: minor
blocking: 否 — 掛鉤只在 lumos 輸出不合約時才崩,且這是 tuple 換成 frozenset 的回歸
引句:「_SPEC_FAIL_CODES = frozenset(LENS_FAIL_REASONS) - _RANGE_ONLY_FAIL_CODES」
問題:原本是 tuple,`in` 靠 `==` 比對。換成 frozenset 後,`in` 要先算雜湊。`_spec_fail_note` 直接拿 `d.get("lens_fail")` 做 `code not in _SPEC_FAIL_CODES`,前面沒有 `isinstance(code, str)`。對照 `_lens_fail_why` 就有這個檢查。
具體失敗情境:lumos(舊版或被換掉)輸出 `{"lens_fail": [], "spec_source": "commit"}`,我實測 `_spec_fail_note` 拋 `TypeError: cannot use 'list' as a set element (unhashable type: 'list')`。`dict` 也一樣。`guard()` 對非 swallow 的掛鉤會把例外往上丟,整支掛鉤崩出去,說明行附不上。
佐證:``scripts/hooks/claude/dispatch-lens-hook.py: `_spec_fail_note`:code not in _SPEC_FAIL_CODES``。

severity: minor
blocking: 否 — 只影響說明行的措辭,不影響安全
引句:「shown_rel = f" {rd['rel']}" if _LENS_SPEC_NODE_NAME_RE.fullmatch(rd["rel"]) else」
問題:`_LENS_SPEC_NODE_NAME_RE` 限 1 到 80 字,是為節點名設計的,現在拿來套整條計劃路徑。路徑本身 `docs/<名>-knowledge/Projects/…md` 就佔了 40 字以上。
具體失敗情境:我用 `git ls-files -z` 掃本 repo 870 篇圖譜筆記,有 15 篇完整路徑超過 80 字,全被判成「不收」。這些合法的長計劃名在提交寫法下,來源行會誤印成「計劃來源:提交 xxx 的(路徑含不收的字元)」,實際上字元全部合法,只是太長。編排者會被誤導去查檔名。
另外全形括弧、`+` 等合法中文檔名字元也不在字元集裡(節點名在本 repo 為 0 筆,影響目前只在計劃路徑)。
佐證:``scripts/lumos: `_lens_spec_notes`、`_LENS_SPEC_NODE_NAME_RE`(post-patch :49283、:49507)``。

已讀,無 finding:
- `_vault_node_path`:`..`、`.`、空段(雙斜線與結尾斜線)、反斜線、NUL、絕對路徑、符號連結解析後出圖譜,都回 None。合法中文名(含全形括弧)放行。NFD 的 `é` 名在 APFS 上放行,屬正常。
- `_spec_freeze_out_path`:`--out` 為空字串、`.`、repo 根(含絕對路徑、結尾 `/.`)、`..`、`.git/x`、`a/.GIT/x`、`a/./b/../.git/x` 全回 None。repo 內的符號連結上層與符號連結的 `--out` 本身分別被擋(後者交給 `out_conflict`)。
- `.git ` 與 `.git.` 這類帶尾字元的名字在 APFS 是不同名字,不擋是對的。HFS+ 的零寬字元別名(git 自己有專門防護)不在這輪範圍。
- NUL 擋:`_lens_git` 補 ValueError、`_spec_ls_tree_one` 與候選略過、掛鉤的 `"\0" in (rng or spec)`。`MARKER_RE` 用 `\S+`,值不會是空字串,所以那一行 `rng or spec` 不會對 `None` 取 `in`。
- `_spec_commit_index` 的 ls-tree 解析(檔名含空白或 tab)、`_write_bytes_atomic`、`_load_hook_file` 都沒有問題。
- 暫存已清:我自己建的 scratchpad 目錄、`gctl-run-*` 現場與背景測試程序都刪了或停了。

最高等級 major,blocking 1 條。
