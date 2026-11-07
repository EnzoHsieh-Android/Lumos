# r3 收貨更正(2026-11-08 實作時)

- co4 的後半「STATE-9 現成規則格的 `kt-statein-lazily-or-no-timeout` 在主線不存在」:實作時查證不成立——那條規則在 `configs/ast-grep/kotlin-android/rules/state.yml`(會擋那一級,掛 STATE-4),STATE-9 那格是兩條規則的實測紀錄,照舊不改。co4 前半(rules-unwired 給全集等級)照折。
