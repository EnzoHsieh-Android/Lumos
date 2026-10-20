severity: major

資源-sonnet 對 r1-snapshot.md 的審查報告。已讀全文與 r1-intake.md,並查證 `scripts/lumos` 的盤點讀取與限額。

白話先講:這份設計把盤點從幾十個入口變成「入口 × 資產 × 類別」幾萬格,而且所有核可紀錄都塞進同一個 2MB 的登記塊。格子一多,檔案先爆,爆了整份盤點變成「未知」。讀不完整時,格子顯示什麼也沒寫。

## F1 considerations 全放進唯一 inventory 區塊,會撞單檔 2MB 上限
severity: major
blocking: 是(照字面實作,專案一大,整份盤點讀不出來,等於做出壞系統)

- 段落:〈一〉〈四〉。
- 引句:「用來寫「想過、不適用」與「想過、接受風險」的 `considerations` 清單(見〈四〉)。」
- 問題:`considerations` 是 inventory 的欄位。現行規則是全庫最多一份 inventory,而且它是單一登記塊。現行快照單檔上限是 2MB。
  - 佐證:``file: `scripts/lumos:6387` `` 的 `_SECINV_FILE_MAX = 2 * 1024 * 1024`;``file: `scripts/lumos:7089` `` 的 `_secinv_inventory` 在多份時報錯、不任選。
- 具體例:200 個入口 × 平均 5 個資產 × 「全部」類(input-injection、data-exposure)加上其他適用類。這是約 1 萬格。
  - 每筆 considerations 帶入口、資產、類別、理由、補償措施、核可決策、到期日,約 300–400 位元組。
  - 約 5000–7000 筆就超過 2MB。這個數字是估算,spec 沒量。
  - 超過後,該檔得到 `file_too_large`,`read_complete` 變 false,inventory 整份不可用,所有格子變未知。
- 還有累積問題:〈回退〉與表改版都寫「considerations 留著不刪」。這只增不減,遲早碰頂。
- spec 沒寫 considerations 的筆數上限、拆檔方式、超限時怎麼辦。
- 引句:「已寫進消費專案的 considerations 與 pending_questions 不刪。」

## F2 讀不完整或衝突時,格子與 spec-gate 提醒的語意沒寫
severity: major
blocking: 是(實作者得自己決定,容易把「沒讀到」做成「沒有 open」)

- 段落:〈四〉、〈三〉最後一組、S3、S13。
- 問題:現行的 `_secinv_coverage` 在沒有 inventory 時回 `status: unknown`、surfaces 空。v2 的 `cells` 區在下列情況時怎麼呈現,spec 一字未提:
  - (a) `read_complete` 為 false(檔太大、總量超限、`too_many_files`、`changed_during_read`)。
  - (b) inventory 壞掉。
  - (c) 護欄所在的檔沒讀到。
- 具體例 1:某登記護欄的檔因超過 2MB 沒讀到。它覆蓋的格子被算成 `open`(誤報)。若該格同時有 considerations,S3 的衝突漏判,會被當成合法的 `not_applicable`。
- 具體例 2:spec-gate 新增的那一行要印「護欄與 open 格子數」。vault 讀不完整時,它可能印出「0 個護欄」。作者會讀成「這份計劃沒有資安登記」。
- 引句:「spec-gate 這一行是新增的提醒:計劃 `lands_in` 或 `related` 連到的 Systems 有資安登記時,印出那些護欄與 open 格子數,不擋。」
- S3 說「列錯誤並退出 2」,沒說其他格子還輸不輸出,也沒說 JSON 形狀。
- 需要補的:(a)(b)(c) 時 cells 區必須整體標「未知」,不輸出 open 數;spec-gate 那行要印「盤點讀取不完整」。

## F3 沒有任何預算或上限條款,效能只留給「實作時量一次」
severity: minor
blocking: 否(spec 明講要量,但驗收條款綁不到)

- 段落:〈實務隱患〉資源。
- 引句:「實作時對 200 個入口、50 個資產的合成 inventory 量一次時間與輸出大小再定上限。」
- 問題:S1–S14 沒有任何一條是上限、時間或輸出大小,量測也沒有失敗條件。`security list` 要「逐格列出」(S1),輸出對格數線性成長且無截斷規則。
- 具體例:200 × 50 × 約 9–11 類,最壞約 9–11 萬格。每格含狀態與表版號,約 150 位元組,輸出約十幾 MB。終端與 `--json` 管線都扛不住。
- 現行盤點的做法是在規格階段先寫設計值(2MB、64MB、1 萬檔)。本篇沒照做。
- 需要補:在實作前把格數上限、輸出摘要規則(預設只印 open 與計數,`--all` 才逐格)、逾時寫進條款。

## F4 格子比對沒指定索引,朴素實作是二次方
severity: minor
blocking: 否(實作選擇,但 spec 的 200×50 規模正好踩到)

- 段落:〈四〉、S3、S14。
- 問題:現行 `_secinv_surface` 已是「每個入口掃一遍所有 live 護欄」,見 ``file: `scripts/lumos:7208` ``,複雜度 S×C。
  - v2 的格子條件是「三件事」加類別。
  - 還要對每格做 S3 衝突檢查,以及「同一格有兩列 considerations 也算錯」。
  - 照字面逐格掃護欄與 considerations,就是 cells × (controls + considerations)。
- 具體例:9 萬格 × 2000 條護欄 ≈ 1.8 億次比較,純 Python 是分鐘級。
- 需要補:規定先建 (surface, asset, category) 索引,護欄與 considerations 各一遍線性建表,格子用字典查詢。
- 引句:「同一格只要同時有「覆蓋它的護欄(不論那條護欄的 reported_status)」與「considerations 裡 outcome 是 not_applicable 或 risk_accepted 的一列」」

## F5 spec-gate 每次多做一次整庫安全讀取
severity: minor
blocking: 否

- 段落:〈三〉最後一組、S13。
- 問題:spec-gate 的提醒需要知道「連到的 Systems 有沒有資安登記」。`pitfalls --stage` 不讀筆記庫,所以這個資訊只能來自 `_secinv_snapshot`。它會安全讀整個圖譜,最多 1 萬檔、64MB,再逐檔 recheck lstat。
  - 佐證:``file: `scripts/lumos:6660` ``;spec-gate 本身已跑測試與相依回歸,見 ``file: `scripts/lumos:10115` ``。
- 本 repo 圖譜約 909 篇、12.8MB,可接受。但 spec-gate 是常跑指令,spec 沒說這行要不要先用便宜條件把關。
  - 例如先看 `lands_in` 或 `related` 連到的節點有沒有 `lumos-security-v1` 字樣,沒有就完全不做整庫快照。
- 需要補:寫明這個把關條件,否則實作者會每次都跑完整快照。

## F6 「每格一個候選問題」沒有題數預算與重跑冪等
severity: minor
blocking: 否

- 段落:〈二〉、〈三〉「問題怎麼進待決問題」。
- 引句:「每格產生一個候選問題,問題句由表的模板加上入口、資產、角色名稱組成。」
- 問題:
  - 沒寫產生題目的是哪個指令。
  - 沒寫每份計劃一次最多進幾題。
  - 沒寫重跑會不會重複 `question-add`。
- 具體例:同一份計劃連到 200 個入口,跑兩次就是兩份各數百題。`pending_questions` 寫在開頭欄位,每次 `pitfalls --stage` 與規格閘都要解析它。
  - 〈三〉另說格子狀態「不靠這段字算」,所以也不能拿題目前綴當去重鍵。
- 需要補:每份計劃一次的題數上限、以「格子身份」去重的規則、超過時只提摘要。

## 已讀,無 finding
- 〈三〉`triggers` 判法:`re.search` 對全文跑一次,詞表是固定短詞,沒有巢狀量詞,無 ReDoS。「至少 N 個不同詞」一次掃完詞表即可。`--stage` 只讀一個計劃檔,記憶體不是問題。
- 〈現況〉的重跑指令:讀 298 個 `_計劃` 檔,一次性操作,規模小。
- 〈二〉鏡像常數與漂移測試:12 列 × 10 欄的表比對,成本可忽略。
- 〈五〉P2 量測:人工標 40 篇,規模小;模型費用已歸母計劃另核可。
- 〈四〉risk_accepted 的 30 天:純日期比較,無資源問題。
- S1、S2、S4–S12、S14:不涉及資源。

最嚴重 severity: major;blocking 共 2 條(F1、F2)。
