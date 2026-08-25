# 架構對齊審查報告——code-cascade-reminder r1

審法:對照 `scripts/lumos` 現有 doctor 檢查(E1/E2/E3/S/S2/W)實碼、`git show 12a745f^` 還原 patch 前版本核對行號、實跑 `t_doctor_cascade_reminder`(9 個 `check()`,全綠)與 `lumos doctor`,並逐檔核 `governance/rel-cascade/*.jsonl` 與 `governance/review-reports/cascade-reminder/r1-*.md` 五席審計原始檔。

## 1. code 側:E4 對照 E1/E2/E3 慣例

對齊:E4 直接呼叫 `warn_soft`、不經 `_soft_list`。`_soft_list`(scripts/lumos:853)是 S/S2/E1/E2/E3/K 共用的「逐節點列舉、封頂 8 篇、印『還有 N 篇』」框架,E4 的輸出設計是單一聚合訊息(不逐帳本列舉),不落在 `_soft_list` 的適用場景,不算漏用。

severity: minor｜blocking: 否｜判準:乾淨時整段不印(不含 section 抬頭)與 E1/E2/E3/S/S2 一律印 `section()`+`ok()` 的行為確實不同,但已在同一段程式碼上方寫明理由,且 Check W(scripts/lumos:1420 `if _nudge: section("W", ...)`)已是同檔既有的「無事完全靜默」先例,E4 並非孤例新創。
引句:「刻意全靜默設計:乾淨時整段不印(不佔版面)」

severity: minor｜blocking: 否｜判準:輸出順序落在 E2 之後、E3 之前,即「E4」的字面編號比它實際印在畫面上更晚出現的「E3」還大,對照著讀 doctor 輸出的人容易以為漏看了一段。程式碼註解引用的理由(避開某測試字串切片窗)經核對並不精確——`t_doctor_soft_sections_truncate_by_default` 切的是 `[S]`到`[E1]`的窗口,E4 早已印在 `[E1]` 之後,擺在 E2 後或 E3 後都不會落進那個窗口;真正需要避開的窗口(`e3seg = r.stdout.split("[E3]")[1].split("[H]")[0]`,scripts/test_lumos.py:1894)才會因為插在 E3 之後而被牽動,註解點名的測試對不上真正的風險點。
引句:「避開 `t_doctor_soft_sections_truncate_by_default` 的 [S]..[E1] 字串切片窗」

severity: minor｜blocking: 否｜判準:`gov_events` 全庫 14 處 append 裡,check-s/s2/e1/e2/e3/k/j/r 一律每個違規節點各留一筆、`nodes` 填實際 stem;E4 是唯一一個 `kind: "warned"` 的 check-* 卻用 `nodes: []` + 聚合 `note` 字串的形狀(唯一同形態的是不同 kind 的 `doctor-run` 彙總事件)。這在語意上站得住——cascade 帳本本來就不是圖譜節點,沒有 stem 可填——但這個「唯一例外」沒有在註解或計劃裡被指名為刻意偏離,只泛稱「12 處無一例外都呼叫」,沒提形狀本身也不一樣。
引句:「"nodes": [], "note": f"unseen={len(_casc_unseen_ts)} broken={_casc_broken}"」

## 2. docs 側:計劃 v2 / Issue 結案 / 兩篇驗證 / Systems KEY 互相對照

對齊:修法 A/B/C/D 的處置在 Issue 結案橫幅與計劃 v2 d5 兩處講法一致(A 供 supersede 指路採納、B 供 doctor E4 採納、C 兩張舊欠帳判完採納、D 留給原 Issue 另議不入本案)。
引句:「D 照 Issue 原文另議,不入本案(已死節點引用面,規模不同)」

對齊:計劃 v2 PRIOR-ART 段點名的每個行號(`scripts/lumos:8103`/`8162`/`8288`/`486`/`496`/`950-956`)逐條核對 `git show 12a745f^:scripts/lumos` 的版本,全部精確命中對應函式/區塊,沒有錯位或事後才對得上的巧合。

severity: minor｜blocking: 否｜判準:CASCADE-EMPTY(翻案零 typed 鄰居→帳本永久零判定、E4 會長鳴)這個已知縫,只寫在 `Verification/2026-08-25_連鎖佇列軟提醒落地.md` 一處(KEY 與 revalidate_when 都有附回頭看條件,合鐵則4);但計劃 v2 自己的「實務隱患」清單(status 已是 done)、Issue 結案橫幅、`Systems/lumos-cli-read` 的 KEY 摘要三處都沒提到這條——同一件事只單點記載,是這個專案自己記過的「知識同步散落會漏」那種缺口,不影響現有測試,但下一個只讀 Systems KEY 或計劃本身的人會漏接。
引句:「CASCADE-EMPTY(翻案無 typed 鄰居)的帳本會永久零判定」

## 3. 兩篇驗證筆記宣稱抽驗(對 repo 現況)

verified 對齊:「blocking↔severity 綁定矛盾率 0/18」屬實——五席報告(s1:4 條/s2:3 條/s3:6 條/arch:3 條/ext:2 條,合計 18 條有 severity 標記的 finding)逐條核對,major 一律配 blocking:是、minor 一律配 blocking:否,無一條反過來;blocking 加總剛好 11,與計劃 v2 引的「18 審項/blocking 11」一致。
引句:「blocking↔severity 綁定矛盾率 0/18」

verified 對齊:「九斷言」屬實——`t_doctor_cascade_reminder` 內恰好 9 個 `check(...)` 呼叫,直接執行該函式(對現有 repo 狀態)9 條全綠,無需修補。
引句:「[test:t_doctor_cascade_reminder] 九斷言」

severity: major｜blocking: 是｜判準:「E4 亮起→熄燈」這個大方向屬實(現跑 `lumos doctor` 完全不出現 E4 段落,三張帳本確實都已判完),但同一條 KEY 附帶的計數「prune 1/confirm 2」與誠實邊界段的「三筆判定 by=ai」跟 `governance/rel-cascade/*.jsonl` 實際內容對不上——三張帳本合計是 4 筆 transition(1 pruned + **3** confirmed,全部 by=ai),不是 3 筆(1+2)。差的那一筆是 `c-20260804063546-eb0fe2fc.jsonl` 裡同一張帳本本身就有兩筆判定(1 pruned + 1 confirmed),疑似把「3 張帳本」直接算成「3 筆動作」漏算了這張雙動作的帳本。這正是這個專案自己記過的「審計紀錄條數必逐檔數」那種失誤模式,在一篇 status: pass 的驗證筆記裡重演。
引句:「三張單全判完(prune 1/confirm 2,by=ai 走不可信欄)」

severity: minor｜blocking: 否｜判準:`decision-supersede` 的 T1b 白話指路行在 CASCADE-EMPTY(零 typed 鄰居)分支下也會無條件印出,告訴使用者「上面列的每個 NEIGHBOR 都要回頭判」,但上一行明明剛印過零鄰居;這個情境正好是驗證筆記另外承認的已知縫(帳本永久零判定),但白話指路句本身在這個分支會講出「去看上面每一個」卻上面什麼都沒有的矛盾指示,文件沒有點名這個子情境。
引句:「上面列的每個 NEIGHBOR 都要回頭判」

## 總結

最嚴重 severity:**major**(3.3「E4 亮起→熄燈」內的計數子宣稱與帳本實況不符);blocking 共 **1** 條。其餘 5 條均為 minor / blocking:否,屬「解釋不完整」或「說法散落單點記載」層級,不擋。