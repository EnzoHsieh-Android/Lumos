---
type: issue
status: done
created: 2026-07-24
related:
  - "[[Systems/lumos-cli-lifecycle]]"
  - "[[Systems/lumos-deinit]]"
  - "[[Projects/teardown一鍵拆機_計劃]]"
pitfall_when:
  - "content:_deinit_remove_vendored"
tags:
  - type/issue
  - status/done
summary: |-
  FLAG:ORIGIN
  KEY:bug=_deinit_remove_vendored(scripts/lumos:6293-6306)對 scripts/hooks、scripts/templates 兩夾整夾 shutil.rmtree(非逐檔白名單)——使用者若在這兩夾放自有檔(自己的 git hook / 範本),deinit/teardown 會一併永久刪除,reinstall 救不回(std Codex teardown審 F9,2026-07-24)
  KEY:root cause=移除端不對稱——頂層 5 檔走 _VENDORED_TOOLKIT 精準白名單,但兩個 dir 走整夾刪、硬假設「Lumos-owned」(docstring 6294-6295 自述)。安裝端 vendor 進這兩夾的檔沒留 manifest,故移除只能整夾刪或靠 src 列舉
  KEY:影響面=只在使用者往 scripts/hooks|scripts/templates 塞自有檔時咬人;標準 lumos 專案這兩夾純 lumos → 無感。deinit 與 teardown 皆中(teardown 呼叫 cmd_deinit);屬「destructive-but-recoverable」的例外——reinstall 復原不了使用者自有檔
  KEY:★已修(2026-07-24)★=_deinit_remove_vendored 改成★對稱安裝端逐檔刪★——安裝端 _vendor_toolchain 對兩夾走 src.rglob 逐檔 copy,故移除端也從 src 列舉 lumos 檔清單、只刪這些、保留使用者放這兩夾的自有檔;夾空了才移、有留檔則保留+warn。fallback(a):src 缺(None/來源夾不存在)→ 保守留夾+warn 不刪(never delete unknown)。cmd_deinit 傳 src 進去(原簽名沒傳)。[test:t_deinit_remove_vendored_preserves_user_files,t_deinit_remove_vendored_no_src_conservative]
  DECISION:[2026-07-24 修]走「對稱安裝端逐檔白名單」正解(非最小版),使用者要求解 F9 即修;fallback 選(a)保守留夾(使用者裁定,never delete unknown)。同批繼承殘留 F4(剝 CLAUDE.md 正規化 sentinel 外)、F12(uninstall 移全部 skills)仍記於 [[Systems/lumos-cli-lifecycle]]、未修(影響更小、未開票)
---
# deinit 整夾刪使用者檔（F9）

## 現象
`lumos deinit`（及呼叫它的 `lumos teardown`）移除 vendored 工具時，對 `scripts/hooks/`、`scripts/templates/` 兩個資料夾**整夾 `shutil.rmtree`**。若使用者在這兩夾放了自有檔（自己的 git hook、自己的範本），會被**一併永久刪除**，且 `reinstall`/`bootstrap` 復原不了。

## Root cause
`_deinit_remove_vendored`（`scripts/lumos:6293-6306`）的移除策略不對稱：
- **頂層 5 檔**走 `_VENDORED_TOOLKIT` 固定白名單——精準，只刪 lumos 檔。
- **兩個 dir**（`scripts/hooks`、`scripts/templates`）走整夾遞迴刪，docstring 自述「Lumos-owned，不靠 src 列舉」——**硬假設這兩夾純屬 lumos**。

安裝端 `_vendor_toolchain` 沒有留下「vendor 進這兩夾了哪些檔」的 manifest，所以移除端拿不到精準清單，只能整夾刪。

## 影響面
- **只在**使用者主動往 `scripts/hooks/`／`scripts/templates/` 放自有檔時才咬人。標準 lumos 專案這兩夾是純 lumos 的 → 無感。
- `deinit` 與 `teardown` 都中（teardown 內部呼叫 `cmd_deinit`）。
- 破壞了「destructive-but-recoverable」的宣稱——reinstall 救得回 lumos 檔，救不回使用者自有檔。

## 提議修法（未實作）
1. **逐檔白名單化（正解）**：安裝時記錄 vendor 進這兩夾的檔清單（manifest），移除只刪 manifest 內檔＋夾空了才刪夾；夾非空（有外來檔）→ 刪 lumos 檔、保留夾＋使用者檔＋warn。
2. **最小版**：`rmtree` 前掃夾內有無「非 lumos 已知」檔，有則保守只刪已知檔、留其餘。

## 已修（2026-07-24）
使用者要求解 F9 → 走**提議修法 1（逐檔白名單，正解）**：`_deinit_remove_vendored(root, src)` 從 `src/scripts/hooks/**`、`src/scripts/templates/**` 列舉 lumos 檔（對稱 `_vendor_toolchain` 的 rglob 安裝），只刪這些、保留使用者自有檔、夾空了才移、有留檔則保留＋warn。fallback 選 **(a)**：src 缺（來源 clone 沒了/沒給 `--source`）→ 保守留夾＋warn、不刪（never delete unknown）。`cmd_deinit` 傳 `src` 進去。

測試：`t_deinit_remove_vendored_preserves_user_files`（使用者 hook/範本保留、lumos 檔刪）、`t_deinit_remove_vendored_no_src_conservative`（src 缺保守留）、既有 `t_deinit_remove_vendored` 更新傳 src ＋端到端 `t_deinit_cmd_basic`/`t_deinit_graph`（`_deinit_run` 注入真 repo 當 src）——全套 1372 綠。

來源＝Codex 跨家族審 teardown 設計時揪出（見 [[Projects/teardown一鍵拆機_計劃]] 審計修正紀錄 F9）。**同批 F4/F12 仍未修**（影響更小，留 [[Systems/lumos-cli-lifecycle]] 殘留紀錄）。
