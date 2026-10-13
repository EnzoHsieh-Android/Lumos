severity: minor

我在 `211ccd4e` 的淺複製上驗過:`lumos lint` 四篇(計劃、`Systems/loop-convergence-recording`、兩篇新 Issue)都是 0 問題,`lumos doctor` 是 0 issues,`-k quote_full_span` 78 條全綠。沒有碰到 `Systems/design-loop` 的 ★INVARIANT★(處置閘第五步)。`Systems/loop-convergence-recording` 新增的 WHY/RULE 跟程式現況一致,`[retire:when-symbol:scripts/lumos::_quote_rows_full_span_v1]` 指到的符號存在。第二階段的項目沒有被提前做:`_QUOTE_WRITE_RULE` 仍是 `legacy`,`templates.md` §1 錨定紀律那行、`_CODEX_AGENT_INSTRUCTIONS`、其他文件都沒動。

1. 第一階段提交順帶改了計劃沒列的兩份技能文件
severity: minor
blocking: 否
引句:「折入要**新增機制**(新設定鍵、新帳欄、新指令或旗標)時,先在審計修正紀錄寫一行」
file: `skills/lumos-design-loop/SKILL.md:34`
- 計劃〈兩階段上線〉寫「文件一句都不改」,〈同步改的地方〉第一階段只列 `scripts/lumos` 與 `scripts/test_lumos.py`。
- 這個提交卻改了 `skills/lumos-design-loop/SKILL.md`(新增「折入要新增機制」一條)和 `skills/lumos-design-loop/templates.md`(回滾席那一列加了「列出所有凍結、補凍、重算入口」)。
- 這兩條來自跑滿回顧和新 Issue「凍結接受非綠判定」,跟引句判準無關,所以不違反「不能先寫整段保證」的原意。
- 但計劃的第一階段清單沒登記,Systems 節點也沒寫,接手的人在計劃裡查不到。
- 建議補一句進計劃〈同步改的地方〉第一階段,或拆成獨立的 docs 提交。

2. gov --stats 四格互斥只靠「五筆全是引句判準」釘住,先判開頭這個順序沒有被釘
severity: minor
blocking: 否
引句:「四格互斥:先判 note 開頭是不是 quote-rule:(引句判準擋下,note 裡可能引到別的字樣),其餘照原本的包含判斷」
file: `scripts/test_lumos.py:26938`(`t_quote_full_span_compare_and_event`)
- 我把 `_rn` 與 `_rf` 的來源從 `_rest` 改回 `_rej`,也就是回到「note 裡含 report-not-normalized 就算那一格」。
- 改完後 `-k quote_full_span_compare`(15 條)和 `-k gov_stats`(59 條)全綠,這個破壞沒被抓到。
- 原因是測試裡 5 筆 `quote-rule:` 事件的 `quote=` 片段都不含 `report-not-normalized` 或 `findings-over-reported`,也沒有混合其他種類擋下事件的案例。
- 這個先判開頭的順序是程式註解自己說的理由,卻沒有測試守它。
- 建議加一筆 `quote=` 片段含 `report-not-normalized` 的引句擋下事件,斷言它只進「引句判準」那一格。

其他核對結果:
- 計劃 S1–S8 的條款字面和測試斷言逐條對得上。S5 的「載體列之後有無章非載體列也不影響」,是靠 `gate()` 讀到的章必須是 v1 釘住的。
- Verification 與 Issue 寫的數字略有出入:Verification 寫 306 個已凍結迴圈,Issue 與計劃寫 305 份判定檔,我數到 307 份,其中 rc1 恰好是 Issue 列的那 5 份。多的可能是併入主線的新增,不影響結論。
- 新 Issue「消費專案接入靜默失效回放漂移」我重現了:回放確實報 `留痕` 漂移,和 Issue 描述相符。
- 我另外跑了五類邊界輸入,結果都符合計劃:前綴照抄加編造、第二對沒有標籤的引號、`」` 出現在圍欄內、1 萬個落單收尾引號、5 萬層巢狀。其中圍欄內的落單 `」` 會判 stray,這是計劃明定「不遮蔽」的取捨,不算 bug。

實驗目錄 `/tmp/lumos-seat-work/code-引句錨定整段比對/合約-sonnet/` 已刪除。

總結:最高等級 minor,blocking 共 0 條
