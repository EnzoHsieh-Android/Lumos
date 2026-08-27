# r1 正確性席（claude/sonnet）
severity: minor

Finding 1 — clean（核心不變式查證通過）
引句(scripts/lumos:4022): `★純記帳,不改降級規則★:降級去向仍由 folded/accepted 決定,本欄只記辯方怎麼表態、不回頭改判閘。`
窮舉 refute_verdicts 出現點＝gov stats 聚合/讀回 mapper/簽章/early guard/寫側驗證/argparse/dispatch。disposal gate（scripts/lumos:11010-11012）只讀 findings_set/folded_set/accepted_set，完全不讀 refute_verdicts。不變式成立，非 blocker。

Finding 2 — minor（evidence 態未與 accepted-set 交叉核對）
file:line: scripts/lumos:3427-3428
evidence 態被統計文案當「實際降級的候選池」，但寫側不核對該 id 是否真在 accepted-set。有人記 f1=evidence 而 f1 在 folded → 統計「拿反證降級 1」但 f1 沒降，挖空該欄用途（重啟條件樣本池不可信）。

Finding 3 — minor（測試名實不符）
file:line: scripts/test_lumos.py:5159-5160
「不改判閘」斷言只比對存回的 folded_set/accepted_set，從未真跑 loop status --disposal，未涵蓋「加了 --refute-verdict 後判閘結果不變」的不變式。若日後判閘改讀 refute_verdicts 仍恆綠。非假綠（若覆寫 folded_set 會翻紅）但覆蓋不足。

Max severity: minor
