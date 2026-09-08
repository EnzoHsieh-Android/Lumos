<!-- 外家否決席 -b r2(Codex gpt-5.6-sol, xhigh, --sandbox read-only);原始逐字稿 r2-codex-raw.txt;正規化:去行尾雙空白、去重複印出的第二份 -->
severity: major

前輪 1 — 修了但引入 finding 1：雙反引號與條款後的未閉合反引號已成 `untagged/fail`；`` `[S1]` 條款 `` 按 inline-code 規則跳過，`[S1] 甲 `x` [test:t_ok] `y`` 為 `bound/ok`，但未閉合反引號放在編號前仍可靜默放行。
引句:「雙反引號 span 先剝,再剝單反引號 span(沿用 INLINE_CODE_RE)」

前輪 2 — 修了但引入 finding 2：單獨 `~~~` fence 已遮住內容，但與 ``` 交錯會反轉可見性，讓範例成為證據並吞掉真條款。
引句:「if ln.lstrip().startswith(("```", "~~~")):」

前輪 3 — 沒修好(重現)：`- [S1] 已標 [manual:人看一次]\n→ [S1] 第二次定義沒標` 仍只產生第一筆 `manual`，處置閘回 `ok`；同編號的未知清單項被既有定義遮掉。
引句:「listlike = [b for b in undef if b.get("listlike")]」

前輪 4 — 沒修好(重現)：單行註解已修，但 `<!--\n[S1] 只是註解\n-->` 仍被解析成 `untagged` 真條款並硬擋。
引句:「line = re.sub(r"<!--.*?-->", "", raw)」

前輪 5 — 修好：handoff 現在回傳並印出 `duplicate=1`，索引錯誤仍維持 `total=null`；`spec-trace` 的 duplicate 也改印 ✗。
引句:「(f"、編號重複 {_cc['duplicate']}" if _cc.get("duplicate") else "")」

前輪 6 — 修了但引入 finding 5：docstring 已改成「定義編號後到行尾」，但相鄰註解仍保留相反的未閉合反引號語意。
引句:「配對範圍=同一行、定義的 [SN] 之後到行尾(一行一條;後面再出現的 [SN] 是引用,不切段)」

1.
severity: major
blocking: 是 — 認不得的未閉合反引號前綴會刪掉整條並放行，違反「認不得→擋」。
引句:「line = line.split("`", 1)[0]」
file: `scripts/lumos:4080` 最小重現 ``"`[S1] 真條款沒標"`` 得 `rows=[]、gate=skip`；前置合法 S1、再寫未閉合反引號開頭的 S2，整閘得到 `ok`。

2.
severity: major
blocking: 是 — 不同 fence 字元共用一個 toggle，能把假證據放出來並把真正未標條款吞掉。
引句:「if ln.lstrip().startswith(("```", "~~~")):」
file: `scripts/lumos:2518` 最小重現為開 ```、其中出現 `~~~` 與帶 `[manual:人看一次]` 的 S2、再以 ``` 關閉並接未標 S3；HEAD 只看見 S2，`gate=ok`。

3.
severity: major
blocking: 是 — 圈號編號不被判成條款或未知清單，可靜默繞過。
引句:「_CLAUSE_ENUM = r"(?:[A-Za-z一二三四五六七八九十甲乙丙丁]{1,2}[.、)）]\s*)?"」
file: `scripts/lumos:4052` `十一、[S1]` 實際落入白名單而 `fail`，`(1) [S1]` 為 `listlike=true/fail`；但合法 S1 後接 `① [S2] 真條款沒標` 得 `S2 listlike=false、gate=ok`。

4.
severity: major
blocking: 是 — 正常的散文標籤被當未知清單，造成處置閘假紅。
引句:「_CLAUSE_LISTLIKE_RE = re.compile(r"^\s*(?:[^\w\s]+\s*|\w{1,3}[.、)）:：]\s*)*\[S(\d+)\]")」
file: `scripts/lumos:4053` 最小重現 `注:[S1] 只是引用` 與合法 S1 後的 `Q:[S2] 只是引用` 都得到 `listlike=true、gate=fail`。

5.
severity: minor
blocking: 否 — 只造成維護者誤讀，不改目前執行結果。
引句:「未閉合的反引號剝不掉,但一行只認一條所以」
file: `scripts/lumos:4075` 註解仍說未閉合反引號剝不掉，但 `scripts/lumos:4080` 實際會截掉第一個反引號之後的全部文字。

最嚴重 severity: major；blocking 6 條。
