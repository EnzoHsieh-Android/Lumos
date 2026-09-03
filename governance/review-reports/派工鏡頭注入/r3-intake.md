# r3 前置留痕(派工鏡頭注入)

日期:2026-09-03(晚)。r3=上限輪、末輪驗收紀律:只審 r2→r3 delta(r2 折入的 12 處+定序一句)與銜接處;新 minor 照寫照記。
機械排乾:refcheck ok 6/missing 0;prose-lint 0;pitfalls --check 有節;lint 0;doctor 0。

## 收貨三道(五席)

| 席 | 條數 | 最高 | blocking | quote-check | refcheck |
|---|---|---|---|---|---|
| s1 通才 | 2 | blocker | 1 | 全錨 | 13/13 |
| s2 載荷安全 | 4 | blocker | 3 | 全錨 | 11 ok / 2 missing(臨時 repo 路徑) |
| s3 極端輸入 | 6 | blocker | 2 | 全錨 | 6 ok / 1 missing(臨時 repo 路徑) |
| arch 架構對齊 | 4 | major | 4 | 全錨 | 17/17 |
| ext Codex | 5 | major | 4 | 1 句錨不到(f3「固定席「清單」」巢狀引號截斷)→ f3 不採信;內容(藏)升格 d3 | 4/4 |

合計 21 條(2+4+6+4+5)、blocking 14(1+3+2+4+4)、blocker 4(s1-f1/s3-f1 合約行判定同題、s2-f1 主線 ref 可被樹內 hook 改、s2-f2 快取可偽造)——逐檔 grep 數的。

## 佐證通道機械重現(編排者)

- s1-f1 / s3-f1 / cx-f4 / arch-f8「合約行不在行首」:`grep -n "^INVARIANT_RE\|^CHECKPOINT_RE\|^IRREVERSIBLE_RE" scripts/lumos` → 2405/2776/2777 皆 `^KEY:` 錨定 → HIT。
- s2-f1「樹內 hook」:`git config core.hooksPath` → `scripts/hooks`(樹內)→ HIT;編排者首版寫「未指向樹內」是錯的,已改並立 Issue。
- s1-f2 / s3-f6「remote 不叫 origin」:`git remote -v` → 只有 `Lumos`;`git rev-parse --abbrev-ref main@{upstream}` → `Lumos/main` → HIT,改用 upstream。
- arch-f7/f8/f9/f10「重寫既有 helper」:主線判定 `scripts/lumos:16748-16760`、`find_vault` 11391、`_git_commit_exists` 2971 → 開檔核 HIT。
- s3-f2「子目錄 ls-tree 相對路徑」:s3 臨時 repo 實測;git 文件語意一致 → HIT。
- s2-f3「find_vault 取排序第一個」:`scripts/lumos:11375-11400` → HIT。

## 處置摘要

20 條採信全折(blocker 輪 accepted 必空);不採信 1 條(cx-f3)內容升格 d3。
折入=hook 薄殼/邏輯進 lumos `dispatch-lens`、base 樹解析圖譜根與白名單、主線 upstream 優先、快取私有目錄+owner 檢查、範圍文法收緊、SHA-256、--show-toplevel、威脅模型(checkout 即執行=repo 整體風險,立 Issue)、d3。
★上限輪:r3 折入的新段落(薄殼分層、base 樹解析、快取 owner 檢查)沒有第四輪,攤 Enzo。★
