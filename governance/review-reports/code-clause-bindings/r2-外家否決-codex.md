<!-- 外家否決席 r2(Codex gpt-5.6-sol, xhigh, --sandbox read-only;第一次用 terra 跑到一半「模型滿載」沒交報告,逐字稿 r2-codex-raw-attempt1-capacity.txt);原始逐字稿 r2-codex-raw.txt;正規化:去行尾雙空白、去重複印出的第二份 -->
severity: major

前輪 1 — 修了但引入新洞：其他副檔名已改成 FAIL，但 `code` 開頭、非 `code-` 的設計審編號會跳過整道閘，見 finding 1。
引句:「不看副檔名——外家席:.patch 跳過只看尾碼會被設計審拿 patch 當審材繞過」

前輪 2 — 修了但引入新洞：四個空白已擋住，四個標點仍被當成有效人工驗法，見 finding 2。
引句:「[manual: ] 空的或太短=沒講怎麼驗=未標」

前輪 3 — 修好：CLI help、雙語指令文件與主要 skill 指引均改成「未標 rc1」，舊制認領欄明示僅供對照。
引句:「條款級追溯:計劃 [SN] 條款那一行綁的 [test:]/[manual:](裁決,有未標 rc1)」

前輪 4 — 修了但引入新洞：純反引號 ID 不再算條款、表格列已算定義；但真正條款同一行的反引號範例會被當成第二條款，見 finding 3。
引句:「只在反引號出現的 S9 → 非定義,不進未標」

1.
severity: major
blocking: 是 — 合約只豁免 `code-`，但 indeterminate 分支令合法設計審名稱可關掉第五步。
引句:「loop 編號 {loop_id!r} 看不出是設計審還是代碼審,不判;新迴圈請用 code-<主題> 或不帶 code 前綴」
file: `scripts/lumos:13453` `_roster_kind("codefake")` 得到 `None` 後直接回傳 `skip`。
最小重現（已實跑）：`loop_id="codefake"`、新制時間與未標條款得到 `skip`，同一審材用 `design-real` 得到 `fail`。

2.
severity: major
blocking: 是 — `[manual:]` 只驗長度，四個標點即可偽造「已寫人工驗法」並放行。
引句:「manual = [x.strip() for x in MANUAL_REF_RE.findall(seg) if len(x.strip()) >= _MANUAL_MIN_CHARS]」
file: `scripts/lumos:4130` `len()` 沒驗證內容含任何可讀文字。
最小重現（已實跑）：`- [S1] 甲 [manual:!!!!]` 得到 `state=manual`，完整第五步輸出 `1 條全標` 並回 `ok`。

3.
severity: major
blocking: 是 — 條款行中的反引號格式範例會製造不存在的未標條款，使有效設計審無法通過。
引句:「定義行:這一行所有 [SN] 都算定義,各認到下一個 [SN] 之前」
file: `scripts/lumos:4118`、`scripts/lumos:13482` 只要整行由真條款開頭，反引號內的後續 ID 也會成為 `defined/untagged`。
最小重現（凍結碼逐式重放）：`### [S1] 真條款 [test:t_ok],例如 \`[S9] 範例格式\`` 得到 `S1=bound、S9=untagged`，第五步翻紅。

4.
severity: major
blocking: 是 — 常見 Markdown task-list 條款會被歸為範例，整份未標計劃反而以零條款通過。
引句:「定義行=該 id 第一次出現在行首的那一行(去 - * # > 數字. 粗體/反引號符號)」
file: `scripts/lumos:4090`、`scripts/lumos:13480` 前導 `[ ]` 不在容許語法內，所得 `undefined` 又被閘排除。
最小重現（已實跑）：`- [ ] [S1] 甲` 輸出 `0 條全標;另有 1 個 id 只在範例/引用裡出現` 並回 `ok`。

5.
severity: minor
blocking: 否 — 只誤導 handoff 顯示，處置閘本身仍會對索引錯誤 fail-closed。
引句:「回 (rows, err)。索引建不起來(設定壞)回 ([], 一句原因),呼叫端印出來、不炸查詢。」
file: `scripts/lumos:20916`、`scripts/lumos:21009` 索引失敗時保留 `index_error` 卻不顯示，文字輸出會把有條款的計劃報成「驗收條款 0 條」。

補核無 finding：cutoff 會按 UTC 比較，cutoff 前的 `+08:00` 舊帳仍跳過；無時區時間會 fail-closed。`INV_TAG_RE` 收進 `manual` 後只剝除乾淨宣稱文字，沒有把 manual 誤算成 ★INVARIANT★ 的測試或審計。

`python3 scripts/test_lumos.py -k clause` 未能實跑：唯讀環境沒有可用暫存目錄。

最嚴重 severity: major；blocking 4 條。
