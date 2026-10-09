severity: major

這份 diff 有兩處引入第二種做法,都在 scripts/lumos。一是 RULE 行的解析和「有沒有過期」的判斷自己寫了一套,二是 `.lumos/config.json` 的讀取和檢查又寫了一套。其餘分層、錯誤處理和掛鉤旗標退路都跟鄰居一致。以下行號都是 `/Users/enzo/harness/lumos-toolchain-target-arch`(HEAD `fd2bd3ec`)的 scripts/lumos。

## 問 1:分層與依賴方向

**對齊。**
- **推送前熱路徑沒有載圖譜。**
  - `_pitfall_diff_collect` 只讀起點版宣告來分哪些檔用目標基準(`:41690`),不讀節點。這跟 `_stack_questions_config` 註解寫的「check 跑在 pre-push、不走載 vault 的 helper」同一個規矩(`:26816` 附近)。
  - `_arch_target_check_lines`(`:41244`)只對字串和 git 輸出做事,不載圖譜。
  - 規則原文由派工鏡頭附,節點用 `git show <起點版>:<vault>/<節點>.md` 讀。這跟 `_dispatch_lens_role_text`(`:46399`)和 `_lens_contract_lines`(`:45389`)同一層,依賴方向正確。
- **doctor 載圖譜。** `_arch_target_doctor_lines(env)`(`:1967`)用 `env.notes`,doctor 本來就載圖譜,沒問題。
- **`last_arch`。** 掛法跟 `last_dispositions`、`last_bound`、`last_lint_new` 相同:函式屬性、進函式先清、寫進 verdict、再印(`:48458-48460`、`:48573`、`:49024`)。
- **新增的熱路徑成本。** pitfalls 和 `code-loop check` 各多幾次 `git show`,不屬於跨層直呼,不算 finding。

**不對齊。** ARC-1、ARC-2、ARC-4、ARC-5 的細節見問 3。

## 問 2:命名與錯誤處理

**對齊。**
- **壞宣告的處理。** `_arch_targets_config` 的 `(rules, warnings)` 回傳形狀、「整份不用」的措辭、警告不回填專案原值,都跟 `_review_roles_config`(`:26636`)一致。
- **出錯當沒有。** `_dispatch_lens_arch_text` 的「寬接並印 stderr 提醒」跟 `_dispatch_lens_role_text`(`:46399-46408`)一致。
- **掛鉤旗標退路。** `ARCH_RE`、`wants_arch_target` 和 `_opt_flags` 重叫,是把既有 role 那條擴成兩個旗標,沒另起一套(hook `:30`、`:173`、`:448`)。
- **測試夾具。** 沿用 `_role_git_repo`、`check(...)`、`print("  ✓ …")`(test_lumos.py `:41076`)。

**不對齊。**

ARC-6
- 內容:hook 的 `_role_text` 現在也回傳 arch_text,名字沒改,讀的人會以為只有角色段。
- 引句:「def _role_text(r) -> str:」
- 佐證:scripts/hooks/claude/dispatch-lens-hook.py:267
severity: minor
- blocking: 否

ARC-7
- 內容:doctor 的宣告清單用裸 `print` 自己拼出「      • 」,這個格式本來是 `warn_soft` 輸出的。清單也插在 L 段尾端,與 L 段(筆記開頭欄位格式)無關。鄰居的資訊行是 `ok(...)`(`:1726`)或 `warn_soft`(`:1755`)。
- 引句:「print(f"  目標架構宣告 {len(_atl)} 條(架構對齊席在這些範圍改拿目標規則當基準):")」
- 佐證:scripts/lumos:1755-1767
severity: minor
- blocking: 否

## 問 3:第二種做法

**ARC-1 RULE 行的解析和過期判斷,自己重寫一套**
- 內容:`_arch_target_rules`(`:41198`)自己用 `_ns_summary_logical` 加 `slot_parse` 抽 RULE 行,自己比 `status == "superseded"`,自己用字串比對 `until[:10] < today`。專案已有:
  - `parse_rule_fields`(`:3904`)是 RULE 欄位的單一入口,並且特地處理舊寫法的行。
  - `_rule_stale_keys`(`:3989`)的註解寫「門檻與判法只有這一份」,lint 和 doctor S16 共用。
  - `_note_summary_entries`(`:4038`)是摘要條目的共用入口,有單行 `summary:` 的退路。
- 具體不一致:
  - doctor 路徑把 `"---\n"+fm_lines+"\n---\n"` 手拼後丟給 `_ns_summary_logical`,等於重做 `_note_summary_entries` 的第一行,漏掉單行 summary 的退路。
  - 判 superseded 時,既有寫法是 `(status or "active").lower()`,新碼沒轉小寫。
  - 「有效 RULE」的定義變成第三套:只看「沒作廢」,跟 S16 的定義不同。計劃筆記還特地寫「規則不另立語法」,實作卻另立了解析器。
- 引句:「fields = {k: v for k, v, err in slot_parse(rest)["fields"] if not err}」
- 佐證:`scripts/lumos:3904`、`scripts/lumos:3989`、`scripts/lumos:4038`
severity: major
- blocking: 是

**ARC-2 `.lumos/config.json` 的讀取與檢查是第二套**
- 內容:
  - `_arch_targets_at`(`:41128`)自己用 `_lens_git show ... binary=True` 讀,自己處理 BOM、嚴格 UTF-8、`RecursionError`。
  - 專案的做法是 `_json_at_ref` 讀(`:45416`),再用 `cat-file -e` 判斷「檔在但讀不懂」,最後交給 `_review_roles_config`(`:26732-26734`)。
  - `_arch_targets_config` 又複製了一份 `_review_roles_config` 的逐條檢查迴圈,還多擋 `..` 段。
  - 結果是兄弟宣告 `review_roles` 不擋 `..`,`arch_targets` 擋,兩份檢查會各自漂。
  - 嚴格 UTF-8 的理由成立,但該擴充 `_json_at_ref` 或抽共用,不該另立讀法。
- 引句:「r = _lens_git(root, "show", f"{ref}:.lumos/config.json", binary=True)」
- 佐證:scripts/lumos:26732-26736、scripts/lumos:45416
severity: major
- blocking: 是

ARC-3
- 內容:`_arch_target_vault_rel`(`:41295`)是第三種「找 ref 那一版的圖譜資料夾」的寫法。
- 現況:專案已有多種,而且互相不一致,所以不硬判,標 ⚠ 交編排者:
  - `_ns_vault_rel`(`:31885`)
  - 派工鏡頭圖譜段用 base 樹加 `_vault_slug_of`(`:46541`)
  - 設計審用工作樹 glob(`:46695`)
- 引句:「r = _lens_git(root, "ls-tree", "-d", "--name-only", ref, "docs/", quote=True)」
- 佐證:scripts/lumos:46541、scripts/lumos:46695、scripts/lumos:31885
severity: minor
- blocking: 否

ARC-4
- 內容:`_arch_target_changed_files`(`:41267`)是派工鏡頭裡第二支「列改動檔」的實作。同一條派工路徑的角色段用 `_review_role_changed_files`(`:26690`),其 docstring 寫「派工角色段與推送前分級那一行共用這一支」。
- 差異:新函式刻意跟 pitfalls 的 `added` 同口徑,不含純刪除,所以有理由。但 pitfalls 的 `added` 是行內解析、沒有可共用的函式。
- 結論:兩邊都沒共用函式,鄰居本身不一致,⚠ 交編排者。
- 引句:「r = _lens_git(root, "diff", "--numstat", "-z", "--no-ext-diff", "--no-textconv", base, head)」
- 佐證:scripts/lumos:26690
severity: minor
- blocking: 否

ARC-5
- 內容:專案有 `nfc(s)`(`:426`),全檔 136 處使用。新碼寫了 8 處 `unicodedata.normalize("NFC", ...)`,同一份 diff 裡的 doctor 又用 `nfc(...)`,同一份 diff 兩種寫法並存。
- 引句:「rules.append((unicodedata.normalize("NFC", pat), unicodedata.normalize("NFC", node)))」
- 佐證:scripts/lumos:426
severity: minor
- blocking: 否

不對齊共 7 條,其中 major 2 條(ARC-1、ARC-2);ARC-3、ARC-4 標 ⚠ 交編排者。
