# fromscratch-m1 — 凍結 findings 語料（3 輪 panel，人裁實質收斂）

design-loop `fromscratch-m1`（M1：regen 節點 provenance 分級 + 拒絕發明無證據合約）。panel 模式：每輪 3 sonnet 異鏡頭 + Codex 否決席 + opus 辯方（r1）。發現數 9→6→3 遞減、性質由設計矛盾退至測試枚舉；r3 canary 3/3 全精準、設計層零存活 → 機械 gate 形式 FAIL（存活 major + 殘餘 3.0）但人裁實質收斂（2026-07-16，plan node decisions#d1）。校準用途：replay 對照各模型接住率。

## r1（canary a✗ b✓ c✓｜存活 9｜max blocker）

canary：a=合約鏈豁免矛盾（升級補證即滿足全部要求、繞 [test:]）✗ A 席漏（findings 依紀律剔除，top_dirs 細節經編排者機械自核採信）；b=未定義離線跳驗旗標 ✓（性質偏「無留痕逃生口」記偏離）；c=未定義欄位寫回+stale 接不住 ✓ 精準。Codex：核心可建、無結構性障礙、7 接線零件。辯方 2 場：shallow-clone major→minor（doctor --ci 唯一消費者=本機 pre-push、repo 無 CI）、per-pointer subprocess major→minor（~1.2s vs hook 既有 ~32s）。

存活（全折 v2）：掃描範圍三處矛盾（blocker，B+C）→釘死只掃 summary；`KEY:推測:★INVARIANT★` 對 INVARIANT_RE 隱形（B+Codex）→raw 行獨立偵測；refcheck 抽取入口不可直接複用+top_dirs 靜默放行（B+Codex+A自核）→`_validate_repo_ref` 共用；Check G 字母撞名（B+Codex）→改 J；SCALAR_KEYS 缺 regen（B+C+Codex）；共用檢查器防兩入口漂移（Codex）；shallow 殘餘 warn_soft+留痕；效能 presence-guard+批次 note；INV_TAG_RE 擴充（C+Codex）。

## r2（canary 3/3 caught 首有效輪｜存活 6｜max major）

canary：a=未定義帳檔（六帳封閉清單/gitignore/cochange 三處接不住被翻出）✓ 精準；b=lint 側 warns 一律升格 errs（與 J-c/J-d 非阻擋保證邏輯不可共存+兩重現場景）✓ 精準；c=未定義巡檢旗標 ✓ 精準。Codex 複核：核心可實作、r1 接線缺三塊。

存活（全折 v3）：留痕通道簽名不足（Codex+C）→`(errs, warns, gov_events)`，doctor --ci 才落帳、lint 高頻不落帳；兩入口映射表未明訂（Codex+B，含戳破 r1 辯方只考慮 doctor 入口的盲點）→映射表釘死、warns 兩側皆非阻擋；雙報消歧 predicate 寫死（Codex+C）；INV_TAG_RE 影響面列全 11 處（Codex）；lint「不掃 repo」原則例外明文（B）；presence-guard 術語錨定（A）。

## r3（canary 3/3 全精準｜存活 3｜max major｜cap 末輪）

canary：a=隱藏寫回（`/checked` 後綴偽裝效能優化——A 席列舉全庫 atomic_write_verify 呼叫點證「寫入只走使用者主動指令」+映射表外第四副作用通道）✓ 完美；b=未定義測試 fixture（JSON 案例矩陣——全篇唯一出現/與零依賴純 Python 測試慣例矛盾）✓ 精準；c=訊息數矛盾（「兩則並列」vs「恰一則/continue」+推理出偽裝敘事）✓ 精準。

存活（全折 v4，全屬測試策略完整性、設計層零）：raw 行四組合測試補全（major，B——附實測 1836-1840 迴圈不含 ★IRREVERSIBLE★ → 分支不對稱明記）；J-b 佚失四態（minor）；SCALAR_KEYS 迴歸測認領（minor）；editorial：INV_TAG_RE 計數 8→11 處。

## 人裁實質收斂（誠實天花板）

1. 機械 gate 形式 FAIL 的兩因：r3 存活 major（已折）+ capture-recapture 殘餘 3.0（單席單維度 singleton——測試枚舉類「可能還有漏」的誠實訊號）。
2. 裁定理由：設計層 r3 零存活；殘餘風險=測試格再漏，恰為實作 TDD + code-loop mutation 冒煙天生接住之物。同主網 3 輪人裁前例。
3. 照例：收斂只證「三輪醒著的審計員沒再找到設計層 major」，不證沒有更深的洞；canary 判定/嚴重度/溯源排除為編排者自判，非 tamper-proof。
