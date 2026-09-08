severity: blocker
<!-- 外家否決席 r3(Codex, --sandbox read-only;原始逐字稿 r3-codex-raw.txt;正規化:去重複印出的第二份、去行尾雙空白) -->
severity: blocker

前輪①填 1 就過：修了但引入 X；不再可填 `reported`，但合法報告若在敘述或程式碼範例提及 `severity: minor`，會被額外計數或被殘留偵測誤拒。
引句:「★第三版:不讓人填,也不容忍格式★」

前輪②檔級行：修好；檔首專用檔級行使首條 finding 不會再被扣作檔級。
引句:「檔首(跳過開頭的 HTML 註解與空行)第一個非空行必須是檔級」

前輪③子字串 a1/a10：修好；r2 intake 的 `b1`–`b13` Markdown 表列可按換行列驗，整字邊界加同列 HIT/MISS 足以排除 a1→a10。
引句:「每個 id 要在 intake 檔裡有一列同時含「整字的 id」」

前輪④self-found 口袋：修好；移除可由人任意標註的集合，S 僅作「自找或漏併」的觀測推導。
引句:「★不加 --self-found-set★,存活多於席位報的 S 由讀側算式推出」

前輪⑤多席粒度：沒修好(重現)；同席可留下留痕列再留載體列，N 依列加總會重複，但 M/R 仍只取載體。
引句:「多席同輪時 M/R 只來自唯一載體,席位漏併進載體集合的機器查不到」

1. 未列殘留等級寫法可靜默少算

severity: blocker
blocking: 是；可被接受的報告把真 finding 寫成未偵測格式時，N 不再是機器可信的「報了幾條」。
引句:「新的寫法(例如把等級寫成「嚴重度:高」)不會被擋、也不會被數」
file: `governance/review-reports/審查有沒有用記帳/r3-snapshot.md:80` 最小重現：檔首 `severity: clean` 後寫 `Severity: blocker`、`sev: blocker` 或 `嚴重度：高`；皆非 `_report_severities` 的精確小寫 ASCII 宣告，計數仍為 0/少算且提案明定不拒收。

2. 同席重複記帳使 N 重複、S 被壓低

severity: blocker
blocking: 是；同一份席報告可有一筆留痕列及一筆載體列，現有寫側只 append，沒有 `(loop, round, auditor)` 唯一性守衛。
引句:「N=該輪席位列 `reported` 加總」
file: `scripts/lumos:5270` 最小重現：同一 `loop/r1/auditor` 先記一筆 `reported=2` 留痕，再記同報告的載體列 `reported=2, findings-set=f1,f2`；N=4、M=2、R=0，S 被算成 0，實際席位報數卻是 2。

總結最嚴重 severity: blocker；blocking 2 條。
