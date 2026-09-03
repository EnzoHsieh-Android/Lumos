## 第一輪六條驗收

- r1-f1: 已解——明定 hook 加入 `ANCHOR_FILES`，並納入 `anchor approve`。
- r1-f2: 未解——§3 已限 code-loop，但共用的 §7.6 同時要求「code 改標記」與「design 不動」，無法照字面同時成立。
- r1-f3: 已解——明定以 hook payload 的 `cwd` 傳入 `--repo`。
- r1-f4: 未解——顯示內容雖改讀 base，但固定席的選取仍由待審工作樹圖譜計算，且 base 未驗證為可信主線。
- r1-f5: 已解——零固定席明定不注入，並新增零篇驗收。
- r1-f6: 未解——§3 已不碰 design-loop，但共用 §7.6 仍留下無範圍的衝突。

## 範圍與模板

### f1

severity: major  
blocking: 是

引句:「代碼迴圈的架構對齊席 §7.6「圖譜裡相關功能筆記」那格→同一行標記。」

file: `governance/review-reports/派工鏡頭注入/r2-snapshot.md:95`  
file: `/Users/enzo/.claude/skills/lumos-design-loop/templates.md:236`

§7.6 是 code-loop 與 design-loop 共用的單一模板，沒有 code-only 分支；把第 245 行改成標記必然也改到 design-loop，與 spec 第 97 行「設計迴圈 §1/§7.6★不動★」互斥。照字面實作仍會讓無 diff 範圍的 design-loop 帶標記，或根本無法完成指定修改。

## 待審分支載荷

### f2

severity: major  
blocking: 是

引句:「內容用 `git show <base>:<節點路徑>` 讀★base 那版★」

file: `governance/review-reports/派工鏡頭注入/r2-snapshot.md:83`  
file: `scripts/lumos:16400`

`impact --diff --json` 的 `node` 實際是 vault-relative 路徑，例如 `Systems/lumos-cli-lifecycle.md`，不是 repo-root-relative；直接代入會執行 `git show <base>:Systems/...`，而真正 tracked 路徑是 `docs/<vault>/Systems/...`。spec 沒定義 vault 路徑解析，照字面做會令所有既有節點都被誤判為「本分支新增」。

### f3

severity: major  
blocking: 是

引句:「理由:工作樹的圖譜筆記是待審分支的一部分」

file: `governance/review-reports/派工鏡頭注入/r2-snapshot.md:83`  
file: `scripts/lumos:16371`

內容雖從 base 讀，但 `impact --diff` 建立 `Env` 時仍載入工作樹 vault，因此哪些節點入選、節點名、關係與合約分類仍受待審分支控制。這只隔離了正文，沒有隔離固定席清單本身，待審者仍可刪改關係以壓掉應出現的主線固定席。

### f4

severity: major  
blocking: 是

引句:「base=標記左側;節點在 base 不存在」

file: `governance/review-reports/派工鏡頭注入/r2-snapshot.md:83`

spec 沒規定 `<base>` 的生產者，也沒驗證 resolved base 是可信主線或待審 HEAD 的共同祖先；填成待審分支上的任意 commit 時，`git show` 仍會讀到攻擊者控制的筆記。把「左側可解析」等同「不可控主線」使載荷隔離合約可被標記本身繞過。

## 錨點與知識同步

### f5

severity: major  
blocking: 是

引句:「`ANCHOR_FILES` 加一行並 `lumos anchor approve`。」

file: `governance/review-reports/派工鏡頭注入/r2-snapshot.md:89`  
file: `docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md:16`

現況圖譜把機制明定為「5錨點」及「runner×2+hooks×3」，新增第六個錨點後 spec 沒要求同步此唯一真相來源。照計畫只改 code/baseline，會使圖譜合約與 `ANCHOR_FILES` 現況直接矛盾。

## `--repo`、零固定席、enforcement 四元組

已讀，無 finding。

## 時間預算、快取、失敗放行、回滾

已讀，無 finding。

最高 severity：major；blocking 5 條。
