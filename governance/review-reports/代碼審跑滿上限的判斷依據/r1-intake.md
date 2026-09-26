preflight-4: ran

# r1 前掃(便宜 agent 固定清單,2026-09-26)

①②③ 無命中。④ 三條現況宣稱(loop next 已有 cap-reached、沿用既有帳本欄位與凍結審材、沿用 quote-check 引句定位)皆成立;其餘 9 條命中都是「計劃要做、還沒實作」的功能,不是錯。

編排者另修:末節「loop next 的 record_cmd 還在建議 caught|missed」已於 2026-09-25 修掉,改寫成已修(重現:`lumos loop next 代碼審跑滿上限的判斷依據` 輸出的 record_cmd 是 `canary record none`)。
補「實務隱患」節(pitfalls --check 要求)。

## 收貨後編排者重現(2026-09-26)

- 整合席 F1「loop next 對 panel 格式迴圈一律 rc2、到不了 cap-reached」:機制**重現不到**——`lumos loop next design-筆記欄位關卡補齊`(high 設計審,已跑 3 輪)rc0 正常出「接下來第 4 輪」。但**觀察成立而且更糟**:`loop next code-記憶索引大小守衛`(standard,已 4 輪)出「接下來第 5 輪…最多跑 3 輪」、`code-驗收前提欄位可改`(已 3 輪)出「第 4 輪」、設計審那個也一樣——★現行處置帳迴圈跑超過上限,loop next 從來不回 cap-reached★,計劃想掛的出口在今天的迴圈上不會觸發。 → HIT(觀察)/MISS(機制)
- 阻擋密度(發現裡 major 以上 ÷ 正文字數/300):23 / (3246/300) = 2.13,超過重寫建議門檻 1。

## 更正(2026-09-26,同日)

上面把整合席 F1 的機制記成「重現不到」是錯的:我跑 `loop next` 時沒帶 `--spec`,只走到「少了 --spec → gate-pending」那一步。帶上 `--spec` 重跑:
`lumos loop next code-記憶索引大小守衛 --spec governance/review-reports/code-記憶索引大小守衛/r4-snapshot.patch` 與 `lumos loop next design-筆記欄位關卡補齊 --spec docs/lumos-toolchain-knowledge/Projects/筆記欄位關卡補齊_計劃.md` 都印「擋下:panel 閘自 2026-08-25 甲裁後僅供舊迴圈回放」→ 整合席機制 HIT。
根因(讀 scripts/lumos 的 loop next 判定段):沒帶 --spec 先回 gate-pending(排在 cap 前);帶了 --spec 就委派舊 panel 閘,新迴圈被擋 → 兩條路都到不了 cap-reached。2026-08-25 之後開的迴圈,cap-reached 結構上不可達。
