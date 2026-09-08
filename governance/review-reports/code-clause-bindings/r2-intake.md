# code-clause-bindings r2 — 收貨與編排者機械重現(末輪驗收)

preflight-4: n/a(code 迴圈)

三席驗收 r1 的 13 條折入(全量 r2-snapshot.patch 1221 行、delta 960 行)。

## 收貨三道

| 席 | quote-check | refcheck | seat-check |
|---|---|---|---|
| 單reviewer-sonnet | ⚠ 16 句 1 句 <10 字(在「修好」段,不掛 finding) | ok 11 | 觀測 |
| 架構對齊-sonnet | ✅ 全數錨定 | ok 15 | 觀測 |
| 外家否決-codex(sol/xhigh) | ✅ 全數錨定 | ok 8 | 觀測 |

★外家席第一次用 terra 跑到一半「Selected model is at capacity」沒交報告(逐字稿 r2-codex-raw-attempt1-capacity.txt),退 sol 重跑;兩次它都實跑到同樣的繞法。★
★13 條 r1 折入,三席各自驗:單reviewer 12 條「修好」、f1 判「修了但引入新洞」;架構席前輪六條五條「已對齊」;外家席前輪四條兩條「修好」、兩條「修了但引入新洞」。★

## 編排者自己重現的

| # | 席 | 我怎麼驗 | 結果 |
|---|---|---|---|
| g1 同一行「真條款 + `[S9] 範例`」仍讓閘 FAIL | 單 N1 blocker、Codex #3 | 純函式餵那一行 → S9 defined/untagged | **HIT** → 反引號內容整段遮掉再掃(位置不變) |
| g2 我改 reference.md 時掃進別人同檔未提交的一段 | 單 N2 major | `git show 0e1faab -- reference.md` 有 scope/ 那列 | **HIT**(第五型第四次)→ index 反向套用那段、工作樹保留 |
| g3 INV_TAG_RE 量詞對所有標記放寬成 `*` | 單 N3 minor | 讀正則 | HIT → 只對 manual 放寬 |
| g4 計劃讀不到我這步軟 FAIL、G3 硬擋 rc2 | 架 minor | 讀兩段碼 | HIT → 回 "abort",呼叫端 return 2 |
| g5 docstring 寫四種跳過實際五種 | 架 minor | 數分支 | HIT → 跟 g6 一起回到四種 |
| g6 loop 編號 code 開頭沒連字號 → `_roster_kind` None → 跳過 | Codex #1 major、獨立審計附註 | `_disposal_clause_step(loop_id="codefake")` → skip | **HIT** → None 當設計審(fail-closed) |
| g7 `[manual:!!!!]` 四個標點算靠人 | Codex #2 major | 純函式 → manual | **HIT** → 要含實字 |
| g8 `- [ ] [S1] 甲` 勾選框不在白名單 → 零條款照過 | Codex #4 major | 純函式 → undefined;閘印「0 條全標」ok | **HIT** → 勾選框算定義行;有 [SN] 但零條定義改成擋 |
| g9 handoff 索引建不起來印「0 條」 | Codex #5 minor | 讀碼 | HIT → 講原因 |
| g10 「索引建不起來 fail-closed」半句沒測試 | 獨立審計 | grep 測試 | HIT → 補 cg-l |

翻紅釘六個全翻紅:不遮反引號(6)/ code 開頭都跳過(2)/ 標點也算實字(2)/ 零條款照過(2)/ 勾選框不認(5)/(g10 的分支本身就是新測試釘住)。折完 clause 58、disposal 101、handoff 54、lint 174、guard 308 全綠。

## 折入(10 條,去重後)

g1(單 N1、Codex #3)/ g2(單 N2)/ g3(單 N3)/ g4(架 m1)/ g5(架 m2)/ g6(Codex #1、審計附註)/ g7(Codex #2)/ g8(Codex #4)/ g9(Codex #5)/ g10(獨立審計)。
★INVARIANT★ 文字隨語意再改(勾選框、零條定義擋),獨立審計在 g10 之前已判「真合約」;文字本輪的補充只是把碼裡已有的行為寫全。

## 我判錯、被席位糾正的

- r1 我把「範例行不算定義」改成「lead 行上所有 [SN] 都算」——正好把 blocker 換了個殼;正確做法是把反引號內容整段當文字遮掉。
- 我在同一天第四次把別人未提交的段落掃進 commit——這次是文件檔,因為我只對兩個大檔做了 hunk 分類。★以後 `git add` 任何被別 session 碰過的檔都要分 hunk。★
- 我對「格式看不懂」的預設是「不算條款」,外家席證明那等於「不認得的寫法全放行」。

## 留痕紀律

★這一份在按下記帳之前寫完★。carrier=單reviewer-sonnet(最高 blocker、算人數)。

## 處置

10 條全部折入,accepted 為空(輪內有 blocker)。r3(上限)派全新席只掃 r2 折入的 delta 與驗收。

(本檔在此之後不再修改。)
