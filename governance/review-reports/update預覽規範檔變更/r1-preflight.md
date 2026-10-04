# update預覽規範檔變更_計劃 — 前掃報告

## ① 未定義的旗標

**計劃原句** (第 29 行)：
> 做:`lumos update --dry-run`,預覽三件事——每個紀律區塊目標檔(CLAUDE.md、AGENTS.md 或 AGENTS.override.md)會怎麼變、哪些工具檔會被換新、其餘會做但這裡不細算的動作。

**查到的事實**：
`scripts/lumos:45837-45841` — update 子命令的 argparse 定義只含三個旗標：
```
p = sub.add_parser("update", help="從 Lumos 唯一源更新本專案 vendored 工具組")
p.add_argument("--source", help="Lumos 來源 repo 路徑...")
p.add_argument("--no-pull", action="store_true", help="不 git pull 來源,用現有")
p.add_argument("--allow-stale", action="store_true", help="來源拉不到最新時...")
```
缺少 `--dry-run` 旗標。`cmd_update` 函式簽名（20912 行）也沒有 `dry_run` 參數。

**結論**：
計劃要求的 `--dry-run` 旗標在程式碼中不存在；旗標加入計劃的預實作。

---

## ② 機械宣稱不符 — 函式拆分

**計劃原句** (第 34-35 行，做法第 2 項)：
> 把 `_reinject_claude_block` 拆成「算出新內容」與「寫回去」兩段,預覽只呼叫前一段;真的 update 走同一段算法,兩邊不會算出不同的結果。

**查到的事實**：
`scripts/lumos:20311-20395` — `_reinject_claude_block` 函式定義。檢查內容：
- 第 20321-20323 行：計算 body（`_expected_claude_body` 呼叫）
- 第 20331-20339 行：讀目標檔
- 第 20342-20345 行：目標不存在時 **寫檔** (`_write_lf` 在 20344)
- 第 20347-20350 行：sentinel 檢查
- 第 20352-20367 行：無區塊時 **寫檔** (`_write_lf` 在 20366)
- 第 20384-20387 行：有差時 **寫檔** (`_write_lf` 在 20387)

函式為單一整體，尚未拆成「算出新內容」（無寫檔）與「寫回去」（執行寫檔）兩段。

**結論**：
計劃預期的函式拆分在程式碼中尚未實施；現況是單一函式整合計算與寫檔邏輯。

---

## ③ 範圍自相矛盾

**無** — 範圍（第 27-30 行）與做法（第 32-40 行）、驗收條款（第 51-57 行）之間無明顯自相矛盾。

---

## ④ 其他機械宣稱驗語意

**無誤命中** — 以下宣稱驗證通過：

1. 「套用時現在只印 CLAUDE.md 的前 20 行差異」
   - `scripts/lumos:20294-20296` ✓ 正確實作

2. 「真的 update 在來源 repo 只刷新紀律區塊」
   - `scripts/lumos:20925-20931` ✓ 正確實作

3. 「`lumos deinit --dry-run` 只印會動到什麼」
   - `scripts/lumos:20020-20033` ✓ 正確實作（純預覽，無 mutation）

4. 「工具檔用 `_VENDORED_TOOLKIT` 加 `_VENDORED_TREE_FILES`、逐位元組比」
   - `scripts/lumos:20579-20602` (常數定義) ✓
   - `scripts/lumos:20608-20611` (逐位元組 digest 函式) ✓ 正確實作

---

## 壞引用（[[...]] 連結）

**無** — 計劃引用的三個連結均存在於 docs/lumos-toolchain-knowledge/ 底下：
- `[[Projects/交接2026-10-03_計劃]]` ✓ 存在
- `[[Systems/lumos-cli-lifecycle]]` ✓ 存在
- `[[Systems/lumos-deinit]]` ✓ 存在

