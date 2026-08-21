# doctor-run事件-std r1-s2 對抗審計 — LENS: ledger 語意與讀寫路徑

角色:外部第三方審計,對象=`/tmp/doctor-run事件-std-r1.md`(spec,尚未落地實作——`scripts/lumos`/`scripts/test_lumos.py` 均未見 `doctor-run` 字樣)。逐條核對 LENS 六問,對真代碼逐行印證。

## 逐問核對

1. **dedup 鍵對 doctor-run 的效果**——`cmd_gov` dedup 鍵 `k = (r["commit"], frozenset(r["nodes"]), r["gate"], r["kind"], r.get("token", ""))`(scripts/lumos:3060,實際行見下)。doctor-run 事件 nodes 恆 `[]`、gate/kind 恆固定、無 token 欄 → 同一 commit 兩次 `--ci` 產生的兩筆事件鍵完全相同,`gov` 顯示折成 1 筆;但 `_append_governance_log`(scripts/lumos:421)是純 append,原始 `.governance-log.jsonl` 每次都多寫一行。**spec 的敘述屬實,已核。**
   - 引句:「dedup 鍵含 commit,同 commit 多次 --ci 在 gov 顯示上折成一筆」— 與 scripts/lumos:3060 `k = (r["commit"], frozenset(r["nodes"]), r["gate"], r["kind"], r.get("token", ""))` 行為一致。severity: n/a(核實通過,非缺陷)。

2. **`note` 是否真是 mapper 讀的欄位**——`.governance-log.jsonl` 的 mapper 在 `cmd_gov` 內:`"detail": d.get("note", "")`(scripts/lumos:2995)。spec 已標注★light r1 M1★改成 `note`,與此行完全對應,**確認修正正確**、非 `detail`。
   - 引句:「"nodes": [stem(x) for x in d.get("nodes", [])], "detail": d.get("note", "")」severity: n/a(核實通過)。

3. **`gates=<n>` 計數定義是否無歧義**——所有 check-* gate 字面值(check-r/check-s/check-e1/check-e2/check-e3/check-k/check-j)在 `run_doctor` 內都以固定字串 append 進同一個 `gov_events` list(scripts/lumos:785-1308 一路可查)。"issues" 亦是同一函式作用域內、緊跟在 `_append_governance_log` 呼叫後就拿來印總結的那個既有計數器(`print(f"...⚠ 發現 {issues} 個 issue...")`,scripts/lumos ~1332)。"gates=<本次有事件的 check-* gate 數>" 可機械翻成 `len({e["gate"] for e in gov_events if e["gate"].startswith("check-")})`,計算式唯一、無第二種合理讀法。判定:**不含糊**。

4. **`--stats` 的「不同 nodes 值數」是否經 union-empty 規則印 n/a**——`_render_gov_stats` 逐列 `a["nodes"].update(n for n in r["nodes"] if n)`,doctor-run 的 `nodes` 恆 `[]` → 集合恆空 →`nd = "n/a" if not a["nodes"] else str(len(a["nodes"]))` 印 `n/a`(scripts/lumos:2934,2953-2954 一帶)。**與 spec 聲稱一致,已核實。**`_STATS_NODE_SEMANTICS` 確實不需加項(該表只用於「值非空但語意非圖譜節點」的情況,如 anchor-approve;doctor-run 是空集合,不進這條分支)。

5. **`gov <node>` 定位過濾是否排除 doctor-run**——`if node: q = stem(node); ded = [r for r in ded if q in r["nodes"]]`(scripts/lumos ~3057-3059)。doctor-run nodes 恆 `[]`,`q in []` 恆假 → 自動排除,**確認「無需特判」的說法正確**。

6. **消費者是否斷言 gov 輸出行數、是否真的跑了 doctor --ci**——查 `t_gov_query`(test_lumos.py:2939)與全部 `t_gov_stats_*`(2976-3163):皆用 `_stats_fixture`/手寫 jsonl 建假帳,**沒有一個呼叫真正的 `doctor --ci`**,故本次改動不會讓它們多出一行意外資料。唯一真的跑 `doctor --ci` 的是 `t_governance_log_write`(2914-2933,即「gov-log: 純 doctor 不寫」所在函式):第一段斷言 `"check-r" in log.read_text(...)`(子字串檢查,非行數/相等比對)不受新增 doctor-run 行影響;第二段驗證純 `doctor`(無 `--ci`)不寫檔——此路徑完全不觸發 doctor-run 事件(spec 明確限定只在 `ci=True` 分支加),**不會破**。`t_gov_stats_gate_drift`(3047)掃描全檔 `"gate": "字面值"` 要求 ⊆ `_KNOWN_GATES`:spec 同時在 `run_doctor` 加字面值 `"doctor-run"` 且在 `_KNOWN_GATES` 補項,兩處同步,**不會使漂移測試翻紅**;「動態 gate 寫點恰 1 處」釘子也不受影響(doctor-run 是字面值,非 f-string/變數)。

## light r1 兩條修正的存活複查

- blocker(「隱藏」無機制定義):現文字已明確限定「`gov` 時間軸(非 `--full`)」+「stats 要看得到它才能當棘輪分母」,對照 `cmd_gov` 實際結構(`ded` 同時餵給 `--full` 逐筆迴圈與 `_render_gov_stats`,唯有非 `--full` 的 else 分支才是聚合列印),過濾動作只能落在該 else 分支內部、不能上移到 `ded` 本身(上移會連 `--full`/`--stats` 一起濾掉,與「stats 照列」自相矛盾)。文字雖未把「濾在 else 分支內、不濾 ded」寫死成一句話,但用「(非 --full)」+「stats 要看得到它」兩個限定詞已经把落點釘住,經與 scripts/lumos:3042-3078 的 if full/else 結構比對,**唯一自洽的實作位置就是 else 分支內部**——不構成新的 blocker。
- major(欄位名 `detail`→`note`):已於第 2 點逐行核實修正正確。

## 未被光輪處理但值得記錄的觀察(均非 blocker/major)

- 目前 `.governance-log.jsonl` 只在「有事件」時才被 touch;`--ci` 是 pre-push hook(scripts/hooks/pre-push:148)與 CI workflow(.github/workflows/ci.yml:25)的既有步驟。加了 doctor-run 之後,**乾淨的一次 `git push` 從此每次都會在本機留下一行未 commit 的 `.governance-log.jsonl` diff**(先前 0 issues 時完全不動檔案)。這是設計本身要的效果("乾淨 run 因此恆有一筆可寫"),機制上不會壞任何東西——`.governance-log.jsonl` 已在 `_BOOKKEEPING_FILES` 白名單(scripts/lumos:10299),code-loop 的簿記豁免通道(scripts/lumos:14113-14124)本就是為這種「pass 後又多寫一行簿記」情境設計,可正確吸收;但 spec「實務隱患」段只寫了「效能——每次 --ci 多一行」,沒點名這條「每次 push 後工作樹必髒」的行為改變。判定 minor(non-blocking,建議寫入節點但不擋)。
- 時間軸「N 筆(近 X 天)」的結尾統計行讀 `len(ded)`(既有行為,doctor-run 加入後這個數字會恆比非--full 畫面實際印出的行數多,因為 doctor-run 列會被過濾掉不印卻仍計入 len(ded))。此落差在 advisory 折疊上本來就存在(既有機制,折疊本就會讓印出行數 < len(ded)),doctor-run 只是再貢獻一種同類落差,不算新引入的缺陷類別,minor/non-issue。

## 結論

逐問核對六題全部與真代碼吻合,light r1 的 blocker/major 兩條在現文字下均已正確收斂、未見復發或新等級缺陷;本輪(ledger 語意/讀寫路徑視角)未發現 blocker 或 major。

findings: blocker=0 major=0 minor=2
