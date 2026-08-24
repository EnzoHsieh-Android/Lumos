# selfaudit-loop-v5 r3 架構對齊審查

角色:只判「跟本 repo 既有做法一不一樣」,不判設計本身對不對、不重審 v1-v6 已經吵過的內容。
範圍:被審 `/tmp/selfaudit-loop-v5-r3.md`(243 行),只看 v7 delta——rsync 排除層/stale 釋放配額/窄鎖 NB/orphan 分家/旗標清單修正/pathspec 補 FAIL/四函式切縫/選序固定/d4。五道對照題逐一列在下方,對照物開頭列出。

---

## ① make_sandbox 加參數 vs repo 對既有函式擴充的慣例

**對照物:`scripts/scenario_probe.py:80` 現行 `def make_sandbox(src):`——單一必填位置參數,現有兩個呼叫端。**
`scenario_probe.py:210`(`run_probe`,派工用的 AI 安全沙盒,docstring 明記 2026-08-23 事故後補的三道 push 隔離)
與 `scripts/test_lumos.py:443`(沙盒測試)都只傳一個 `src`,不知道任何排除清單。

repo 對「擴充既有函式/呼叫路徑」有明文寫死、且實際驗過的規矩——`docs/lumos-toolchain-knowledge/Projects/design-loop重設計_實作計畫.md:31`:
「相容鐵則:任何中間 commit 上,現行 design-loop／code-loop 的既有呼叫(不帶新旗標)行為一字不變——每包附一條
「舊呼叫不變」回歸斷言」,`Verification/2026-08-04_design-loop重設計落地T1-T7.md:15` 記錄「相容鐵則逐包驗訖
(零新參舊呼叫 rc0 無新鍵)」——這不是我方推論出的慣例,是本 repo 自己在另一次擴充既有派工/CLI 機制時立下、
且已跑過回歸測試驗證的規矩。`scripts/lumos` 對既有函式加欄位也幾乎清一色走 `xxx=None`/`xxx="預設值"`
保留舊行為(grep 到的例子:`cmd_contracts(env, rel=None)`、`cmd_self_audit(env, rel, model="sonnet", date=None)`、
`cmd_canary(env, kind, auditor=None, ...)` 等十餘處簽名)。

spec(第 71-76 行)只寫「make_sandbox 加排除清單參數,rsync 就不抄 `governance/review-reports/`…」,通篇沒有一個字
提到:新參數要不要給預設值(例如 `exclude=None` 對應空清單)讓兩個既有呼叫端維持原行為、需不需要同步改這兩處、
有沒有比照「相容鐵則」寫一條「舊呼叫不變」回歸斷言。對照 repo 自己驗過的先例,這是明確的規格空白,且波及的
是安全關鍵機制(AI 沙盒的 push 隔離,2026-08-23 剛出過事故),不是無關緊要的內部函式。判 major。

引句:「make_sandbox 加排除清單參數,rsync 就不抄」

---

## ② LOCK_EX|LOCK_NB 引 _goldset_lock——引用對得上實碼嗎

**對照物:`governance/eval/refresh_labels.py:52-73` 的 `_goldset_lock`。**
鎖檔=`str(goldset_path) + ".lock"`(獨立鎖檔,非鎖資料檔本身);模式=`fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)`;
失敗行為=`OSError`→raise `BlockingIOError`,呼叫端(`cmd_apply`/`cmd_repin`)接住後印一行錯誤訊息、rc 非零、資料檔不動。
grep 全 repo `.py` 檔,這是唯一一處生產用 `flock`(另一處是它自己的測試 `t_refresh_atomic_and_lock`),spec 稱其為
「repo 唯一先例」查證屬實。

spec(第 119-122 行)寫「鎖模式照 repo 唯一先例 `_goldset_lock`(refresh_labels.py):LOCK_EX|LOCK_NB 快速失敗,
搶不到=本輪跳過 selfaudit 段、印一行」——鎖旗標(`LOCK_EX|LOCK_NB`)逐字對得上實碼;spec 只宣稱借用「鎖模式」
(非阻塞快速失敗這個行為特徵),沒有宣稱照搬 `_goldset_lock` 整段回收邏輯——兩邊失敗後的下一步本來就不同
(`_goldset_lock` 失敗是整支 CLI rc 非零退出,selfaudit 失敗是「跳過本輪這一段、其他工作照跑」),spec 沒有把
兩種不同情境混講成「一樣」,是誠實的借用而非誤引。測試段(第 156 行)「flock:兩進場用兩個行程/兩個 open 控柄
模擬…樣板照 t_refresh_atomic_and_lock」也與 `scripts/test_lumos.py:21289-21316` 的真實測試手法(獨立 file handle
持鎖+另開 subprocess 撞鎖)吻合。

補充查證:此點在上一輪(v5-r2,`governance/review-reports/selfaudit-loop-v5/r2-arch.md` 對照物③)曾被判 major
(「flock 用法未引用 `_goldset_lock`、鎖是否阻塞式未寫明」);v7 delta 已明確補上引用與行為描述,該缺口已解。
本輪查無新的不對齊,判對齊。

---

## ③ orphan 這個新 kind 與三本事件帳的 kind 命名風格一致嗎

**對照物:`docs/.governance-log.jsonl` 實際 kind 值集合 = {approved, cap-reached, converged, degraded, green, passed, ran, skipped, warned};
`docs/.canary-log.jsonl` = {caught, missed, none};`docs/.ci-log.jsonl` 本身沒有 `kind` 欄(用 `conclusion`,如 success)。**

spec 自訂的週帳 `kind ∈ started/done/fail/abort/stale/orphan/nag`(第 110-116 行)在字面風格上與既有兩本帳一致:
全小寫、單一英文字或連字號複合詞,無大寫、無底線、無中文混入。`orphan` 本身就是這個模子出來的字。唯一可挑剔的
是既有兩本帳的值多半是「過去式動詞/形容詞」(approved/degraded/warned/caught/missed),`orphan` 是名詞——但這條
「詞性」規則在既有帳本身就不嚴(`green`、`none` 都不是過去式動詞),而 selfaudit 自己這本新帳裡 `fail`/`abort`
也是原形動詞、`stale` 是形容詞,非過去式——本來就是混合詞性的本地集合,orphan 加入不算破壞既有一致性。

判對齊,⚠(此判準本身缺乏機械可驗的硬規則——既有帳的 kind 命名從未寫成正式規範,「詞性」這把尺是本審查員推論
出來的,不是查得到的成文慣例,信心中等)。

---

## ④ d4 的寫法照決策四欄慣例嗎——對 frontmatter 實檔驗

**對照物:`skills/lumos-project-notes/reference.md:700` 明文——「`context` / `alternatives_considered` / `why_chosen` /
`trade_offs` 是業界 ADR 標準四欄位」,741-744 表格規定「重大決策」(定義含「流程變更:三階段流程 / 工作流順序 /
API 契約版本」)四欄位皆「✅ 必填」,756-757 行 Claude 填寫義務第 1、2 條:「不可省略只填 content+valid」/
讀到舊筆記只有 content+valid 但內容是重大決策要主動詢問補齊。這條規矩在圖譜裡不是邊角料——`Systems/core-invariant-baseline.md`、
`Projects/先問世界_存量掃描裁定.md` 都把「ADR 四欄位」列為 lumos 對比同類工具的領先特徵。**

被審檔案自己的 frontmatter 就是最直接的對照組:d1(第 19-24 行)、d2(第 25-30 行)、d3(第 31-36 行)三條全部帶
`context:` + `why_chosen:` 兩個獨立鍵,唯獨 d4(第 37-40 行)只有 `content:` / `id:` / `decided:` / `valid:` 四鍵——
`context`(d1/d2 授權字面只蓋「兩輪皆敗」)與 `why_chosen`(裁定理由=越界代表自動鏈無法安全繼續)原本該分開寫的
內容,被整坨塞進 `content:` 一句話裡,靠一個土法「裁定理由=」字樣頂替正式的 `why_chosen:` 欄位。

d4 本身是「範圍刀越界算不算修復鏈失敗」的政策邊界決定,屬於表格定義的「流程變更」重大決策,文中還自己註記
「Enzo 可否決」——分量上並不比同檔 d1-d3 輕,卻是四條裡唯一 ADR 欄位不完整的一條,同一份 frontmatter 內部就
不一致,直接違反 reference.md 的「重大決策四欄必填」明文規則,也違反本檔自己前三條決策已經立下的先例。判 major。

引句:「d4:範圍刀越界視同修復鏈失敗、落 pending 停自動重試」

---

## ⑤ 配額公式寫法 vs repo 既有 spec 用公式還是用例子

**對照物:spec(第 115-116 行)「配額=quota−(本週 started 行數−其中終局為 stale 的行數)」是代數式寫法。**
查 `docs/lumos-toolchain-knowledge/Projects/*_計劃.md` 同類技術規格,公式化寫法在本 repo 是既有慣例、非孤例:
`Projects/hook必看召回修復_計劃.md`「`final = pins + free[:min(top, quota)] + rescued(≤N)`」、
`Projects/檢索PPR邊權_計劃.md`「融合式=R'=R+w_P·P 線性疊加」與「該臂兩庫皆不劣於 −0.02 且至少一庫勝出 >+0.02」、
`Systems/reversibility-governance-ledger.md`「dedup 在讀時做,key = (commit, frozenset(nodes), gate, kind, token)」。
這些都是把邏輯寫成公式/類程式碼運算式直接嵌進中文散文,而非改寫成純敘述性例子。

本篇的配額公式與這個既有寫法風格一致(中文散文中嵌代數式、變數名照程式碼命名),不算不對齊。判對齊。

---

## 不對齊清單

| # | 位置(spec) | 對照物 | 嚴重度 |
|---|---|---|---|
| 1 | spec:74(段落第 71-76 行) | make_sandbox 加排除清單參數,未講是否給預設值保既有兩呼叫端(`scenario_probe.py:210`／`test_lumos.py:443`)行為不變;repo 有明文且已驗過的「相容鐵則」先例(`design-loop重設計_實作計畫.md:31`、`Verification/2026-08-04_design-loop重設計落地T1-T7.md:15`) | major |
| 2 | spec:37-40(d4 決策條目,frontmatter) | d4 缺 `context:`/`why_chosen:` 兩鍵,同檔 d1-d3 皆有;違反 `skills/lumos-project-notes/reference.md:700-744` 明文「重大決策 ADR 四欄必填」規則 | major |

**不對齊共 2 條,其中 major 2 條。**
