severity: minor

已讀這次修補差異和完整改動,並真跑了 `-k nogo`,結果 180 passed、0 failed。

**已讀,無 finding**
- `loop status --light` 抽出的 `_light_gate_fails`:ratchet、empty、judged 的先後順序和原本一致。`OSError` 上拋後仍由呼叫端回 rc2,`_cost_summary` 的印出位置沒變。
- 規格閘 PASS 那行改了文字:我 grep 了 scripts、hooks、skills,沒有程式拿「直接實作,不派審」當解析依據。依賴它的只有測試,測試已同步改。
- 留痕多了 `needs_light_review` 欄:沒有任何讀者讀這一欄,推送前是重新判斷,所以不會因舊留痕少這一欄而壞掉。
- 門規則版本升到 3:doctor 的前 30 份統計只數版本等於現行的留痕。版本 2 沒上過主線,所以沒有舊留痕需要處理。
- `_spec_gate_push_stale` 改回傳 tuple:呼叫端只有 `_spec_gate_push_one` 一處,已跟著改。
- 兩個版本號釘值(`_NOGO_SKIP_LOGIC_VERSION`、`_DOOR_RULE_VERSION`)和指紋測試一致,測試綠。

severity: minor
blocking: 否 — 只影響流程出路和提示文字,不會放行不該放行的計劃,也不會弄壞既有輸出
引句:「迴圈 {loop_id} 曾經有一輪抓到 major 以上,light 從此永久失效(ratchet)」
問題:推送前的輕量審固定用 `_loop_id_for_plan(prel)` 當迴圈編號。`loop status --light` 遇到 ratchet 時,建議的出路是開新編號(原編號加 `-std`)。推送前這一側換不了編號,所以這條出路對它無效。
具體失敗情境:
- 計劃的輕量審出過一次 major,作者照意見修了計劃,想再審一次。
- 推送前只讀同編號的帳,ratchet 永久成立,此後每次推送都被擋。
- 唯一的出路是在計劃寫 `plan_risk: high` 走完整設計審。尾句有提到這條,但修好後想只複審一次的人沒有路。
- 另外,若這個編號先前已有 standard 或 high 的定錨,`loop next --tier light` 會因 tier 不一致而 rc2,提示的指令本身就敲不過。
佐證:``file: `scripts/lumos:9157` `` 和 ``file: `scripts/lumos:9158` `` 是 ratchet 分支。這是設計取捨,不是程式錯,所以標 minor。

severity: minor
blocking: 否 — 只是文件與提示字串,不影響判定
引句:「PASS(風險低):可以實作;不做清單略過了危險詞,推送前要一筆輕量設計審通過(指令見上)」
問題:
- `skills/lumos-design-loop/SKILL.md` 第 13 行仍寫「印 `PASS(風險低)` → 不進本迴圈、直接實作」。這次 PASS 行有了「不做清單略過危險詞時要輕量審」的分支,SKILL 沒同步,只改了 `templates.md`。照 SKILL 走的下一個 session 會直接實作,到推送前才被擋。
- `_nogo_light_cmd` 印出的 `--spec` 路徑沒加引號。計劃檔名含空白時,照抄會壞掉。
具體失敗情境:AI 只讀 SKILL 就跳過輕量審。多數計劃檔名沒有空白,所以後者實際影響很小。
佐證:``file: `skills/lumos-design-loop/SKILL.md:13` ``、``file: `scripts/lumos:8265` ``。

最高等級為 minor,blocking 共 0 條。
