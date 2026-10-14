severity: minor

我查了三件事:矛盾句子、條款與測試的對應、新規則本身。
- 條款 S1 到 S15 綁的 12 支測試都存在,對得上。
- S11 到 S14 的測試有走完整條路徑(沒審、審沒過、審過、留痕過期、重跑規格閘後要再審、夾帶句子逐句各跑一份)。
- 文件裡還留著跟新規則矛盾的舊句,另有一個放行條件比說明寫的鬆。

severity: minor
blocking: 否 — 只是文件與手冊的舊句沒跟上,推送前的檢查照新規則擋,程式行為沒錯。
引句:「PASS(風險低):可以實作;不做清單略過了危險詞,推送前要一筆輕量設計審通過(指令見上)」
問題:程式新增了「風險低但要輕量審」這一支,計劃〈做法〉5 自己寫了收工要搜遍 repo、把舊句補齊或標歷史。這個 patch 只改了雙向門計劃的兩處和規格閘的硬訊號與版本號兩行,下面這些「風險低就直接實作、不派審」的句子都沒補。
- `Systems/規格閘.md` 的 FLOW 行寫「PASS(風險低)不派審」。
- `Systems/規格閘.md` 的 KEY 行寫「過了印 PASS(風險低):直接實作不派審」。
- `Systems/規格閘.md` 的流程句寫「風險低 → … → 直接實作 → 推送前…」,沒提輕量審這一關。
- `skills/lumos-design-loop/SKILL.md` 寫「印 PASS(風險低) → 不進本迴圈、直接實作」。
- `skills/lumos-design-loop/reference.md` 有「風險低(都沒命中+四行已排除)不派審」。
- `skills/lumos-project-notes/commands/05-設計審查迴圈.md` 和 `commands/INDEX.md` 寫「過了印 PASS(風險低) 直接實作不派審」。
- `Projects/雙向門放行_計劃.md` 的設計節寫「印 `PASS(風險低):直接實作,不派審`」。

具體失敗情境:下一個 session 的 AI 只讀 design-loop 手冊或規格閘筆記,會以為只要出現 PASS(風險低)就能直接實作,不知道不做清單略過了危險詞時還要補一筆輕量審。它推送時才被擋,多繞一圈。
佐證:file: `skills/lumos-design-loop/SKILL.md:13`
佐證:file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:16`
佐證:file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:32`
佐證:file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:71`
佐證:file: `skills/lumos-design-loop/reference.md:535`
佐證:file: `skills/lumos-project-notes/commands/05-設計審查迴圈.md:12`
佐證:file: `docs/lumos-toolchain-knowledge/Projects/雙向門放行_計劃.md:209`

severity: minor
blocking: 否 — 計劃的決策 d1 已把「審查員自己看漏」和「刻意繞法」列為接受的天花板,這裡是它沒講到的更大的缺口。
引句:「不比整份計劃的雜湊(cur_sha_override=那筆審查自己的 result)」
問題:`_spec_gate_push_light` 把雜湊鏈驗證的比對對象換成那筆審查自己的 result 雜湊,這項檢查恆為真。放行條件只剩三件:帳上最後一筆輕量審的等級在 clean 或 minor、有 `result_sha256`、記在規格閘留痕之後。它沒檢查那筆審查審的是不是這份計劃,也沒檢查審查席有沒有真的看過被略過的那幾行。d1 的代價欄只寫了「審過後又改回原樣」這一種繞法,範圍比實際的窄。
具體失敗情境:作者在跑完 `spec-gate` 之後,自己敲 `lumos canary record none --loop 甲 --severity clean --spec 任一檔`,記一筆帶 `result_sha256` 的 clean 輕量審,推送前就放行了。測試 `t_prepush_nogo_light_review_required` 的 `_ngl_review` 也是這樣直接寫帳,沒有任何一個案例驗證「審的不是這份計劃就不算」。
建議:二選一。把 d1 的 trade_offs 改寫成「輕量審只驗帳上有一筆過的、晚於留痕,不驗審查對象」,或讓放行改比被略過那幾行的指紋。
佐證:file: `scripts/lumos`(patch 中 `_spec_gate_push_light`,標示 `cur_sha_override=(rounds[-1].get("result_sha256") ...)` 的那行)

整體最高等級是 minor,blocking 共 0 條。
