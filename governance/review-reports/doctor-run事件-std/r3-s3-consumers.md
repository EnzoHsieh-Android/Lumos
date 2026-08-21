# doctor-run事件-std r3-s3 對抗審計 — LENS: consumers/CI/hooks

角色:獨立第三方審計,對抗但憑事實。對象=`/tmp/doctor-run事件-std-r3.md`。★核對過:r3 文件與 `governance/review-reports/doctor-run事件-std/r2-snapshot.md` 逐字 diff 為空(K=2:連續第二輪 delta=0)。範圍=dr-common 指定四問(display-loop-only filtering、stats 斷 count==2、note 鍵、已清推導)+ 自行獵洞,聚焦 consumers/CI/hooks。

## 現況核對(先確認機制仍未落地,審的是設計不是代碼)

`grep -n "doctor-run" scripts/lumos scripts/test_lumos.py` 全部零命中——本案仍是純 spec,`scripts/lumos`/`scripts/test_lumos.py` 未改動。以下四問對照的是「設計文字」與「現有真代碼結構」是否自洽。

## 四問覆核

**① display-loop-only filtering(過濾只作用在顯示迴圈,不動 `ded`)**:讀 `scripts/lumos:2958-3143`(`cmd_gov`)確認結構——`ded` 在 3021-3029 dedup 建好後同時餵給 `full`/else 的印出分支(3036 起)與 3140 `_render_gov_stats(_raw, ded, ...)`。`_is_advisory`(3038-3040)只認 `kind=="warned"`,doctor-run 設計 `kind="ran"` 天生不會被摺疊吃掉,若不特判會直接落進 else 分支底部的逐行 `print` 而印出——與設計文字「摺疊與逐行印兩處各自 `continue`」描述的落點完全對應,兩處 `continue` 缺一,doctor-run 就會漏印或漏濾。結構性核實通過。

**② stats 斷 count==2**:`_render_gov_stats`(2910-2973)的 `ded` 桶計數來自形參 `ded`(未被過濾動過的同一份列表),`agg[gate]["ded"] += 1` 對每個去重列都會執行——若未來實作誤把過濾前置到 `ded` 本身,`agg["doctor-run"]["ded"]` 會是 0,測試 3 的 `== 2` 直接失敗,不會被「gate 名有沒有出現」矇混過關。dedup 鍵 `(commit, frozenset(nodes), gate, kind, token)`(3029-3030)对两次不同 commit 的 `--ci` 會給出不同鍵 → 兩筆都存活入 `ded` → raw=2/ded=2,與斷言一致。核實通過。

**③ note 鍵**:`.governance-log.jsonl` 的 mapper(2992-2994)讀 `d.get("note", "")`(不是 `detail`)→ 塞進 `detail` 顯示欄。設計文字要求事件寫 `"note": "issues=<n> gates=<m>"`,與 mapper 讀鍵一致。測試段落已無殘留 `detail`(r1 外家 #2 修正存活)。核實通過。

**④ 已清推導**:doctor-run 事件 `nodes` 恆空,`node` 縮限模式的過濾 `q in r["nodes"]`(3032-3034)對空 list 恆 False,doctor-run 天然被排除於 node 視角外,無需特判——與設計「node 縮限模式下 nodes 為空本就不命中」一致,且與 `_STATS_NODE_SEMANTICS`(2907,只列 `anchor-approve`)不需為 doctor-run 新增條目的說法一致(`nd = "n/a" if not a["nodes"] else ...`,2938-2944,doctor-run 恆落 n/a 分支)。核實通過。

## consumers/CI/hooks 面獨立獵洞(不重複 r1/r2 已核對的 Q1-Q5)

- **CI workflow**(`.github/workflows/ci.yml:25`):`python scripts/lumos doctor --ci` 在 ephemeral runner 上執行,workflow 全程無 `git status --porcelain`/`git diff --exit-code`,新增的 doctor-run 行不會被推回、不會使任何 job 翻紅。
- **pre-push**(`scripts/hooks/pre-push:148`):`if "$PY" "$GRAPHCTL" doctor --ci; then exit 0; fi`——rc 判斷完全基於 `run_doctor` 既有的 `issues`/`strict` 邏輯(scripts/lumos:1330-1334),doctor-run 事件只 append 進 `gov_events` 清單、不觸碰 `issues` 計數或 return 值,設計文字「不改判定、不改 rc」核實成立。
- **anchor approve 這條獨立寫者**:`cmd_anchor_approve`(scripts/lumos:10113-10151)直接呼叫 `_append_governance_log(v, [{"gate": "anchor-approve", ...}])`,與 `run_doctor` 完全獨立的呼叫點——新增的 doctor-run 插入點(`run_doctor` 內、既有 `_append_governance_log` 呼叫之前)不會被 anchor approve 路徑觸發第二次,兩個寫者互不干擾。
- **`_BOOKKEEPING_FILES`/code-loop 簿記豁免**(scripts/lumos:10299-10300、14113-14126):白名單是**檔案路徑**粒度(`docs/.governance-log.jsonl`),不是內容/事件類型粒度,新增一種 `gate` 字面值不改變這條路徑本身在不在白名單裡——豁免通道對 doctor-run 事件自動適用,無需改動。
- **`t_gov_stats_gate_drift`**(scripts/test_lumos.py:3047-3062):新寫入點 `"gate": "doctor-run"` 是字面值(非 f-string/變數),不會讓「動態 gate 寫點恰為 1 處」的釘子多出第 2 處;只要 `_KNOWN_GATES` 同步加入(設計已列待辦),漂移測試自動吃到,無需額外改動測試本身。
- **`_COCHANGE_DEFAULT_EXCLUDE`**(scripts/lumos:11148-11154)、`_scaffold_project` 的 vault `.gitignore` 範本(scripts/lumos:8968-8969)——都是路徑層級排除,不因 `.governance-log.jsonl` 內多一種事件類型而改變行為;vault `.gitignore` 放錯層(蓋不到 `vault.parent` 的實際落點)是既有落差,r1-s3 已核實非本案引入、判 minor、記入 `[[Issues/寫下風險當成處理風險]]`,r2-s3 已再次核對維持未變,本輪第三次獨立核對仍維持同一結論、未發現升級證據。

## 判定

四問(display-loop-only filtering / stats count==2 / note 鍵 / 已清推導)逐一對照真代碼結構複核,全部核實成立;consumers/CI/hooks 面(CI workflow、pre-push rc、anchor-approve 獨立寫者、code-loop 簿記白名單、gate 漂移測試、co-change 排除清單)逐項獨立獵洞,未發現任何新的 blocker/major。唯一相關的既有 minor(vault `.gitignore` 放錯層 → 消費專案帳本恆髒的量級被文件低估)在 r1-s3 已核實、r2-s3 已覆核維持不變,本輪(r3,K=2 第二輪 delta=0)第三次獨立核對仍然維持,不新增、不升級。

**沒有 ≥major 殘留。**

findings: blocker=0 major=0 minor=0(本輪範圍內新增數;既有 r1-s3 minor 1 項未變、未重複計入)
