severity: major

**Finding 1:「只准問一次」可以用換反例編號或換合約文字繞過**

severity: major
blocking: 是 — 編排者一個人就能把同一個反例問到出現 untestable,再記成殘留
引句:「同一個反例只准問一次,不能換代理重問到聽見想要的答案」
攻擊步驟:
- 輸入:先對 `c1` 記 `--verdict testable`,再對同一個反例記 `C1`、`c1.`,最後在合約文字尾端加「。」再記 `c1`。
- 結果:四次都回 rc=0 並寫進帳,其中 `C1`、`c1.` 和改字後的 `c1` 都記成 untestable。改字後用 `guard residual --add ... --case c1` 成功,標記寫上,索引 1 條。
- 原因:`_RESIDUAL_CASE_RE` 區分大小寫,又允許 `.`、`_`、`-`。唯一鍵是 `fp+case`,而指紋綁的是整句宣稱文字,改一個標點指紋就變。
- 另有兩個缺口:`--case` 沒有跟審計實際列的反例綁在一起。`--checker` 是自己填的字串,沒驗它跟 `[audit:]` 的審計員是不是不同的代理。所以「第二個代理」沒有機械保證。
實驗證據:file: `scripts/lumos`(patch 內 `_RESIDUAL_CASE_RE`、`_residual_claim_fp`、`cmd_guard_residual_ask`)

**Finding 2:手改合約行加 `[residual:]` 再 `--reindex`,doctor 完全不報**

severity: major
blocking: 是 — 繞過寫入閘的檢查,doctor 事後也看不出
引句:「把標記寫上合約行(寫入當下驗決策、問答、checker 行與 [audit:]),並重寫殘留索引給 pitfalls 分級讀。」
攻擊步驟:
- 輸入:用編輯器在已審合約行尾加 `[residual:Projects/a_計劃#d12]`,不跑 `residual-ask`,再執行 `lumos guard residual --reindex`。
- 結果:`--reindex` 回 0。治理帳裡沒有任何 residual-ask 列。doctor 輸出沒有任何殘留相關行。
- 原因:`_doctor_residual_lines` 只驗決策還在、索引和圖譜一致,不驗治理帳裡有沒有對應的 untestable 問答,也不驗決策內容有沒有 checker 行。
- 一併:`--reindex` 本身不驗任何東西。決策也不必屬於這條合約,任何含 `checker:` 字樣的現行決策都能重複拿來用。
- 補充:我的測試環境裡 `doctor --strict` 回 1,沒有查是哪一項造成的,不能當作它抓到了這個問題。
實驗證據:file: `scripts/lumos`(patch 內 `_doctor_residual_lines`、`cmd_guard_residual` 的 reindex 分支)

**Finding 3:拿掉殘留標記不需要任何同意,分兩次推送就躲過高風險代碼審**

severity: major
blocking: 是 — 正是「記了殘留之後改程式卻不被要求走高風險審」
引句:「讀起點:同一個提交把標記拿掉、改程式也躲不掉;讀頂端:這次推送才加的殘留也算」
攻擊步驟:
- 輸入:push 1 只跑 `guard residual --remove ...`,標記和索引一起清掉,是純圖譜和治理資料的改動。push 2 再改 `src/a.py`。
- 結果:`_residual_tier_hits` 在 push 2 的範圍(起點已不含殘留)回 `[]`,分級回到 standard。`--remove` 回 0,不需要第二個代理、也不需要重審。push 1 本身沒有程式檔,判 light。doctor 沒報任何東西。
- 對照:同一批變更用跨兩個提交的整段範圍,才回 `['src/a.py']`。
- 原因:分級只比「這次推送的起點」。「重審」只是 `--remove` 印出的一句提示,沒有機械強制。
- 延伸:手改或刪索引也一樣。只要標記和索引條目同步消失,doctor 就一致,不會有人被要求補回殘留。
實驗證據:file: `scripts/lumos`(patch 內 `_residual_tier_hits`、`_cmd_guard_residual_locked` 的 remove 分支)

**Finding 4:索引內容和路徑注入影響有限**

severity: minor
blocking: 否 — 只會讓分級多升 high,不會漏升
引句:「不存在、讀不出、形狀不對 → 空集合(什麼都不做)」
說明:
- 索引裡的檔案路徑只拿來和 diff 檔名比對,沒有檔案系統存取,沒有注入出口。
- 殘留決策指標不收 `]`,也不收 `[[`,而且必須指到真實存在的決策。
- 殘留決策可以靠大小寫不敏感的節點比對指到同一筆決策。
- 惡意索引最多造成誤升 high 的干擾,屬於可用性問題。
- 索引壞掉會靜默回到原分級,這是 fail-open,Finding 3 已涵蓋它的後果。

總結:最高等級 major,blocking 共 3 條(Finding 1、2、3),另有 1 條 minor 不擋。
