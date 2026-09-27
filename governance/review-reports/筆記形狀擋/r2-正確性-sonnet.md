severity: blocker

## F1 放行寫法的釘版本語法會讓既有 refcheck/G1 硬閘把合法引用判成幻覺證據

severity: blocker
blocking: 是 —— 作者照這份 spec 要求寫的「放行寫法」,會讓同一段文字在既有的 refcheck/G1 硬閘(design-loop settle、loop status --gate)下被判成「missing」而卡住簽核,是這份設計自己教人寫、卻自己打自己的系統性錯判,不是邊角案例。

引句:「反引號包著或裸寫都算」

佐證與重現(在 repo 現有程式碼上實測,不是臆測):

1. spec〈兩條規則〉第 1 點定義「放行寫法」為 `路徑@<提交>:數字`(例:`` `scripts/lumos@1234567890ab:100` ``),並要求作者用它取代裸的 `路徑:數字` 才能過 note-shape。
2. 這段文字本身仍會被寫進同一批知識筆記,而知識筆記的引用檢查(refcheck)與 design-loop 的 G1 硬閘(`lumos loop status --gate`、`cmd_settle`)全部呼叫同一支共用抽取器 `_node_code_ref_tokens`(scripts/lumos:19854)。這支函式目前完全不認得 `@<提交>` 這個新語法:它只用 `_suffix_re = re.compile(r":([^/]+)$")`(scripts/lumos:19859)去抓最後一段 `:數字`,`@<提交>` 那截會原封不動留在 token 裡一起送進 `_validate_repo_ref`。
3. 我實際跑了這段(用 repo 既有的 `_refcheck_scan`,對照真實存在的檔案 `scripts/lumos`):
   ```
   text = '引用 `scripts/lumos@1234567890ab:100` 這一行'
   _refcheck_scan(text, repo_root)
   → [{'token': 'scripts/lumos@1234567890ab', 'line': '100', 'status': 'missing', 'excerpt': ''}]
   ```
   即使 `scripts/lumos` 這支檔真實存在、`1234567890ab` 也不是隨便亂寫,結果仍是 `missing`——因為 `_validate_repo_ref` 在沒有 `at_sha` 時是直接拿 `repo_root / token` 去 `Path.exists()`(scripts/lumos:19834),而 token 是字面上帶了 `@1234567890ab` 的假路徑,repo 裡當然沒有一支檔案真的叫這個名字。
4. `_validate_repo_ref` 其實已經支援 `at_sha` 參數可以對指定提交驗證(scripts/lumos:19804-19833),`_git_tree_has`/`_git_tree_text` 也都在(scripts/lumos:29734-29740)——換句話說,驗證放行寫法在技術上可行,**但這份 spec 完全沒提到要教 `_refcheck_scan`/G1 那條路先把 `路徑@<提交>` 切成 `(路徑, at_sha)` 再呼叫 `_validate_repo_ref`**;spec 只講「note-shape 自己」怎麼驗放行寫法,沒處理「同一段文字被 refcheck/G1 這個既有使用者读到」的情況。
5. 這直接打臉 PRIOR-ART 自己的宣稱與 S9 的驗收條件:PRIOR-ART 寫「預設行為不變,refcheck、改檔前推筆記、每支檔有家三個既有使用者不受影響」,S9 也要求「抽取器加的兩個選項預設關閉,refcheck…對同一段文字的抽取結果應與改動前相同」——這兩句只保證「舊文字」抽取結果不變,完全沒討論「這份 spec 自己要求作者新寫的 `路徑@<提交>:數字` 文字」在既有 refcheck/G1 眼中會發生什麼事。實測結果是:凡是任何一篇正在走 design-loop 簽核(G1 是硬閘,見 scripts/lumos:10172-10199、9317-9396)的筆記,只要作者照這份 spec 的要求把行號引用改寫成放行寫法,G1 就會把它判成「檔案不存在」而擋簽核——跟這篇被審 spec 自己借用的 `_validate_repo_ref` docstring 描述的「J-c dangling=幻覺證據」是同一種錯判,只是這次是這份設計自己造出來的假陽性。
6. 影響範圍不是理論:`docs/lumos-toolchain-knowledge/Projects/` 底下的計劃筆記本身就是 G1/refcheck 的檢查對象(cmd_refcheck 的用法就是「給一個 .md 路徑」),而這份 spec 要求的放行寫法正是要寫進這類筆記裡取代危險的裸引用——兩者用途完全重疊。

## F2 「認裸文字」的抽取機制沒有定義,現有語料已出現會撞到這個機制邊界的真實寫法

severity: major
blocking: 是 —— S1 的驗收依賴一支尚未定義行為的抽取邏輯,實作者沒有規則可循,只能自己猜char-class/斷詞,猜錯的方向(多抓或少抓)都會讓「新增行號引用」這條規則失準,而 spec 沒有給出任何裁決依據。

引句:「反引號包著或裸寫都算」

佐證:

1. 目前 `_node_code_ref_tokens`(scripts/lumos:19854)的候選字串來源固定是 `INLINE_CODE_RE.findall(_strip_fences_text(text))`(scripts/lumos:19861)——也就是「先剝出所有反引號區間,只在那些區間裡找路徑」。「裸寫」代表要在沒有反引號包住的自由中英夾雜散文裡自己找出「這一段是路徑:行號」,這不是幫既有函式加一個 if 選項就能做到的事,而是要另外定義一套「候選字串邊界」的規則(中文標點、全形括號、URL、wikilink `[[...]]`、decision id `d12` 這類形狀都要排除)。spec 通篇沒有給出這條新掃描規則的定義,只用一句「認裸文字」帶過。
2. 這不是空想的邊界:本 repo 現有圖譜筆記裡已經有一模一樣形狀的裸文字寫法會撞到這個問題——`docs/lumos-toolchain-knowledge/Systems/autonomous-iteration-loop.md:39` 的 `DEP:` 行裡寫著「governance/autonomous-loop.sh(被 daily-governance.sh:26 以 --dry-run 6 呼叫)」,`daily-governance.sh:26` 沒有反引號、也沒有目錄斜線前綴,是最典型的「裸寫路徑:行號」。如果「認裸文字」的候選規則只沿用「必須含 `/`」的舊過濾(現有 `_node_code_ref_tokens` 的 `if "/" not in token: continue`,scripts/lumos:19873),這一類「檔名:行號」寫法會被漏收(規則形同虛設);如果為了收它而放寬成「檔名(含副檔名):數字」也算,則會跟中文散文裡常見的「檔名.後綴 + 冒號 + 數字」巧合(例如版本號、章節號寫法)混在一起,兩個方向 spec 都沒有給實作者判準。
3. 由於 S1 的 [test:t_note_shape_line_refs_existing_code_new_only] 與 S9 的 [test:t_node_code_ref_tokens_defaults_unchanged] 都是「應該」語氣的行為描述而非規則定義,審稿當下無法判斷這支尚未寫出的抽取器會不會漏擋(裸寫沒被收進候選)或誤擋(把版本號/章節號當成路徑引用),需要實作前先把候選字串的字元類與邊界規則寫進 spec 或條款,才有東西可以測。

〈front matter / lands_in / related〉已讀,無 finding
〈白話 / 依據〉已讀,無 finding
〈RETIRE-IF / REVISIT〉已讀,無 finding
〈做法 > 範圍與行〉已讀,無 finding(上線點截斷、合併只算自己改的、decisions 區塊用區塊行範圍判而不靠解析欄位,三者的描述跟「每支檔有家」現有的 `_nodehome_golive`/`_nodehome_clamp_base`/`_nodehome_merge_own_changes` 邏輯一致,沒有看到新增的分岔點)
〈治理帳寫入加鎖(移出)〉已讀,無 finding(移出後本計劃只照既有 `_gate_event` 寫帳,不改它的鎖行為,跟 [[Issues/治理帳多個寫入者都沒上鎖]] 現況一致)
〈紀律範本改寫〉已讀,無 finding
〈消費專案的 CI〉已讀,無 finding
〈條款 S1〉已讀,無 finding
〈條款 S2〉相關發現見 F1(放行寫法的驗證只顧 note-shape 自己,沒處理同一文字餵給既有 refcheck/G1 的後果)
〈條款 S3〉已讀,無 finding(`[來源:...]` 用「來源」二字,`SRC_REF_RE` 只認字面 `\[src:`——scripts/lumos:4270——不會撞名,S3 的「不應被重建守衛當成檔案路徑」這句核對屬實)
〈條款 S4〉已讀,無 finding
〈條款 S5〉已讀,無 finding
〈條款 S6〉已讀,無 finding
〈條款 S7〉已讀,無 finding
〈條款 S8〉已讀,無 finding
〈條款 S9〉相關發現見 F1、F2(「與改動前相同」只顧到舊文字,沒顧到 spec 自己教人寫的新文字;裸文字選項本身沒有定義候選規則)
〈條款 S10〉已讀,無 finding
〈條款 S11〉已讀,無 finding
〈回退〉已讀,無 finding(指令留一版空殼、鎖與抽取器選項不撤,順序合理)
〈誠實界線〉已讀,無 finding(圍欄內舊輸出被擋、消費專案沒接 CI 擋不住的兩條界線都已誠實揭露且各自附了 RETIRE-IF/doctor 事後掃描;唯獨沒有揭露 F1 這種「自己的放行寫法會撞既有 refcheck/G1」的風險)
〈審計修正紀錄〉已讀,無 finding(r1 七席折入紀錄與現行文字一致,鏡像核對數字沒有內部矛盾)

## 實務隱患(逐類,審稿員自己過一輪)

- 守衛面(誤擋/繞過):spec 自己列的 RETIRE-IF 覆蓋了「繞過變多」「擋不住」「零觸發」三種,但沒把 F1(新語法反過來讓既有硬閘誤擋)算進「守衛面」風險——這是本審查新增的風險面,已列 F1。
- 併發:note-shape 只讀不寫筆記,治理帳寫入沿用既有無鎖寫入器,寫帳失敗不改變擋不擋(`_gate_event` 既有契約)——沒有新併發風險。
- 效能:提交前只查暫存區差異、推送前用範圍限定+上線點截斷,不會退化成整庫掃描(spec 明確排除空樹兜底);沒有看到熱路徑疑慮。
- 資源:不開新連線、不開新檔案控制代碼,git 呼叫皆為既有包裝函式;無資源洩漏疑慮。
- 對外送出:已排除(spec 自己也這樣寫),核對屬實——全部呼叫都是本機 git 與檔案讀取。
- 不可逆:已排除,核對屬實——擋下不產生提交、hook 不動工作目錄,回退步驟裡的「指令先留空殼」也考慮到消費端 CI 相容性。
- 金流:無關,核對屬實。
- PII/認證/限流/快取/遷移:與本功能(本機文字掃描)無關,不適用。

## 圖譜節點逐條判(hook 附加的三個節點)

- [[Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋]]:不影響——本計劃是這篇 Issue d1/d2/d3 決策的其中一半機械落地,沒有改動這篇本身記錄的稽核數據或決策內容,計劃裡的 REVISIT/RETIRE-IF 也跟這篇的量測口徑(抽樣、doctor 覆蓋率)一致,沒有互相矛盾之處。
- [[Systems/每支檔有家]]:不影響——這份 spec 只讀用 `_nodehome_code_kind`、`_visible_lines` 等既有函式本身(不修改它們的實作),且明講「不套每支檔有家『不要求有家』的那些豁免」,即改用更窄的判定而非改動共用函式的既有行為;因此每支檔有家自己的提交前/推送前/健檢三段契約(含它 summary 裡列的多支 PITFALL 與 t_nodehome_* 測試)不會被這份 spec 的改動波及。
- [[Issues/治理帳多個寫入者都沒上鎖]]:不影響——這份 spec 明確把加鎖移出到這篇 Issue,自己只照既有 `_gate_event` 契約寫帳(失敗不改變擋不擋),而且在〈實務隱患〉裡已註明「本計劃讓每次提交都寫一筆,頻率會變高」,跟這篇 Issue 正文「注意:筆記形狀擋_計劃上線後每次提交都會寫一筆事件」的說法完全對得上,沒有隱瞞或矛盾。

## 總結

最嚴重 severity:blocker(F1)。blocking 共 2 條(F1、F2)。
