severity: major

## 範圍與結論

白話版:這輪把目標架構段的輸出統一收進 `_arch_target_text`,同時給了字數上限。上限靠「從頭保留、超過就整行丟掉」實作。結果被審分支的作者只要在目標目錄裡放幾個檔名夠長的檔案,整段規則原文就送不到審查席。

我實跑了一個重現案例(見 finding 1)。另外跑了 `-k arch_target`(96 passed)、`-k name_show`(67 passed)、`-k dispatch_lens_hook`(138 passed)。`-k kill_esc` 選中 0 個測試,沒有可跑的子集。

severity: major
blocking: 是 — 被審分支可控的檔名可以讓整段目標規則靜默消失,架構對齊席拿不到規則就會放過 major 級違規。
引句:「lines = _lens_spec_cap_lines(lines)」
問題:標題行(節點名加最多 20 支命中檔)不在 `per_node` 字數分配裡,也沒有自己的上限。名字出口會把反引號、反斜線、私用碼位等跳脫成 6 到 10 個字元。20 支檔乘以每支最多 300 字再乘以跳脫倍數,單行就能超過整段上限 12000。`_lens_spec_cap_lines` 只能整行保留或整行丟棄:第一行就放不下時,它丟掉這一行和後面所有行。結果是節點標題、全部規則原文、其他節點都不見,只剩段首句、一行「已截」和段尾那句「違反一條規則=major」。
具體失敗情境:
- 輸入:目標目錄 `app/Domain/**` 宣告了 `Systems/DDD目標`,節點有有效 RULE。被審分支新增 20 支檔,檔名是 200 個反引號加編號加 `.py`。
- 結果:我在 `/private/tmp/.../cr-lr7-通才/r4` 實跑 `dispatch-lens main..HEAD --arch-target --json`,`arch_text` 只剩 241 字。內容是「[目標架構] …」首句、`(已截:附加段超過 12000 字,原本 24711 字,後面的沒附)`、「違反一條規則=major…」。
- 影響:審查席看不到任何規則,也看不到哪些檔屬於目標組,卻仍被告知違反規則就是 major。
- 退步:r6 之前規則至少會送到;現在這個「上限」讓 DoS 變成靜默放行。
- 建議:標題行的檔名清單套進同一份字數分配;或規則行優先保留、檔名清單才截;或截到沒有規則時明說「規則沒附」。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:44408` ``、``file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:44396` ``

severity: minor
blocking: 否 — 只是說明文字誤導,不影響規則本身有沒有送到。
引句:「cut:比對只算到一半的原因(_arch_target_lens_split),有就印一行。」
問題:宣告整份壞掉時,`rules` 是空的,實際上沒有任何比對在進行,但 `_arch_target_split` 仍照檔數上限算出 `why`。
具體失敗情境:
- 輸入:`arch_targets` 有一條 path 以 `/` 開頭(壞宣告),分支改了 2300 支檔。
- 輸出:我實跑得到兩行警告。第一行是「第 602 條 path 不合法;這次整份不用,全部照鄰居審」,第二行是「只算到一半(改動檔 2300 支只比了前 2000 支),沒比到的檔照鄰居審」。第二行與第一行矛盾,而且是噪音。
- 建議:`rules` 為空時不要印 cut。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:44385` ``

severity: minor
blocking: 否 — 沒有機器檢查「目標規則」引句,影響的是審查席抄規則的準確度。
引句:「規則每條截 _ARCH_TARGET_RULE_SHOW 字、每篇規則照字數分配」
問題:規則原文改走名字出口後有三個差異。
- 反引號和反斜線變成 `\u0060`、`\u005c`。
- 整條包進 ‹…›。
- 超過 200 字截斷。

專案的 RULE 行常帶反引號路徑,而且整條 entry 含 `[依據:…][since:…]` 等欄位,很容易超過 200 字。但 `templates.md` §7.6 仍要求審查席逐字抄「目標規則:「<規則原文 ≥10 字>」」,沒提 ‹› 和跳脫。
具體失敗情境:
- 輸入:規則是 `Domain 不依賴 `ORM` 型別`。
- 輸出:派工詞印成 `\u0060ORM\u0060`,審查席照抄後與筆記原文對不上。
- 輸入:規則句尾有「除非…」的例外,位置超過 200 字。
- 輸出:例外被截掉,審查席會誤判。

佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:44417` ``;重現同 finding 1 的 `r1`,已讀。

## 重點檢查項結果

- **`_arch_target_text` 其他呼叫者**:已讀,無 finding。全 repo 只有兩個呼叫點,都是派工鏡頭(代碼審 `_dispatch_lens_arch_text`、設計審 `_dispatch_lens_spec_arch_text`)。推送前分級走 `lumos:45231`,呼叫的是 `_arch_target_split(files, rules)`;新參數預設值都是 None,行為與輸出不變。doctor 和 pitfalls 不用 `_arch_target_text`。
- **`_kill_esc` 預設行為**:已讀,無 finding。`wide=False` 時 `_kill_esc_one` 對所有碼位都輸出 `\u{o:04x}`,與舊寫法逐字相同,基本平面外的碼位也一樣。hook 的 `_spec_name_show` 一律用 8 碼,與 lumos 的 `wide=True` 一致,名字顯示比對測試綠。
- **下游格式依賴**:已讀,無 finding。templates.md §7.6 只靠「[目標架構]」這個字面和「目標規則:「…」」格式。hook 不偵測段落內容,只轉送 `arch_text`,也不再二次加框。段落現在以框線行開頭,這一點沒有下游依賴。
- **設計審與代碼審輸出一致性**:已讀,無 finding。兩條路都經同一支 `_arch_target_text` 加框。例外是代碼審的錯誤與備援路徑(`lumos:50296` 的主線說明和 `_arch_target_fail_text`)沒有加框,但內容只有固定字串加例外類別名,沒有作者可控值。
- **主線功能互相影響**:已讀,無 finding。`_lens_render_body` 在 diff 模式下 `max_chars=None`,房間是無限大,合約行與殘留徽章行為不變。設計審的 `marks`、`_lens_spec_cap_and_count` 只在設計審路徑生效。JSON 的 `listed` 與 `shown` 欄位只在 arm 時存起來,沒有下游依賴這兩個值的語意。
- **時間預算**:已讀,無 finding。2300 支檔加 601 條宣告的案例,目標段本身很快、只被檔數與宣告條數上限截斷,並明說了。整個派工鏡頭 21 到 61 秒主要花在圖譜段,不是這輪修補造成的。

最高等級 major,blocking 1 條。
