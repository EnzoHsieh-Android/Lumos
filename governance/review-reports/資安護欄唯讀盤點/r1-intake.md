# 資安護欄唯讀盤點 r1 收貨

preflight-4: ran

## 前掃（非正式席位）

審查員 security_list_preflight；先補未定義欄位、圍欄文法及完整標籤字面，再凍結正式審材。命令尚未實作，不把規格案例稱作執行證據。

| 項目 | 修改前 → 後 | 查證與裁定 |
|---|---|---|
| PF1 | retired取代ID未命名 → replacement_id，補source巢狀鍵及required/null條件 | HIT：原表未給完整鍵，補明確規格；非正式finding |
| PF2 語意 | Verification stale/invalid/failed → 合法五態逐一映射，未知值獨立錯誤 | HIT：`sed -n '21178,21192p' scripts/lumos` 顯示合法值為pass/stale/superseded/pending/abandoned；invalid/failed不是節點合法status；已訂正，保留runner與節點狀態區別 |
| PF3 語意 | 重用圖譜載入 → 安全讀取後Env.from_texts，不直接用load_vault或一般Env | HIT：`sed -n '600,625p' scripts/lumos` 顯示stat/read_text直接讀；`sed -n '695,714p' scripts/lumos` 與 `sed -n '758,776p' scripts/lumos` 顯示一般Env沒有內容快照，env_text會再讀。新指令原有安全限制不變，修正重用範圍；未重構共用載入器 |
| PF4 | security-relevant → flag/security-relevant | HIT：對齊既有完整標籤 |
| PF5 | 頂層圍欄未定義 → column 0精確三反引號、排除一般範例圍欄、變體報錯 | HIT：補文法與錯誤邊界 |

舊否決概念檢查：不新增獨立證據帳、不從散文推論驗收、不自動交付或設done，保持後端證據擴充縮案邊界。新JSON入口是否構成不必要第二種做法，交架構席正式審，不以名稱不同自行豁免。母計劃d4已被d5取代，本案不要求所有資安條目升格Invariant。

## 正式席位收貨

六席全部回覆後才寫入報告及修改真檔，r1-snapshot不變。報告格式正規化檢查通過；六席quote-check全錨、refcheck零壞引用、seat-check零漏查／越界。resources另補本人已讀審材路徑；arch/correctness由原席補正檔級與finding級severity位置，不改觀察及判級。

派工單每席原已帶materials，收貨另在頂層鏡射同一materials供seat-check讀取；不是新增審材。六席只用了同家族gpt-5.6-sol，無跨家族有效性宣稱。

## 編排者重現與處置

| ID | 原席 | 重現／採信 | 處置與對應例 |
|---|---|---|---|
| A1 | arch F1 | HIT，原語實跑沒有未閉合診斷，且原碼指定唯一圍欄判定 | 折：抽出共用區段與閉合原語，保持舊回退；S12四反引號包示例仍不得登記 |
| C1 | correctness F1 | HIT，2個Unicode等價路徑進Env只剩1篇 | 折：進Env前查NFC碰撞，列兩出處且rc2；S9 |
| C2 | correctness F2 | HIT，凍結schema只有路徑、無kind關聯，無法對上behavior/review | 折：evidence_refs每項kind/node，缺必要kind列missing；S13 |
| C3 | correctness F3 | HIT，來源範圍漏明定；普通Path.read_text跟隨symlink實跑讀到合成外部哨兵 | 折：來源與引用共用安全讀取，S3包括來源symlink |
| C4 | correctness F4 | HIT，凍結條款沒有比較點，S8無成功讀取間改寫案例 | 折：初始manifest、每檔前後fstat、末次manifest；S11。採資源席較小的metadata方案，不用第二次全文雜湊；不能抓惡意還原的邊界明示 |
| E1 | edge F1 | HIT，同C1，獨立重現輸出2→1 | 折：同C1；保留獨立席身份、不重算成另一種缺陷 |
| I1 | integration F1 | HIT，active/not_applicable在原unmapped/candidate_only均不命中 | 折：衍生逐入口適用性、未獨立驗證與缺陷ID集合；S13，active/verified也不洗成已驗 |
| I2 | integration F2 | HIT，先test非symlink為真，再置換symlink，read_text讀到合成外部哨兵；共用nofollow原語回None | 折：逐層dir_fd/nofollow讀取與普通檔驗證，S3含置換；不單靠先檢查再開檔 |
| R1 | resources F1 | HIT，同C3 | 折：同C3與S3 |
| R2 | resources F2 | HIT，現有read_text先整檔配置；凍結S1–S8無容量界線測試 | 折：binary有界讀取在解碼解析前，超限退出2；S10三種限額及加一案例 |
| R3 | resources F3 | HIT，同C4，原驗收沒有改寫／替換的排程點 | 折：同C4與S11 |
| S1 | simplicity F1 | HIT，原字面要求所有一般圍欄未閉合皆錯；無標記old.md也被擋 | 折：僅原文含專用標記篇章檢查嚴格閉合；S12保留無標記舊筆記好例 |
| S2 | simplicity F2 | HIT，同C2；兩份behavior不能滿足review | 折：保留required_evidence作需求，kind/node作宣告證據，不把已有報告當需求全集；S13 |

13條全部spec型、全折、accepted空、refuted為none；不是13個獨立根因。S1–S13仍是實作前驗收設計，未跑新CLI，不能稱產品行為翻紅或修復驗證通過。

### 實際執行證據

1. `python3 -B -c 'import runpy; m=runpy.run_path("scripts/lumos",run_name="probe"); e=m["Env"].from_texts("/tmp/nonexistent-in-memory-vault",{"Systems/e\u0301.md":"---\ntype: system\n---\nA","Systems/\u00e9.md":"---\ntype: system\n---\nB"}); print("NFC source_count=2 parsed_count=",len(e.notes)); print("unclosed_visible=",list(m["_visible_lines"]("before\n```text\nhidden\nafter".split("\n"))))'`
   輸出：`NFC source_count=2 parsed_count= 1`；`unclosed_visible= [(1, 'before')]`。只驗既有原語，未讀實際Unicode命名檔案。
2. 用apply_patch在本次mktemp目錄建立合成inside/outside哨兵，`test ! -L /tmp/lumos-security-intake.nKx6lA/vault/Systems/source.md`退出0；將來源移為held.md，再以`ln -s`令原路徑指向同一臨時目錄vault外的outside.md；沒有讀系統機密或使用者資料。執行`python3 -B -c 'from pathlib import Path; import runpy, os; p=Path("/tmp/lumos-security-intake.nKx6lA/vault/Systems/source.md"); print("unsafe_read=",p.read_text().strip()); m=runpy.run_path("scripts/lumos",run_name="probe"); print("nofollow_fd=",m["_regular_own_fd"](p,os.O_RDONLY,require_owner=False))'`。
   輸出：`unsafe_read= SYNTHETIC_OUTSIDE`；`nofollow_fd= None`。序列化模擬check→置換→use窗口，非統計競態測試。
3. `sed -n '350,415p' scripts/lumos`、`sed -n '4936,4985p' scripts/lumos`：共用圍欄狀態機與寬鬆回退可見；`sed -n '1384,1430p' scripts/lumos`：已有nofollow/nonblock/fstat原語，可在既有入口擴充而不抄第二套。
4. `rg -n 'evidence_refs|required_evidence|coverage|未閉合|S8' governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md`：核對上表規格反例的原條款；這是文字／資料流重現，不冒充未實作CLI的執行結果。

fold-check提示正文有--json而summary沒有：本project無summary，CLI契約及輸出契約皆明列文字與JSON，屬無摘要造成的提示，不補重複權威描述。鏡像與圖譜自足性另交全新代理核對。

鏡像審補正：S2原仍泛稱未閉合圍欄，現已限定含專用標記篇章並加入無標記好例，與正文及S12對齊。核對席讀到intake撰寫前的待填段；交回完整收貨表重新核對，不把前後時間差誤記成正式新finding。

全新security_r1_fold_audit回驗：F1/S2與F2/完整intake均已讀無finding，合約候選未誤標Invariant；最嚴重clean、blocking 0。此為鏡像與圖譜自足性審，不冒充第二輪正式設計審。
