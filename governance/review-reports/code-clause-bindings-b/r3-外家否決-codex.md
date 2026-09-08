<!-- 外家否決席 -b r3(Codex gpt-5.6-sol, xhigh, --sandbox read-only);原始逐字稿 r3-codex-raw.txt;正規化:去行尾雙空白、去重複印出的第二份 -->
severity: major

前輪 1 — 修了但引入 finding 1：直接的未閉合 `` `[S2] `` 已擋、`` ``[S2]`` `` 正確略過，但 `` `x [S2] `` 仍靜默放行。
引句:「反引號在編號前讓條款消失而放行(→ 原始行像條款就擋)」

前輪 2 — 修了但引入 finding 2、3：```／~~~ 交錯已修好，但未比對圍欄長度，且四空白縮排仍被誤認成圍欄。
引句:「```/~~~ 交錯反轉可見性(→ 圍欄各自配對)」

前輪 3 — 修了但引入 finding 4：①、⑴ 已擋，㈠、ⅰ 仍被當散文而放行。
引句:「圈號 ① 也是清單,沒標就擋(-b r2 外家 #3)」

前輪 4 — 修了但引入 finding 4：cf.／vs.／注:／詳見: 已不誤擋，但同次收窄也讓 `aa.` 編號靜默放行。
引句:「字母編號限單字母且帶分隔符,cf./vs. 是散文」

前輪 5 — 修好：舊的未閉合反引號註解已移除，docstring 與實作都改成截斷後段。
引句:「★哪些字看得見=沿用全檔唯一那兩份實作★:_visible_lines」

前輪「沒修好」1 — 修好：`→ [S1]`、`| [S1] |`、`> [S1]` 第二次出現均產生 duplicate 並阻擋。
引句:「不管這個編號有沒有在別處合法定義,都要擋」

前輪「沒修好」2 — 修了但引入 finding 5、6：單純跨行註解已略過，但同列關閉再開啟、行尾開啟及註解內 fence 的狀態轉換仍錯。
引句:「跨行 HTML 註解 <!-- … -->:整段不算內容」

1.
severity: major
blocking: 是 — 認不得的反引號前綴仍可令真條款消失後放行，符合「認不得→放行」。
引句:「原始行看起來是條款定義、遮完反引號卻看不到 [SN](反引號在編號前面)→ 認不得就擋,不放行」
file: `scripts/lumos:4106` 最小重現為合法 S1 後接 `` `x [S2] 真條款沒標 ``；HEAD 只回 S1/manual，gate=`ok`。

2.
severity: major
blocking: 是 — 四反引號圍欄被三反引號提前關閉，令合法計劃中的程式碼範例被誤擋。
引句:「開著的圍欄是哪一種(``` 或 ~~~):只有同一種才能關」
file: `scripts/lumos:2536` 最小重現 ````\n```\n- [S1] 圍欄範例\n``````；HEAD 把 S1 判為 untagged、gate=`fail`，因為只保存前三個圍欄字元。

3.
severity: major
blocking: 是 — 四空白縮排不是 Markdown fence，卻會吞掉其後真條款並放行。
引句:「fenced code 邊界(``` 與 ~~~ 都是 CommonMark 圍欄;2026-09-08 條款綁定 -b r1 外家席補 ~~~)」
file: `scripts/lumos:2534` 最小重現 `    ```\n- [S1] 真條款沒標\n    ````；HEAD 因 `lstrip()` 得 `rows=[]、gate=skip`。

4.
severity: major
blocking: 是 — 未收錄的明顯編號被當散文，符合「認不得→放行」。
引句:「a. / 一、/ 十一、/ 甲) / ① 這種短編號也是清單;★單字母且必帶分隔符★」
file: `scripts/lumos:4080` 合法 S1 後分別接 `aa. [S2]`、`㈠ [S2]`、`ⅰ [S2]`，三案皆得 S2=`undefined,listlike=false`、gate=`ok`。

5.
severity: major
blocking: 是 — 註解狀態以整行丟棄，既會放出仍在註解內的條款，也會吞掉註解前的真條款。
引句:「跨行 HTML 註解 <!-- … -->:整段不算內容(單行的由 _strip_inline_markup 剝)」
file: `scripts/lumos:2543` 最小重現 `<!--\n-->  <!--\n- [S2] 註解\n-->` 得 `fail-untagged`；`- [S2] 真條款沒標 <!--\n-->` 則只剩合法 S1、gate=`ok`。

6.
severity: major
blocking: 是 — 註解內的 fence 先於註解狀態被處理，會吞掉註解結束後的真條款。
引句:「fenced code 邊界(``` 與 ~~~ 都是 CommonMark 圍欄;2026-09-08 條款綁定 -b r1 外家席補 ~~~)」
file: `scripts/lumos:2535` 最小重現 `<!--\n```\n-->\n- [S2] 真條款沒標\n````；HEAD 只回合法 S1/manual，gate=`ok`。

最嚴重 severity: major；blocking 6 條。
