severity: major

我讀完整份 diff 與修補差異,並對真代碼做了行為重現。修補差異裡的 `_e2e_ai_pending_one` 掛鉤複本、查表式 `_e2e_owner_index`、`_confirm_tty_timeout` 上界、`_e2e_gate_fps` 的 `same_e2e` 都沒出錯。極端輸入(2、3、4 號與歸屬鏡頭)沒走出放行的錯誤路徑。重現用 `test_lumos` 的 `_e2eg_proj` 輔助函式,另在一份 `git archive` 副本上做了 13 組改壞實驗。

**1. `waive --commit` 解不到的十六進位提交,沒有測試守**

severity: major
blocking: 是
file: `scripts/lumos:41910-41919`(`_e2e_waive_commit`)
引句:「if commit and not re.fullmatch(r"[0-9a-fA-F]{4,40}", commit):」
- 失敗場景:計劃 S40 與題目主題都寫「`--commit` 只收解得到的提交」。解析後那道 `re.fullmatch(r"[0-9a-f]{40}", full)` 是唯一擋「十六進位但不存在」的關卡,例如 `--commit deadbeef`。
- 重現:在副本把那道改成 `if False:`,`-k t_android_e2e_input_guards` 與 `-k t_android_e2e_waive` 都照綠。守衛測試只送 `"zz"*300`,被前一道十六進位檢查擋掉,根本走不到後一道。改壞後 `commit` 會把空字串寫進紀錄與治理帳。
- 歸因:有證據的修復回歸。`_e2e_waive_commit` 是這一輪新增的,測試與它同一個提交進來,但只守了非十六進位那一半。修前版本沒有這支函式。

**2. `--ack` 與 `--list` 吞掉「沒讀到的份數」,還說沒有待看**

severity: major
blocking: 是
file: `scripts/lumos:41856`(`_e2e_ack_targets`)、`scripts/lumos:41834`(`_e2e_waive_list`)
引句:「pend = dict(_e2e_ai_pending_all(root, budget=60)[0])」
- 失敗場景:S41 規定 doctor、`--ack`、開場提示三處都要講沒讀到的份數。修補只改了 doctor 與掛鉤,`--ack` 取 `[0]` 把 unread 丟掉,`--list` 根本沒算。
- 重現:建 501 份紀錄,修改時間全相同(git clone 後的常態),只有指紋排最後的那份有未看的 AI 放行。
  - `waive --ack --all` 印「沒有還沒人看過的 AI 放行。」,回 0。
  - `waive --ack <那份完整指紋>` 同樣印這句,回 0。
  - `waive --list` 印「沒有任何放行。」。
  - 開場掛鉤與 doctor 同時說「另有 N 份沒讀,看 waive --list、標 --ack --all」。三條指令都到不了那份,而且講的是假話。
- 修前也是同樣吞掉,只是 doctor 與掛鉤那時也沒講。
- 歸因:有證據的原有漏查。修補補了兩處,漏了第三處。

**3. 路徑寫成 `.//x` 通過設定檢查,卻永遠對不到**

severity: minor
blocking: 否
file: `scripts/lumos:40324-40343`(`_e2e_relpath_err` 與 `_e2e_norm`)
引句:「return p.strip().rstrip("/").removeprefix("./")」
- 失敗場景:`_e2e_norm(".//app/src/main/A.kt")` 得到 `/app/src/main/A.kt`,以 `/` 開頭卻通過檢查,因為「以 `/` 開頭」只檢查了去 `./` 之前的 `q`。
- 重現:`shared_paths: [".//app/src/main/A.kt"]`,`macrobench --check-config` 回 0。改 A.kt 後,`./app/src/main/A.kt` 版要求整套,`.//` 版只要求 `login.ok`。
- `exclude`、`features.paths` 寫錯是往保守方向(要整套)。只有 `shared_paths` 是往放行方向。
- 歸因:有證據的原有漏查。修前 `_e2e_relpath_err` 逐字相同。

**4. 舊分支只改記憶體設定,擋下訊息講錯原因**

severity: minor
blocking: 否
file: `scripts/lumos:41624-41627`(`_e2e_gate_fps`)
引句:「這個提交沒有 e2e 段,App 程式卻跟分岔點不一樣:先把主線合進來再驗收」
- 重現:兩端都沒有 `e2e` 段、主線的 `e2e.stability` 為 true,分支只改 `stability_scenarios.player.driver`。結果是擋下,訊息卻說 App 程式不一樣(其實沒動)。同一支分支只改文件則正確回 `not-required`。擋下本身是對的,只有訊息誤導。
- 歸因:有證據的原有漏查。修前這種分支不論改什麼都被擋,修補只修了純文件那半。

**5. 紀錄欄位型別不對,走成「判定內部出錯」**

severity: minor
blocking: 否
file: `scripts/lumos:40695-40712`(`_e2e_record_err`)
引句:「if not isinstance(fr, dict) or any(not isinstance(v, dict) or v.get("result") not in E2E_RESULTS for v in fr.values()):」
- 重現:`runs.ran` 是清單、`runs.ran.flows` 含數字、`feature_runs.*.skipped` 是整數,各自回「判定內部出錯(AttributeError/TypeError…)」。
- 判不清就擋這條成立,但訊息叫人設 `LUMOS_SKIP_ANDROID_E2E=1`,不是修紀錄,也沒帶 `bad_record`。
- 歸因:有證據的原有漏查。

**6. `--commit beef` 取到同名分支**

severity: minor
blocking: 否
file: `scripts/lumos:41917`
引句:「full = (_nodehome_git(root, "rev-parse", "-q", "--verify", f"{want}^{{commit}}") or b"").decode().strip()」
- 重現:建分支 `beef` 指向 main,`--commit beef` 存成 main 的 40 碼,不是以 `beef` 開頭的提交。
- 歸因:有證據的原有漏查。

**三問**
1. 原問題的修復效果:
   - 舊分支只改文件:實測回 `not-required`。
   - 拿掉 `e2e` 段:擋下且不叫人合主線。
   - 深層巢狀紀錄:`record_scan` 測試與 `M17` 改壞實驗都紅,有守住。
   - 數量上限講出來:只在 doctor 與掛鉤成立,`--ack` 與 `--list` 不成立(見 2)。
2. 修補處的相鄰路徑:
   - `_e2e_gate_evaluate` 最後再看一次出口;拿掉那行,`gate_unclear_blocks` 紅。
   - 新的查表歸屬與 `_e2e_scope_hit` 一致。
   - 以下都判成擋下或不要求,沒有放行的錯誤路徑:只刪檔、改名、一支檔同屬兩個功能、`shared_paths` 空、`app_dirs` 相互包住、`./` 與結尾斜線、`""` 與 `.`、tag、detached HEAD、縮寫的 `--at-sha`、不存在的 `--at-sha`、orphan、新 repo、只列效能的功能。
   - 邊角:`LUMOS_TTY_TIMEOUT` 的 `0`、負數、NaN、`inf`、`1e400`、`86401` 都符合預期,`0` 讓人類答覆也變成 AI 放行,屬使用者明設。
   - 紀錄目錄是捷徑、FIFO 都被 `lstat` 與 `S_ISREG` 擋下。
3. 新發現同一案例修前修後:
   - 發現 1:修前沒有這支函式,修後有且少守。
   - 發現 2:修前 doctor 與掛鉤也沉默,修後只有 `--ack`、`--list` 繼續沉默。
   - 發現 3 到 6:修前修後都一樣。

**總結:最高等級 major,擋實作的 2 條(發現 1、2),其餘 4 條 minor。**

實驗暫存已用字面絕對路徑刪除,只有 `/tmp/lumos-seat-work/code-e2e-gate/邊界-sonnet/` 與 `gctl-run-8yeg1ji_`。副本裡 `t_android_e2e_ai_waiver_notice` 的基準線本身就有 3 條紅,所以我不拿它當改壞實驗的依據。
