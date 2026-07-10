# cochange-guard design-loop 存活 findings（辯方裁決後，2026-07-10 凍結）

## r1（canary a/b 2/2 caught）
- [blocker] pre-commit「末段追加」死碼（每路徑顯式 exit；docs-only 在 :88 早退）→ 插入點改 Gate 1 前（capture 3/3）
- [blocker] 驗收案例方向矛盾（改 README.md 期待警告但 conf(主⇒en)=0.375<0.8）→ 例子反向
- [major] rules 門檻語意未定 + 舉例 0.778/0.795 低於 0.8 → rules 預設套門檻
- [major] rc「恆 0」vs rc 2 矛盾 → 條件式改寫
- [major] 裸 lumos 不在 consumer PATH → vendored 路徑+python 解析
- [major] quotePath 中文檔名 octal 逃逸 → -c core.quotePath=off
- [major] --range 與 pitfalls --diff 慣例不一致 → 改 --diff
- [major] 散落清單交付未列 → 交付同步清單節
- 辯方降級 4：rename 訊號重置(minor,documented debt;活風險例證偽——e710ad4 全 M 零 R)、anchor 連動(minor,checklist;baseline opt-in)、生成檔噪音(minor;實測 1/22、4/247)、開放題未回應(clean;原型已答)

## r2（canary c caught / d missed → 輪無效；slot2 findings 剔除、2 條經編排者機械覆核折入）
- [blocker] 排除清單 pattern 不生效（r1 修 refcheck 時自己去掉 .jsonl 副檔名 + fnmatch `**/` 不吃根層〔編排者實測〕）→ 精確 pattern + 雙試演算法
- [major] zero-commit rc 三段矛盾 → 統一 rc 0 + rev-parse 判別
- [major] 0.8 論證措辭歧義 → 消歧（>0.8 過擬合、<0.8 誤報升）
- [major] 478/508 口徑混用 → 註明
- [major] --staged/--diff 互斥未定義 → 皆缺 rc2、同給 diff 優先
- [major] 2>/dev/null 吞警告風險 → stream 釘死 stdout
- [major] 交付清單漏 README/README.en/ARCHITECTURE 4+ 處 41 計數 → 補齊
- minor×7（python fallback、Gate 0 限縮 debt、--all 語意、型別、fail-open 措辭、驗收全路徑、anchor 註記）

## r3（canary a missed / b caught → 輪無效；cap=3 到頂；slot1 findings 剔除、2 條經編排者機械覆核折入）
- [major] --diff 底層指令未釘死（pitfalls 是 -U3 全文 diff 勿照搬；含 slot1 的 --diff quotePath gap）→ 釘 `git -c core.quotePath=off diff --name-only <A..B>`
- [major] config fallback 提示 stream 未定（會被 hook 吞）→ 釘 stdout
- minor×6（PRIOR-ART 引用口徑〔調研節點 0 次 Herzig/CodeMaat/CodeScene，補來源節〕、support 硬底線全域+--all 超集、json 精度、exclude 合併測試、SKILL.md 子分類歸完整性/影響、6/6 數字）

## 收斂裁定（編排者，使用者預先授權決策）
PANEL GATE 在 cap=3 到頂形式未過（輪有效 4/6 caught、capture 殘餘高——lens-diverse panel 低重疊之統計假象）。裁定實質收斂：所有 ≥major 折入前經機械覆核、r3 opus 否決位僅 1 minor 且確認前輪折入零漂移。護欄：canary-log 連 2 missed（r2s2→r3s1）→ 本 loop 後續與下個 loop 審計員升 opus。
