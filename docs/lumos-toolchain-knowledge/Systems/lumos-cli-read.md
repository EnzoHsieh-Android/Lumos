---
type: system
status: done
created: 2026-06-26
updated: 2026-07-15
self_audit: sonnet/2026-06-26
tags:
  - type/system
  - status/done
summary: |-
  FLOW:任一讀指令 → find_vault(從 cwd 往上找 docs/*-knowledge 或 standalone vault root) → load_vault(掃全 .md、解 frontmatter+wikilink) → Env(notes/by_stem/edges) → 各 cmd_* 純讀印出 → return 0(查無/正則錯=非0)
  KEY:read/traverse 12 原語全建在記憶體 Env 之上(notes 字典 + 雙向 edges + by_stem 索引);純讀、不寫檔、無副作用,與 7 個寫入原語(set/append/new/decision-* …)互斥
  KEY:進場三步入口固定 search(定位節點) → context(掃脈絡,頭部突顯 ⚠ 合約) → contracts(查硬合約 invariant 改=breaking),CLAUDE.md 規定動既有系統第一個工具呼叫必須是 lumos 而非 grep/Read/DB
  KEY:doctor 是全圖權威巡檢(4 檢查 orphans/unresolved/verified_by 雙向/plan_refs 意圖鏈 + 同名守衛 + frontmatter lint + Check T/R/H;Check P 失效檔案認領(inline-code 路徑指死碼);Check E1 失效背書(verified_by 指向 stale/fail 驗證→死背書)+ Check E2 建在被推翻決策上(決策 valid:false+ended → M2 共用 typed 索引查連入來源、updated 早於 ended → 落後邊;decision_refs 精化只標指到那條;M3 帳本抑制 terminal ts>=ended 跳過=主/補網不重報)+ Check E3 意圖鏈斷義(decision_refs 指翻案決策+dangling 浮出);關係層皆軟提醒);與 lint 分工——lint 只看單篇 node-local、predicts pre-push 會不會擋
  KEY:search 預設排除 fenced+inline code(對齊 doctor 連結抽取慣例,--code 才含)、大小寫不敏感 substring、--regex 切正則;結構化查詢走 contracts/decisions/stale 而非 search
  KEY:讀指令屬「專案層」——以 cwd find_vault 鎖定本專案 vault(不受同名 vault 影響);對比 install/bootstrap 的「機器層」(全域 lumos + user-scope skills)
  DEP:scripts/lumos load_vault/Env/find_vault｜extract_contracts(contracts/context 共用)｜parse_decisions(decisions/stale)｜status_of(links/map/stale 標狀態)
  KEY:stale --candidate 無 --match 直接 rc2 拒絕(反直覺限制:即使給了 --candidate 沒帶 --match 也拒,避免列全 vault 變噪音);--candidate --match <詞> 才有效
  TEST:scripts/test_lumos.py(t_-prefixed Python 回歸,非 doctor Check T 認的 C# xunit)
related:
  - "[[Systems/lumos-cli-write]]"
  - "[[Systems/lumos-cli-lifecycle]]"
decisions:
  - content: 讀寫原語嚴格分軌——12 個讀指令純讀記憶體 Env 不碰檔;一切 frontmatter 寫入走 set/append/decision-* 等寫入原語(走 atomic_write_verify:寫 tmp → re-parse 自驗 + lint 無新指紋 → atomic rename)
    context: 直接手改 frontmatter 會繞過寫後自驗與鐵則防護(YAML 格式爆、ghost 節點、裸合約),且讀指令若兼寫會讓「查脈絡」帶副作用
    why_chosen: 讀路徑零副作用才能放心當入口反覆掃;寫路徑集中過 atomic 自驗閘,任一步敗則 tmp 丟棄原檔不動,保證圖譜永遠可解析
    decided: 2026-06-26
    valid: true
  - content: doctor(全圖權威)與 lint(單檔快檢)分工——lint node-local 不掃 repo 比 doctor 快、寫完一篇立刻自驗、error 即 pre-push 會擋的同類;doctor 跑全圖跨節點完整性 + [test:] 存在性
    context: 每寫一個節點都跑全圖 doctor 太慢、回饋慢;但單檔檢查看不到跨節點完整性(orphans/雙向同步/意圖鏈)
    why_chosen: 兩段式——寫節點當下用 lint 拿快回饋(預測 pre-push),收尾再用 doctor 跑全圖權威巡檢;push 前 pre-push 仍兜底再擋一次
    decided: 2026-06-26
    valid: true
  - content: 讀指令以 cwd find_vault 鎖定「專案層」vault(往上找 docs/*-knowledge 或 standalone vault root),不受多專案同名 vault 影響;與 install/bootstrap 的「機器層」分軌
    context: Obsidian CLI 的 vault= 只吃資料夾 basename,多專案都叫 docs/knowledge 會撞名;lumos 改以 cwd 往上找消歧
    why_chosen: cwd-based 定位讓任何專案子目錄直接 lumos <cmd> 都鎖到正確 vault,機器層工具(全域 lumos/skills)則一次裝好共用
    decided: 2026-06-26
    valid: true
verified_by:
  - "[[Verification/2026-07-14_relguard_E1失效背書]]"
  - "[[Verification/2026-07-14_relguard_E2建在被推翻決策上]]"
  - "[[Verification/2026-07-15_主網M1_決策穩定ID]]"
  - "[[Verification/2026-07-15_主網M2_typed-edge索引]]"
  - "[[Verification/2026-07-15_主網M3_cascade帳本]]"
  - "[[Verification/2026-07-15_主網M4_觸發與連鎖]]"
---
# lumos-cli-read

`scripts/lumos` 的 **read/traverse 核心原語**(12 個)——圖譜的查詢與遍歷面。對既有系統動手前,CLAUDE.md 規定第一個工具呼叫必須是這組 `lumos` 讀指令,而非 grep / Read / Explore / DB(code 讀不出「為什麼 / 邊界 / 哪些是不可改合約 / 驗過沒」)。

源起:CLI 核心非日報觸發(read 原語是 lumos 工具鏈的地基能力,非某日報 gap/inspiration 衍生的單一功能)。

## 共同地基
所有讀指令先 `find_vault`(從 cwd 往上找 `docs/*-knowledge` 或 standalone vault root)→ `load_vault` 掃全 `.md`、解 frontmatter + wikilink → 建記憶體 `Env`(`notes` 節點字典、`by_stem` 名稱索引、雙向 `edges` = (out_e, in_e))。各 `cmd_*` 在此 Env 上純讀、印出、`return 0`(查無資料 / 正則無效等 → 非 0)。**全程不寫檔、無副作用。**

## 12 個原語(對應 cmd_* / scripts/lumos)
- **進場三步(入口固定順序)**
  - `search <詞> [--path Systems] [--regex] [--files-only] [--code]`(`cmd_search`):全文搜尋 frontmatter+body,大小寫不敏感 substring。**預設排除 fenced + inline code 區塊**(對齊 doctor 連結抽取慣例),`--code` 才含;`context` 標記命中區域(★INVARIANT★/KEY/fm:欄位/body)。職責=自由文字,結構化查詢走 contracts/decisions/stale。
  - `context <節點> [--brief]`(`cmd_context`):節點 + 鄰居 summary 壓縮索引(MemPalace closet)。**頭部直接攤出 ⚠ 合約**(extract_contracts);`--brief` 只給 meta + summary 首兩行 + 鄰居名單(壓 token)。
  - `contracts [節點]`(`cmd_contracts`):合約登記簿,列 `★INVARIANT★`(改=breaking)/ `★DEBT★`(可改);**只認 KEY 行前綴標準格式**;★INVARIANT★ 顯示綁定的 `[test:]`,未綁=⚠(doctor Check T 會擋)。
- **巡檢 / 完整性**
  - `doctor [--ci]`(`cmd_doctor`):全圖權威健康巡檢——4 檢查(1/4 Verification orphans、2/4 unresolved wikilinks 破連結、3/4 verified_by 雙向同步、4/4 plan_refs 意圖鏈)+ 同名守衛 + frontmatter lint + Check T(★INVARIANT★→測試綁定)/ Check R(可逆性回退)/ Check H(漏標可逆性軟提醒,僅 --ci 掃 diff)+ Check P(失效檔案認領:inline-code 路徑指向已不存在檔案)+ Check E1/E2/E3(關係層:E1 失效背書 verified_by→stale/fail、E2 建在被推翻決策上 決策翻案而 typed 連入來源未跟上——鄰居有 decision_refs 時精化為只標指到那條、且 M3 rel-cascade 帳本有 terminal 判定(ts>=ended)即跳過＝主/補網不重報、E3 意圖鏈斷義 decision_refs 指向的決策已翻案+dangling 浮出;皆軟提醒)。`--ci` = `--strict` + 無色彩,且是 `.governance-log.jsonl` 唯一寫者。
- **遍歷 / 關聯**
  - `links <節點>` / `backlinks <節點>`(`cmd_links`,reverse=True 即 backlinks):列連出 / 連入節點 + 狀態。
  - `map <節點> [--depth 2]`(`cmd_map`):鄰域樹狀展開,`↺` 標已出現過(防環)。
  - `export --folders <…> [dot|mermaid]`(`cmd_export`):導出指定資料夾子圖為 graphviz dot / mermaid。
- **決策 / 重驗 / 概覽**
  - `decisions [節點] [--superseded]`(`cmd_decisions`):讀單篇 ADR 決策;`--superseded` 全 vault 掃 `valid:false` 被推翻的決策。
  - `stale [--match <字串>] [--candidate]`(`cmd_stale`):`status:stale` 清單;`--match` 掃 valid_under + revalidate_when 命中(含 Archive);`--candidate --match <關鍵字>` 聚焦活躍 Verification 的 revalidate_when(排 Archive)= 「改 X 時該重驗哪幾篇」。bare `--candidate` 或空 `--match` 直接 rc2 拒絕(避免列全部變噪音)。
  - `recent --days N`(`cmd_recent`):近 N 天修改節點(mtime 排序)。
  - `stats`(`cmd_stats`):各資料夾節點數 + total。

## 關鍵設計
- **讀寫嚴格分軌**:這 12 個全純讀;寫入走另 7 個原語(set/append/new/archive/decision-add/decision-supersede/self-audit),經 `atomic_write_verify`(寫 tmp → re-parse 自驗 + lint 無新指紋 → atomic rename,任一步敗則 tmp 丟棄原檔不動)。詳見寫入原語節點。
- **doctor vs lint 分工**:doctor 全圖權威(跨節點 + [test:] 存在性);`lint <節點>` 單檔 node-local 快檢,predicts pre-push 會不會擋。寫節點當下 lint,收尾 doctor。
- **專案層 vs 機器層**:讀指令以 cwd `find_vault` 鎖本專案 vault(不受同名影響);install / bootstrap 是機器層(全域 `lumos` + user-scope skills),不在本節點範圍。

## 已知限制
- `search` 對 fenced/inline code 內字串預設看不到(需 `--code`);要查「散文裡剛好提到 ★ 字面」與「真合約標記」靠 `contracts` 的 KEY 行錨定區分,不靠 search。
- 同名節點:`find` 取第一個並印 `⚠ 同名筆記` stderr 警示;消歧靠資料夾前綴命名(`docs/<slug>-knowledge/`)。

## 相關
- 操作表權威:`CLAUDE.md`(入口三步 + 標籤規範)、`skills/lumos-project-notes/SKILL.md`(23 子命令全覽:讀取 12 + 寫入 7 + 安裝/生命週期 4)。
- 實作落點:`scripts/lumos` `cmd_search`/`cmd_context`/`cmd_contracts`/`cmd_doctor`/`cmd_links`/`cmd_map`/`cmd_export`/`cmd_decisions`/`cmd_stale`/`cmd_recent`/`cmd_stats` + `load_vault`/`Env`/`find_vault`。
- 回歸測試:`scripts/test_lumos.py`(Python t_-prefixed)。
- 對稱寫入原語見 [[Systems/lumos-cli-write]];安裝 / 生命週期見 [[Systems/lumos-cli-lifecycle]];`lumos --help` 為現行權威。

## 近期修正
- 2026-07-11 export html 視覺化七項優化（使用者提案全採）：①標籤 LOD（重要度排名×相機距離預算,hover/選中恆顯）②驗證摺疊預設開（Verification 隱藏、母節點標 ✓N 徽章、選中母節點自動現形）③單擊容差（pointerup 位移<5px 兜底,修 3D 旋轉吃 click）＋2D/3D 切換（numDimensions+鎖旋轉）④搜尋 Enter 飛至最佳命中開面板（前綴>包含,同級取重要度）⑤「只看合約」chip（合約節點+其 verify 目標）⑥面板返回鈕（navStack;搜尋跳轉不入棧=已知取捨）⑦時間軸生長回放（節點 date/created,拉桿+▶ 播放）。真機驗證：Chrome 擴充+Playwright 雙路實測全過;t_export_html +10 骨架斷言。


- 2026-07-11 export html 視覺化修：節點面板關閉鈕 `#close` 被後繪的 `#phead`（透明背景）蓋住，真實點擊被攔截而程式呼叫正常——Playwright elementFromPoint 實測定位，補 `z-index:3`。教訓：疊層 UI 的可點性要用真實命中測試驗，不能只驗 handler 有綁。
