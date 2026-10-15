severity: major

整份 spec 已逐節讀完,spec 引用的函式與檔案都已開檔核對。`cmd_loop_next`、`_is_toolchain_repo`(`scripts/lumos:25437`,判別鍵為 `skills/lumos-project-notes/SKILL.md`,有 6 處呼叫)、`_TIER_ROSTER`、`("code","high")` 的 `資安` 席(`required-gated`)、`t_security_seat_doc_sync`、`t_disposal_security_seat_required`、`t_roster_code_high_has_security_seat`、`t_templates_security_seat_section` 都存在,「沒有程式比對併發席名」也屬實。`code-` 前綴的判法也與 `scripts/lumos:16275` 和 `scripts/lumos:16280` 一致。

## 固定席逐條判

**判定:不影響。**
- **既有合約:** spec 明說不動編制表、處置閘和席名,`t_roster_code_high_has_security_seat`、`t_disposal_security_seat_required` 保持成立。
- **既有守衛測試:** `t_templates_security_seat_section` 的切段方式是 `split("\n## ")`,新增內容只要用 `###` 或粗體小標,就不會截斷 §7.8 原段。`t_security_seat_doc_sync` 要求設計審 `SKILL.md` 不含「資安席」,spec 沒動那檔。
- **殘留風險:** 另有兩處風險不破壞固定席,見 finding 1 與 finding 3。

---

severity: major
blocking: 是 — 三類之外有一類真洞從此沒人看,而 spec 的〈實務隱患〉把它說成「少看一類」,實作者會照字面把派工詞做成漏掉這些洞。
引句:「派工範圍只看三類」
段落:〈新規則〉1、〈實務隱患〉守衛面。
問題:
- 原 §7.8 第 5 類「執行邊界:hook、安裝腳本、CI 會不會執行不可信位置的檔;shell 插值;寫進使用者全域設定;授權範圍被放寬」,在新三類裡沒有對應。
- 新 ① 只管「進到給 AI 的指令」,新 ② 只管「讀寫」,都不管「執行」。
- 原 §7.8 寫明 d6 的成因是「repo 公開、README 教一行安裝、打開陌生 repo 時 hook 曾執行對方的程式」。這些成因與「單人本機、AI 依序操作」無關,是外部第三方攻擊面。
- 被整類拿掉的還有:
  - 密鑰與個資進公開 repo 或帳本。帳本與卷證會進 git 並公開,本機路徑和使用者信箱都可能在內。
  - 新依賴與供應鏈。
  - 安裝腳本與 CI 工作流。
- spec 只在「範圍外」處理了「刻意多步偽造」,沒有把「執行不可信檔案」「密鑰進公開 repo」「安裝腳本」明列為接受或納入。
- 這與使用者裁定的三類字面相符,但裁定沒說這些也不看。至少要明寫兩者之一:納入 ②(讀寫越界擴成「讀寫與執行越界」),或在 RULE 與 REVISIT 裡明講「接受不看」。
佐證:
- 原清單見 `skills/lumos-design-loop/templates.md:412`(§7.8 標題與「為什麼有這一席」)。
- 原清單第 5 類見 `skills/lumos-design-loop/templates.md:439` 附近。
- CI 工作流存在:`.github/workflows/ci.yml:7`(`pull_request` 觸發)。

---

severity: major
blocking: 是 — 「所有專案都適用」的刪檔紀律只落到三份圍欄,必派的架構對齊席和 §2/§4、§7.5 兩處仍不帶,無人看顧時照樣卡住。
引句:「§1、§3、§7.8 各份派工詞圍欄第二行(寫 `git -C <那個目錄>` 那句)句尾補「刪檔照 §0 那條寫字面絕對路徑」」
段落:〈做法〉9、S10。
問題:
- `templates.md` 裡有 6 個含 `LUMOS-SEAT:` 的派工圍欄:§1(行 29)、§2(行 79,§4 照它)、§3(行 141)、§7.5(行 322)、§7.6(行 342)、§7.8(行 417)。
- §0 自己列的就是 §1、§2、§3、§7.5、§7.6、§7.8 六處。
- spec 只補 §1、§3、§7.8,漏掉 §2/§4 辯方、§7.5 規格符合席、§7.6 架構對齊席。
- 架構對齊席每個 code 分級都「required」派(見 `_TIER_ROSTER`),幾乎每輪都派到,而且「無人看顧」正是 spec 自己點名的失敗情境。
- S10 的測試也只驗這三份,漏掉的圍欄不會被守住。
- 還有一個遺漏:新增的〈工具鏈本 repo 的範圍〉第二個 §7.8 圍欄也要有這句,spec 沒明列,S10 的「每份派工詞圍欄」也沒涵蓋它。
佐證:
- ``file: `skills/lumos-design-loop/templates.md:22` ``(§0 列的六處)。
- ``file: `skills/lumos-design-loop/templates.md:79` ``、``file: `skills/lumos-design-loop/templates.md:322` ``、``file: `skills/lumos-design-loop/templates.md:342` ``(漏掉的圍欄)。

---

severity: minor
blocking: 否 — 兩處自相矛盾的敘述,做錯的後果是 S3 測試和回退描述對不上,不致壞系統。
引句:「原本那個圍欄一字不動,開頭補一句「消費專案用這份」」
段落:〈現況〉第一列(原六類段一字不動)、〈做法〉2 對照〈做法〉3 與 9。
問題:
- 〈做法〉2 與 S3 都說原圍欄不動、六類仍完整在段外。
- 〈做法〉3 要在原圍欄的「不報」裡補「工具鏈本 repo 歸資源席」,〈做法〉9 要改原圍欄第二行。兩處都改動了原圍欄內部。
- 〈回退〉的措辭同時列了「§7.8『不報』補的那幾句」,也承認有改。
- 「一字不動」與「補句」並存,實作者無從判斷哪個為準。「開頭補一句」是補在圍欄外還是內,也沒寫。
- 建議統一為:圍欄內只改這兩處,其餘不動。
佐證:``file: `skills/lumos-design-loop/templates.md:417` ``(原圍欄第二行);``file: `skills/lumos-design-loop/templates.md:439` ``(「不報」段)。

---

severity: minor
blocking: 否 — 影響派工人判讀,只是文案誤導。
引句:「在「應派」段後印(編制表算不出來、印「目前算不出該派誰」時也照印)」
段落:〈做法〉5。
問題:
- 規則是「`code-` 開頭就印」,沒有限 tier。
- light 與 standard 的 code 編制(`("code","light")`、`("code","standard")`)根本沒有資安席,也沒有「併發與資源」鏡頭席。light 只有架構對齊,standard 是單 reviewer 加架構對齊。
- 那行文字仍會寫「資安席照…、併發與資源席改資源鏡頭」,對編排者是誤導。
- 建議限定 `eff_tier == "high"`,或把文字改成「若派資安席/資源席」。
- 同處還有:沒帶 `--tier` 的 legacy 編號也會被印。
佐證:``file: `scripts/lumos:14014` ``(light/standard 編制)。

---

severity: minor
blocking: 否 — 屬於 spec 對自己風險方向的錯誤宣稱,現實發生機率中等。
引句:「結果是工具鏈本 repo 暫時照舊規則審,方向是多審不是少審。」
段落:〈實務隱患〉版本錯位;〈做法〉5。
問題:
- 範圍由「vault 所屬 repo 根」或 `--repo` 決定,不是由被審的 diff 決定。
- `templates.md` §3 須知①自己寫了「會談開在 A、審 B 的分支」是實際發生過的情境。
- 在工具鏈會談裡不帶 `--repo` 審消費專案的分支,會印出工具鏈範圍,消費專案被收窄範圍審,方向是少審,與 spec「消費專案照舊」承諾相反。
- spec 只分析了舊版 lumos 配新範本,沒分析跨 repo 派工這一向。
- 建議在那行或 §7.8 段註明「以被審 repo 為準,跨 repo 派工時改 `--repo <被審 repo>`」,並在 REVISIT 的抽查裡加這一項。
佐證:``file: `scripts/lumos:16316` ``(`_root = Path(repo).resolve() if repo else _vault_repo_root(env)`);``file: `skills/lumos-design-loop/templates.md:112` ``(須知①)。

---

severity: minor
blocking: 否 — 處置流程在邊角情況下沒有明確出口。
引句:「blocker 照處置閘規則不能放行;範圍外的 blocker 只能走「改文件拿掉保護說法」那條折。」
段落:〈新規則〉1 對照〈做法〉2 的新圍欄「標 minor、blocking: 否」。
問題:
- 新圍欄叫資安席把範圍外手法標 minor,規則段卻預期有範圍外的 blocker,兩者不一致。
- 若範圍外 blocker 在文件裡根本沒宣稱防護(沒有「那句不存在的保護說法」可拿掉),spec 沒給出口。
- 實際出口只能是辯方駁倒或降級,而 spec 要求「不加機制」「折或放行」二選一,沒提辯方。
- 處置閘明文「輪內有 blocker 席,accepted 必須為空」,這種 blocker 會卡住迴圈。
- 建議補一句:範圍外一律標 minor;若仍被標 blocker,走辯方降級並附理由。
佐證:``file: `scripts/lumos:27974` ``(blocker 不得放行)。

---

severity: minor
blocking: 否 — 文件同步守衛範圍小於實際提到資安席與鏡頭的檔,日後會漂。
引句:「`t_toolchain_lens_scope_doc_sync`(照 `t_security_seat_doc_sync` 的逐檔列舉寫法)」
段落:〈做法〉4 與 6、S5。
問題:
- 既有 `_SEC_SEAT_DOC_FILES` 有 6 個檔,含 `skills/lumos-project-notes/reference.md` 和 `docs/methodology/圖譜即合約.md`(行 151 敘述資安席「high 必派、問閘會擋」)。
- 新守衛與修改只覆蓋 3 個檔,方法論和 project-notes reference 描述資安席時沒補範圍,是同一份規則散落的另兩處。
- 〈現況〉表格又列了「規則散在哪」卻漏這兩檔。
- 〈做法〉4 還寫 `06-代碼審與推送.md`「同上一份鏡頭列」,但該檔並沒有「併發與資源」那一列,只有 high 必派資安席那句,所以「併發與資源改資源鏡頭」在該檔是新增敘述而非修改。
- 驗收條款編號順序是 S10、S11、S9,且 S9 的 `[manual:]` 與 S8 的 `[manual:]` 都沒有機械檢查。這屬排版瑕疵。
佐證:
- ``file: `scripts/test_lumos.py:57812` ``(`_SEC_SEAT_DOC_FILES`)。
- ``file: `docs/methodology/圖譜即合約.md:151` ``。
- ``file: `skills/lumos-project-notes/commands/06-代碼審與推送.md` ``(無「併發與資源」字串)。

---

## 其餘各節

- **裁定來源、怎麼分辨工具鏈本 repo:** 已讀,無 finding。
  - `_is_toolchain_repo` 是同 repo 的 `skills/lumos-project-notes/SKILL.md` 是否存在,與 spec 描述一致。
  - 「消費專案自己放這個檔就誤判」被 spec 歸為刻意手法,合理。
- **不改的部分、不做、回退:** 已讀,無 finding(「七支測試」的數量對得上)。

## 實務隱患鏡頭

| 風險類 | 隱患 |
|---|---|
| 守衛面(範圍收窄後沒人看的洞) | 有,見 finding 1 |
| 消費專案誤用工具鏈範圍 | 有,見 finding 5(跨 repo 派工) |
| 舊 lumos 配新範本 | 無。spec 的「多審」判斷正確:沒有那一行就用原圍欄。 |
| 新 lumos 配舊範本 | 無。多印一行,範本沒有對應段,編排者找不到而退回原圍欄,仍是多審。 |
| 注入 | 無。印出的是固定字串,不帶帳上自由文字。 |
| 併發、效能、資源 | 無。`loop next` 只多一次 `is_file()`。 |
| 可逆性 | 無。純文件加一行輸出,回退描述完整。 |

最高等級 major,blocking 2 條。
