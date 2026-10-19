severity: major

範圍:修補差異的測試那半 `r2-repair-tests.patch`,在 `web-gaps` 修後版本 5f8f8e48 上,用我自己的複製工作樹做破壞實驗。複製工作樹已用字面絕對路徑刪除。

白話:這次新補的測試有三處是「看起來有守,拿掉守衛卻照綠」。作者說只有結構斷言會紅的兩個故障變體,我實測到整套都不會紅。

## Findings

1. guard kill 的撞名檢查沒有行為測試,可以整段停用
- 位置:`t_guard_kill_shares_collision_check`(測試檔 `scripts/test_lumos.py`)。
- 問題:①②直接呼叫 `_name_collision_reason`,證明的是共用函式,不是 `cmd_guard_kill` 有擋。真正的接線只靠 ③ 的 `"_name_collision_reason(" in inspect.getsource(m.cmd_guard_kill)` 子字串比對。
- 破壞實驗:把 `scripts/lumos` 的 `if _coll:` 改成 `if False and _coll:`,撞名的配方就照跑。`-k t_guard_kill_shares` 回 3 passed 0 failed;`-k guard_kill` 全部 292 passed 0 failed。
- 為什麼擋不住:賦值那行還在,子字串比對照過。撞名配方不被擋,殺傷力就可能是被別支測試打紅的,結果不可信。
- 該怎麼補:用 `_fs_bt_repo` 風格的夾具跑 `cmd_guard_kill`,斷言撞名配方的 verdict 是 error 且 detail 含「撞名」。
- 歸因:未判定。修前版本沒有這支測試,不能算修復造成的回歸。
severity: major
- blocking: 是
- 規則出處:`03-寫回圖譜.md` 第 5 條「修 bug 與關鍵守衛要證明抓得到錯」,以及第 6 條「它們不能取代行為驗證」。
- 引句:「check("③guard kill 呼叫這一支(結構檢查,補 ①②)", "_name_collision_reason(" in src, "")」

2. settle 共用名稱檢查同樣只有結構斷言
- 位置:`t_bind_name_problem_shared` 的 ③。
- 破壞實驗:把 `cmd_guard_settle` 裡的 `method, why = _bind_name_problem(...)` 改成 `why = None  # _bind_name_problem(`。註解裡剛好留著字串,③ 照過。`-k bind_name_problem_shared` 3 passed;`-k settle` 105 passed 0 failed。
- 後果:`guard settle --test "x\x1b[2K"` 這類非法名會直接寫進 `[test:]`。
- 該怎麼補:跑 `lumos guard settle <待完成守衛> --test "有 [括號]"`,斷言 rc 2 且沒寫檔。
- 歸因:未判定,理由同上。
severity: major
- blocking: 是
- 引句:「check("③settle 與 bind 都呼叫它(結構檢查,補 ①②)", "_bind_name_problem(" in inspect.getsource(m.cmd_guard_settle)」

3. `_bind_name_problem` 的「放行」分支沒有測試,擋住就沒人知道
- 位置:`t_bind_name_problem_shared` ①②。只測了「擋」(`API: 逾時`),沒測 `web:下單 停用` 或 `web: 下單`(正確寫法)能過。
- 破壞實驗:把 `explicit = re.match(...) is not None` 改成 `explicit = False`。`-k bind` 共 124 passed 0 failed。
- 後果:錯誤訊息教使用者寫成 `<平台>:<名稱>`,這個改壞後就會被自己擋掉。`settle` 沒有 `--platform` 可用,等於多平台專案裡帶冒號的名稱永遠綁不了。
- 該怎麼補:加一條斷言 `_bind_name_problem(root, "web:下單 停用", None)` 回 `why is None`。
- 歸因:未判定。
severity: major
- blocking: 是
- 引句:「_nm2, why2 = m._bind_name_problem(root, "API: 逾時", None)」

4. `_bind_name_problem` 對全形冒號的判斷跟讀取端不一致,測試沒釘
- 位置:`scripts/lumos` 的 `_bind_name_problem` 用 `re.search(r"[:：]", m)` 判斷。
- 實測:多平台設定下,`_bind_name_problem(root, "API：逾時 顯示重試", None)` 被擋,訊息說「冒號前面會被當成平台前綴」。但 `_split_test_ref` 對全形冒號回 `(預設平台, 整串)`,也就是會整串當名稱。`S53` 測試明寫這條行為。
- 後果:寫入端比讀取端更嚴,訊息講的原因不成立。測試沒有任何一條釘住全形冒號。
- 影響只是過度保守,所以 minor。
- 歸因:未判定。
severity: minor
- blocking: 否
- 引句:「if platform is None and re.search(r"[:：]", m):」

5. 記憶體測試在 Windows 上必紅,且註解與斷言的門檻不一致
- 位置:`t_comment_strip_big_string_memory`。
- 問題一:子程序 `import resource` 在 Windows 沒有這個模組。`stdout` 為空會走 `ValueError`,得到 `grow=None`,斷言紅。
- 慣例對照:同檔 `t_install_includes_skills` 等用 `if sys.platform == "win32": raise _SrcOnly(...)`。
- 問題二:docstring 寫「< 200MB」,斷言寫 `< 300MB`。
- 我已驗證這支在 macOS 穩定:舊正規式實測 1001MB,測試翻紅;新正規式通過。
- 歸因:未判定。
severity: minor
- blocking: 否
- 引句:「check("①額外記憶體 < 300MB、< 2 秒", grow is not None and grow < 300 * 1024 * 1024 and secs < 2.0,」

6. Windows 擋字測試的 ② 在 Windows 上是空斷言
- 位置:`t_test_name_ok_windows_shell_chars` 的 ②。
- 問題:`m._test_name_ok("x & calc & y") or old` 在 Windows(`old` 為 True)恆真,沒有驗到任何事。
- 補法:改成只在 `not old` 時檢查,或加 `_SrcOnly` 說明。
- 歸因:未判定。
severity: minor
- blocking: 否
- 引句:「check("②POSIX:照收", m._test_name_ok("x & calc & y") or old, "")」

## 已驗,沒問題的部分

- **⑪b 夾具改動沒有拿掉守衛。** 我把 `doctor` 那行的 `_kill_esc(seg)` 拿掉,`t_doctor_kill_recipe_drift` 的 ⑪b 翻紅(輸出是原始 `\x1b[2K`)。
  - 原本放在前綴裡的控制字元,現在已被 `_TEST_PLAT_LIKE_RE` 限制成英數、底線、連字號,前綴上的跳脫變成不可達的防禦。
  - 名稱與設定檔的平台名清單仍被覆蓋。
- **記憶體測試的翻紅釘是真的。**
  - 把 `_C_STRIP_RE` 改回舊的群組加星號寫法,測試翻紅。
  - 子程序量最大常駐記憶體,在 macOS(位元組)與 Linux(KB)的單位換算正確。
  - 用 `r0` 當基準,不依賴牆鐘;2 秒上限偏寬鬆。
- **撞名三個呼叫端的覆蓋。**
  - 推送前閘和規格閘都走 `_run_bound_tests`,有 S49、S50、S36 等行為測試。
  - guard kill 是第三個呼叫端,只有結構斷言(見第 1 條)。

## 三問

- **原問題修復效果:** 只確認了記憶體上限與 ⑪b 夾具有行為證據。guard kill 撞名與 settle 共用檢查沒有行為證據,見第 1、2 條。
- **修補處相鄰路徑:** `_bind_name_problem` 擋的路徑有測,放行的路徑沒有(第 3 條)。
- **新發現同案例修前修後:** 第 1 到 3 條在修前沒有對應測試,歸因都是未判定,只能說修後的測試擋不住這些改壞。

## 未驗範圍

- 沒跑修前版本的對照。
- 沒驗 Linux 或 Windows 的實際數字。
- `t_archive_...`、`t_playwright_file_anchor_hint`、`t_test_in_tree_escaped_title` 只讀不跑破壞實驗。

最嚴重 severity: major,blocking 共 3 條(第 1 到 3 條)。
