severity: major

# 代碼審 r1 通才-opus 席報告:殺傷力配方當場試跑

範圍:凍結 patch `governance/review-reports/code-殺傷力配方當場試跑/r1-code.patch` 全部 hunk(計劃、guard-kill／代碼審修正關卡兩篇 Systems、scripts/lumos、test_lumos.py、四份指令文件)。實驗都在自己的 `git clone --shared`(`trc-r1-work-通才-opus/repo`、`/mut`)裡做,沒有碰 repo 根。

## F1 `--id` 對到「物件、但欄位型別壞」的配方時 guard kill 照樣崩潰,回 1(跟 survived 同碼),--json 下 stdout 是空的
severity: major
blocking: 是
引句:「if rid in want and not isinstance(r, dict):」
file: `scripts/lumos:15325`
file: `scripts/lumos:15155`
file: `docs/lumos-toolchain-knowledge/Issues/guard kill遇到格式壞的配方整支崩潰.md:13`

1. 計劃〈範圍〉寫:「不修既有的「格式壞的配方讓 guard kill 當掉」(已有 Issue,這次只保證 `--id` 不會把人帶進那個崩潰)」。這裡講的 Issue 對「格式壞」的定義是:「元素不是物件、`file`/`old`/`new` 是數字」,它給的重現就是 `{"file": 5, "old": "x", …}`。條款 S1 也寫:「對到格式壞的配方時應回 2、印出 kill-rm 指令、不當掉」。
2. 實作的 `_guard_kill_pick` 只擋「不是物件」(〈做法〉① 第 2 步也只寫了「(不是物件)」,所以計劃自己前後不一致)。結果是 Issue 自己的重現配方,`--id` 照樣會把人直接帶進那個崩潰:
   - 一篇筆記放兩條配方:Issue 的重現配方 `{"file": 5, "old": "x", "new": "y", "test": "TestLimitFive", "invariant": "上限恆為5"}`,加一條正常的。
   - 先 `guard kill Systems/Limit --id deadbeef`。對不到時印的列表照樣把壞的那條列成一般列,還附上短身分,結尾叫人「只跑某一條」:
     ```
     f7bada2c923e  合約 "上限恆為5"  檔 (不是字串:int)  原文 "x"  test "TestLimitFive"  平台 (預設)
     只跑某一條:lumos guard kill Systems/Limit --id <短身分>
     ```
   - 照抄跑 `guard kill Systems/Limit --id f7bada2c923e --json`:
     ```
     rc= 1 stdout= '' | stderr 末行: TypeError: join() argument must be str, bytes, or os.PathLike object, not 'int'
     ```
   - 同一組實驗裡,`old: null` 一樣崩(`count() argument 1 must be str, not None`,rc 1)。`invariant` 是數字、`test` 是陣列的不會崩。
   - 重現指令:`/opt/homebrew/bin/python3 trc-r1-work-通才-opus/e2.py trc-r1-work-通才-opus/repo`(用的夾具是 `_mk_kill_env`、`_kr_note`、`_kr_recipe`、`_kr_lum`)。
3. 為什麼算 major:
   - 崩潰時回 1,跟固定席合約「survived→rc1」撞同一個回傳碼。腳本與 hook 會把「工具當掉」讀成「測試咬不住」。
   - `--json` 下回 1 而 stdout 是空的。照合約的字面,崩潰不算「成功跑完」,不在範圍內;但消費端只看到回傳碼 1,會去解析 JSON 然後失敗。
   - `--id` 這條路恰好是新加的導流:失敗時的列表直接把壞配方的短身分端給人抄。計劃明講要守的保證,在 Issue 自己的重現上就破了。
   - doctor P2 對同一條配方判成 malformed、給的修法是 kill-rm,`--id` 這裡卻沒擋。同一個「格式壞」在兩處判得不一樣。
4. 修法方向:`_guard_kill_pick` 的判法對齊 `_kill_recipe_judge` 判 malformed 的條件(至少 `invariant`/`file`/`old`/`new` 不是字串、`platform` 不是字串或 null),也可以直接比 `_kill_recipe_id(rel, r) != _kill_recipe_key(rel, r.get("invariant"), r.get("file"), r.get("old"))` 再補 `new`/`platform` 的型別檢查。〈做法〉① 第 2 步、`docs/.../Systems/guard-kill.md` CLI 那句「對到格式壞的配方回 2」要同步改。S1 ⑥ 現在只造字串元素,要加一格 `{"file": 5,…}`。

## 逐條對照計劃條款 S1–S4

- **S1**:實作跟條款一致(上面 F1 的「格式壞」範圍除外)。
  - 解析放在函式裡、讀完整篇之後、合約片段過濾之前,用的是對整篇的身分清單。對不到、不是十六進位、對到多條,三種都印共用逐行列表到標準錯誤,結尾是「只跑某一條」。
  - 突變實驗:把 `_guard_kill_pick` 搬到片段過濾之後,`t_guard_kill_only_ids` ⑦ 翻紅(8 綠 1 紅),順序有守住。
  - ⑤b 是直接呼叫 `_guard_kill_pick` 測的,標題寫的「片段只留一條也一樣」它本身沒走到片段過濾。不過整體順序已由 ⑦ 守住,不另報。
- **S2**:實作跟條款一致。
  - 寫入失敗(rc≠0 或 warn_box 空)直接回,不試跑。
  - 只更新 covers 時 warn_box 放的是既有那條,身分不含 covers,`--id` 對得到(⑦ 綠)。
  - `--try` 傳完整 64 碼身分,`_kill_norm_prefix` 收 8–64 碼,沒問題。
  - 回傳碼直接用 guard kill 的,不看 weak(設計審已裁)。
  - rc 2 那三種都印「配方已寫進筆記,試跑沒跑成」,寫入失敗的路徑不印。
- **S3**:實作跟條款一致。
  - `listed` 只收真的逐條加進 items 的狀態碼(`cfg`、`noroot` 不收)。
  - 最近一筆比 `ts`;同一個 `ts` 時檔內後面那筆贏;`ts` 不是字串的當最舊。
  - 短身分與合約前段都從 `_recipe` 算;行尾兩句照條款。
  - 單一支檔的 diff 帶 `--literal-pathspecs`,單次逾時夾在剩餘時間內。
  - 突變實驗:拿掉 `--literal-pathspecs`,⑪ 翻紅。
- **S4**:實作跟條款一致。
  - 平台用樹裡那份設定;平台不在設定、或釘不住版本的配方跳過。
  - 突變實驗:拿掉 `plat in unpinned`,⑤ 翻紅。
- 四支條款測試在我的 clone 全綠:9/7/12/5。

## 其他走過、沒發現問題的路徑

- **kill-rm「行為不變」屬實**:
  - `_kill_norm_prefix` 跟原本那行正則一字不差;錯誤訊息仍用 `rid!r`。
  - `_kill_match_prefix` 回的 `hit` 跟原本的 `sorted({…})` 相同,三種擋下訊息原樣保留。
  - `_guard_kill_rm_rows` 逐行內容與順序不變,重複註記仍是「移除會一起移掉」,結尾「移除:」仍由 `_guard_kill_rm_list` 印。
  - `t_guard_kill_rm` 44 綠。
- **不給 `--id`/`result_out` 時 guard kill 不變**:`id_prefixes=None` 不進挑選;`result_out` 只在不是 None 時寫。`t_guard_kill_rc_precedence` 4 綠、`t_guard_kill_json_purity` 6 綠。`--id` 擋下的訊息全走標準錯誤,`--json` 成功時 stdout 只有 JSON。
- **新舊互讀**:
  - 舊 kill-log 沒有 `weak`/`head_sha`/`recipe_id` 的行,會被 `_backing_kill_rows` 濾掉,不會讓 P2 誤列。
  - `_recipe` 只加在記憶體裡的行物件上;合約背書那端(`_contract_backing_apply` → `_backing_judge_groups`)不序列化也不比對整列。`-k backing` 41 綠。
  - 新閘名 `check-p2s` 已登記,`t_gov_stats_gate_drift` 5 綠。
- **例外與 None**:
  - doctor 先設 `_p2 = None`,第一段整段丟例外時,survived 清單照樣算(listed 是空集合、自己建 ctx)。
  - `_kill_file_changed_since` 碰到設定讀不了、`file`/`platform` 型別不對、平台不在設定、找不到 repo 頂、時間用完,都回 True(行尾加「之後改過」),不會崩潰。
- **時間上限**:單次 diff 夾在 `min(10, 剩餘)`;用完的直接判「改過」、不快取,符合計劃。`_kill_plat_top` 不受這 20 秒管,但它會快取,而且通常沿用 P2 第一段建好的 ctx,只有第一段整段丟例外時才會重問。我造不出會超時的情境,不報。
- 既有測試 `t_guard_kill_add_warns_drifted_recipe` 31 綠、`t_doctor_kill_recipe_drift` 30 綠。

## 固定席判讀

- **Systems/guard-kill**(★INVARIANT★ rc 優先序、★INVARIANT★ `--json` 純度):
  - 新參數不給時,兩條合約的程式路徑一行沒動(對應的測試都綠)。
  - `--id` 只縮小要跑的配方集合,rc 的算法不變;擋下的訊息只走標準錯誤。
  - 例外是 F1:`--id` 對到欄位型別壞的配方時,崩潰回 1,跟 survived 撞碼,`--json` 下 stdout 是空的。字面上屬於「rc2 早退」與「成功跑完」以外的崩潰,但計劃明講 `--id` 要避開這個崩潰,所以列 major。
- **Systems/bound-tests-gate**:不影響。這份 diff 沒動 code-loop check、固定席測試的解析與執行,也沒改它讀的 impact 資料。
- **Systems/授權與歸屬**:不影響。沒有新增被複製的檔,`_VENDORED_TOOLKIT` 與 scripts/lumos 檔頭的 SPDX/MIT 沒動。
- **Systems/測試假綠形態**:不影響。新的反向斷言都有同一次執行的前置斷言撐著(S4 ②③ 靠 ①;S3 ②④ 靠 ①;S2 ⑥ 先斷言判重擋下)。我做的三個突變都翻紅,條款測試不是空殼。
- **Systems/lumos-cli-read**:不影響。search 的過濾沒動。
- **Systems/loop-convergence-recording**(RISK):不影響。修正關卡只多了提醒字串(`notes`),不寫事件欄位,也不改回傳碼。
- **Systems/lumos-cli-lifecycle**:不影響。改的是 skills 底下的 reference.md 與指令速查,不是 re-inject 的 CLAUDE.md 哨兵區。
- **Systems/pitfalls-code-loop**(RISK):不影響。pitfalls 的分級與代碼審留痕都沒動。
- **只列名的其他 18 篇**(design-loop、reversibility-governance-ledger、check-t-sentinel、doctor-irreversible-hint 等):這份 diff 只動了 doctor 的 P2 段、`_KNOWN_GATES` 加一個名字、`_lens_git` 加一個可選參數(關鍵字參數、預設 20,其他呼叫端不受影響),沒有碰它們宣稱的行為。

最高等級:major,blocking 共 1 條
