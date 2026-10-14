severity: minor

我只動了 scratchpad 裡的複本,沒改 `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/`。有三處是實際跑過的:對 git replace 與 grafts 兩支測試各做一次變異,另跑了 Issue 與計劃的 `lumos lint`(都 0 問題)。S21–S36 的 16 條條款都找得到對應測試,方法名跟計劃的 `[test:]` 對得上。Issue 的四段(症狀、根因、現在怎麼繞、什麼條件算修好)齊全。兩處 REVISIT 都是行首、`YYYY-MM-DD 一句話` 的格式,lint 沒有抱怨。

### 發現

severity: minor
blocking: 否 — 錯誤的保證只出現在測試裡,放行行為本身安全,沒有任何路徑因此漏審
引句:「使用者環境設 GIT_NO_REPLACE_OBJECTS=0 也蓋不過入口(強制設值)→ 照擋」
問題:git replace 那支測試的 ② 斷言抓不到任何錯,它的名字(強制設值)和它守的東西對不上。git 2.39.2 只要這個環境變數「有設值」就關掉 replace,連 `0` 也一樣,而 ② 剛好設成 `0`。
具體失敗情境:我在複本裡把入口的 `os.environ["GIT_NO_REPLACE_OBJECTS"] = "1"` 分別改成 `setdefault` 和 `pass`。改成 `pass` 時 ① 紅了,② 仍綠;改成 `setdefault` 時 ①、② 都綠。也就是說「強制設值」的退化,這個斷言永遠抓不到。
副作用是 replace 這條路其實不需要強制設值,任何值都安全,所以 ② 的前提本身是空的。建議刪掉 ②,或改成直接斷言入口跑完後 `os.environ` 裡有這個變數。
佐證:`scripts/test_lumos.py:60970`(變異實測)、`scripts/lumos:52969`
對照:grafts 那支測試的 ② 是真的有效。拿掉入口那行 `GIT_GRAFT_FILE`,① 和 ② 都紅了。

severity: minor
blocking: 否 — 屬於測試缺口,放行行為沒有被破壞
引句:「os.environ.pop("GIT_DIFF_OPTS", None)」
問題:入口新增的 `GIT_DIFF_OPTS` 與 `GIT_EXTERNAL_DIFF` 清除沒有任何條款或測試守著。S28 只管 replace,S36 只管 grafts。`規格閘.md` 的 PITFALL 寫了 `GIT_DIFF_OPTS=-u0`,但它的 `[test:]` 只列 replace 和 grafts 兩支。
具體失敗情境:有人刪掉這兩行 pop,全套測試照綠,讀差異的閘又少了前後文。測試檔裡只有拿掉這些變數的乾淨環境輔助函式用到這個名字。
佐證:`scripts/lumos:52971`、`docs/lumos-toolchain-knowledge/Systems/規格閘.md:83`

severity: minor
blocking: 否 — 只是文字不一致,判定規則本身沒有被改壞
引句:「略過了危險詞的計劃,每一份多一席輕量審;寫錯不做清單的代價從「漏審」變成「多審一席」」
問題:「輕量審」的窗口與編制,七處文件說法不一。決策 d1、SKILL.md、templates.md 已經改成「一筆輕量審、至少一席不是架構對齊,沒有留痕就是整本帳」。計劃〈做法〉6 的代價句、`規格閘.md` 的 WHY 代價欄(「每份多一席輕量審」)和 code-loop SKILL(「過一席輕量設計審」)還停在舊說法。實際編制也不是一席:`design-loop.md` 寫 design/light 是通才加一席架構對齊。
具體失敗情境:讀者看到「一席」,就只派一席通才,漏掉規格閘要的架構席或留痕規則,推送前反而被擋。
佐證:`docs/lumos-toolchain-knowledge/Projects/規格閘不把不做節的詞算進風險_計劃.md:82`、`docs/lumos-toolchain-knowledge/Systems/規格閘.md:77`、`skills/lumos-code-loop/SKILL.md:44`

severity: minor
blocking: 否 — 只影響文件讀者,不影響放行
引句:「風險低綁上會紅的測試直接實作（不做清單略過了危險詞的，推送前要一筆輕量設計審）；推送前再驗一次」
問題:只改了 `docs/心智模型.md` 的圖片 alt 文字,圖本身(`assets/spec-gate-zh.svg`、`spec-gate-en.svg`)沒動。
- 英文版 `docs/mental-model.md:180` 的 alt 沒同步。
- 同一節內文仍寫「風險低:不派設計審」,沒提到這個例外。
- `docs/指令參考.md:66` 與 `docs/command-reference.md:66` 的 spec-gate 說明也沒提。

具體失敗情境:看圖的人和英文讀者仍以為風險低就完全不用審。
佐證:`docs/心智模型.md:178`、`docs/mental-model.md:180`

severity: minor
blocking: 否 — 條款有一半只在大小寫不敏感的檔案系統上被驗
引句:「檔案系統分大小寫,大小寫不同就是不同檔,這一條不適用」
問題:S31 後半(路徑大小寫不同但是同一個檔,應放行)的斷言③,在大小寫敏感的系統上只印一行文字就略過,不計入 check。條款在 Linux CI 上沒有被驗到,「S31 都綁到測試」的說法只在 macOS 成立。
具體失敗情境:CI 跑在 Linux 時,把 `_same_file_path` 改回純字串比對,整套照綠。
佐證:`scripts/test_lumos.py:61060`

severity: minor
blocking: 否 — 斷言本身沒錯,只是缺前置證明
引句:「超深巢狀行只跳過 → rc0、沒有堆疊」
問題:S23 的測試沒有前置斷言證明那一行真的會讓 JSON 解析丟 RecursionError(全域規則要求「證明現場成立」)。我用 python3.14 實測確實會丟,所以現在有效;但 Python 日後放寬遞迴上限,這支測試會變成空轉。另外它只覆蓋推送前這一條讀帳路徑。
佐證:`scripts/test_lumos.py:60841`

最高等級 minor,blocking 0 條。
