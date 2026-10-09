severity: minor

結論:沒有第二種做法,也沒有跨層直呼。有 5 條小的不一致,結構都是對的。

## 三問

**1. 分層與依賴方向:大致對齊。**
- 新碼放在 `cmd_decisions` 正下方(`scripts/lumos:18133`、`:18175`、`:18217`),放法跟 `cmd_decisions` / `cmd_query`(`scripts/lumos:18438`)一樣。
- 抽共用的 `_superseded_decisions` 是好做法。`decisions --superseded` 與新指令共用同一支,沒有留兩份。
- 切 frontmatter、判圍欄、算一句話都走既有函式:`split_frontmatter`、`_visible_lines`(`:4871`,全檔唯一的圍欄判定)、`_gist`(`:12604`)、`slot_parse` / `_slot_vals`、`_note_summary_entries`。
- 規格閘(`_spec_gate_front`,`:7690` 一帶)呼叫後面才定義的 `_rejections_collect`。這是同一個模組,執行時才解析,方向沒問題。
- 有兩處是自己重寫鄰居已有的小功能,見 F1、F2。因為量小,我判 minor、不判 major。

**2. 命名與錯誤處理:大致對齊,有 3 處不同(F3、F4、F5)。**
- 命名跟鄰居一致:`cmd_` / `_` 前綴、常數大寫 `_REJ_*`、argparse 的 `dest="rej_json"`(跟 `q_json`、`st_json`、`search_json` 同型)、`HELP_WHEN` 有登記、`main()` 分派緊貼 `decisions`。
- `--json` 的 `ensure_ascii=False, indent=2` 跟 `cmd_query`(`:18479`)一樣。
- 函式內 `import json` 在檔裡很常見(`:1058`、`:1621`、`:5601` 等)。

**3. 第二種做法:沒有新增整套做法。**
- 子指令註冊、分派、`HELP_WHEN` 全照舊。
- 測試佈景沿用 `mkvault()` + `write()` + `run()`,規格閘那條沿用 `_mk_spec_gate_repo`(`scripts/test_lumos.py:53038`)和 `_sg_plan2`。
- 偽造收集失敗用 `patch.object(m.sys, "stdout", ...)`,檔裡已有多處同寫法(`scripts/test_lumos.py:39590` 等)。
- 只有 F1 到 F5 這幾個局部差異。

## F1 認 WHY 行的方式與鄰居不同,摘要段的迴圈也重寫了一份
severity: minor
blocking: 否
引句:「_REJ_WHY_RE = re.compile(r"^\s*(?:[-*]\s+)?WHY\s*[:：]")」
佐證:file: `scripts/lumos:4041`
- 摘要段:`_rejections_of_note` 自己跑 `_note_summary_entries` → `partition(":")` → `slot_parse`。這個迴圈正是 `_slot_summary_entries`(`:4041`)的內容,只是那支一次掃全庫、這裡一次一篇。
- 正文段:鄰居認前綴行用 `SYMBOL_RE`(`:4654`、`:4688`),只收 ASCII 冒號。新碼另訂 `_REJ_WHY_RE`,多收全形冒號和項目符號。
- 結果是同一個 `WHY：` 寫在摘要裡不算、寫在正文裡算。
- ⚠ 正文段專案沒有現成的「讀正文前綴行」函式可對,這半條交編排者裁。摘要段那半確定有現成寫法。

## F2 讀全文沒走 `env_text`
severity: minor
blocking: 否
引句:「text = (env.vault / rel).read_text(encoding="utf-8-sig")」
佐證:file: `scripts/lumos:755`
- `env_text(env, rel)` 是專案的共用讀法,有 29 處呼叫,也處理「記憶體裡的 Env」。新碼自己 `try/except (OSError, UnicodeDecodeError)` 再讀一次。
- 鄰居自己也不一致:`_gist`(`:12604` 一帶)、`_rank_fields` 都是行內直讀。
- ⚠ 這點交編排者裁,我只標 minor。

## F3 JSON 的路徑欄位名與值的形狀跟其他指令不同
severity: minor
blocking: 否
引句:「items.append({"source": rel[:-3], "kind": "superseded-decision",」
佐證:file: `scripts/lumos:18479`
- 其他輸出筆記的 JSON 都用 `"node": rel`,帶 `.md`:`cmd_query`(`:18479`)、`:5314`、`:14729`、`:17896`、`:18053`。
- 新指令用 `"source"` 且去掉 `.md`。`"source"` 在專案裡另有「圖的邊起點」的意思(`:19025`)。
- 文字輸出也印去 `.md` 的路徑,而 `cmd_query` 和 `search` 印帶 `.md` 的 `rel`。

## F4 規格閘提醒:內嵌 try/except pass,而鄰居是抽成小函式、窄例外、印出原因
severity: minor
blocking: 否
引句:「print(f"[spec-gate] 舊否決: 圖譜寫下的有 {_rej_n} 筆;動手前跑 lumos rejections 讀完、按概念比對,撞到先問人")」
佐證:file: `scripts/lumos:7275`
- 其他風險判定的印行都抽成獨立函式,例如 `_spec_gate_print_door`(`:7275`)。新碼直接塞進 `_spec_gate_front` 本體。
- 鄰居的「略過」路徑用窄例外並印出原因:`except (ValueError, OSError) as e: print("[spec-gate] 跑: —(平台設定讀不動:{e};略過)")`(`:7719` 一帶)。
- 新碼是 `except Exception: pass`,靜默吞掉,使用者看不出提醒為什麼沒出現。
- 「只提醒不擋」的語意是一致的,只是寫法跟印出方式不同。

## F5 空結果沒有「無…」那種訊息
severity: minor
blocking: 否
引句:「print(f"共 {len(items)} 筆。按概念比對你的提案,不是比字面;撞到就先問人:上次因為這個理由否決,現在還這麼想嗎?")」
佐證:file: `scripts/lumos:18143`
- 兄弟指令的空結果會單獨印一句:`cmd_decisions` 印「無被推翻的決策」,`cmd_query` 印「無節點符合條件」。
- 新指令空圖譜時照樣印標題加「共 0 筆」,以及「按概念比對你的提案…撞到就先問人」這句提示。
- 測試 `t_rejections_json_and_empty` ④ 把「共 0 筆」釘成預期,所以這是設計取捨。

不對齊共 5 條,其中 major 0 條
