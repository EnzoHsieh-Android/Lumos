severity: minor

整體判斷:說明文字和三支搬走的測試對得上,沒有改到會影響行為的程式。只有一條措辭上的小毛病。

**檢查一:說明講的搬遷對象與三支測試的斷言**
- 引句:「③ 搬到 t_prepush_newbranch_merged_tip、④⑤ 搬到 t_prepush_newbranch_tip_on_main、」
  - `t_prepush_newbranch_merged_tip`(scripts/test_lumos.py:30122)只剩 ③:先合過主線再首推,斷言放行。
  - `t_prepush_newbranch_tip_on_main`(scripts/test_lumos.py:30147)含 ④:頂端已在主線,放行。⑤ 有兩個斷言:舊值找不到擋下,推標籤只提醒。
- 引句:「⑥⑦ 搬到 t_prepush_newbranch_range_fallback(判準不變)。」
  - `t_prepush_newbranch_range_fallback`(scripts/test_lumos.py:30165)含 ⑥:`push-range` 失敗退回空樹並講一句。⑦ 是被訊號殺掉就停下。
  - 原測試留下 ① 和 ②,說明寫的「S1、S2」與計劃節 S1、S2 一致。

**檢查二:翻紅釘有沒有跟著測試走**
- 引句:「翻紅釘:掛鉤不呼叫 push-range(照舊空樹)→ ①紅。」
  - 原測試只剩 ①② 兩組,翻紅釘只列 ① 合理。
  - 新三支的翻紅釘(③紅、④紅、⑥紅/⑦紅)各自對應自己的斷言。

**檢查三:允許名單那行註解**
- 引句:「2026-11-07 [[Projects/Android寫法回合結束檢查與改檔前推列_計劃]] 佔位符 → 詞的共用核心」
  - 只改了註解文字,`ALLOWED` 集合的成員沒變,沒有改到行為。
  - 這個計劃連結是否存在,我沒有逐一查。

**檢查四:範圍內有沒有動到其他程式**
- `scripts/` 下除 `test_lumos.py` 外沒有任何改動。`test_lumos.py` 本身的改動只落在這兩處說明文字。
- 計劃筆記 S3 到 S6 的 `[test:]` 綁定和 `存量漂移守衛.md` 的 `[test:]` 清單,都已經指到新測試名。

severity: minor
blocking: 否
引句:「[新分支首推 S1、S2] 推分支的新分支首推(遠端舊值全零)改用」
- 新測試說明用的 S3、S4、S5、S6 對應計劃節,但 ⑦ 的訊號中斷情境被併進 S6。
- 搬到 `t_prepush_newbranch_range_fallback` 的說明只寫「S6」,沒寫 ⑦ 屬於 S6 的後半句。
- 這只是標示不夠細,不影響行為。
- 佐證 file:`scripts/test_lumos.py:30166`;計劃節在 `docs/lumos-toolchain-knowledge/Projects/新分支首推會擋的閘改用真起點_計劃.md:67`。

總結:說明裡的搬遷對應都跟三支測試的實際斷言一致,沒有改到任何會影響行為的程式,只有一條不擋推送的標示小瑕疵。
