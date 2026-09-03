# r1 外家否決席報告(Codex, gpt-5.6-sol, sandbox=read-only)

來源:第三次執行(前景),耗時 288 秒。前兩次為同一份派工詞的背景執行,亦各自完整收尾(結論同為 blocker;首次 blocking 6 條、二三次各 7 條)。

---

severity: blocker
1. **blocker — `folded_set` 無法反推出可機械刪除的條款**

blocking: 是——核心劣化算子沒有可重現的 `finding ID → 報告 finding → 折入後文字範圍` 映射，實驗目前無法按 spec 執行。

引句:「被刪的條款不是我自己想的,是從該迴圈帳上 `folded_set` 反推」

file: `docs/.canary-log.jsonl:354` 的 `folded_set` 只有 `["R1", …, "R15"]`；同列另存報告與快照路徑，但沒有 ID 對應的文字、修改範圍或 patch。

file: `docs/.canary-log.jsonl:356` 另一實例也只是 `quotecheck欄位`、`prescribe缺源` 等人工短標籤，不是可刪文字。

即使由 ID 找到席報告，報告引句引用的是「送審前已有的問題證據」，不等於「作者後來為解決該 finding 新增的文字」。中間至少缺：

`folded ID → 原 finding 全文 → 處置 commit/diff → 唯一新增文字區間 → 可逆刪除邊界`

同一 finding 還可能造成多處修改、改寫既有句子或與其他 findings 合併，不能由一段引句自動反推。

severity: blocker
2. **blocker — 預註冊選出的前 8 個樣本，多數沒有算子所需的前後兩輪**

blocking: 是——固定選樣規則與「比較相鄰快照找折入內容」的資料前提互斥，第一批樣本無法照規格產生 treatment。

引句:「該條款是同一份文件的前一輪(r(N-1))由某一席寫進報告、並被編排者折入的」

依 spec 的「設計審、末輪 findings ≥ 3、迴圈名字典序前 8」重算，得到：

`Android側UI測試綁圖譜工作流`、`about-code-field`、`about-code-field-v2`、`about-code-field-v3`、`about-code-impl`、`about-code-impl-std`、`auto-loop-repair`、`auto-loop-repair-v2`。

其中 `about-code-field`、`about-code-field-v2`、`about-code-impl`、`auto-loop-repair`、`auto-loop-repair-v2` 的選中末輪都是 r1，根本沒有 r0 快照可比較。

file: `docs/.canary-log.jsonl:500` 顯示 `about-code-field` 的入選輪為 r1。

file: `docs/.canary-log.jsonl:504` 顯示 `about-code-field-v2` 也被當成另一個 loop，卻重用 `about-code-field/r1-snapshot.md`。

file: `docs/.canary-log.jsonl:510` 顯示 `about-code-impl` 只有 r1 材料。

file: `docs/.canary-log.jsonl:690` 顯示 `auto-loop-repair-v2` 又重用 `auto-loop-repair/r1-snapshot.md`。

因此不只缺相鄰輪，8 個觀測也包含同一材料的別名重複，違反獨立樣本假設。

severity: major
3. **major — 「76 個可用迴圈」與帳面重算不符，且未定義去重單位**

blocking: 是——抽樣母體不確定會直接改變字典序前 8、有效樣本數及結果解讀。

引句:「其中 **76 個留有凍結快照且末輪 findings > 0**,可直接用」

對 `docs/.canary-log.jsonl` 的 868 列，以有 `findings_set` 的 222 筆分組、取每個 loop 最後一筆後重算：

- 共有 80 個 loop ID，27 個 `code-`、53 個設計審。
- 80 個末筆的 `findings_set` 都非空，且都有存在的 `snapshot_path`。
- 若按末輪 snapshot 路徑去重，只剩 73 份不同材料，不是 76。

file: `docs/.canary-log.jsonl:504-505` 的 `about-code-field-v2` 與 `about-code-field` 共用同一報告及 snapshot。

file: `docs/.canary-log.jsonl:690-694` 的 `auto-loop-repair-v2` 同樣重用 `auto-loop-repair` 的整組材料。

所以 76 既不是 loop ID 數，也不是獨立末輪 snapshot 數；spec 必須明訂排除條件與觀測單位後重新列出母體。

severity: blocker
4. **blocker — quote-check 不能判定「有沒有重新點出被刪條款」**

blocking: 是——主指標 M1 的判定器只驗字面來源存在，沒有驗 finding 身分或「缺漏」語意，復原率數字沒有有效 oracle。

引句:「判定=報告引句能逐字錨回快照,沿用既有 quote-check」

file: `scripts/lumos:11453-11455` 只從報告抽取所有標成「引句」的文字。

file: `scripts/lumos:11461-11472` 只做正規化後的子字串存在檢查。

file: `scripts/lumos:11782-11786` 明定其功能是確認報告引句可在派工快照找到，防止引句自我成真。

這只能回答「某句引用是否真的出現在 treatment 快照」，不能回答：

- 該 finding 是否指向被刪條款；
- 同義改述是否算復原；
- 引到附近文字但提出別的問題是否算命中；
- 被刪整段已不存在時，審查員如何逐字引用那段文字。

尤其 treatment 已刪除目標文字，若要求引句就是被刪原文，quote-check 理應判 miss；若容許引附近文字，又需要尚未定義的語意配對器或人工盲判。

severity: major
5. **major — 8 個樣本無法支撐 35%／70% 所宣稱的強結論**

blocking: 是——門檻在 n=8 下不能對應宣稱的推論力度，會把高度不確定的點估計直接翻成開案或關案。

引句:「M1 ≤ 35% → 確認自家也有漏項盲區,外部數字站得住」

n=8 時比例只能以 12.5% 跳動：

- `≤35%` 實際只有 0/8、1/8、2/8；
- `≥70%` 實際只有 6/8、7/8、8/8；
- 中間只有 3/8、4/8、5/8。

而 spec 又把 0/8 與 8/8 判為校準失敗，因此真正會觸發決策的只剩 1–2/8 或 6–7/8。即使 6/8，95% Wilson 區間約為 41%–93%，仍涵蓋 50%；2/8 約為 7%–59%。它們不能支持「外部數字不成立」或「確認自家盲區」。

引句:「M4 > 10% → 儀器噪音過大」

M4 在 8 個 control 下只要出現 1 次就是 12.5%，立即越線；0 次則仍不能證明偽陽率低於 10%。這把尺在首批樣本中幾乎只能做「零次／至少一次」判斷。

severity: major
6. **major — control 與 treatment 並未隔離模型隨機性，M2/M3 無法歸因於刪除**

blocking: 是——若沒有配對重跑、順序隨機化及重複次數，兩組差異可能完全來自模型抽樣波動。

引句:「其餘完全相同」

file: `docs/.canary-log.jsonl:400-404` 顯示同一輪、同一材料的不同席，findings 數可從 4 到 18，且 canary 結果也有 caught/missed 差異，證明席位輸出本身有明顯變異。

spec 只各跑一次 control/treatment，沒有規定：

- 哪組先跑及順序隨機化；
- 同模型、模型版本、temperature/seed 是否固定；
- 每個條件重複幾次；
- M2 的 findings 如何跨重跑去重；
- M3 應餵入哪份聚合後的處置帳。

因此 M2 的數量／severity 差異和 M3 的 PASS/FAIL 改變不能歸因於那一段刪除。

severity: major
7. **major — 「落點換到收斂閘」不足以區隔已停案方案**

blocking: 是——本案真正需要執行的關鍵步驟仍發生在人工派工與報告語意判定，pre-push 收斂閘沒有提供所宣稱的機械強制點。

引句:「本案不落在派工那一刻,落在收斂那一刻。」

file: `docs/lumos-toolchain-knowledge/Projects/impact鏡頭機械化_計劃.md:18-21` 的有效決策不是只否決某個時間點，而是裁定 agent 派工本身沒有 hook 可攔，新增指令仍是「可能不跑的指令」。

file: `docs/lumos-toolchain-knowledge/Projects/impact鏡頭機械化_計劃.md:38-40` 再次明載 `loop next` 或新指令都沒有機械強制性。

file: `scripts/lumos:11478-11483` 顯示收斂閘只重算既有帳、留痕及引句錨定；它不會自動建立 treatment、不會派同一組審查員，也不會判斷 finding 是否復原了目標條款。

所以「重跑同一派工詞」「建立兩組」「把新報告對到被刪條款」仍全在閘外，仍依賴人記得執行。若本案只是一場手動一次性實驗，可以與停案的「常設機械化」區分；但就不能以「落在收斂閘、pre-push 真的會擋」作為區分理由。

最嚴重 severity：blocker；blocking 共 7 條。
tokens used
96,598
