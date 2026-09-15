severity: major

## 1. 題目卷會把編輯片段中的既有答案原樣印出
severity: major
blocking: 是——正常出題流程可把答案帶進宣稱不含標註的材料，直接破壞獨立判斷。
引句:「lines.append(f"- {c['id']}｜改到的檔:`{c['file']}`｜改動:{c.get('delta', '(未記)')}")」

`material` 排除了頂層 `labels`，但沒有處理題目內容本身來自答案檔的情況。出題器允許路徑含 `eval` 的 JSON 入題，再從 Git diff 擷取新增行作為 `delta`。因此金標或評審答案檔的改動，可以成為題目內容。

file: `governance/eval/build_goldset.py:132`
file: `governance/eval/build_goldset.py:136`
file: `governance/eval/build_goldset.py:149`

記憶體內執行實際 `cmd_material`，給它合法字串：

```text
"Systems/Beta.md": {"final": 2, "claude": 2, "codex": 1}
```

輸出完整保留節點、最終答案及兩席分數，卷頭仍宣稱不含既有標註。

新測試只把答案放進頂層 `labels`，編輯片段仍是 `(x)`，守不到這條來源路徑。應加入答案檔改動形成編輯題的案例，並在出題及材料出口拒絕或隔離這類題目。

file: `scripts/test_lumos.py:26681`

## 2. 種子綁的是共用分組常數，並非題庫身分
severity: minor
blocking: 否——跨題庫隔離與回溯承諾不成立，但先排序仍已移除原始名次順序。
引句:「_salt = str(gs.get("split_salt") or gs.get("snapshot_commit") or "")」

出題器把所有題庫的 `split_salt` 設為同一個 `lumos-retr-v1`。只要這個欄位非空，`snapshot_commit` 永遠不參與種子。

file: `governance/eval/build_goldset.py:12`
file: `governance/eval/build_goldset.py:240`

因此不同題庫中同編號、同長度的候選，會使用相同位置排列；題意及快照不同也一樣。這不是不同 `cid` 都退化：`S01`、`S02` 確實使用不同種子。

可重現性另有兩個邊界：

- 缺少 `split_salt` 時，重釘快照會改變種子；記憶體實驗確認候選不變也會換序。
- 候選成員改變時，先排序不能保證重現舊卷；必須保存當次材料才能回溯。

新洗牌測試使用單一題庫，沒有比較不同題庫身分或缺少 salt 後的重釘情境。應使用明確、穩定的題庫識別值，並補這兩類測試。

## 3. `repin` 失敗訊息仍直接公開未洗牌名次
severity: minor
blocking: 否——這是既有旁路；需要讓標註者接觸診斷輸出才會污染，但本次兩項修補沒有封住它。
引句:「# 未標判定回傳的順序★就是現行排序的名次★,原樣端出去等於先告訴標註者「系統認為誰該排前面」,」

`repin` 遇到未標候選時，逐題直接遍歷 `collect_unjudged` 回傳的 `nodes`，印到 stderr。標註者若用這份失敗清單補標，仍會看到原始名次。

file: `governance/eval/refresh_labels.py:231`
file: `governance/eval/refresh_labels.py:234`

記憶體內執行實際失敗分支，輸入 `rank1、rank2、rank3`，輸出原序且回傳 1。未執行 Git 或任何寫入。

新增測試只驗 `delta` 與 `material`，不能保護這個出口。建議失敗訊息只提供數量與產卷指令，或共用候選呈現函式。

## 驗證與交付限制

完成唯讀檢查及記憶體內重現；未執行完整測試或 `/tmp` 變異測試。環境禁止寫入，連 shell 暫存檔建立都遭拒，因此未能寫入指定的 `r1-外家finder-codex.md`；以上為完整報告。未修改 repo，也未寫入評測歷史。

總結：應先封住答案經編輯題內容流入材料的路徑，再接受本次防污染修補。
tokens used
76,578
severity: major

## 1. 題目卷會把編輯片段中的既有答案原樣印出
severity: major
blocking: 是——正常出題流程可把答案帶進宣稱不含標註的材料，直接破壞獨立判斷。
引句:「lines.append(f"- {c['id']}｜改到的檔:`{c['file']}`｜改動:{c.get('delta', '(未記)')}")」

`material` 排除了頂層 `labels`，但沒有處理題目內容本身來自答案檔的情況。出題器允許路徑含 `eval` 的 JSON 入題，再從 Git diff 擷取新增行作為 `delta`。因此金標或評審答案檔的改動，可以成為題目內容。

file: `governance/eval/build_goldset.py:132`
file: `governance/eval/build_goldset.py:136`
file: `governance/eval/build_goldset.py:149`

記憶體內執行實際 `cmd_material`，給它合法字串：

```text
"Systems/Beta.md": {"final": 2, "claude": 2, "codex": 1}
```

輸出完整保留節點、最終答案及兩席分數，卷頭仍宣稱不含既有標註。

新測試只把答案放進頂層 `labels`，編輯片段仍是 `(x)`，守不到這條來源路徑。應加入答案檔改動形成編輯題的案例，並在出題及材料出口拒絕或隔離這類題目。

file: `scripts/test_lumos.py:26681`

## 2. 種子綁的是共用分組常數，並非題庫身分
severity: minor
blocking: 否——跨題庫隔離與回溯承諾不成立，但先排序仍已移除原始名次順序。
引句:「_salt = str(gs.get("split_salt") or gs.get("snapshot_commit") or "")」

出題器把所有題庫的 `split_salt` 設為同一個 `lumos-retr-v1`。只要這個欄位非空，`snapshot_commit` 永遠不參與種子。

file: `governance/eval/build_goldset.py:12`
file: `governance/eval/build_goldset.py:240`

因此不同題庫中同編號、同長度的候選，會使用相同位置排列；題意及快照不同也一樣。這不是不同 `cid` 都退化：`S01`、`S02` 確實使用不同種子。

可重現性另有兩個邊界：

- 缺少 `split_salt` 時，重釘快照會改變種子；記憶體實驗確認候選不變也會換序。
- 候選成員改變時，先排序不能保證重現舊卷；必須保存當次材料才能回溯。

新洗牌測試使用單一題庫，沒有比較不同題庫身分或缺少 salt 後的重釘情境。應使用明確、穩定的題庫識別值，並補這兩類測試。

## 3. `repin` 失敗訊息仍直接公開未洗牌名次
severity: minor
blocking: 否——這是既有旁路；需要讓標註者接觸診斷輸出才會污染，但本次兩項修補沒有封住它。
引句:「# 未標判定回傳的順序★就是現行排序的名次★,原樣端出去等於先告訴標註者「系統認為誰該排前面」,」

`repin` 遇到未標候選時，逐題直接遍歷 `collect_unjudged` 回傳的 `nodes`，印到 stderr。標註者若用這份失敗清單補標，仍會看到原始名次。

file: `governance/eval/refresh_labels.py:231`
file: `governance/eval/refresh_labels.py:234`

記憶體內執行實際失敗分支，輸入 `rank1、rank2、rank3`，輸出原序且回傳 1。未執行 Git 或任何寫入。

新增測試只驗 `delta` 與 `material`，不能保護這個出口。建議失敗訊息只提供數量與產卷指令，或共用候選呈現函式。

## 驗證與交付限制

完成唯讀檢查及記憶體內重現；未執行完整測試或 `/tmp` 變異測試。環境禁止寫入，連 shell 暫存檔建立都遭拒，因此未能寫入指定的 `r1-外家finder-codex.md`；以上為完整報告。未修改 repo，也未寫入評測歷史。

總結：應先封住答案經編輯題內容流入材料的路徑，再接受本次防污染修補。
