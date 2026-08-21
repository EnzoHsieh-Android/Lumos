C1 [✅] pre-commit 有 Gate DG(緊接 Gate CC 之後)呼叫 `lumos delguard --staged` | 證據: scripts/hooks/pre-commit:42(Gate CC 標記),53(Gate DG 標記),57(`"$CC_PY" "$REPO_ROOT/scripts/lumos" delguard --staged 2>/dev/null || true`)

C2 [✅] S1(`_delguard_parse_diff`)per-file 回收表(added dict)+stopword(`_DELGUARD_STOP`)+域路徑段排除(`c.startswith(seg) or ("/"+seg) in c`)+lockfile/.md 不抽 token | 證據: scripts/lumos:11381-11451(尤其 11403-11405 排除判斷、11414/11443 `.md` 跳過、11445-11450 per-file 回收比對)

C3 [✅] `_delguard_confidence` 用單次 `git grep --cached` 對所有 token 一次查完,全域(排除 vault/排除域)零命中→high,仍有命中→low | 證據: scripts/lumos:11454-11487(11465-11471 單次 `git -c core.quotePath=off grep --cached -w -F -e t1 -e t2 …`;11487 `"low" if t in alive else "high"`)

C4 [✅] `_delguard_vault_scan` 用組合 regex(rx)+逐 token regex(per,與 `_delguard_confidence` 的 pats 同款,程式碼自身稱「三件套」)找命中節點與原句;排序 key `(conf!=high, folder!="Systems", node, line_no)`——folder 只影響排序、不濾掉非 Systems 命中,且 Systems 排最前 | 證據: scripts/lumos:11490-11529(11499-11500 兩組 regex,11458 註解稱「同款三件套 regex」,11505/11520/11528 排序 key)

C5 [✅] S2(`_delguard_purelink`)判定純連結編輯,若該檔同時是 S1 vault 命中(`hits`)→ 進 `fake_sync` | 證據: scripts/lumos:7037(LINK_KEYS 定義)、11532-11551(`_delguard_purelink`)、11615-11619(`if _delguard_purelink(dl) and any(h["node"]==rel for h in hits): fake.append(rel)`)

C6 [✅] S3 於 stdout 印「退場前自問」三問(對應改了什麼/逐句判是否成立/成立或作廢,新增連結不算同步) | 證據: scripts/lumos:11638-11639

C7 [✅] advisory 恆 rc0:`|| true` 兜 crash(pre-commit)、`except Exception` 兜底降級、python 內建 deadline(`LUMOS_DELGUARD_DEADLINE`,例外/ValueError 皆退預設 2.0)、git diff rc≠0 走同一路徑降級,訊息走 stdout | 證據: scripts/hooks/pre-commit:57(`|| true`);scripts/lumos:11563-11565(讀 env、預設 "2.0")、11591-11596(git diff rc≠0 raise 進 except)、11600-11613(timeout 降級走 print/stdout)、11641-11646(`except Exception` 兜底、`print` 走 stdout、`return 0`)

C8 [✅] `--json` 輸出含 tokens/hits/fake_sync/degraded(另有 dropped/reason) | 證據: scripts/lumos:11568-11570(降級 JSON)、11620-11623(正常路徑 JSON:`{"tokens":…, "dropped":…, "hits":…, "fake_sync":…, "degraded": False}`)

C9 [✅] git grep 用 `--cached`;git diff 帶 `-M`,並搭配 `-c core.quotePath=off -c diff.noprefix=false -c diff.mnemonicPrefix=false` | 證據: scripts/lumos:11465(`git -c core.quotePath=off grep --cached …`)、11586-11588(`git -c core.quotePath=off -c diff.noprefix=false -c diff.mnemonicPrefix=false diff --cached -M --no-color`)

C10 [✅] vault-only repo(`graph_root=="."`)時靜默 return 0 | 證據: scripts/lumos:11579-11583(`gr_rel = …; if gr_rel == ".": return 0`)

C11 [✅] 先驗參數 `DELGUARD_TOKEN_CAP=40`、`DELGUARD_TOP_N=10`;顯示逐條列出時因 hits 已依信心排序(高信心優先),故超過 top-10 截斷仍優先保留高信心項目逐條列出,且 dropped/rest 統計行恆列印(不因截斷清零) | 證據: scripts/lumos:11369-11370(常數定義)、11528(hits 排序 conf 優先)、11631-11635(`hits[:DELGUARD_TOP_N]` 逐條 + `rest`/`dropped` 統計行);測試佐證 scripts/test_lumos.py:10998-11011(cap flood fixture 驗 dropped>0、top-10 截斷、rest 統計行)

C12 [✅] 排除域與 pre-commit `should_exclude` 對齊,7 目錄(node_modules/bin/obj/.git/dist/build/__pycache__)+3 lockfile(package-lock.json/yarn.lock/pnpm-lock.yaml);由 `t_precommit_whitelist_drift_guard` 釘防第三份清單漂移 | 證據: scripts/lumos:11366-11368(`_DELGUARD_EXCLUDE_DIRS` 7 項、`_DELGUARD_EXCLUDE_LOCKFILES` 3 項);scripts/hooks/pre-commit:88-102(`should_exclude` case 行同 7 目錄+3 lockfile);scripts/test_lumos.py:1706-1734(`t_precommit_whitelist_drift_guard` 內 1724-1734 段逐項比對 `_DELGUARD_EXCLUDE_DIRS`/`_DELGUARD_EXCLUDE_LOCKFILES` 對齊 pre-commit)

C13 [✅] S3 問句同步收錄在 `lumos-project-notes` skill 的退場段 | 證據: skills/lumos-project-notes/SKILL.md:239-252(「退場自問」1-3 問內容對應 delguard S3;252 行明text「S1 命中時會機械吐上面 1-3 這三問」)

C14 [✅] `t_delguard`(scripts/test_lumos.py:10863 起,單一函式)靜態含 78 條字面 `check("delguard…")` 斷言 + 1 條迴圈(對 `_DELGUARD_EXCLUDE_DIRS` 7 項)於執行期展開 7 條 = 85 條 `check()` 呼叫;內容涵蓋 LINK_KEYS/S1 抽取/S1 信心/S1 掃描/S2 假同步/S3 CLI 整合/fail-open(超時+內部錯誤)/deadline/cap 邊界(超 45 符號)/標頭計數鑑別力前置斷言/pre-commit 掛載對齊 | 證據: scripts/test_lumos.py:10863(函式起點)、10863-11369(全函式,下一個 `def t_` 為 11370 `t_canary_record_persist`);Task 標記 10864/10881/10894/10904/10918/10945/11134(Task1-7);78 條 `grep -c 'check("delguard'` + 1 條迴圈行(11042-11044,對 7 項 `_DELGUARD_EXCLUDE_DIRS` 逐項 check)= 85

C15 [✅] 全量測試在 commit 95c4224 為 2515/0(全數通過) | 證據: docs/.governance-log.jsonl:15463(`"commit": "95c4224", "gate": "code-loop", "kind": "passed", … "detail": "…全量 2515/0@95c4224…", "head_sha": "95c422488655fbde0a7bc5ddb639a51bf18bfe67"`);另 docs/.governance-log.jsonl:15465(同分支後續 commit d09f880 記「全量 2515/0」)

✅15 ❌0 ❓0 ⏭0
