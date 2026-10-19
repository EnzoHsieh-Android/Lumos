severity: major

審查範圍是修後 b76b570e 的 r2-repair-tests.patch,主程式的對照靠 r2-repair-lumos.patch。修前版本用 55da596f 取得。所有拆掉守衛的實驗都在 `/tmp` 的複本上做,沒動 repo。

白話先講:這批新測試大多抓得到它們要抓的錯。但有兩處是「修補改了行為,測試沒跟上」,其中一處還讓平常寫的指令被誤報成缺檔。

1.
severity: major
blocking: 是
- 位置:`_ref_cmdline_token` 改成只有「第一個詞之後有 `-` 開頭的詞」才截成第一個詞(r1 邊1 的修補)。
- 問題:筆記裡很常見的「路徑加子命令、沒有旗標」現在整串被當成路徑,誤報 missing。計劃 [S18] 寫的是「路徑加參數」,修補把它窄化成只認旗標,新測試只覆蓋旗標那一種。
- 具體例:筆記寫 `scripts/lumos doctor`,repo 裡 `scripts/lumos` 存在。
  - 輸入:一份 plan.md,內含 `scripts/lumos spec-gate 甲_計劃`、`scripts/lumos search "作廢 收回"`、`scripts/lumos doctor`。
  - 指令:`lumos refcheck plan.md --repo .`
  - 修前(55da596f):`✓ ok scripts/lumos`,統計 missing 0。
  - 修後:三條都是 `✗ missing`,統計 missing 3。
  - 同一支函式也餵 doctor P 段(`scripts/lumos:3522`),預期同樣誤報。
- 測試缺口:`t_ref_path_spaced_dir_not_cut` 只放 `scripts/e2e.sh --cleanup` 和 `src/a.py extra words`。後者既沒斷言,而且本來就不存在,所以抓不到這個回歸。
- 歸因:有證據的修復回歸。
引句:「if len(words) > 1 and any(w.startswith("-") for w in words[1:]) and not exists(s):」

2.
severity: major
blocking: 是
- 位置:`t_prepush_spec_gate_done_in_range` ④ 的前置多了 `flip.ok`,新測試 `t_prepush_spec_gate_done_stale_still_checks_nogo` ②也一樣。
- 問題:修補後「推送前就已完成的計劃、留痕過期」改成還是跑測試、紅了照擋(`_spec_gate_push_one` docstring 寫「其餘找得到的測試照跑、紅了照擋」)。原本 ④ 是在測試紅(`flip.ok` 已刪)的狀態下期待放行。修補把 ④ 的現場改成綠,沒有補一條「過期且測試紅 → 擋」的測試。
- 拆掉守衛實驗:
  - E:過期時直接回提醒、完全不跑測試 → 10 支 `prepush_spec_gate_done*` 全綠。
  - F:`if reds and not (done and stale):` 紅了也放行 → 10 支全綠。
  - 對照:拆掉不做清單那道(A)、永遠當 done(B)、gone 後提早 return(D)、gone 不濾掉(C),都有測試翻紅。
- 具體改壞:過期、done、條款測試紅時推送放行,所有測試照綠。
- 小缺口:`t_prepush_spec_gate_done_gone_still_runs_rest` 的 docstring 寫「兩支都找得到且綠 → 過」,檔裡沒有這條斷言。
- 歸因:有證據的修復回歸。這是修補新宣稱的行為,測試沒鎖。
引句:「(d / "tests" / "flip.ok").write_text("")      # 留痕的測試綠(代碼審 r1 起寬待時找得到的測試照跑)」

3.
severity: minor
blocking: 否
- 位置:`_spec_gate_pick` 同秒改取後列(`k >= bk`)。
- 問題:這個改動是為了讓「兩筆 ts 都讀不懂 → 取後列」那條斷言成立(兩筆都是 -inf,`>` 取不到後列)。副作用是 ts 讀得懂、同一秒、token 不同時,治理帳的列會贏過本機審查帳的列。docstring 還寫「呼叫端把本機審查帳那筆放最前」。
- 測試缺口:新測試只覆蓋 -inf 平手,沒有「有效 ts 同秒」的斷言。把有效 ts 的平手改回取先列,測試照綠。
- 歸因:有證據的修復回歸(修前 `>` 是取先列),判定是否該變沒有獨立依據。
引句:「if best is None or k >= bk:      # 同時間(秒級 ts 常撞)取後列的」

4.
severity: minor
blocking: 否
- 位置:`_NS_NEG_CLAUSE_PUNCT` 從「任何 Unicode 標點」收窄成明列的集合(r1 邊4、安2 的修補)。
- 問題:集合收了 ASCII 的 `,;:!?`,卻沒收 `.`、引號、`[`。同時 `_NS_NEG_COND_OPEN` 拿掉「只要」,真正的條件句也變成提醒。
- 實測 `_ns_negation_hits`(修前 → 修後是否提醒):
  - `資料還沒回來時.`:否 → 是
  - `資料還沒回來時"載入中"`:否 → 是
  - `還沒登入時[顯示]`:否 → 是
  - `還沒登入時“顯示”`:否 → 是
  - `只要尚未登入就導到登入頁`:否 → 是
  - `尚未登入時/顯示登入`:否 → 是,這個是刻意要的。
- 測試缺口:`_NEG_V4_QUIET` 沒有這些寫法。
- 影響:只是提醒、不擋,所以 minor。
- 歸因:有證據的修復回歸(前半是刻意取捨,但 `.` 單獨漏掉看起來是疏忽)。
引句:「_NS_NEG_CLAUSE_PUNCT = set(",,、。;;:!?!?…—")」(原文為全形與半形混用的同一行)

5.
severity: minor
blocking: 否
- 位置:`_nodehome_worktree_homes` 新增的 `not fp.is_symlink()` 守衛。
- 問題:把這個守衛拿掉,`worktree_home` 和 `nodehome` 兩組共 727 支測試全綠,沒有任何測試用捷徑檔當節點。
- 歸因:有證據的原有漏查(守衛是修補新加的,測試沒補)。
引句:「捷徑檔不跟(同 _nodehome_reader 讀磁碟的守衛)」

6.
severity: minor
blocking: 否
- 位置:doctor S14 改成 `_spec_gate_latest_merged(env) or _spec_gate_latest_records(env)`(r1 架8)。
- 問題:改回只讀本機帳,`-k s14` 3 支和 `-k doctor_spec_gate` 2 支都綠,沒有「只有治理帳有留痕」的測試。
- 歸因:有證據的原有漏查。
引句:「兩本帳合讀(跟推送閘同一支;讀不到治理帳就退回只看本機帳)」

7.
severity: minor
blocking: 否
- 位置:`t_set_help_lists_keys` ②改成對照 `SCALAR_KEYS | COND_KEYS`。
- 問題:改成對照程式常數是對的,但用子字串比對 `k in flat`,`status`、`type`、`updated` 在說明首句「改一篇的單一值欄位(status / updated / type…)」就出現了。把這三個從欄位清單拿掉,斷言照過。
- 我沒有實際拆掉清單驗證,是從 `set --help` 輸出推出來的。
引句:「check("②常數裡每個欄位都同時出現在說明與擋下訊息", r.returncode == 2 and all(k in flat and k in r.stderr for k in keys),」

8.
severity: minor
blocking: 否
- 位置:`t_docs_catalog_count_wording` ③。
- 問題:原斷言要求 `_docs_command_count_claims(ref)` 真的掃得到 reference.md 的總目錄句。新斷言只確認那個子字串存在,docstring 卻還寫「所以會被掃到」。①只驗了手寫字串,真檔排版若讓守衛掃不到,不會紅。
引句:「check("③reference.md 真的用總目錄那種寫法(所以會被守衛掃到)", "個指令的總目錄" in ref, "")」

9.
severity: minor
blocking: 否
- 位置:規格閘「實作後補跑紅」的前置警告。
- 問題:偵測用 `status --porcelain --untracked-files=no`,untracked 的新實作檔不會觸發「先提交」警告。第 3 步(新檔實作換成空殼)正是會把這種檔覆寫掉的情形。fixture `t_spec_gate_manual_red_checks_uncommitted` 只放已追蹤檔的改動,沒碰這條。
- 歸因:有證據的原有漏查。
引句:「st = _lens_git(_vault_repo_root(env), "status", "--porcelain", "--untracked-files=no")」

**三問的回答**
- 原問題的修復效果:
  - 以下都有拆掉守衛會翻紅的證據:不做清單那道(A)、永遠當 done(B)、gone 不濾掉(C)、gone 後提早 return(D)、summary 總開關(H)、`--nth` 擋(I)、結尾斜線(J)、冒號數(N,50.29s)、planned 集合(O,逾時 180s)、cochange 預設(L、L2)、S8 綠勾(M)。
  - 缺證據的有:過期且測試紅(E、F)、symlink(G)、S14 合併讀(P)。
  - 時間類測試(1 秒、4 秒)的餘裕分別是 2800 倍與 158 倍,沒有牆鐘風險。
- 修補處的相鄰路徑:#1 是相鄰路徑回歸(路徑加子命令),#3、#4 是判定邊界變動。`_fm_touch_updated`、`_has_line_break`、`_probe_cond_keys` 這幾處等價重構,我讀過沒發現差異,未另外做行為實驗。
- 新發現的修前修後結果:
  - #1 的修前/修後結果在上面。
  - #4 的 `_ns_negation_hits` 兩版對照在上面。
  - #2、#3、#5、#6 是測試缺口,以修後版本的拆守衛實驗為證,無修前對照。

跑過 `-k` 子集的測試全綠。沒跑全套,也沒驗 CI。

最嚴重:major,blocking 共 2 條。
