severity: major

我只讀了 diff 與鄰居程式,沒有跑任何東西。

**1. 分層與依賴方向**

鄰居是 `_codeloop_pass_mech` 經 `_codeloop_guard_verdict(..., mech_only=True)` 進推送判定,沒有直接伸進選擇點內部。
- 鄰居:`scripts/lumos:73381`(`_codeloop_pass_mech`)、`scripts/lumos:79685`(`_codeloop_guard_verdict` 的 `mech_only` 參數)。
- 推送端入口:`scripts/lumos:17448`(`_spec_gate_push_check` 呼叫 `_choice_push_round`)。
- 新碼:`_codeloop_pass_choice` 放在同一區、同一個呼叫位置,排在 `_codeloop_pass_mech` 之後(位置跟鄰居一致)。但它直接呼叫選擇點區的內部函式 `_choice_push_has_kotlin`、`_choice_push_round(..., site="pass")`、`_CHOICE_PASS_TAIL`,沒走判定函式那一層。
- 這條我判 minor 並標 ⚠ 交編排者:`_choice_push_round` 本來就是為了被別處呼叫而加了 `site` 參數,所以不確定算不算「跨層直呼」。

引句:「bad = _choice_push_round(None, rr, f"{old}..{tip}", (remote, f"refs/heads/{name}"), site="pass")」
severity: minor
blocking: 否

**2. 命名與錯誤處理**

跟鄰居一致。
- 命名:`_codeloop_pass_choice` 對 `_codeloop_pass_mech`;`_CHOICE_PASS_*` 對 `_CHOICE_PUSH_*`。
- 回傳:都回 bool,`_codeloop_pass_gate` 擋下都是 `return False, None`。
- 出口訊息:都印原因、再印 stderr 的「代碼審還不能記通過…」,最後是 `lumos code-loop pass --loop <編號> --note ...`(`scripts/lumos:73396-73398` 對應新碼的 `print` 兩行)。
- 帳:都用 `_gate_event_or_warn(repo_root, "code-loop-pass", "blocked", ..., hard=True, head_sha=, ref=, extra={"blocks": [...]})`,擋下原因 `blocks` 帶 `"choice"` 對應鄰居的 `reason_kind`。
- `gov --stats` 的 `pass_blocked` 與 `_gov_choice_counts` 其他計數同一寫法(`c[...] += 條件`,`scripts/lumos:17944` 附近)。
- `_choice_push_ledger` 的 `rev` 傳 `None` 是 `_gov_rows_at` 本來就支援的用法(`scripts/lumos:65601`)。

不對齊 0 條。

**3. 第二種做法**

(a) 取分支名:新碼自己用 `symbolic-ref -q --short HEAD`,專案已有共用的 `_redbase_branch_name`(`scripts/lumos:15391`)與 `_git_current_ref`(`scripts/lumos:12195`)。
- `_redbase_branch_name` 的註解明寫不用 `--short`,因為有同名 tag 時會回 `heads/<名>`,前後寫的名字會對不上。新碼踩的正是這個寫法。
- `_codeloop_pass_gate` 本來就收了 `branch` 參數(`scripts/lumos:73429`),新碼卻另外重算一次。
- 鄰居 `_choice_range` 在 `scripts/lumos:77889` 也用 `--short`,所以「專案裡本來就有兩種」。但共用版本註明是為了統一,新碼多加了一處手寫。

引句:「r = _lens_git(rr, "symbolic-ref", "-q", "--short", "HEAD")」
severity: major
blocking: 是

(b) 字樣替換機制:新碼引入 `_CHOICE_PASS_WORDS`(逐條 `str.replace` 的對照表)加 `_choice_site_words`,把推送字樣在輸出時換成 pass 字樣。
- 專案原本的做法是 pass 沿用推送前同一段擋下訊息:`_codeloop_pass_mech` 的註解寫「每道印推送前同一段擋下訊息」,再補 pass 自己的出口(`scripts/lumos:73378-73379`)。專案裡沒有別處用事後字串替換改訊息。
- 它還讓每個 `print` 與事件備註都要記得包一層 `_choice_site_words`,漏包的句子會留著推送字樣。
- 同一圈判定還另有 `_CHOICE_PASS_FIX` 蓋掉 `_CHOICE_PUSH_FIX`,這是第三處按場合分流的字樣來源。

引句:「_CHOICE_PASS_WORDS = (("[spec-gate 推送前]", "[code-loop pass 選擇點]"), ("選擇點推送前擋下", "選擇點 pass 預判擋下"),」
severity: major
blocking: 是

(c) 取遠端舊值:新碼手算 `refs/remotes/<remote>/<name>`,沒有就用全 0,再組成 `old..tip`。鄰居 `_choice_range` 與 `scripts/lumos:52971` 都直接傳全 0,讓 `_push_range_start` 自己決定起點(註解寫「起點只在那裡算一處」)。
- 新碼同時還帶 `push=(remote, ref)`,所以起點最後仍走 `_push_range_start`,結構上沒另起一套。
- 但多了一種「模擬掛鉤輸入」的舊值寫法,我判 minor。
- 新測試的 `_cpc_git` 是新的小工具,跟 `_ck_*`/`_ckp_*` 的做法沒有衝突。

引句:「old = _lens_full_sha(rr, f"refs/remotes/{remote}/{name}") or "0" * len(tip)」
severity: minor
blocking: 否

不對齊共 4 條,其中 major 2 條

相關檔:`/Users/enzo/harness/lumos-finding-seat/scripts/lumos`、`/Users/enzo/harness/lumos-finding-seat/scripts/test_lumos.py`
