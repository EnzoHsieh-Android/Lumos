severity: major

我跑了 S51–S58 綁定的測試和處置閘相關測試(`-k disposal` 185 支、`t_prepush_nogo_std` 20 支、S58 守衛 4 支),全綠;`spec-trace` 58 條全綁、`lint` 0 問題。以下是綠燈蓋不住的缺口。

**S51–S58 與綁定測試的對應**:八條都對得上測試,測試也驗到條款本身。S51 同時驗了寫回放行與改被略過行擋下,S54 兩種席位缺口都測了,S55 有放行與擋下的對照。唯一例外是 S5 的條款文字已過期,見第 2 條。

**「major 改開 -std」在各手冊的說法**:中文的 AGENTS、CLAUDE、心智模型、指令參考、兩份 skill、commands/05、Systems 都一致。英文的 `docs/mental-model.md` 與 `docs/command-reference.md` 也寫了,措辭一致。INDEX.md 不計。

severity: major
blocking: 是 — 「整類拿掉」的宣稱不成立,同一族第四次可被打穿,且〈實務隱患〉沒寫天花板
引句:「改成整類拿掉。」
問題:`_strip_zero_width` 只拿 Cf 類別加一張手列的碼位表。Unicode 裡一樣看不見、但不屬 Cf 也不在 `_INVISIBLE_EXTRA` 的字元沒被拿掉。我實測把這些字元夾在「退款」和「payment」中間,`_door_keyword_hits` 全部回空。
- 蒙古文變體選擇符 U+180B、U+180C、U+180D、U+180F(Mn)
- 點字空白 U+2800(So)
- 高棉固有母音 U+17B4、U+17B5(Mn)

對照:U+061C、U+E0020、U+200E 都命中。
具體失敗情境:計劃在「## 做法」寫「實作退⠀款流程」(中間是 U+2800),門判風險低,不派設計審,也不進不做清單的輕量審。r6、r7、r8 已連三輪被同一族打穿。這次改成「整類」,仍只是另一張更長的列舉。
測試缺口:`t_zero_width_strip_all_invisible` 的 `_INVISIBLE_CASES` 沒有這幾個碼位,所以測試綠。
文件缺口:Systems/規格閘.md 的 PITFALL 和計劃第 63 點都寫「整類」,沒有天花板句,也沒有 REVISIT。違反「承認風險要附回頭條件」。
修法:把這幾個碼位補進去並加測試,或把話改成「列舉到的字元」,補上天花板句與可數的 REVISIT。
佐證:``scripts/lumos: `_strip_zero_width`(repair.patch 第 496–500 行附近)``、``scripts/test_lumos.py: `_INVISIBLE_CASES`(約 64985 行)``、``docs/lumos-toolchain-knowledge/Systems/規格閘.md:99``

severity: major
blocking: 是 — S5 條款文字與程式、綁定測試互相矛盾,條款是驗收合約
引句:「[S5] 門判定規則版本應是 6。」
問題:程式 `_DOOR_RULE_VERSION = 7`,綁定測試 `t_door_rule_version_pin` 斷言 `door_rule=7`,但計劃條款仍寫 6。r8 修補把版本升到 7,卻沒改條款。
為什麼綠燈蓋不住:`spec-trace` 只查「綁了沒」,不查內容,所以仍顯示 ✓。
具體失敗情境:照條款文字驗收的人或 AI 會判「7 ≠ 6」不符,或反過來把程式改回 6。
順帶的小不一致:Systems/規格閘.md 第 38 行把「沒上過主線」只套到版本 1–5,程式註解寫的是「2–6 沒上過主線」。同一行的「2=逐句判初版」也和程式的「2=跳過不做標題下的清單」說法不同。
佐證:``docs/lumos-toolchain-knowledge/Projects/規格閘不把不做節的詞算進風險_計劃.md:103``、``scripts/test_lumos.py: `t_door_rule_version_pin`(約 63031 行)``、``scripts/lumos:7973``

severity: minor
blocking: 否 — 屬於事前已披露的設計取捨,單人威脅模型下機率低,但出口跟處置閘的行為不同
引句:「讀帳讀不懂的行(壞行、超深巢狀、不是物件的行)跟 (a) 一樣跳過,擋下時訊息帶一句跳過幾行。」
問題:S56 說推送前 (b) 出口「共用同一支處置閘判定」。但 `_nogo_full_review_gate` 呼叫 `_disposal_judge` 時沒傳 `bad_linenos`,而 `loop status --disposal` 與 `loop next` 有傳。後兩者遇到壞行是 rc2(fail-closed,理由是壞行會讓「最後一輪」判歪);(b) 直接跳過,放行時還一字不提,只有擋下時才帶「已跳過」。
實測:`-std` 已過處置閘,再往帳尾端追加一筆被截斷的 r2 major(壞 JSON)。
- 推送前:rc 0,放行。
- `loop status 甲-std --disposal`:rc 2,「審查記錄檔有 1 行讀不懂,沒辦法確定『最後一輪』是哪輪」。

具體失敗情境:寫帳寫到一半被截斷,最後一輪 major 被當成不存在,推送放行。
測試缺口:S53 的測試只證明「壞行不崩」,沒對照處置閘的 rc2。design-loop.md 的 WHY 說「處置閘要那些行號 fail-closed」。
建議:放行時也印一句跳過行數,或在 S56 與 WHY 明寫「(b) 不繼承壞行 fail-closed」。
佐證:``scripts/lumos: `_nogo_full_review_gate`(repair.patch 第 777–778 行)``、``scripts/test_lumos.py: `t_prepush_nogo_std_bad_ledger_lines`(約 64904 行)``

severity: minor
blocking: 否 — 只是提示訊息比手冊少一句,不影響放行判定
引句:「推送前要一筆輕量設計審通過(指令見上)。條款的測試做綠了才推得上去」
問題:`spec-gate` 自己印的兩處提示(`_spec_gate_print_door` 的「推送前要有一筆輕量設計審通過…」,以及 PASS 行這一句)都沒講「抓到 major 改開 -std」。其餘手冊與推送前擋下訊息都有。使用者最先看到的是 spec-gate 的輸出。
測試缺口:S58 的守衛只掃 `.md`,不掃程式印出的字串;手冊裡英文那兩份也不在它的比對範圍(它找的是「不做清單」加「輕量」)。
具體失敗情境:拿掉英文手冊或 `command-reference.md` 的 `-std` 句,測試仍綠。
佐證:``scripts/lumos:8386``、``scripts/lumos:8986``、``scripts/test_lumos.py: `t_design_loop_manuals_nogo_major_std`(約 64870 行附近)``

severity: minor
blocking: 否 — 回頭條件有執行路徑,但量不到一類情況
引句:「數治理帳裡 kind=nogo-light-review-missing 的擋下事件:每一筆的 nodes 指的計劃路徑,現在主線上還在不在」
問題:REVISIT 可執行。事件由 `_nogo_light_block_event` 寫入,帶 `nodes:[prel]`,`docs/.governance-log.jsonl` 也有納入版控。但它只數「被擋過」的計劃。

洗掉 major 的完整路徑是:輕量審記 major,改檔名後新編號乾淨,從沒被擋,就沒有事件。這條路量不到。「0 份就當沒有」會高估安全。
建議:補一句「未被擋過的路徑不在此量測範圍」,或另加一個對審查帳的查法,比對有 major 輪的編號是否對應到已不存在的計劃。
佐證:``docs/lumos-toolchain-knowledge/Projects/規格閘不把不做節的詞算進風險_計劃.md:167``、``scripts/lumos:9505``

**其他確認**:
- design-loop.md 的 ★INVARIANT★(處置閘第五步)綁定的三支測試和 `-k disposal` 全綠,`_disposal_judge` 抽出沒破壞合約。
- `_under_root` 收斂的各處與原拼法等價。`loop next` 的 `record_cmd` 會印 `--snapshot` 與 `--reviewed`,templates 要求 -std 帶快照是做得到的。

最高等級 major,blocking 2 條。
