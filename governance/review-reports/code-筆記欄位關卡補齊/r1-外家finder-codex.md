severity: major

## F1 巢狀專案會讀錯設定檔，gate on 靜默降成 warn
severity: major
blocking: yes
引句:「+    mode, cfg_warns = _note_lint_config(_repo_root_from_env(env))」
`cmd_lint` 與 doctor 都用 `_repo_root_from_env` 找設定根；它遇到第一層名為 `docs` 的祖先便停止，而不是找 Git 根。若 vault 在 `/repo/packages/app/docs/demo-knowledge`、設定在 `/repo/.lumos/config.json`，兩個入口會改讀不存在的 `/repo/packages/app/.lumos/config.json`，把明確設定的 `gate: on` 當成未設定的 `warn`，因此違規只提醒、不擋提交或 CI。file: `scripts/lumos:1210`、`scripts/lumos:4829`、`scripts/lumos:10613`；同檔已有能正確向上找 `.git` 的 `_vault_repo_root`，file: `scripts/lumos:7425`。
翻紅重現（已實跑）：
```sh
python3 -B -c 'import runpy,types,pathlib; m=runpy.run_path("scripts/lumos", run_name="lumos_review"); N=types.SimpleNamespace; print(m["_repo_root_from_env"](N(vault=pathlib.Path("/repo/packages/app/docs/demo-knowledge"))))'
```
實際輸出 `/repo/packages/app`，不是放置專案設定的 `/repo`。

## F2 空字串日期繞過日期與既有 cutoff 規則
severity: major
blocking: yes
引句:「+        if v is not None and str(v).strip() != "" and not _note_date_ok(str(v)):」
日期欄位存在但寫成 `created: ""` 時，新增規則因空字串直接跳過；既有 aliases、status 值域等規則又以 created 日期決定是否啟用，因此同一個空值能同時繞過日期檢查及 cutoff 後的結構守衛。例如 `status: not-a-real-status` 仍得到零錯誤。決策的 `decided`、`ended` 使用相同空字串豁免。file: `scripts/lumos:4910`、`scripts/lumos:4929`、`scripts/lumos:5141`、`scripts/lumos:5145`。
翻紅重現（已實跑）：
```sh
python3 -B -c 'import runpy,types,pathlib; m=runpy.run_path("scripts/lumos", run_name="lumos_review"); N=types.SimpleNamespace; fm=["type: system","status: not-a-real-status","created: \"\"","summary: |-","  KEY:x","tags: []"]; fields,blocks,lint=m["parse_frontmatter"](fm); note=N(fields=fields,fm_lines=fm,lint=lint,stem="X",block_keys=blocks,targets=[],rel="Systems/X.md"); env=N(notes={"Systems/X.md":note},vault=pathlib.Path("/definitely/missing/vault")); print(fields); print("old=",m["_lint_collect"](env,"Systems/X.md")); print("new=",m["_lint_new_rules"](env,"Systems/X.md"))'
```
實際輸出包含 `created: ''`，且 `old= ([], [])`、`new= []`。
