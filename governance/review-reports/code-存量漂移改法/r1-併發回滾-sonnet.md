severity: major

審材:r1-snapshot-a.patch(scripts/lumos)逐 hunk 讀完;實驗在 `git clone --shared` 出來的 /private/tmp/r1cr/w(HEAD=53b6389c),用 test_lumos 的 `_df_repo/_df_fix` 造場景,直譯器 /opt/homebrew/bin/python3。

## F1 --kind c2 --keep 帶 --dry-run 照樣寫了表態檔
severity: major
blocking: 是
引句:「        return cmd_drift_ack(env, rel, line, "c2", o["reason"])      # 照留:等同帶清單的 c2 表態」
佐證行:file: `scripts/lumos:cmd_drift_fix(patch 內 1401 行附近)`;`_drift_fix_args_err` 的 `_DRIFT_FIX_OPTS` 不含 dry_run,所以 --dry-run 對 c2 --keep 是合法組合
1. 走到哪:`cmd_drift_fix` 在 `_drift_fix_args_err`、`_drift_fix_target` 之後、`_drift_fix_load` 之前,遇到 `kind == "c2" and o.get("keep")` 就直接 `return cmd_drift_ack(...)`,`o["dry_run"]` 從沒被看。
2. 重現(臨時 clone,Issues/K 連到已收尾計劃、c2 在第 3 行):
   `lumos --vault <v> drift fix Issues/K 3 --kind c2 --keep --reason "還沒解決,等上游" --dry-run`
   輸出 rc=0「✓ 表態記下了(DACK-adf2e130)…」,`governance/drift-acks.jsonl` 多了一行 `{"id":"DACK-adf2e130",…,"kind":"c2","related":["Projects/Done_計劃.md"],"seq":1}`,治理帳也記了 acked 事件。
3. 壞在哪:計劃節內文與 help 都宣稱 `--dry-run` 只印改前改後、不寫筆記、不寫帳;這條路徑寫了帳、還把一筆 c2 發現靜音(提交進去後 check 就不再列)。預覽指令是人最會先跑的那個,在這裡等於直接動手。

## F2 驗證失敗給的救法 `git checkout --` 會把同一篇先前已成功、有帳的工具改動一起丟掉,帳卻留著
severity: minor
blocking: 否
引句:「在 repo 根目錄跑 git checkout -- {cx['repo_rel']} 」
佐證行:file: `scripts/lumos:_drift_fix_clean_err(patch 內 1136 行附近)`(同一篇可累積多筆工具改動、靠帳指紋放行)
1. 時序:同一篇驗證紀錄先 `drift fix … --kind c3 --status pass`(成功、帳 DFIX seq1、未提交),再對同一篇 `--kind c4 --old … --new …` 遇驗證失敗(實驗用 `LUMOS_DRIFT_FIX_FAULT=verify`;現實裡是別人的 `lumos set` 在寫入與讀回之間改了同一篇)。
2. 照訊息 `git checkout -- <路徑>` 後:那篇回到 HEAD,c3 那筆改動也沒了(`status: pending`),但 `governance/drift-fixes.jsonl` 仍有 c3 那筆 DFIX-d9d368a2(seq1,after_sha256 對不上任何現況)。重跑 c3 會再多一筆重複的帳。
3. 影響:修復帳(稽核用)與磁碟不一致;訊息沒講「會連先前的工具改動一起還原」。另外若失敗是同時的合法編輯造成的假警報,救法也會丟掉那個人的編輯。

## F3 帳行含 U+2028/U+0085 時,寫入自驗過關、讀取端卻把整行丟掉,同一篇不能接著修
severity: minor
blocking: 否
引句:「    for ln in raw.decode("utf-8", errors="replace").splitlines():」
佐證行:file: `scripts/lumos:_jsonl_append_verified 8499`(用逐行迭代自驗,只認 `\n`);讀取端 `_drift_jsonl_rows` 用 `str.splitlines()`,會在 U+2028/U+2029/U+0085 斷行
1. 走到哪:`--kind c4 --new "已提交 的乾淨樹"`(`_drift_c4_text_err` 只擋 `\n`、`\r`)成功,`changed` 裡帶著未跳脫的 U+2028(`json.dumps(ensure_ascii=False)` 不跳脫它)寫進帳。
2. 重現:接著對同一篇 `drift fix Verification/V 3 --kind c3 --status pass` → rc=2「有未提交的改動(不是 drift fix 自己留下的)」——`_drift_fix_last_sha` 讀不到那一行(切成兩段壞 JSON 被略過),指紋對不上;對照組沒有 U+2028 時同一步成功。`_drift_next_seq` 同理會把序號重發(讀不到那行就少算 max)。
3. 影響:「同一篇可以一項一項修、修完一起提交」在這個輸入下失效,錯誤訊息把原因說成別人的改動;`drift ack` 的 `text`(筆記原行)含這些字元時同樣讀不回、seq 重號。方向是失敗即擋,沒有放行風險。

## F4 修復帳與表態檔共用的路徑檢查讓既有的 `drift ack` 在 `governance/` 是符號連結時突然做不了
severity: minor
blocking: 否
引句:「            if cur.is_symlink():」
佐證行:file: `git show 19162c1e:scripts/lumos` 的 `cmd_drift_ack` 只做 `fp.parent.mkdir(parents=True, exist_ok=True)` 就寫;新版改走 `_drift_ledger_append` → `_drift_ledger_path_err`
1. 重現:repo 內 `governance` 是指向共用目錄的符號連結時,`lumos drift ack Issues/K 3 --kind c4 --reason …` rc=2「…/governance 是符號連結——帳檔與它在 repo 裡的上層目錄都要是一般的檔案與目錄,不往裡寫」(基準版本可寫)。
2. 影響:升級後這類消費專案的 ack 全部被擋,沒有覆寫開關;不是新功能(fix)的路徑,是既有指令的行為退化。修復帳新增這道檢查合理,但表態檔原本沒有,計劃裡沒有列為升級相容取捨。

## F5 修復帳寫不進去(或程序在寫筆記後被殺)留下的狀態沒有補帳的路
severity: minor
blocking: 否
引句:「筆記已改好,但修復帳沒記到;{cx['repo_rel']} 的改動用 git diff 看得到」
佐證行:file: `scripts/lumos:_drift_fix_record(patch 內 1385 行附近)`
1. 重現(`LUMOS_DRIFT_FIX_FAULT=ledger` 模擬寫帳失敗;SIGKILL 落在 `_drift_fix_write` 與 `_drift_fix_record` 之間效果相同):筆記已改、帳沒有。
2. 之後:重跑同一筆 → rc=2「有未提交的改動(不是 drift fix 自己留下的)」(那一筆發現也已消失,本來就不會再跑);同一篇的其他 fix 也同一句話擋。唯二出路是提交(帳永久缺一筆)或 checkout(丟掉修好的內容)。訊息只說「用 git diff 看得到」,沒說怎麼補。
3. 寫入與寫帳之間隔著鎖外的 `_drift_fix_verify`(重建整份圖譜物件),這段時間也是這個狀態;此窗口內另一個 `git commit -a` 會把筆記提交而沒有帳。

## F6 c1 / c5 的判定依賴家節點,鎖內指紋只比守衛紀錄那一篇
severity: minor
blocking: 否
引句:「            if cx["path"].read_bytes() != cx["raw"]:」
佐證行:file: `scripts/lumos:_guard_pass_home` 與 `_drift_fix_c5` 都用鎖外新建的 `cx["env2"]` 讀家節點的正式行
1. 時序(⚠ 未能重現,需兩程序在秒級窗口對打):fix 在 T0 建圖譜物件(家節點有綁測試的正式行)→ T1 另一個程序對家節點改掉/刪掉那條正式行(拿同一把鎖、合法)→ T2 fix 拿鎖,只比守衛紀錄指紋,通過,把守衛紀錄改成 pass 並寫「合約改由 [[家]] 的正式合約行守」。
2. 寫後驗證的 `handled` 只看守衛紀錄自己(status 是 pass、c1/c5 消失),不重驗家節點,所以不會被抓到。窗口很小,列出供 lens 對照。

## F7 舊版讀新帳:修復帳不在舊版的簿記檔名單
severity: minor
blocking: 否
引句:「                      "governance/drift-fixes.jsonl")」
佐證行:file: `scripts/lumos:35328`(`_disp_git_diff…` 用 `_BOOKKEEPING_FILES` 判「其後只有簿記增量」,基準版本的名單沒有這個檔)
1. 回滾/混版:退回舊版或另一台還沒升級的機器,在已 `code-loop pass` 留痕之後又提交了 `governance/drift-fixes.jsonl`,舊版判成「記錄 sha 之後動了代碼(非純簿記增量)」→ 留痕失效、要重跑代碼審。
2. 其他方向的回滾沒問題:舊版讀新的 drift-acks(多了 related/seq)照舊按 (路徑,原文,種類) 認,不會出錯;舊版不讀修復帳。

## 圖譜鏡頭固定席(逐條判定)
- Systems/guard-kill.md(★INVARIANT★ rc 優先序、--json 純度):diff 沒動 `guard kill` 的 rc 判定與 JSON 輸出路徑;不影響。
- Systems/lumos-cli-read.md(search 預設排除 superseded):diff 沒動 search;不影響。
- Systems/lumos-cli-lifecycle.md(re-inject 只覆蓋 sentinel 間):diff 沒動 re-inject;不影響。
- Systems/bound-tests-gate.md(code-loop check 逐支真跑綁定測試):`_BOOKKEEPING_FILES` 多一項只會讓純簿記的後續提交被豁免,不改閘的判定;不影響(混版問題見 F7)。
- Systems/授權與歸屬.md(授權檔不得進 _VENDORED_TOOLKIT、主程式檔頭 SPDX+MIT):diff 沒碰檔頭與白名單;不影響。
- Systems/測試假綠形態.md(還原翻紅釘要配前置斷言):屬 b 檔測試;本席只審 a,不評。
- Systems/design-loop.md(處置閘第五步):diff 沒碰 loop 判定;不影響。
- Systems/pitfalls-code-loop.md(★RISK★):簿記檔名單多一項,pitfalls 端 .jsonl 本就被副檔名排除;不影響。
- 超出上限只列名的節點:未逐條讀,不下判斷。

## 已查過、判定沒問題的(給收貨端對照)
- 鎖:寫入鎖只包「比指紋+atomic_write_verify」;鎖外做 git 與圖譜重建,兩個 fix 同篇同時跑,後到者在鎖內比指紋不符被擋(無互蓋);不同篇同時跑,seq 在鎖內取、帳追加也在鎖內,無同號(單工作樹)。
- `drift fix` 與 `guard settle`/`lumos set` 同時跑:都經同一把 `_vault_write_lock`,指紋是整篇位元組,會被別人改的就是這個,判定正確;例外見 F6(家節點)。
- 兩工作樹各自追加同號 seq:`_drift_bound_latest` 取同號全算,方向是要求全部涵蓋,只會多列、不會少列(下次 ack 遞增即收斂)。壞行/半行:`_drift_ledger_append` 先補換行,壞行被 `_drift_jsonl_rows` 略過;U+2028 例外見 F3。
- c2/c3 舊表態不再算數:c2/c3 在 `_drift_check_core` 只進 `listed`,`cmd_drift_check` 在沒有 must/unknown 時回 0,升級後不會多出擋推送的項目,只會多列(doctor Z 是 warn_soft、不進 issues)。
- 資源:新增的 git 呼叫多數走 `_lens_git`(20 秒逾時);`_plan_first_commit` 有 timeout=20;`_git_is_shallow`(既有)沒有逾時但只是 rev-parse;檔案 handle 皆 with 包住。`_drift_fix_changes` 的 SequenceMatcher 對大量重複行是平方級(實測 1 萬條相同行 8 秒),一般筆記不觸發,未列為 finding。

最高等級:major
