---
type: system
status: done
created: 2026-06-30
updated: 2026-06-30
self_audit: sonnet/2026-06-30
tags:
  - type/system
  - status/done
verified_by:
  - "[[Verification/2026-06-30_check-p-stale-claims]]"
summary: |-
  FLOW:Check P(doctor 段尾第 7 檢查)掃節點正文 inline-code 路徑 → 先 FENCE_RE.sub("",text) 剝 fenced、INLINE_CODE_RE.findall 後逐一 .strip("`") 剝反引號 → 刪尾端行號 :\d+(?:-\d+)?$ → 若含 "/" 且首段 ∈ repo_root 直接子目錄 → (repo_root/token).exists() 否 → warn_soft 軟提醒(不計 issues、不改 rc)
  KEY:repo_root 沿用 Check C 設的區域變數(同函式內 scope 複用,不重算);無 docs/ 佈局 repo_root is None → ok 跳過
  KEY:偽陽性防護:路徑須含 / ∧ 首段必在 top_dirs{p.name for p in repo_root.iterdir() if p.is_dir() and not p.name.startswith(".")} ∧ 跳 "://" (protocol)、跳已見路徑(seen_paths 去重) [test:t_doctor_check_p]
  KEY:軟提醒輸出格式:行號 `「<rel>:<line> → <token>(已不存在)」`,無行號 `「<rel> → <token>(已不存在)」`;與 warn_soft 閉包配對;不動 issues 計數與 doctor 終 rc
  DEP:FENCE_RE(:39)｜INLINE_CODE_RE(:40)｜warn_soft(閉包)｜repo_root(Check C 區域變數)
  TEST:t_doctor_check_p(案例 1-6:失效認領/存在不報/散文/fenced/無路徑/無docs佈局略過)
  VERIFY:[[Verification/2026-06-30_check-p-stale-claims]]
decisions:
  - content: Check P 採軟提醒 warn_soft(不計 issues、不影響 rc)而非硬封鎖 warn
    context: 圖譜節點引用死碼是「可能漂移」(碼被刪改)而非「必然破功」(wikilink 破連結);維護者需快速反應但不應被自動流程阻斷 push(給人工判斷空間)
    why_chosen: 對標 Check S(self_audit 過期)與 Check V(valid_under 日齡)都採軟策略,同等級提醒;硬封鎖適合「必須修的缺陷」(Check T/R),軟提醒適合「應該檢視的漂移」(Check S/V/P)
    decided: 2026-06-30
    valid: true
  - content: 路徑提取嚴格遵循 brief 規則避免偽陽性(須含 /、首段 ∈ top_dirs、跳 :// 與已見)
    context: 散文中大量「foo/bar」形圖案(maker/checker、API 慣例命名等);generic 規則會噪音爆表,須精確鎖定「repo 真實路徑」
    why_chosen: 段落中涉及 repo_root.iterdir() 盤點 top_dirs,當時的設計 cost 已付,複用 top_dirs 過濾首段 + seen_paths 去重可靠度高;protocol :// 與行號 :\d+ 都是分類器
    decided: 2026-06-30
    valid: true
  - content: Check P 插在段尾(Check V 之後、if ci: 之前);順序 T→R→S→H→K→V→P
    context: 新檢查應尾插(不改既有 1-4 與 G/L/C/T/R/S/H/K/V 排序);邏輯輕(repo root 檢查)應靠後
    why_chosen: doctor 從全圖(Check 1-4 orphan/unresolved/verified_by/plan_refs)→ 同名守衛/frontmatter/合約/可逆/審計/日齡/diff-hint/組合,末尾再掃 repo 路徑一致性
    decided: 2026-06-30
    valid: true
---
# check-p-stale-claims

doctor 的第 7 檢查 **Check P:失效檔案認領**——掃每個節點正文內 inline-code 路徑引用,若指向 repo 已不存在的檔案則 warn_soft 軟提醒(「圖譜指向死碼?」)。不計 issues、不改 exit code(rc0 軟提醒,rc1 才硬擋)。

與 [[Check T:★INVARIANT★ 合約測試綁定|Systems/check-t-sentinel]] / [[Check R:可逆性回退|Systems/check-r-guard]] 不同,Check P 是「可能漂移」信號而非「必然破功」,給維護者動機但不自動阻斷流程。

## 檢查邏輯

1. **無 docs/ 佈局 → 跳過** (`repo_root is None`)
2. **掃每個節點正文** `for rel, n in sorted(notes.items())`
3. **路徑提取**
   - 先 `FENCE_RE.sub("", text)` 剝 fenced code block
   - `INLINE_CODE_RE.findall(...)` 獲反引號區段 `` `...` ``
   - 逐一 `.strip("`")` 剝定界符
   - `_line_re.sub("", raw)` 刪尾端行號(`:10` 或 `:10-20` 形式)→ token
4. **篩選標準**
   - 跳 `"://"` (protocol — 不是 repo 路徑)
   - 須 `"/" in token` (非散文詞語)
   - `token.split("/")[0] in top_dirs` (首段必在 repo 直接子目錄)
   - 去重 `seen_paths` (同節點同路徑只報一次)
5. **檢驗 & 報告**
   - `(repo_root / token).exists()` 否 → 失效認領
   - 帶行號: `"<rel>:<line> → <token>(已不存在)"`
   - 無行號: `"<rel> → <token>(已不存在)"`
   - `warn_soft()` 印出但不計 `issues` 變數

## 觸發案例

| 案例 | 路徑 | 行號 | 跳過? | 理由 |
|------|------|------|-------|------|
| 1 | `` `scripts/ghost.py` `` | — | ✓ 報 | 檔不存在,Check P 抓到 |
| 2 | `` `scripts/real.py:10` `` | 10 | — | 檔存在,行號被剝,检查 pass |
| 3 | `` `and/or` `` | — | — | 無 /,非路徑 |
| 4 | `` `scripts/ghost.py` `` (fenced 內) | — | — | fenced 先剝,不進 span 清單 |
| 5 | `` `cmd_context` `` | — | — | 無 /,非路徑 |
| 6 | `` `scripts/deleted:行號` `` | 行號 | — | 含中文 `:\d+` 不配,token=原始字符(檢查 true) |

## 軟提醒 vs 硬擋

- **Check T/R** → 硬擋(rc1):合約必綁、不可逆必回退
- **Check S/V/P** → 軟提醒(rc0):self_audit 過期、valid_under >90 天、路徑死碼

軟提醒讓文檔維護者有審視的動力(Obsidian 側邊欄提示),但不阻斷 CI push(給人工判斷)。

## 與其他檢查的互動

- **Check C (core_refs)**:Check P 只掃 inline-code,Check C 掃 frontmatter `core_refs:` 欄位(互補)
- **Check 2 (Unresolved wikilink)**:Check P 掃 `` `路徑` ``,Check 2 掃 `[[wikilink]]`(語法不同)

## 實作細節

- `re.compile(r":\d+(?:-\d+)?$")` 匹配行號尾端並剝除
- `repo_root.iterdir()` 盤點 top_dirs(過濾隱藏檔、只取目錄)
- `seen_paths` 集合去重(同節點同路徑只報一次)
- `OSError` 捕捉讀檔失敗(跳過該節點)

---

**相關參考**

- [[Systems/lumos-cli-read]] — doctor 全圖權威巡檢
- [[Systems/check-t-sentinel]] — Check T:★INVARIANT★ 合約測試綁定(硬擋)
- [[Systems/check-r-guard]] — Check R:可逆性回退(硬擋)
