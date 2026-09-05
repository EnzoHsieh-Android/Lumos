# code-six-fixes r2 delta 回歸審查

審查對象:`governance/review-reports/code-six-fixes/r2-snapshot.patch`(bde1217^..bde1217,即「r1 修法」到「r2 修法」的差)。逐 hunk 讀完並實跑驗收、寫最小重現。

**流程性提醒(先講,影響本報告怎麼讀)**:審查過程中(約 15:52)發現工作樹已經在 `scripts/lumos`、`scripts/hooks/claude/dispatch-lens-hook.py`、`scripts/test_lumos.py` 上多了**未進 r2-snapshot.patch 的第三輪未提交改動**(註解自標「外家 r1 M2 / r2 M」「外家 r2」),時間點緊接在 `r2-外家finder.md`(15:52 產出)之後。核對後,那個外家 finder 已經獨立抓到本報告下面 (e) 的 blocker 與附帶的 Codex 提示語 minor,並且已經被即時修掉——但這兩處修法**不在**我被交付要審的 r2-snapshot.patch 裡。以下判定一律針對 patch 檔本身(=HEAD bde1217 的內容),blocker/major 兩條已經跟活動中的工作樹核對過「現在已經修了」。

## (a) 修復驗收(逐項實跑)

1. `python3 scripts/lumos dispatch-lens --spec /etc/hosts --repo . --json` → rc=2,印「擋下:計劃筆記不在這個 repo 裡 /etc/hosts」。
severity: clean
blocking: 否
引句:「擋下:計劃筆記不在這個 repo 裡 {spec_path}」
file: `scripts/lumos:17627`(訊息模板;實際判斷是前一句 `sp.resolve().relative_to(root.resolve())`)

2. 計劃寫 `scripts/../../x.py`:regex 真的抓到候選字串(已用 `re.findall` 實測命中),但 `inside = p.resolve().relative_to(root.resolve())` 的穿越檢查擋下,`code_files` 維持空、不收。實跑一個真的把候選路徑指到 repo 外的臨時檔案,`text`/`code_files` 皆空、rc=0,沒有洩漏。
severity: clean
blocking: 否
引句:「inside = p.resolve().relative_to(root.resolve()) is not None」
file: `scripts/lumos:17650`

3. `dispatch-lens --spec x.md --status --repo . --json` → rc=2,印「擋下:--status、--spec 一次只能給一個…」。
severity: clean
blocking: 否
引句:「擋下:{'、'.join(_modes)} 一次只能給一個」
file: `scripts/lumos:18901`

4. 有檔但 0 席:實跑一個計劃只提到一支沒人依賴的程式檔,輸出多了一行「…沒牽到任何帶合約/事故的節點」,`rc=0`、`listed=0`,不再是空字串,編排者能分辨「鏡頭跑了但沒東西」與「鏡頭掛了」。
severity: clean
blocking: 否
引句:「沒牽到任何帶合約/事故的節點」
file: `scripts/lumos:17706`

## 逐項判定

5. `Path(__file__).resolve()` 在三種載入方式下都正確指回「正在執行的那份 lumos」:SourceFileLoader 載入(`spec_from_file_location("lm", GRAPHCTL, ...)`)時 `__file__` = 傳入的實際檔案路徑(已用 python 直接印證);被 vendor 到消費端專案時,消費端自己那份 `scripts/lumos`(doctor 的 `vendored-cli` 檢查證實各專案是各自一份實體檔、非 symlink,見 `_lumos_src()`/`_version_nudge` 的版本戳比對邏輯)執行時 `__file__` 自然指向消費端自己的檔,不會誤連回來源庫。`rr`/`data` 在 `subprocess.TimeoutExpired` 例外時直接 `except Exception: skipped_files.append(f); continue`,`continue` 早於任何 `data.get(...)` 呼叫,不存在用到未賦值 `data` 的路徑。
severity: clean
blocking: 否
引句:「skipped_files.append(f); continue」
file: `scripts/lumos:17676`(前一行 `except Exception:`)

6. dict 合併三種情況實測:n 不在 pinned → kind=`計劃連結`、contract=None、files=[];n 在 pinned 且 kind 為 None → kind 仍還原成純`計劃連結`但 contract/files 留用 pinned 的值(這條分支目前不可達,因為 `_LENS_KIND.get(kind)` 的 kind 只會是 direct/incident/indirect 三個字串之一,永遠命中,None 分支是防禦性程式碼,無害);n 在 pinned 且 kind 有值 → kind=`計劃連結+直接相依`,contract/files 正確保留。三案例皆已用等價 Python 片段實測輸出比對過。
severity: clean
blocking: 否
引句:「listed = [{"node": n, **({"kind": "計劃連結", "contract": None, "files": []} | pinned.get(n, {})」
file: `scripts/lumos:17696`

7. `_lens_render_listed` 用 `.get()` 讀 kind/files,diff 模式的 `listed` 元素在來源(`listed.append({"node": node, "rel": rel, "kind": ..., "contract": ..., "files": files_ok})`)本來就保證這三個鍵一定存在(kind/contract 可能是 None、files 可能是 []),所以 `.get()` 與原本 `[...]` 存取行為逐位元相同;`dispatch-lens` 全套 56 個既有測試(含「主線節點被列出且貼了 base 版合約行」「分支改的假合約行不出現」)全過,截斷提示「合約行超過 40 行」現在由同一個函式印,兩模式必然一致。
severity: clean
blocking: 否
引句:「_lens_render_listed(lines, listed, _read_base, cap, max_lines, _bidx)」
file: `scripts/lumos:17585`(diff 模式呼叫;spec 模式對應呼叫在 `scripts/lumos:17717` 的 `_read_wt`)

8. **delguard 部分結果的 `--json` 輸出說謊(blocker)**:`_partial` 算出來後只餵給治理帳(`_delguard_log_result`),`--json` 那行印出的 `"degraded"` 卻是寫死的 `False`,完全沒接 `_partial`。用 monkeypatch 讓 `_delguard_vault_scan` 睡過 deadline 才回傳(模擬「被截斷、回部分結果」)重現:治理帳正確記成 `kind=degraded reason=timeout-partial`,但同一次呼叫的 `--json` 印出 `{"...,"degraded": false}`——自動消費端(pre-commit/CI/別的 lumos 子命令解析這段 JSON)會把不完整掃描當成完整成功放行,直接牴觸函式自己 docstring 寫的「`--json` 降級契約…皆同款」承諾。工作樹目前已有未進本 patch 的修法(`"degraded": _partial, **(...)`),但那不是我審的這份 patch 裡的內容。
severity: blocker
blocking: 是
引句:「_partial = time.monotonic() - t0 > deadline   # 外家 r1 M2:掃描被 deadline 截斷回部分結果,不能算 ok」
file: `scripts/lumos:14294`(問題行);計算式在 `scripts/lumos:14285`

9. ⚠ delguard `_partial` 用「回傳後量到的總耗時 > deadline」當「有沒有被截斷」的判準,理論上會誤判:若 `_delguard_vault_scan` 剛好在最後一次內部 `deadline_check()` 通過之後、自然掃完全部檔案才返回,而這段「最後一段沒被檢查覆蓋的處理時間」把總耗時推過 deadline,結果會是「完整掃描」卻被記成 `degraded/timeout-partial`(方向與 (8) 相反,不是少報而是多報)。已用 monkeypatch 重現該時序(scan 內只呼叫一次 deadline_check 且回 False,自己再睡到過 deadline 才 return),但真實情況的觸發窗口很窄(僅單一檔案或 2000 行批次的處理時間),算不出具體多常發生,標記信心較低。
severity: minor
blocking: 否
引句:「_partial = time.monotonic() - t0 > deadline   # 外家 r1 M2:掃描被 deadline 截斷回部分結果,不能算 ok」
file: `scripts/lumos:14285`

10. `_delguard_log_result` 的 `hits` 元素目前唯一呼叫來源是 `_delguard_vault_scan`,其實作保證每筆 hit 都有 `node` 鍵;就算未來哪個呼叫端傳入缺 `node` 的 hit,整個函式體包在 `try/except Exception: pass` 裡,best-effort 不會炸主流程。
severity: clean
blocking: 否
引句:「_append_governance_log(Path(gr), [{"gate": "delguard", "kind": kind, "hard": False,」
file: `scripts/lumos:14203`

11. bash `while IFS= read -r` 雖然在管線右側跑在 subshell,但 bash 的函式定義會被 fork 出的 subshell 完整繼承,實測 `log` 在 subshell 裡呼叫可以正常輸出;`out` 沒有任何 `LOG:` 行時(模擬舊版 python 模組)迴圈跑 0 次,但緊接著的 `log "回放週跑原始:..."` 不在迴圈內、無條件執行,已實測驗證「不會一行都不記」,只是退化成印原始 JSON 那行、遺失逐項計數。
severity: clean
blocking: 否
引句:「echo "$out" | sed -n 's/^LOG://p' | while IFS= read -r _l; do log "回放週跑:$_l"; done」
file: `governance/autonomous-loop.sh:258`

12. `_is_advisory` 折入 `kind=ok` 只影響 `cmd_gov` 預設(非 `--full`)畫面的折疊聚合;`--full` 那支迴圈直接吃 `ded`、完全不呼叫 `_is_advisory`,逐筆印出沒變。`--stats` 呼叫獨立的 `_render_gov_stats`,裡面只用 gate 分組算 raw/ded/nodes/commits/dates 計數,沒有任何比率把 `kind` 拿來分子分母(`_render_gov_nags` 另一支才看 kind,而且明寫只認 `kind == "warned"`,`ok` 不會混進去)。
severity: clean
blocking: 否
引句:「return (not r["hard"]) and r["kind"] in ("warned", "ok") and not r.get("token") and not r["detail"]」
file: `scripts/lumos:3721`

13. **新增 `dict | dict` 合併語法違反本專案自訂的 Python ≥3.8 相容承諾(major)**:同一支 `scripts/lumos` 檔案在 10425 行明寫「★不用 `Path.is_relative_to()`★——那是 Python 3.9+,本專案宣告 ≥3.8」,但 r2 這行新增的 `{"kind": ...} | pinned.get(n, {}) | {...}` 用了 PEP 584 的 dict `|` 合併運算子,同樣是 CPython 3.9.0 才加入、3.8 不存在(`dict.__or__` 未定義,執行期會丟 `TypeError`)。本機沒有 python3.8/pyenv/docker 可裝來直接重現丟例外,標「未能重現」並依規定降級(blocker→major);但語言事實明確、且與同檔案既有的禁用慣例直接衝突,信心仍高。
severity: major
blocking: 是
引句:「{"kind": "計劃連結", "contract": None, "files": []} | pinned.get(n, {}) | {"kind": "計劃連結"」
file: `scripts/lumos:17696`(對照禁用慣例:`scripts/lumos:10425`)

14. Codex `--claim` 超時提示語建議手跑 `lumos dispatch-lens --status` 來「看它算不算得出來」,但讀 `cmd_dispatch_lens_status` 的實作只是讀既有武裝檔的 meta.json 印剩餘席次,完全不執行 `--claim`、不重算也測不出逾時風險——這與 Claude 分支(`cmd=rng` 或 `--spec {spec}`,重跑的就是真正逾時的那個指令)語意不對稱,操作者跑完 `--status` 看到正常狀態反而可能誤以為問題已排除。此點與獨立跑的「外家」複審員(`r2-外家finder.md`)判定一致,且工作樹已有未進本 patch 的修法把 `cmd` 改成 `--arm ... 重新武裝(--status 只看剩幾席、不重算)`。
severity: minor
blocking: 否
引句:「TIMEOUT_NOTE.format(what="(Codex 席:--claim)", cmd="--status", n=10)}}, ensure_ascii=False))」
file: `scripts/hooks/claude/dispatch-lens-hook.py:79`

## 小結

- 上一輪六個修法點(①~④)的驗收行為全部如預期,(a) 四項與 (b)(c)(d)(f)(g) 皆乾淨。
- 唯一貨真價實的 blocker 是 delguard `--json` 的 `degraded` 欄位寫死 `False`,沒接新算出來的 `_partial`——違反函式自己宣告的降級契約,已用重現腳本驗證;另有一條 major(dict `|` 合併違反 ≥3.8 承諾,未能在本機直接跑 3.8 驗證,依規定降級標記)。
- 兩個 minor(delguard 時間式誤判、Codex 提示語建議錯指令)嚴重度較低,附帶標記信心。
- 工作樹在審查期間已經對 blocker 與其中一個 minor 做了未進本 patch 的即時修補,詳見報告開頭「流程性提醒」。

max severity: blocker
