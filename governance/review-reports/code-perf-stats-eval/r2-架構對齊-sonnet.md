severity: clean

**1. 結構與位置跟鄰居一樣嗎?** 一樣。
- 新 Verification 放在 `Verification/` 底下,檔名是日期加主題,跟 `Verification/2026-10-23_macrobench實機端到端.md` 同形。
- 章節順序是白話段、`## 怎麼量`、`## 結果`、`## 沒驗的`。對照 `Verification/2026-10-23_Android驗證收據第零階段試跑.md:18-49` 的 `## 怎麼跑的`、`## 結果`、`## 不涵蓋`,結構一致,只是章名不同。`## 沒驗的` 在 `Verification/2026-08-22_受波及合約測試真跑閘落地.md` 等檔已有先例。
- 研究資料放 `governance/research/macrobench/2026-10-24-perf-stats/`,跟 `2026-10-23-lab-tablet/` 同層同命名。這個目錄的檔已經在 git 裡。
- 功能節點補 `verified_by` 一條,接在既有清單最後,跟前面五條同格式。
- 計劃保留在原本的 `Projects/Android效能判定統計化_計劃.md`,沒有另開新檔。

**2. 寫法跟鄰居一樣嗎?** 一樣。
- Verification 的開頭欄位是 `type/status/date/valid_under/revalidate_when/tags/plan_refs`,跟 `Verification/2026-10-23_macrobench實機端到端.md:1-17` 逐欄一致。`valid_under` 用清單,該檔也是清單。`Verification/2026-10-24_Android記憶體與穩定性實驗室驗收.md:1-6` 用單行字串,兩種寫法都已存在。
- 結尾 `REVISIT:日期 一句要做什麼` 獨立一行,跟 `Verification/2026-10-23_macrobench實機端到端.md` 末行同形。
- 計劃裡 `RETIRE-IF:` 一條一行,連寫三條,有先例:`Projects/探針隔離與清理收斂_計劃.md` 有 5 條,`Projects/代碼審修復穩定性試行_計劃.md` 等有 3 條。每條都帶「看到什麼就撤」的條件,這點跟 `Projects/Macrobenchmark退步提醒_計劃.md:90` 一致。
- `PRIOR-ART:`、`REVISIT:`、`## 待辦` 的位置沒變。`REVISIT:2027-03-31` 夾在待辦清單中間,`Projects/Android記憶體與穩定性驗收_計劃.md:81` 也有 REVISIT 放在段落中間的做法。
- 連結都用 `[[Verification/…]]` 和 `[[Projects/…]]` 的 wiki 連結寫法。

**3. 有沒有引入第二種做法?** 沒有。
- 新 Verification 沒有為量測另開檔案格式或位置,實驗腳本指向 macrobench-lab,數字出處指向 governance/research。
- 計劃把待辦從六條改九條,仍是同一份有編號清單,沒有拆成新節點。
- 新 Verification 沒有綁測試名,但它的主旨是規則評測而非功能,`Verification/2026-10-23_macrobench實機端到端.md` 的綁測試(`t_macrobench_real_tablet_lab`)只是該篇的內容。這不是另一種做法。

不對齊共 0 條,其中重大 0 條
