preflight-4: ran

# r1 前掃留痕(派工鏡頭注入)

日期:2026-09-03(晚)。前掃席=haiku,固定四項清單(未定義詞/壞引用/範圍矛盾/機械宣稱驗語意),
外加 11 條機械宣稱清單逐條實開檔驗。編排者對每條回原檔核過再處置。

## 機械排乾

- `lumos refcheck` — 對得上 3 / missing 0 / out_of_range 0
- `lumos prose-lint` — 0 處模糊措辭
- `lumos pitfalls --check` — 有節(命中 self-governance,已答)
- `lumos doctor` — 全圖 0 issues(406 篇)

## 前掃四項結果(haiku,55 次工具呼叫)

①未定義詞:無。②壞引用:無(11 條交叉引用逐條開檔)。③範圍矛盾:報 1 條(見語意-1,編排者核為誤讀)。④機械宣稱:11 條中 7 對、3 部分對、1 誤讀。

## ④ 語意類命中(修改前→後;席位可覆核推翻)

### 語意-1 「同位置的 impact-hook.py」被讀成「同 matcher」(前掃誤讀,但措辭確實含糊)
- 前掃:現行 impact-hook 掛 `Edit|Write|MultiEdit`,不是 Agent → 判「設計與實裝矛盾」。
- 編排者核:原意是「同一個事件 PreToolUse」,matcher 本來就不同;不是矛盾。
- 修:「同位置的」→「同事件、不同 matcher 的(它掛 Edit|Write,本案掛 Agent)」。

### 語意-2 「固定席每篇標為什麼被釘、被哪個檔牽連」是文字說明非結構欄位(部分對)
- 前掃:`_print_sync_nudge` 文字版有備註但非欄位。
- 編排者實跑 `lumos impact --diff c3b4f3f~1..c3b4f3f --json`:results 每筆有 `pinned/kind/contract/files` 四個結構欄位(HIT,20 筆/12 釘)。
- 修:內容段改明指 `--json` 欄位,hook 讀 JSON 不 parse 文字。

### 語意-3 「d9 的 cap=8」——d9 只訂截錄,8 是函式預設(部分對)
- 修:兩處改成「d9 訂截錄規則,上限值沿 `_print_sync_nudge` 預設 8」。

### 語意-4 「四支既有 hook」——目錄五支、現役四支(計數含糊)
- 修:改「四支現役 hook(_GLOBAL_CLAUDE_HOOKS;第五支 verification-rot-check.py 已停用)」。

### 語意-5 「code-loop/design-loop 各自的 templates.md」——只有 design-loop 有(前掃判對但補註)
- 修:改「兩套模板都住 lumos-design-loop/templates.md §1/§3」。

### 語意-6 arXiv 數字是轉引(部分對)
- 修:PRIOR-ART 註明轉引來源,本案未重讀論文。

其餘 C5/C6/C7/C8/C10 前掃逐條開檔判「對」,編排者抽核 C7(enforcement儀表板_計劃 內層 20s>外層 10s)、C8(code席爆炸半徑供糧_計劃:25 原文)一致。

## 收貨三道(五席)

| 席 | 條數 | 最高 | blocking | quote-check | refcheck | seat-check 未提材料 |
|---|---|---|---|---|---|---|
| s1 通才 | 9 | blocker | 5 | 全錨 | 13/13 | 5(advisory) |
| s2 接手的人 | 9 | blocker | 7 | 1 句錨不到(f3「照 d9:前 8 篇貼內容,其餘只列名」是改述非逐字)→ f3 不採信 | 18/18 | 10 |
| s3 簡化守護 | 10 | blocker | 7 | 1 句錨不到(f2 引句內含巢狀「」,機械截斷)→ f2 不採信 | 5/5 | 6 |
| arch 架構對齊 | 4 | major | 1 | 全錨 | 21/21 | 10 |
| ext Codex | 6 | major | 6 | 全錨 | 13/13 | 1 |

合計 38 條(9+9+10+4+6)、blocking 26(5+7+7+1+6)——逐檔 grep `^### f` 與 `^severity` 數的。
不採信的兩條內容(d9 只限代碼迴圈)與 codex-f2/s1-f8/s3-f2 重複,已透過他席折入;帳上不計。

## 佐證通道機械重現(編排者)

- s1-f5 / s2-f8 / s3-f7「impact --diff 耗時」:`time scripts/lumos impact --diff c3b4f3f~1..c3b4f3f --json` 12.1s(s1 實測)、`8dd2a12~1..944c2de` 41 檔 17.7s(s2 實測);編排者自跑 `c3b4f3f~1..c3b4f3f --json` 回 20 筆/12 釘 → HIT。
- s3-f5「files 欄位=diff 檔名逐字」:`scripts/lumos:16356` 讀 `git diff --name-only`、`:16399` 原樣寫進 JSON → 開檔核 HIT。
- s2-f2「enforcement 寫死四元組」:`scripts/lumos:12109-12112` 四元組字面存在、不讀 `_GLOBAL_CLAUDE_HOOKS` → HIT。
- s2-f5「review-reports patch 污染固定席」:`templates.md:108-110` 填寫雷①原文存在 → HIT。
- codex-f1 / s1-f1 / s2-f1 / s3-f3「錨點硬約束」:`Verification/2026-09-03_派工攔截點實測.md:71-75` 原文「硬約束,不是提醒」→ HIT(編排者本人所寫,首版撤掉=同日前案死因⑥重演)。
- codex-f3「--repo 未帶」:`scripts/lumos:16345-16351` 無 --repo 時從 cwd 往上找 → HIT。

## 處置摘要

36 條採信:全折(arch-f1「updatedInput 第二種做法」折成 d2 有意識偏離——實測唯一通道、永不 deny、進錨點;blocker 輪 accepted 必空,不走放行)。
★blocking 密度 26 條/約 5000 字,超過 skill「>1 條/300 字建議整份重寫」門檻;編排者判核心(鏡頭/標記/代碼迴圈)未被推翻,在同編號折入,重寫與否攤給 Enzo。★
