# r1 邊界席(極端輸入與失敗路徑代言人)

blocking 判準:照現文實作會立即產生錯誤行為或破壞宿主指令載重語意、或核心規則未定義=blocking;品質/噪音衰減可上線後調參=非 blocking。

**F1|major|blocking:是——fail-open 完全沒寫,advisory 失敗會炸關鍵路徑指令**
段落:實務隱患。引句:「回滾:兩處各為一段 advisory 輸出,`git revert` 即回,無狀態殘留」——隱患清單唯獨沒有「advisory 內部例外不得改變宿主 rc/輸出」。loop next 的 rc 是載重語意(scripts/lumos:5745-5750;test_lumos.py 21 處消費其 --json 與 rc),B 掛點在 mkdir 之前(:9605-9608),search 一顆未接住的例外就讓「不擋照建」變成建檔失敗——與「全 advisory 不擋」自相矛盾。

**F2|major|blocking:是——「CJK 切詞」未定義,spec 對自己開的處置票跳票**
引句:「切詞規則進 spec 且測試各給一例;0 筆時印『無既有節點』」——本文件就是那份 spec,但切詞規則只有一句:「等」是開放列表(dref-v4 的 -v4、auto- 前綴、送審前 CJK 前綴都不在列),「CJK 切詞」無演算法。自己標的★真隱患★處置在同一份文件裡缺席=內部不一致。佐證:scripts/lumos:1953、docs/.canary-log.jsonl 實帳編號(code-標註刷新/dref-v4/auto-2026-08-30/impact-鏡頭機械化 皆實存;__seq0 僅讀側合成鍵 :11067)。

**F3|major|blocking:是——片語單命中抑制 OR 召回,拿事故本尊實測就漏報**
引句:「已裁 A 案、拒加閘)已存在,搜尋一打就中」——只對一個方向成立。實測 spec 管線的自然查詢 `search "impact 鏡頭機械化"`:片語在 送審前impact鏡頭機械化_計劃 帶空白命中 1 篇→多詞回退永不觸發(:2174-2176 一命中即 break)→檔名相似度 0.90 的 impact鏡頭機械化_計劃 整篇被藏,且輸出是「共 1 篇候選」的正常結果、無可起疑訊號。標題只差空白的近名節點正是 A/B 要接的球,現行召回策略在這個形上結構性漏接。佐證:scripts/lumos:2151-2185。

**F4|major|blocking:否——0.6 門檻:高頻合法對與事故對同分段+Verification 81% 觸發率**
引句:「v2/-std/實作計畫 等變體是日常;advisory 不擋 + 相似門檻收在檔名級,誤報成本=多讀一行」——實測:Projects/ 131 檔 8515 對中 ≥0.6 共 57 對,最高分段 0.83-0.92 幾乎全是合法工作流對(X_計劃↔X_實作計畫 8 對 0.85-0.92),與事故對(0.90)同分段、檔名層不可分離;Verification/ 156 檔 127/156=81% 有 ≥0.6 鄰居(日期前綴天然墊高)。「多讀一行」漏算頻率維度——天天亮的燈就是 546 型麻痺,兩段自打。

**F5|major|blocking:否——「未來自主迴圈消費」指向 vault 錯位的消費者,誠實行會變系統性說謊**
引句:「A 的 --json 鍵供未來自主迴圈 prompt 消費(它開迴圈也該看)」——實查:orchestrator-prompt.md 內「loop next」0 命中,且其所有 lumos 呼叫走 `--vault __SCRATCH__/kg`(scratch canary vault,近空)。未來若照此行接上,related_nodes 搜的是 canary vault 不是專案圖譜,恆印「無既有節點」——誠實行在此消費者上恆為假陰性,精準複製本案要防的「不知道存在」。佐證:governance/autonomous_loop/orchestrator-prompt.md:8。

**F6|minor|blocking:否——auto-* 日期形編號切詞後=垃圾前 5 筆**
實測 `search "auto 2026 08 30"`:整串 0 命中觸發 OR,逐詞覆蓋 2026:381/385、08:270、30:141,前 5 筆被日期 token 洗出。今天無人對 auto-* 跑 loop next(auto-* 是 wrapper 結局帳),但 spec 未把日期形排除出切詞規則。

**F7|minor|blocking:否——「每次 loop next」無視同函式 N=1 抑噪先例,且 rc2 出口沉默未定義**
cluster_hint 明文「只在 N=1 提…避免噴無效噪音」(:5889-5890),A 卻每輪重印;首呼叫忘帶 --tier 走 rc2 硬擋不經 emit(:5795-5798),spec 未定義 advisory 掛在哪些出口。

**F8|minor|blocking:否——「同詞幹」未定義詞**
lumos 代碼庫 0 命中、無 stemmer,B 第二判準無法實作無法驗收。

查證後無發現(抑噪):① --json 消費者 21 處全逐鍵取值,加 related_nodes 不破壞;② lumos new 無 headless 呼叫端,stderr-當-失敗風險今天不存在(但 spec 未指明 B 印哪個 stream);③ 引用數字抽驗全對(五道檢查/掛點/385 篇/0.59s(重測 0.66s)/546 前例);④ search 零命中 rc=0、vault 缺失在 dispatch 前就 rc2(:17081-17084),F1 暴險面在「vault 在但 advisory 代碼自己炸」。

最嚴重 severity:major;blocking 共 3 條(F1、F2、F3)。

severity: major
