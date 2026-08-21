C1. ✅ ★IRREVERSIBLE★ 缺實質回退在 doctor --ci 與 cmd_lint 皆走 error/errs,計入 issues/errs 使 rc=1(doctor: strict=args.strict or args.ci,issues>0→rc1;lint: return 1 if errs else 0) | 證據: scripts/lumos:786-789(doctor rev_err via warn()),scripts/lumos:2740-2742(lint errs.append),scripts/lumos:14800-14801(strict=args.strict or args.ci),scripts/lumos:1319-1323(issues==0→0 否則 1 if strict else 0),scripts/lumos:2786(lint return 1 if errs else 0);測試 scripts/test_lumos.py:2888

C2. ✅ ★CHECKPOINT★ 缺回退只入 rev_soft/warns,經 warn_soft() 印出但不動 issues,--ci 下仍 rc0 | 證據: scripts/lumos:470-476(warn_soft 不加 issues),scripts/lumos:790-792(CHECKPOINT 分支呼叫 warn_soft);測試 scripts/test_lumos.py:2892-2893(「只有 checkpoint 缺回退 → rc0」)

C3. ✅ ★IRREVERSIBLE★ 合規為 `_rollback_resolved(...) or _guard_resolved(...)` 兩軌 OR 邏輯 | 證據: scripts/lumos:787(`if not (_rollback_resolved(nnote, ref) or _guard_resolved(nnote, guard_ref))`),scripts/lumos:2741(lint 單檔版同邏輯);測試 scripts/test_lumos.py:2896-2911(t_reversibility_guard_doctor)

C4. ✅ ★CHECKPOINT★ 分支只呼叫 `_rollback_resolved`,不讀/不呼叫 `_guard_resolved`(guard_ref 變數存在但未使用) | 證據: scripts/lumos:790(`elif not _rollback_resolved(nnote, ref):  # ★CHECKPOINT★;guard_ref 不讀`),scripts/lumos:2743 同款單檔版(`# ★CHECKPOINT★;guard_ref 不讀`)

C5. ✅ ref 必須恰為字面 `decisions`(`.strip().lower() != "decisions"` 即回 False),且節點 `decisions[]` 需 ≥1 條非空 rollback(或 guard)內容 | 證據: scripts/lumos:2292-2296(`_rollback_resolved`),scripts/lumos:2299-2303(`_guard_resolved`)——兩者對 ref 值域與 decisions[] 非空字串判定完全一致

C6. ✅ `extract_reversibility` 為獨立函式,用自己的 CHECKPOINT_RE/IRREVERSIBLE_RE/ROLLBACK_REF_RE/GUARD_REF_RE,未觸碰 `extract_contracts`(定義於 L1829)或 `INV_TAG_RE`(L1855);段落註解自陳「獨立於 ★INVARIANT★ 合約軸;走平行函式,不碰 extract_contracts/INV_TAG_RE」 | 證據: scripts/lumos:2195(段落標題註解),scripts/lumos:2196-2199(獨立 regex 常數),scripts/lumos:2275-2289(`extract_reversibility` 定義,函式體內無 `extract_contracts`/`INV_TAG_RE` 字樣);測試 scripts/test_lumos.py:2883-2893

C7. ✅ type≠"system" 判為 error(`rev_err.append(...)`/lint `errs.append(...)`);type 缺失時 `.fields.get("type")` 回 None,`None != "system"` 為安全字串/None比較不崩潰,只是照常被判為「標在非 Systems」(非漏判,亦非例外) | 證據: scripts/lumos:782-785(doctor,`t_ = nnote.fields.get("type"); if t_ != "system"`),scripts/lumos:2738-2739(lint 同款);測試 scripts/test_lumos.py:2851-2854(type=issue 案例,rc1 且訊息含「只能在 Systems」)

C8. ❌ 實際讀取 **7** 個來源檔,非六個——多出第 7 源 `CI_LOG_NAME`(僅當 `_ci_config(_ci_root)[0]` 為真時條件載入);函式 docstring 亦明寫「唯讀彙整七帳」 | 證據: scripts/lumos:2954(docstring「彙整七帳」),scripts/lumos:2983-3019(共 7 個 `load(...)` 呼叫:bypass/rot-queue/governance/signoff/kill/canary/ci),scripts/lumos:3013-3019(第 7 源 CI 回流帳,條件載入)

C9. ✅ dedup 發生在 `cmd_gov` 讀取後(排序後迴圈),key = `(commit, frozenset(nodes), gate, kind, token)` | 證據: scripts/lumos:3022-3029(`k = (r["commit"], frozenset(r["nodes"]), r["gate"], r["kind"], r.get("token", ""))`)

C10. ❌ `.governance-log.jsonl` 有兩個寫入者,非「doctor 唯一新寫入者」:`_append_governance_log` 函式自身 docstring 明寫「寫者=doctor --ci + anchor approve」,`cmd_anchor_approve`(約 L10120-10149)在 `lumos anchor approve` 時也會呼叫同一寫入函式(hard=False,gate="anchor-approve"),與 doctor --ci 無關。doctor 侧「只在 --ci 模式下 append」屬實,但「唯一新寫入者」為假 | 證據: scripts/lumos:422(docstring「寫者=doctor --ci + anchor approve」),scripts/lumos:1322-1323(doctor: `if ci: _append_governance_log(...)`),scripts/lumos:10147-10148(anchor approve 呼叫 `_append_governance_log`);測試 scripts/test_lumos.py:2914-2936(t_governance_log_write,僅驗 doctor 側,未涉及 anchor approve 這條路徑)

C11. ❌ `--since` 預設 90 天屬實,但六本帳檔「皆列於 .gitignore(本機本地檔案)」為假:專案根 .gitignore 只忽略 `docs/.ci-log.jsonl`,不含 bypass-log/rot-queue/governance-log/canary-log/kill-log/signoff-log;`git ls-files` 顯示 `docs/.bypass-log.jsonl`、`docs/.canary-log.jsonl`、`docs/.governance-log.jsonl`、`docs/.signoff-log.jsonl` 目前**已被 git 追蹤**(非本機本地檔案),`git check-ignore` 對六個檔名一律回「NOT ignored」 | 證據: scripts/lumos:2953(`since_days=90`),scripts/lumos:14233(`--since` `default=90`);/Users/enzo/harness/lumos-toolchain/.gitignore(僅含 `docs/.ci-log.jsonl`,無其餘五本帳檔);`git ls-files docs/` 命中 `.bypass-log.jsonl .canary-log.jsonl .governance-log.jsonl .signoff-log.jsonl`;`git check-ignore -v` 對六檔皆回 NOT ignored

C12. ✅ Check H 僅 `--ci` 下掃 diff(否則印「僅 --ci 模式掃 diff」略過),`IRREVERSIBLE_HINT_PATTERNS` 含 prod/smtplib/`requests.post`/`boto3`/`DROP TABLE` 等正則,命中走 `warn_soft`(不計 issues、不影響 rc) | 證據: scripts/lumos:1002-1016(Check H 區段,`if not ci: ... else: ... warn_soft(...)`),scripts/lumos:2220-2228(`IRREVERSIBLE_HINT_PATTERNS` 常數,含 `prod`/`smtplib`/`requests\.post`/`boto3\.(client|resource)`/`DROP\s+TABLE`)

C13. ✅ 去噪規則命中:`_is_advisory` 判定 `(not hard) and kind=="warned" and no token and no detail`,同 `(date,gate,kind,node)` 折 ×N;同群組節點 >6 進一步收成「N 節點(前3個)…×次數」摘要行;`--full` 還原逐筆 | 證據: scripts/lumos:3035-3072(`_is_advisory`/`agg`/`>6` 分支/`full` 分支);測試 scripts/test_lumos.py:1555-1593(t_gov_denoise,30 筆折 1 摘要行、「10 節點」+「×3」、`--full` 還原 31 行、≤6 節點小群組逐節點+×2)

C14. ✅ 對抗層增量帳只計 `kind in ("caught","none")`(missed 不計入),依 `findings` 欄位累加,依 severity/auditor 分佈;`findings is None` 的舊輪另計 legacy_rounds、不混入 fold_total | 證據: scripts/lumos:3112-3132(`if r["kind"] not in ("caught", "none"): continue`;`fnd is None → legacy_rounds`;否則累加 `fold_total`/`fold_sev`/`fold_aud`);測試 scripts/test_lumos.py:1631-1644(t_gov_adversarial_increment,含一筆 `kind=missed` 標註「missed 不計折入」)

C15. ✅ `[rollback:]`/`[guard:]` 為獨立 regex(`ROLLBACK_REF_RE`/`GUARD_REF_RE`,L2198-2199)抽出的標籤指針字串,交給 `_rollback_resolved`/`_guard_resolved` 判定;`decisions[].rollback`/`decisions[].guard` 則是 `parse_decisions(note.fm_lines)` 解析出的 frontmatter 結構化欄位(`d.get("rollback","")`/`d.get("guard","")`)——兩套資料來源與存取路徑完全分開,皆未共用 `INV_TAG_RE`(L1855,合約軸專用)或 `strip_test_refs`(L2190-2192,合約軸專用) | 證據: scripts/lumos:2198-2199(標籤 regex),scripts/lumos:2292-2303(`_rollback_resolved`/`_guard_resolved` 讀 `note.fm_lines` 經 `parse_decisions`,非讀標籤字串),scripts/lumos:1855/2190-2192(`INV_TAG_RE`/`strip_test_refs` 定義,函式體內無被 C4-C6 一帶的可逆性函式引用)

✅12 ❌3 ❓0 ⏭0
