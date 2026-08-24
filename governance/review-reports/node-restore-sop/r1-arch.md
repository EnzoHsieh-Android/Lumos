# 架構對齊審查報告——/tmp/node-restore-sop-r1.md(節點還原SOP_計劃 r1)

## 問一:分層與放置

**不對齊(major)。**

材料落地件明白寫著把整份 SOP 塞進單一 commands 子檔:

引句:「`skills/lumos-project-notes/commands/08-節點還原.md`(新檔,現在還不存在,本案交付物):SOP 操作全文(本節七步的指令化版本)。」(/tmp/node-restore-sop-r1.md:99)

但同層兩個處理「多步驟流程」的既有子檔,示範的是相反的分層方式——commands/0N 只放薄表格+一句話指到「完整流程在別處」,不把敘事本體搬進來:

- skills/lumos-project-notes/commands/05-設計審查迴圈.md:3:「白話:一份設計 spec 在動手實作前,讓幾個不知道脈絡的審查員輪流挑毛病……完整流程在 lumos-design-loop skill;這裡只列「什麼時候敲哪個」」
- skills/lumos-project-notes/commands/06-代碼審與推送.md(全檔 16 行純表格,無敘事段落,guard 深規指到 reference.md)

而本專案裡真正收納「敘事型方法論」的既有落腳處是 reference.md——例:reference.md:996-1075〈自足性審計〉〈變體 B:圖譜×程式碼交叉審計〉,整段是多階段散文程序,與被審 SOP 的「步驟 0–6」文類完全同構;reference.md:625-681〈重生守衛(Check J)〉是 SOP 步驟 4 直接呼叫的機制,本身就住在 reference.md。

commands/0N 的鄰居(05/06)一致地把「怎麼做」的完整敘事甩給 skill 或 reference.md,自己只留查表;本案反著做。**應考慮把七步 SOP 本體放進 reference.md(可與既有〈重生守衛〉相鄰或合體),commands/0N 只留一行指標**。下一個要在 commands/ 塞長方法論的人,會在兩種先例間猜。

## 問二:命名與格式

**不對齊,兩處(皆 minor)。**

1. **檔名編號撞號**——材料兩處(:99、:102)指定新檔 `commands/08-節點還原.md`,但 08 已被佔用:commands/ 目前恰好 01–08 八個子檔(08-自動跑的.md),無縫接號;新檔應為 09-。還牽動 INDEX.md「二、八類子檔」表(精確對應 01–08 八列)與 SKILL.md 進場節引用(:102)——全篇一致地用錯號。
2. **探針題落點比同層計劃籠統**——材料只寫「情境探針 ≥3 題……過線=會照 SOP 進場」(:103),沒指名既有探針語料檔 governance/scenarios/commands.jsonl(scripts/scenario_probe.py:169 預設路徑)。對照同層計劃精度(from-scratch重生守衛_計劃明列 t_check_j_regen/t_check_j_git;連結缺失補全_計劃明列 t_link_candidates)——判 minor 非 major(可能是計劃筆記省略,留落地填)。

INDEX 路由行雙表寫法(:100)與現有 INDEX.md 一、二兩張表分工一致,無問題。

## 問三:第二種做法?

**git 考古 vs from-scratch M3——刻意分工,對齊,非重複造輪。** d3 context 明文承認撞點(:35)並留回頭條件(:36);M3 本身標「選配、後續」。兩者對齊、有留痕的分工邊界。

**最小骨架 MOC——同一套機制,對齊。** lumos init 的 _scaffold_project(scripts/lumos:9447-9459)本就會建 MOC/index.md(type: moc);既有慣例「>5 篇建 MOC」(reference.md:1185-1188、SKILL.md:81)同一資料夾機制。SOP 步驟 0 是填這個已存在骨架檔的正文,不是另立索引機制。

**合約候選 vs guard scaffold→bind→audit——引用既有機制,對齊。**「合約候選」一詞已有先例(Projects/連結缺失補全_計劃.md:79「合約候選清單(收斂提名,候選≠已標——蓋章走 guard 流程)」)。

**⚠ 判不準,交編排者:PRIOR-ART 遺漏 reference.md 既有〈變體 B:圖譜×程式碼交叉審計〉。** reference.md:1038-1040 已有以「接手陌生專案」為觸發詞的既有機制:「標準自足性審計需要『主對話脈絡』當比對基準。沒有脈絡時(定期巡檢、接手陌生專案、審很久沒動的大節點),改用程式碼當真值,兩階段、每節點各派一個乾淨 Sonnet agent」——與本 SOP 立案動機字面重疊,但材料的「內部既有零件」清單(:65)完全沒提,也沒交代互補(Variant B=已有筆記的事後查核/SOP 步驟 1–4=從零到有的產出)還是該合併。交編排者裁。

## 結論

不對齊共 3 條,其中 major 1 條(commands/08 全文放置 vs 既有「薄表+指到 reference.md/skill」分層慣例)。minor 2 條(08 撞號;探針題落點精度)。⚠ 判不準 1 條(PRIOR-ART 未核對變體 B)。三處「第二種做法」嫌疑(git 考古 vs M3、骨架 MOC、合約候選)均判對齊。
