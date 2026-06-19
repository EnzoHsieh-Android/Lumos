# Lumos

> 🌐 English version: [`README.en.md`](README.en.md)

> **Lumos —— 揭開全 AI 開發的黑箱,照亮通往正確需求的路。**
>
> (路摸思:點亮咒。一邊照「程式碼」——把藏起來的為什麼、決策、硬合約照出來;一邊照「需求」——用繞不過的對話逼出理解,讓人走對路。Lumos 不替你把需求變對,它把路照亮、讓你自己走對。)

「**圖譜即合約**」方法論的**完整工具組唯一源**。把每一次全 AI 迭代織進「已理解的布」:知識圖譜是專案的唯一真相來源(為什麼這樣設計 / 邊界 / 不可改的合約),用 commit-time 強制力與可執行合約測試確保它不腐爛。

## 內容(完整工具組)

| 類別 | 檔案 | 作用 |
|------|------|------|
| **CLI** | `scripts/lumos` `scripts/test_lumos.py` | 純 python3 標準庫、零依賴。讀(context/search/contracts)、寫(set/append/new,寫後自驗)、巡檢(doctor)、歸檔(archive) |
| **合約守衛 scaffold** | `lumos guard list/scaffold/bind` | 對談驅動:列未綁的 ★INVARIANT★、套範本產**預設紅燈**測試 stub、把 `[test:]` 綁回 KEY 行。斷言本體由人/AI 確認意圖後填(非 code 反推)。範本技術棧專屬、放各專案 `.lumos/guard-templates/` |
| **git hooks** | `scripts/hooks/` | pre-commit 硬擋「改 code 沒更新圖譜」/ post-commit 留痕 / pre-push 跑 doctor |
| **安裝器** | `scripts/install-hooks.sh` `scripts/install-graph-toolchain.sh` `scripts/merge-claude-settings.py` | 把工具組裝進專案 / 設 hooks / 合併 Claude settings |
| **rename/歸檔** | `scripts/graph-rename.sh` `scripts/fetch-notesmd.sh` | 連結改寫(封 notesmd move) |
| **CLAUDE.md 紀律範本** | `scripts/templates/graph-discipline.md` | 「圖譜先行」紀律,注入各專案 CLAUDE.md |
| **skills** | `skills/lumos-project-notes` `skills/lumos-core-knowledge` | 寫給 AI 的圖譜讀寫規範(user-scope 共用) |

## 最快:一鍵 bootstrap(已導入的專案)

clone 一個已導入 Lumos 的專案後,在裡面跑一個指令——**連 Lumos 都自動幫你 clone**:
```bash
git clone <你的專案> && cd <你的專案>
python3 scripts/lumos bootstrap     # 自動:clone Lumos + skills + 全域 lumos + repo hooks
```
然後重啟 Claude Code session。`bootstrap` 是下面「兩種安裝」的自動版(專案自帶 vendored lumos 來跑它)。

## 兩種 scope、兩種安裝(底層;全新專案用 install-graph-toolchain)

Lumos 是**唯一源**;實際生效要分兩層裝(原因:CI 只 checkout 專案 repo、git hook 是 per-repo,所以工具組必須 vendor 進各專案):

**① 每台機器一次(user-scope)**
```bash
git clone <this repo> ~/harness/lumos-toolchain
cd ~/harness/lumos-toolchain
./install.sh                  # skills → symlink ~/.claude/skills/lumos-*
python3 scripts/lumos install # (選用) lumos → ~/.local/bin,全域可用
```
更新 = 在本 repo `git pull`(skills symlink 即時生效)。

**② 每個專案一次(project-scope,vendor 工具組進去)**
```bash
# 從 Lumos 跑,把工具組 vendor 進目標專案 + 注入 CLAUDE.md 紀律 + scaffold 圖譜 + 裝 hooks
~/harness/lumos-toolchain/scripts/install-graph-toolchain.sh --target <專案路徑> --slug <知識庫名>
```
之後該專案 `scripts/lumos`、`scripts/hooks/` 等是 vendored copy(供 CI / hook 自足);要升級就再從 Lumos 跑一次(idempotent:工具組更新、圖譜資料不動)。

## 邊界

Lumos 只放**通用的圖譜工具組**。各專案**自己的東西不進這裡**:業務圖譜內容、app 的發版/部署腳本(如 `release.sh`)、技術棧 skill(vue/csharp 等 project-scope skill)。

詳細上手見 [ONBOARDING.md](ONBOARDING.md);架構全景見 [ARCHITECTURE.md](ARCHITECTURE.md)(唯一源→兩種 scope→消費端、生命週期指令、22 子命令、強制力管線);與 SDD 的差異見 [SDD-vs-Lumos.md](SDD-vs-Lumos.md)。
