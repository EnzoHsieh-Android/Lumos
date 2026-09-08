# code-review-yield r1 — 收貨與編排者機械重現

分級 standard(1 席 + 架構對齊 + 外家否決)。被審的是「審查有沒有用記帳」的實作(寫側拒收+機器數、--refuted-set、讀側漏斗、report-normalize)。
★這批改的是「量審查自己」的帳——被審材料本身就是記帳的規則,席位抓到的每個洞都直接等於一條「編排者可以把數字做好看的路」★。

## 收貨三道

| 席 | quote-check | refcheck | seat-check |
|---|---|---|---|
| 單reviewer-sonnet | ✅ 全數錨定(5/5) | ok 7 | 觀測 |
| 架構對齊-sonnet | ✅ 全數錨定(5/5,純格式重出後) | ok 14 | 觀測 |
| 外家否決-codex(gpt-5.6-terra xhigh) | ✅ 全數錨定(6/6) | ok 6 | 觀測 |

**架構席重出一次,三處全是格式、一個字內容沒改**:①a2 標題裡的「severity: <值>」片語會被我自己剛上線的拒收偵測當殘留——請它改用反引號包住(這正是新規則第一次咬到真報告);②a4 引句跨兩行,改引一行;③a5 引句把 code-loop SKILL(「不碰引句」)和 design-loop SKILL(「不動引句與圍欄」)兩句混在一起,改逐字引其中一份。
三份報告存檔後都先跑 `lumos report-normalize`,單reviewer 與外家席一次就是正規化格式;報告來源是逐字稿最後一則訊息(通知本文會把 `<`/`>` 轉成 HTML 實體,錨不到)。

## 編排者自己重現的(≥major 一律自己查過才折;全部 HIT)

| id | 席 | 怎麼試的 | 結果 |
|---|---|---|---|
| f1 | 單reviewer blocker | 純函式餵 `- minor 問題:文件裡有錯字` 與 `這是個 non-major 的調整` | **HIT**:兩行都被當殘留;`- major / blocking: 是`、`- MAJOR` 也殘留(這兩個本來就該擋) |
| f2 | 單reviewer major | 假 vault 只放 3 筆 blocked 事件、0 輪 reported、0 逃逸,跑 `gov --stats` | **HIT**:整段不印,「記帳被寫側擋下」也不印 |
| f3 | 單reviewer major | intake 只有 ``` 圍欄裡一列 `\| a1 \| 範例 \| MISS \|`,記帳 `--refuted-set a1=…` | **HIT**:rc0,範例列被當真重現紀錄 |
| f4 / c2 | 單reviewer minor + 外家 major | `re.compile(r"(?<![A-Za-z0-9])甲(?![A-Za-z0-9])").search("甲乙 MISS")` | **HIT**:True;換 `\w` 邊界後 甲/甲乙 False、a1/a10 False、a1/a1 True |
| f5 / c3 | 單reviewer minor + 外家 major | 同一秒三筆 canary/blocked(兩筆同 note、一筆不同 auditor)餵 gov --stats | **HIT,比席位說的更糟**:三筆全折成「1 次」——token 只有 ts,連不同 auditor 都分不開 |
| a1 | 架構 major | 到沒有圖譜的目錄跑 `lumos report-normalize rep.md`;對照 `prose-lint` | **HIT**:rc2「找不到知識圖譜」;prose-lint rc0 |
| a2 | 架構 major | `grep -c` 那串宣告行正則 | **HIT**:5 處逐字複製 |
| c1 | 外家 blocker | 純函式餵 `severity: clean\n總結: severity: blocker\n` | **HIT**:issues []、reported 0、floor clean——白名單可夾帶 |
| c4 | 外家 minor | 餵 `﻿severity: clean` | **HIT**:兩處殘留、normalizer changed=0 修不了 |
| c5 | 外家 minor | `--refuted-set " ,"` | **HIT**:rc0、落帳 [] 且沒驗 intake |
| c6 | 外家 minor | `--findings 3` 對 reported 2 | **HIT**:rc2 但治理帳 0 筆事件 |

去重:c2 併 f4、c3 併 f5(同一個洞,兩席獨立抓到;外家席判得比同門席重——CJK 邊界與同秒碰撞它都判 major,我採高)。

## 折入的十四條與修法

- **f1** 破折號型殘留只在等級字後面接「行尾或分隔符」才算:`- major`、`- major / blocking: 是` 擋,`- minor 問題:…`、`non-major 的調整` 放。
- **f2** `gov --stats` 那段的條件多一項:只有 blocked 事件、沒有任何一輪 reported 也印(不然撞牆三次、一輪都沒補記=整段消失,正是留事件要防的盲點)。
- **f3** intake 比對改走 `_visible_lines(keep_fenced=False)`——跟拒收偵測同一套可見性,圍欄裡的格式範例不算重現紀錄。
- **f4/c2** 整字邊界改 `(?<!\w)…(?!\w)`(Unicode 字元類),甲 不因 甲乙 命中。
- **f5/c3** 三個 blocked 事件的 note 尾端帶 8 碼隨機事件碼;gov mapper 的第 5 鑑別子改 ts+note——同秒、同 note 也分得開。
- **a1** `cmd_report_normalize` 拿掉 `env`,dispatch 搬到 vault 閘之前(跟 fold-check/prose-lint 同層);加測試「沒圖譜、不帶 --vault 也能跑」。
- **a2** 抽 `_SEV_DECL_LINE_RE` 當獨立宣告行的唯一定義,五處共用;加測試釘「那串正則字面值全檔只出現一次」。
- **a3** 事件 kind 從 `rejected` 改成 `blocked`——anchor/code-loop 表「這次動作被擋」都用 blocked,canary 不另造同義詞(★這條本來想附理由放行:canary 有自己的 kind 值域;但輪內有 blocker,code 迴圈規則 accepted 必空,而且改名成本是零★)。
- **a4** 兩個參數補 help。
- **a5** code-loop SKILL 原句「編排者改席報告等於改證據」補上「唯一例外=report-normalize --write 的純格式搬移」,不讓新段落跟舊禁令並列打架。
- **c1** 總結句豁免加條件:句裡提到的等級都 ≤ 檔級宣告才豁免;更高就當殘留、檔級行缺一律不豁免。
- **c4** 三個入口都剝 BOM;normalizer 剝掉算一處修改、寫回不帶 BOM。
- **c5** `--refuted-set` 空項 rc2(不准當 none 混過);錯誤訊息講明理由裡別用半形逗號。
- **c6** findings 多於 reported 也留 blocked 事件;`gov --stats` 的擋下次數分三類印。

## 翻紅釘

fold 前(自己的 11 個突變):殘留偵測拿掉方括號/讀側去重拿掉/檔首規則拿掉/intake 整字改子字串/findings≤reported 拿掉/_report_severities 又數圍欄/去重鑑別子拿掉/粗體殘留拿掉/refuted-set 必帶拿掉/拒收整個拿掉——10 個翻紅;**「S 算式少了 R」沒翻紅**(fixture 全是 R=0 的輪),補了一輪 R=1 的帳(N=2、M=2、R=1 → S=1)才翻紅。
fold 後(對每條折入各造一個突變,scratch 複本跑四支新測試):f1 放回舊寫法 / f2 拿掉 _rej 條件 / f3 又看圍欄 / f4 邊界改回 ASCII / f5 token 只用 ts / c1 總結句無條件豁免 / c4 BOM 不剝 / c5 空項又靜默跳過 / c6 不留事件——**9 個全翻紅**(a1 由「沒圖譜也能跑」那條測試釘;a2 由「字面值只出現一次」釘)。

## 寫側新規則第一次咬到既有測試:8 支 17 條翻紅,全是 fixture

full suite(fold 前)4646 綠 17 紅:5 支既有測試的假報告沒有檔級行或宣告行數少於 `--findings`(t_codex_s2_orchestrator/t_finding_kind_ledger_and_stats/t_refute_verdict_ledger_and_stats/t_m1_codeloop_r2_fixes/t_panel_probe_retired);`_sevrep` 助手加 `n` 參數產 n 條宣告;另外 3 支是文件守衛:commands/05 新列格數、四份文件的「68 個頂層命令」→69、report-normalize 缺「什麼時候用」。**這些不是新規則錯,是新規則正確地把「報 3 條卻沒任何宣告行」的假報告擋下來。**

## 留痕紀律

★這一份在按下記帳之前就寫完了★。

## 處置

14 條**全部折入,accepted 為空**——輪內兩席 blocker,依 code 迴圈規則一律折。

(本檔在此之後不再修改。)
