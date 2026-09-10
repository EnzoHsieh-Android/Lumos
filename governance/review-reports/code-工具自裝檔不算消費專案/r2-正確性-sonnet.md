severity: major

## 逐項發現

### F13 「同一行多連結」防呆可被多打一個空白繞過,兩個連結被吞成一個字串、從連結圖裡消失
severity: major
blocking: 是 — 無錯誤訊息、無崩潰,但把兩個合法連結悄悄寫壞成讀不到的死字串,violates「about_code/related 等清單欄位不得靜默寫壞」的既有合約(F4/F7 同系列問題)。
引句:「or "]], [[" in val or "]],[[" in val:」
1. 防呆只認 `]], [[`（逗號後恰一個空白）與 `]],[[`（無空白）兩種精確字串,`related: [[A]] , [[B]]`(逗號前多一個空白)兩種都不含,直接放行。
2. 放行後 `_list_key_scalar_to_list` 把整條 `"[[A]] , [[B]]"` 當成單一值,`fmt_list_item` 因開頭是 `[[` 整串加引號存成一項:`- "[[A]] , [[B]]"`。
3. 實測重現(在 `/tmp` 暫存 vault,repo 用 `scripts/lumos --vault`):寫入 `related: [[Systems/A]] , [[Systems/B]]` 後 `append related "[[Systems/C]]"`,rc=0、輸出「✓ ... 多了一項」,但檔案裡 A、B 兩個連結被黏成一項——且因 `load_vault` 的 fm_targets 要求整值 `re.fullmatch(r"\[\[([^\[\]]+?)\]\]", s)`(佐證:`file: \`scripts/lumos:329\`` 只認恰為一個 wikilink 的值),這一項從此不被索引成任何連結,兩個連結從圖裡消失且沒有任何提示。
4. 這條路徑在改動前不存在:改動前對 scalar 型 LIST_KEYS 呼叫 append 一律 `raise ValueError`(kind != "list"),不可能寫出這種壞值;是這輪修法新開的洞。

### F14 加了引號的同行清單字面(`tags: "[a, b]"`)一樣繞過防呆,被吞成一項亂碼字串
severity: major
blocking: 是 — 同 F13,靜默寫壞欄位且無任何錯誤訊息。
引句:「val.startswith(("[", "{")) and not val.startswith("[[")」
1. 防呆只檢查 `val`(未去引號前的原始文字)開頭是不是 `[`/`{`;若整段被引號包住(`"[a, b]"`),`val` 開頭是 `"`,判斷式為 False,不觸發擋下。
2. 實測重現:寫 `tags: "[a, b]"`,`append tags c`,rc=0、輸出「✓ append ...: tags 多了一項 c」;實際檔案變成 `tags:\n  - "[a, b]"\n  - c`——使用者原本想要的兩個標籤 `a`/`b` 被黏成一個不存在的標籤字面 `[a, b]`,且完全沒有錯誤或警告。
3. 同 F13,這是本輪新增的轉換路徑才可能發生;改動前一律直接 raise、rc2、檔案不動。

### F15 append 重複值時,若欄位原是單一值寫法,會被悄悄轉成多行清單格式並印出「多了一項」的假訊息
severity: minor
blocking: 否 — 最終清單內容仍正確(值沒有遺失或重複),只是格式被改寫、訊息用字不準,不影響資料正確性。
引句:「print(f"✓ append {rel}: {key} 多了一項 {value}")」
1. `edit_fm_append` 內建 dedup:值已存在時 `return fm` 視為 no-op,但 `struct[key][2] == "scalar"` 的轉換(引句錨定行:`fm = _list_key_scalar_to_list(fm, key, struct[key][0])`)發生在 dedup 判斷之前,所以「no-op」返回的其實是已被轉換成多行清單格式的 `fm`,不是原始位元組。
2. `cmd_append` 不比較新舊內容是否相同,對這個「no-op」結果一樣呼叫 `atomic_write_verify` 寫檔,並印出「多了一項 {value}」。
3. 實測重現:`about_code: src/a.ts`(單一值寫法)呼叫 `append about_code src/a.ts`(值完全相同),rc=0、印「✓ append Systems/S.md: about_code 多了一項 src/a.ts」,但檔案已被從 `about_code: src/a.ts` 改寫成 `about_code:\n  - src/a.ts`——並沒有任何一項被「加」進去,訊息與實際動作不符。

## 第一輪修法驗收

F1:修到 — 改成 `_VENDORED_TREE_FILES`/`_VENDORED_TOOLKIT` 精確檔名清單比對,測試「⑤專案自己放在 scripts/hooks、scripts/templates 的程式照樣要掃」實跑通過(`python3 scripts/test_lumos.py -k vendored` 57 passed)。
F2:修到 — lint 過濾(`if _skip_vendored: lint_claims = [...]`)放在 aligned/未 aligned 分流之前、對兩條路都生效,測試⑦兩種 aligned 值都通過。
F3:修到 — 三個 `_stack_changed_ok` 呼叫點(含只刪行那條路)都傳了 `_skip_vendored`,測試⑥「只有刪行時不觸發棧別題」通過。
F4:修到 — `about_code` 不在 `SCALAR_KEYS`(scripts/lumos:10532),`cmd_set` 直接擋下;append/remove 對多筆清單保序不丟項,測試①通過。
F5:修到 — `_about_code_path` 用 `.resolve()` 解析後才跟 repo 根比對,絕對路徑/`../`/目錄/**指向 repo 外的 symlink** 均擋下(symlink 案例已另外重現驗證,rc2)。
F6:修到 — `_set_about_code` 整支函式已移除(grep 全庫零命中),只剩 append/remove 一套規則,set 對 about_code 一律 rc2。
F7:修到 — 含「: 」的路徑經 `fmt_list_item` 補上引號,測試④「讀回來一字不差」通過。
F8:⚠ 未能查證 — 這份 diff 完全不含任何 `docs/` 檔案異動;現存相關筆記(`Projects/消費專案接入靜默失效_計劃.md`)文字目前已正確寫「about_code 只做排序不建連結」,但無法確認是否就是 r1 當時所指、或已在別處修正,判不準交編排者。
F9:修到 — 安裝端 `_vendor_toolchain` 與移除端 `_deinit_remove_vendored` 都改用共用常數 `_VENDORED_TREE_DIRS`,不再各寫一份。
F10:修到 — 問題根源的 `_set_about_code` 函式已整支拿掉,命名/訊息順序不一致議題隨之消失。
F11:修到 — `_os.path.relpath(dirpath, _base)` 移到檔名迴圈外、每個目錄只算一次。
F12:修到(已釘住)— `_is_toolchain_repo` 判別鍵在工具鏈本體仍強制不跳過,測試④專門鎖住這個方向。

## 風險掃描清單
scripts/lumos:17603 的 `open(` 命中:誤報 — 命中的是中文註解裡描述「命中 open(...)」這段文字本身,不是任何實際的檔案開啟呼叫。

總結:最高 severity major,blocking 共 2 條
