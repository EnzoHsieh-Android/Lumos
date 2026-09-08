# r3 intake — 棧別提問表態閘(2026-09-09;末輪驗收:五席 29 條,blocker 7,全折、accepted 空)

preflight-4: ran(首輪已跑;本輪為末輪驗收,前掃不重跑——這行只是讓機械讀側認得本檔)

## 收貨:外家否決席(codex)三條的機械重現(編排者)
- F10 hook 掃描上限接錯層 → HIT:`sed -n 412p scripts/hooks/claude/impact-hook.py` 顯示 `cap_chars: int = 8000`,434-437 行每段截斷+512 distinct token;790 行只送 `{"query","prospective"}`。折法:hook 另送原始 `delta_text`(保留換行、≤2 MB),`query` 語意不變。
- F11 表態座標對不上推送目的地 → HIT:`scripts/hooks/pre-push:197-202` 從 remote ref 取 `_rbranch` 傳給 check;`dispositions` 子命令沒有 `--branch`(argparse 只在 check 加)。折法:`dispositions`/`--carry` 加 `--branch`,check 找不到記錄的訊息講這句。
- F12 壞 config 的閘語意未定 → HIT(spec 缺矩陣;code `_stack_questions_config` 讀不了時已回 gate=all/300 並留 warning)。折法:spec 補矩陣。**引句錨不到快照**(它寫「設定檔壞掉時」,快照原文是「`.lumos/config.json` 壞掉時」)——quote-check 判不採信,但編排者重現屬實,照折、記進 findings-set 並在此留痕。

## 其他席 blocker/major 的機械重現
- B1 merge 主線後兩點式範圍 → HIT:`scripts/hooks/pre-push:179` `_range="$_rsha..$_lsha"`。折法:表態適用性改算 `merge-base(主線, at_sha)..at_sha`,推主線本身才用推送範圍。
- B2 `git grep -F` 子字串 → HIT:`git grep -F -q -e t_lint_scope_polic HEAD -- scripts` rc0;加 `-w` 後 rc1(整字 `t_lint_scope_policy` rc0)。折法:`-w`。
- C4/B7 跨 repo root fatal → HIT:`git grep -q -e foo HEAD -- ../lumos-disposition/scripts` → `fatal: ... is outside repository`,rc=128。折法:root 在 repo 外只做①並註記;其他 rc≠0 講「無法驗證」。
- B3 id 唯一沒釘測 → 部分 MISS:worktree 測試 ① 已驗 `len(ids)==len(set(ids))`;但全表集合未釘。折法:釘全表集合+格式 regex。
- B4 半途超時 → HIT(spec 沒講);code 已保留已查出的 BLOCKED。折法:spec 明寫。
- B5 at_sha 空 → HIT(spec 只講 path:line 退工作樹,test: ②沒定義)。折法:沒 at_sha 一律用 HEAD 對樹驗。
- H1 gov 去重鍵 → HIT:`scripts/lumos:4746` 鍵 `(commit, nodes, gate, kind, token)`,token 只給 canary/rejected。折法:dispositions/recall-miss 拿 ts 當 token。
- H4 supersede 開 rel-cascade → HIT:`grep -rl pitfalls棧別效能追問_計劃 docs/lumos-toolchain-knowledge/Verification/` 命中 `2026-07-20_棧別效能追問.md`(plan_refs 第 10 行)。折法:S10 同一次 `rel-cascade confirm`。
- H2/H3 → HIT(效能檢核目錄無 id 欄;commands/08:7-8、docs/command-reference.md:95、docs/指令參考.md:95 三處文字過期)。折法:S10 補。
- A1/A3/A4 → HIT(code 讀:check 序列早退未在 spec 講明;`_validate_repo_ref` 已有唯一入口;三套 CJK 判定並存)。折法:spec 明寫沿用哪一套(worktree code 已照做)。
- C1/C2/C3/H5 → HIT(同 F10/B3/C3 條)。

## 處置
- 29 條全折成 spec 文字或實作承諾;blocker 輪 accepted 為空。minor 8 條(A2/A5/C5/B6/B7/B8/B9/B10/H6)亦折成 spec 句(命名慣例、非遞迴 ls-tree、carry 不重驗、CJK 範圍、跨 repo、recall-miss 驗 id、搬家計數、id 格式、體積)。
- carrier=正確性席(quote-check 全錨);外家席 F12 引句錨不到,留痕於上。
