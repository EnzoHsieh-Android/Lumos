C1 [✅] root 集合確實含①保留指令 dispatch 分支呼叫、②module-level 語句/class body 呼叫兩類（另有③main 內非 dispatch 頂層陳述式），`_SKILLS = _skills_list()` 確實存在且屬 root②模組層賦值。 | 證據: scripts/slim-gen.py:70-76(root①)、77-80(root②，註解「否則 `_SKILLS = _skills_list()` 這種模組層賦值會讓 helper 落進補集」見 slim-gen.py:8-9)、scripts/lumos:8908(`_SKILLS = _skills_list()`)

C2 [✅] 移除謂詞為可達性閉包補集（`drop = set(funcs) - seen`），非 cmd_ 前綴比對；`_lint_watch_mode`、`run_doctor` 兩函式名皆確認存在且不符 cmd_ 前綴。 | 證據: scripts/slim-gen.py:5-6(docstring 明講)、107(`drop = set(funcs) - seen`)、scripts/lumos:446(`def run_doctor(...)`)、11086(`def _lint_watch_mode(...)`)

C3 [❌] 掃描 3 種型態（Assign/Expr/迴圈）取全集減 DEFAULT_KEEP 的機制屬實，但 DEFAULT_KEEP 實際為 26 支指令，不是 24 支。 | 證據: scripts/slim-gen.py:17-19(DEFAULT_KEEP 字面值，`python3 -c` 實數 len()==26)、321-332(allc 掃描含 Assign/Expr `_add_parser_name` 與迴圈 `_is_registration_loop` 兩路徑，`removed = allc - keep`)；scripts/test_lumos.py:16187 斷言字面為「保留 26 支」且 keep 集合同樣 26 個元素，16209 註解「2026-08-11 code review 抓到三處 24 支殘留」印證 24 是已修正掉的舊值

C4 [✅] 產物為行級刪除（`apply_edits` 對原始行文字切片刪除），`ast.unparse` 全檔僅一處呼叫，且僅在「混合保留與移除指令的迴圈註冊」重排小塊內使用，未用於主體重建。 | 證據: scripts/slim-gen.py:283-299(`apply_edits` 逐行 kill/insert，非樹重建)、271-279(`ast.unparse(node2)` 該處為唯一呼叫點，`grep -n ast.unparse` 全檔僅此一行)

C5 [✅] 雙保險皆存在：`ast.parse(new_text)` 失敗即印錯並 `return 1`；`--emit-manifest` 旗標輸出 `keep_funcs`/`drop_funcs`/`removed_cmds`/`kept_comment_lines` 四欄位。 | 證據: scripts/slim-gen.py:365-369(`ast.parse`→`except SyntaxError`→`return 1`)、308(`--emit-manifest` 參數定義)、377-381(四欄位 json.dumps)

C6 [✅] `_is_registration_loop(n, top_var=None)` 簽名含 `top_var`，函式體內比對 receiver 是否等於 `top_var`（`c.func.value.id == top_var`），docstring 明確描述 2026-07-31 審查以 otherkeep/removeme/x2 合成 fixture 重現此缺陷，且測試檔中存在對應同名合成 fixture。 | 證據: scripts/slim-gen.py:121(函式簽名)、151-153(receiver 比對)、130-136(docstring 敘述缺陷成因與 otherkeep 例子)、scripts/test_lumos.py:16097-16165(`t_slim_gen_nested_loop_registration` 合成 otherkeep/removeme/x2 fixture 重現)

C7 [✅] `collect_edits()` 與 `main()` 內兩處 `allc`/迴圈判斷呼叫 `_is_registration_loop` 均帶 `top_var` 引數（共 3 處呼叫點皆帶）；「兩邊是同一段未防護邏輯」的定調亦見於 test 檔 docstring 佐證。 | 證據: scripts/slim-gen.py:236、264(collect_edits 內兩處)、327(main() 的 allc 掃描)皆為 `_is_registration_loop(n, top_var=top_var)`；scripts/test_lumos.py:16104-16106(docstring：「`collect_edits()`(以及 `main()` 印診斷用的 allc 掃描——兩邊是同一段未防護邏輯...)」)

C8 [✅] `collect_edits()` 對 main.body 的 for 迴圈處理：receiver≠top_var 的 nested for 不會匹配 `_is_registration_loop(top_var=...)`（回傳 False），因此落入一般陳述式分支，若當下正在累積 block（block_name 非 None）則 `block_stmts.append(n)` 併入所屬區塊，隨區塊整體去留，未被單獨剝離處理。 | 證據: scripts/slim-gen.py:232-252(main.body 迴圈；232-238 僅頂層迴圈 continue 跳過、245-251 其餘陳述式含 nested for 併入 `block_stmts`)

C9 [✅] 現行組包清單（`main()` 尾段）含 `get.sh`/`uninstall.sh`，且 chmod 0o755 迴圈涵蓋 `install.sh`/`get.sh`/`uninstall.sh` 三支 `.sh`（曾遺漏、只對 install.sh 補執行位元的「修復前」狀態屬歷史敘述，未逐一考古 git blame，但「修復後」現狀與碼一致）。 | 證據: scripts/slim-gen.py:390-394(item 清單含 "get.sh"、"uninstall.sh")、404-407(`for exe in ("install.sh", "get.sh", "uninstall.sh"): ... p.chmod(0o755)`)

C10 [✅] 組包清單 `for item in (...)` 含 `"claude-block.md"`；`t_slim_gen_dist_ships_entrypoints` 的 expected 清單同步含此項。 | 證據: scripts/slim-gen.py:393(`"README.md", "claude-block.md", "skills"`)、scripts/test_lumos.py:18285(`"README.md", "claude-block.md"`)

C11 [✅] 組包清單含 `install.py`/`uninstall.py`/`install.ps1`/`uninstall.ps1`/`get.ps1`（5 個新檔皆在同一 tuple 內）；chmod 0o755 迴圈僅列 3 支 `.sh`，`.py`/`.ps1` 不在其中。 | 證據: scripts/slim-gen.py:390-393(tuple 含 install.py/install.ps1/get.ps1/uninstall.py/uninstall.ps1)、404(`for exe in ("install.sh", "get.sh", "uninstall.sh")`，僅 3 個 .sh)、400-403(註解明講 .py/.ps1 不需要 chmod 的理由)

C12 [✅] `t_slim_gen_dist_ships_entrypoints` 的 expected 清單元素數確實為 12（get.sh/get.ps1/uninstall.sh/uninstall.py/uninstall.ps1/install.sh/install.py/install.ps1/README.md/claude-block.md/scripts-lumos/skills-SKILL.md），docstring 有「★2026-08 Task 13 擴充★」等對應更新敘述。 | 證據: scripts/test_lumos.py:18282-18286(expected 12 項)、18264-18271(docstring Task 13 擴充敘述)

C13 [❌] 實跑 `python3 scripts/test_lumos.py -k slim_gen`：45 個 checks 全綠（非 25 個）；且 `--help` 顯示保留 26 支指令（非 24 支）。涵蓋的各分項（真檔生成驗證/合成 fixture/巢狀迴圈 fixture/註解密度守衛/交付包完整性守衛）皆存在且確實跑到，但總數與支數兩個數字皆與主張不符。 | 證據: 實跑輸出「45 passed, 0 failed」、首行「✓ 產物 --help == 保留 26 支」；scripts/test_lumos.py:16187(斷言字串「保留 26 支」)

C14 [❌] 密度守衛機制（產物密度不得低於原檔 90%，取代舊 50%/60% 門檻）屬實且可在 test 檔中對應找到；但主張列出的具體數字「原檔 11999 行/686 行註解=5.7%、產物 6203 行/379 行註解=6.1%」與現況不符——實測現行 scripts/lumos 為 15047 行/1078 行註解(=7.2%)，生成產物為 7461 行/597 行註解(=8.0%)，密度未下降之結論方向雖仍成立，但引用的具體行數/註解數已是過時數字（原檔行數已從約 12000 行成長到 15047 行）。 | 證據: scripts/test_lumos.py:16220-16254(`t_slim_gen_keeps_comments`，90% 門檻於 16250：`od >= sd * 0.9`，取代舊門檻的說明見 16224-16227)；實跑輸出「★產物註解密度未下降★(原 1078/15047=7.2% → 產物 597/7461=8.0%)」

C15 [✅] `t_slim_gen_dist_ships_entrypoints` 斷言 dist/ 內存在 get.sh/uninstall.sh/install.sh/README.md/scripts/lumos/skills/lumos-project-notes/SKILL.md（皆為 expected 12 項之子集），且對 get.sh/uninstall.sh/install.sh 三支 `.sh` 檢查可執行位元（`mode & 0o111 != 0`）。 | 證據: scripts/test_lumos.py:18282-18289(存在性檢查涵蓋上述 6 個路徑)、18291-18295(三支 .sh 可執行位元檢查)；實跑輸出對應 checks 全綠

✅11 ❌3 ❓0 ⏭0
