preflight-4: ran

# 精簡改道設計審第 1 輪前掃

2026-10-04；前掃唯讀檢查未定義詞、引用、內部矛盾、工具／skill 語意。`lumos refcheck` 為 missing 0 / out_of_range 0；`prose-lint` 無模糊詞命中；`pitfalls --check` 有實務隱患節；`spec-gate` 判高風險，五條均有人工驗法，兩支相依回歸綠。這些結果不等於設計審 PASS。

| id | 修改前的問題 | 凍結前修正 |
|---|---|---|
| P1 | 「沒有被反例覆蓋的跨入口承諾不放進當輪修補範圍」可讓已採信缺陷被縮出修補，但未交代原處置閘。 | 改成未驗不宣稱已修；採信缺陷仍走原處置閘，無法驗證須標原因。 |
| P2 | 「每次開工與收尾由 skill 入口導向本表」和目前使用者層安裝版缺試行入口不符。 | 寫明 repo skill 有入口，第2案前核對實際載入版本，未同步時直接讀計劃。 |
| P3 | S4 原句無條件要求原席驗收，但 repo reference 只在既有續談條件允許時才做。 | S4 加上既有續談條件，不更動新席與正式席位規則。 |

三點由獨立唯讀前掃提出、於派正式審查前修正；前掃不是正式席，也不以此消除後續新發現。精簡版凍結快照 `r1-snapshot.md`，SHA-256 `6a6d89f829b4b0f0c66fed47b9daf76621fc9fb306223e790baacbb4a2afc097`，151 行。

## 正式席收貨與處置

五席加架構席均讀同一凍結快照，收齊後才把報告存入本目錄。`report-normalize`、`quote-check --spec r1-snapshot.md` 與 `refcheck --repo .` 對六席均通過。`seat-check --dispatch r1-dispatch.json` 對若干席報一份材料沒有逐字點名，屬觀測告警；六席都以快照原句提出可錨定發現，沒有拿其他席報告當佐證。Claude 外家否決另有 `r1-external-veto.txt`，其個別 finding 格式及一處短引句不合正式收貨，故只作額外診斷、不記正式席帳；其中重複領號及生效紀錄可達性仍納入下表處置。

| 去重 id | 席報告與重現（HIT） | 折入位置 |
|---|---|---|
| entry | 正確性、邊界、整合、回退四席同報：`rg -n '五次修復試行\|修復穩定性試行' /Users/enzo/.agents/skills/lumos-code-loop/{SKILL.md,reference.md}` 回 1，實際載入版無入口；repo 版有。HIT。 | `AGENTS.md` 必讀指路，計劃生效前核對接手會談能讀到入口；回退保留指路並讀 stopped 狀態。不從未放行工作樹全域安裝。 |
| verify_link | 整合席：舊 `verified_by` 只指 2026-10-03 PASS，與改道 pending 混淆；原 frontmatter 核對 HIT。 | 舊 PASS 留正文歷史，frontmatter 改指本篇 pending 驗證；正式結果再更新本篇。 |
| claim | 整合席：intake 先寫而五格直到收尾才補，崩潰後可重用第2格；S1 舊順序 HIT。 | 首輪派工前先在五格占位並記 loop/intake/時間；未成功派工仍保留格。 |
| issue_refs | 整合席：第1案交接要求三篇 open Issue，原 `related` 僅一篇；核對 HIT。 | 補兩篇 Issue 連結，三項阻擋入口可從圖譜找到。 |
| concurrency | 併發席與外家：不同 worktree 各讀自己的五格表可重複領號；目前無全域互斥，HIT。 | 限單一指定登記工作樹與明確接手者，轉移前先記交接並核對；發現並行或重號立即停止，資料不作改善結論。沒有聲稱機械互斥。 |
| clock | 併發席：派工前記事會早於派工成功，甚至完全沒派出；第1案曾缺精確首派時刻，HIT。 | 占位時間與成功首派時間分開；後者才算耗時起點，缺成功紀錄記未知。 |
| owner | 架構席：`lands_in` 原列代碼審以外兩個 Systems，會被 `spec-gate` 當落點及相依回歸來源；工具與欄位核對 HIT。 | `lands_in` 只留 `Systems/pitfalls-code-loop`，歷史探針／測試血緣仍留原驗證與 Issue。 |

六席原始報告 10 條，去重為上列 7 項，全部有文字或欄位處置，沒有編排者重現不到而丟棄的 finding。外家其餘 minor 也有去向：不合資格占位案在回顧分列；接手但排除的工作追加理由；「儀器版號」以基準提交辨別，缺值未知。這些都是量測限制，不把案1與後續四案合算改善率。`entry` 的使用者層副本仍未同步，因此本輪設計即使 PASS，實際第2案仍要按計劃生效條件核對入口；本次不代替那個驗證。
