severity: major

# code-d3 r1 正確性席(sonnet)審查報告

範圍:diff 全 707 行逐 hunk 讀完;在 /Users/enzo/harness/lumos-d3 唯讀查證,實驗都在 scratchpad 臨時目錄與複製出來的 repo 副本(`scratchpad/s/`、`scratchpad/m/`)做,沒動 repo。
跑過:`-k kill_add_warns`(45 過)、`-k test_not_bound`(25 過)、`-k guard_kill_add_try`(7 過)、`-k guard_kill_rm`(44 過)、`-k gov_split` 等。

## F1 提醒裡給的 `guard bind … --platform <名>` 與 `--platform <名>` 沒加引號,平台名來自設定檔,照貼會執行任意指令
severity: major
blocking: 是 — 提醒是叫人「照貼」的指令,平台名來自可能不可信的提交(guard-kill.md 自己寫「筆記與設定可能來自不可信的提交」),貼上即命令注入;同檔既有的修法都有 shlex 引號,這裡漏了。
引句:「pf = f" --platform {b['plat']}" if pdata.get("multiplatform") and b["plat"] != dflt else ""」
另一處同族:
引句:「f"先 lumos guard kill-rm {na} --id {_kill_recipe_id(str(rel), recipe)[:12]},再帶 --platform {_kill_esc(b['want'])} 重新 kill-add")」
問題:`.lumos/config.json` 的平台鍵可以是任意字串(load_platforms 照收),配方的 `platform` 欄指到它,doctor P2 第三則(或 kill-add)就把鍵原樣拼進 `lumos guard bind … --platform <鍵>`。`_kill_esc` 只換控制字元,不處理 `;`、空白、`$()`;bind 那條連 `_kill_esc` 都沒有。對照:同一函式的節點名走 `_kill_node_arg`(shlex.quote)、invariant 走 `shlex.quote`,唯獨平台名裸拼。
另:`show()` 的 `f"{p}:{n}"` 也把平台前綴原樣印出,ESC 序列會直接送到終端(guard-kill.md「人寫的字怎麼印」明講設定檔來的平台名要跳脫)。
具體輸入與路徑:config.json 平台鍵 `x;touch PWNED;#`(第二個平台,root 同 `.`),某篇筆記配方 `platform` 設成該鍵、`test` 不在合約清單 → `_doctor_p2_unbound` → `_kill_p2_unbound` → `_kill_binding_msg` 的 unbound 分支,`pf` 裸拼。
重現(實跑,臨時 repo `scratchpad/s/r3`):
```
python3.14 scripts/lumos --vault docs/kg-knowledge guard kill-add Systems/Limit 上限恆為5 --file prod.py --old "LIMIT = 5" --new "LIMIT = 9" --platform 'x;touch PWNED;#' --test TestOther
  stderr: ⚠ 提醒:…lumos guard bind Systems/Limit '上限恆為5' TestOther --platform x;touch PWNED;#(…)
git add -A; git commit -qm n; lumos doctor --verbose   # P2 同樣印出同一行
eval 貼上該行 → ls PWNED  → 檔案存在
```
ESC 版(平台鍵 `x\u001b[2Jy`):kill-add 的 stderr 用 `cat -v` 看到 `x^[[2Jy:TestOther`,控制字元未跳脫。
建議修法:`--platform` 後一律 `shlex.quote(...)`(含 platform 分支的 `want`,可再套 `_kill_esc`);`show()` 的 p 也過 `_kill_esc`;補一格測試用含 `;`/ESC 的平台鍵(見 F2)。

## F2 兩支新測試有「改壞照綠」的空格:非預設平台的 bind 指令、平台前綴顯示、特殊字元擋
severity: minor
blocking: 否 — 屬測試覆蓋缺口,不是行為錯誤;但 F1 正好落在這個缺口裡。
引句:「pf = f" --platform {b['plat']}" if pdata.get("multiplatform") and b["plat"] != dflt else ""」
引句:「if IDENT_RE.match(meth) and not _path_special_chars(inv):」
引句:「return f"{p}:{n}" if pdata.get("multiplatform") and p != dflt else n」
重現(複製 repo 到 `scratchpad/m/repo`,逐一改壞後跑 `-k test_not_bound`,先清 __pycache__):
- 把 `pf` 改成恆為 `""` → 25 passed, 0 failed(沒有任何一格讓 unbound 走到「非預設平台」,doctor ⑪ 走的是 platform 分支)。
- 把 `and not _path_special_chars(inv)` 拿掉 → 25 passed。
- 把 `show` 改成恆回 `n`(不印非預設平台前綴)→ 25 passed。
對照:改壞「先原文失配後未綁」順序 → ⑨ 紅;不去反引號 → ⑥a 紅(這兩格是有效的)。
具體缺的輸入:多平台設定下 kill-add `--test Other --platform ios`、合約清單只有 `TestLimitFive`(預設平台)——應斷言提醒含 `--platform ios`;再加含控制字元/`;` 的平台鍵與 invariant 各一格。
建議:補上述兩三格。

## F3 既有測試 t_guard_kill_add_warns_drifted_recipe 的 ⑨ 格改動:改得對
severity: minor
blocking: 否 — 確認無誤,僅記一個副作用。
引句:「_lp.write_text(_lp.read_text(encoding="utf-8").replace("[test:TestLimitFive]", "[test:b:TestLimitFive]"), encoding="utf-8")」
判斷:不改的話,⑨a(`--platform b`、test 從合約抓)會被新提醒判成「平台不同」而讓「提醒」不在 stderr 的斷言紅;改成 `[test:b:…]` 後配方的 test 欄變成 `b:TestLimitFive`(帶前綴)、platform=b,比對為 ok,⑨a/⑨b 仍只驗原文提醒。替換發生在 `_kr_commit(root, "mp")` 之前,所以進了提交。副作用:⑨ 的配方 test 欄形狀由裸名變帶前綴,原本沒測到「裸名 + --platform b」這個組合,現在由新測試 ⑦ 的反面(平台不同)間接覆蓋。不算缺陷。

## 逐題走查(未發現問題者,各一句)
- 寫入鎖:`_guard_kill_add_locked` 沒新增 return 路徑;`_kill_find_contract` 的 many/none 兩條提早 return 都在 `with _vault_write_lock` 內經由 `return _guard_kill_add_locked(...)` 離開,鎖照舊由 with 釋放。
- 寫入後丟例外:`_kill_add_after_lock` 內 `_kill_check_ctx` 包 try、`_kill_add_warn` 與 `_kill_add_warn_binding` 各自 try;`ctx=None` 時 `_kill_add_warn` 自己重建(同舊行為),binding 靜默略過。`warn_box[0][0]` 索引跟上新形狀。
- warn_box 形狀:全檔只有 `_kill_add_after_lock` 一個讀者(grep 確認),已改成 `(rec, line)`。
- 配方欄位壞(非 dict、test 非字串、platform 為 list、空 test、非法名):`_kill_test_binding` 都回 skip;doctor 端另有逐條 try。
- 多/單平台:單平台傳 `{}` 不切冒號(`[test:t_a:b]` 不誤報);多平台前綴未定義 → noprefix(kill-add 印一行、doctor 不列)。
- 合約片段對到 0 或多條:kill-add 照舊擋;doctor 對不回或多條就不列。
- 設定檔壞 JSON:`pdata=None` → kill-add 與 doctor 皆靜默略過,P2 本來就講過。
- 實跑修法指令(kill-add `--platform ios` 與合約只綁預設平台):提醒給的 `kill-rm … --id` 與 `--platform py` 重新 kill-add 兩步都照貼成功、doctor 該則消失。unbound 的 `guard bind … TestOther` 在平台名正常時可貼可跑(`cmd_guard_bind` 的 `--platform` 旗標存在)。
- 冪等/併發:合約行用鎖內那份,鎖外不重讀,判斷僅用於一行 stderr;兩會談同時 kill-add 同一條,後者被既有判重擋下,不會多印。
- 新舊互讀:舊版工具讀到 `check-p2t` 事件只是名單外,讀取路徑不崩(寫入端才擋未登記閘名);新版寫入 `check-p2t` 已登進 `_KNOWN_GATES` 與 `_GOV_LOCAL_PAIRS`,doctor ⑧ 格驗證分流。
- 寫一半/衍生資料/時間/不可逆:本次只新增唯讀比對與 stderr 輸出,未寫新檔,無此類風險。

## 圖譜鏡頭(固定席節點)
- guard-kill.md(★INVARIANT★ rc 優先序、--json 純度):diff 沒動 `cmd_guard_kill` 與 `_kill_run`,kill-add 的 stdout 與 rc 不變,提醒只加在 stderr,兩條合約不受影響。
- lumos-cli-read.md(search 預設排除 superseded):未動 search 路徑,不影響。
- lumos-cli-lifecycle.md(re-inject sentinel):未動,不影響。
- 測試假綠形態.md(還原翻紅釘需前置斷言):新測試部分格式有「前置斷言」(先 `len(recs)==1`、先看寫入),但 F2 列的幾格是改壞不紅,正屬該節點描述的假綠形態。
- pitfalls-code-loop.md、loop-convergence-recording.md(RISK):未動相關函式,不影響。
- bound-tests-gate.md(code-loop check 逐支真跑綁定測試):未動閘本身;新增提醒只讀 `[test:]` 清單,不改合約綁定。
- 授權與歸屬.md(主程式檔頭 SPDX/MIT):diff 第一個 hunk 在 1319 行起,檔頭未動,不影響。

總結:max severity = major;blocking 條數 = 1(F1)。
