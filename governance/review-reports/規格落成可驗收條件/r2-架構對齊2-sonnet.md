severity: minor

## 一、分層與依賴方向

**對齊,上一輪本席點名的灰色地帶已收斂。**

上一輪(r1)本席判定「`kind: spec-gate` 留痕走 `cmd_canary` 或另開寫入路徑」未寫清楚,是 minor。凍結稿這版已明寫方向:

引句:「留痕走既有審查帳寫入口 `cmd_canary`,把 `kind` 的封閉列舉擴充一個 `spec-gate`」

對照:`scripts/lumos:27854` 現在仍是 `cr.add_argument("kind", choices=("caught", "missed", "none"))`,`_round_valid_m2` 在 `scripts/lumos:6331`——凍結稿把擴充列舉、讀側同步認得都點名了,跟既有「單一寫入口」慣例對齊,此點折清。

逃逸自動記(S9–S11、S18–S20)這部分**已經是落地程式**,不是紙上設計:`_auto_escape`(`scripts/lumos:7497`)、`_vault_write_lock` 包住整段讀-判-寫(`scripts/lumos:7519`)、`_escape_auto_failed` 寫治理帳(`scripts/lumos:7565`)、`pre-push:237/245` 兩處呼叫——與第五節逐字對得上,沒有跨層直呼,分派層次跟 `cmd_canary`/`cmd_pitfalls`/`cmd_spec_trace` 同層。

引句:「寫側上 `_vault_write_lock`(r1 回滾席:兩個 hook 同時寫會繞過去重)」

推送閘讀留痕清單那段(第 163 行)方向也對:推送閘本來就是既有 `_gate_failopen`/`_gate_event_or_warn` 那條 subprocess 呼叫鏈的延伸,沒有新開一條 repo 層以外的路徑。

## 二、命名與錯誤處理

**大致對齊,一處命名跟既有慣例不同形狀(新發現,r1 未點名)。**

- 指令 `spec-gate` 延續 `spec-trace`(`scripts/lumos:4718`)的家族命名,對齊。
- 新 kind `escape-auto-failed` 已經是現行程式的值(`scripts/lumos:7573` `"kind": "escape-auto-failed"`),跟既有治理帳 kind 一律小寫連字號的形狀(`approved`/`degraded`/`step-failed`/`shallow-skip`……)一致。
- 印法三段式:凍結稿寫「照處置閘」,沿用既有 `[disposal]` 白話輸出慣例。

引句:「新閘 `lumos spec-gate <計劃.md>`(印法照處置閘)」

- **命名不一致(minor,新發現)**:新階段名 `push-gate:unreviewed` 用冒號分兩截,但這支 repo 現有 `gate`/`kind`/`stage`/`detail` 欄位裡**沒有任何一個值用冒號組合詞**——全查一遍只有一個誤命中(`"detail": "失敗的步驟:"` 是句子結尾的標點,不是複合值),既有慣例全是連字號(`code-loop`、`push-gate`、`escape-auto-failed`、`check-s5`)。`push-gate:unreviewed` 是這支 repo 第一個冒號複合值,跟既有「同一欄位內用連字號串詞」的形狀不一樣。

引句:「階段記成 `push-gate:unreviewed` 分開數」

file: `scripts/hooks/pre-push:245`(`--stage push-gate:unreviewed`,已落地的程式碼,非假設)、`scripts/lumos:7534`(`if stage == "push-gate:unreviewed"`)

severity: minor

## 三、第二種做法

**沒有第二套解析或第二本帳;一處是全新機制、無舊做法可比,標記為命名層的鄰接風險而非結構違規。**

- `[keeps]` 標記與五型句式驗證是正交檢查(既有 `_clause_bindings_for` 只驗存在性/互異性,不驗定義行文字),不構成第二套解析引擎;PRIOR-ART 也明寫借用 EARS/BDD、不自建。
- 逃逸帳沿用既有 `.escape-log.jsonl`/`cmd_loop_escape`(已落地),四類偵測沿用 `PITFALL_CLASSES`(`scripts/lumos:16998`),沒有另開第二本帳或第二套風險偵測。

引句:「留痕走既有審查帳的寫入原語」

- **回退錨 `git tag pre-spec-gate`(⚠ 判不準,新發現)**:`git tag -l` 在本 repo 目前是空的——沒有任何既有設計實際用過 git tag 當回退錨;唯一提過 git tag 的既有計劃是 `Projects/版本發布流程_計劃.md`,但那是給**發版**用的語意化版本 tag(`vX.Y`),從未落地,跟凍結稿這裡「打一個一次性 tag 當程式碼回退基準點」是不同用途。本 repo 已有一套叫「錨」的既有機制——`Systems/anchor-integrity.md` 的 `lumos anchor verify/approve` + `anchor-baseline.json`,用途是守「把關 hooks/runner 本身沒被悄悄改」,跟這裡「回退錨」語意不同但共用「錨」這個詞。兩者功能不衝突、不是同一份資料的第二套寫法,但**沒有任何既有『回退用 git tag』的先例可對齊**,是全新機制;命名上跟既有「錨點」詞彙相鄰容易混淆(不確定是否構成本題定義的「第二種做法」,標 ⚠ 交編排者判)。

引句:「處置閘第五步改回 git tag `pre-spec-gate` 那一版(落地 S8 前先打這個 tag,r1 回滾席:沒有錨的「原本那一版」會變成猜)」

file: `docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md:1-20`(既有「錨」機制的用途與範圍,五個固定錨點+approve 留痕,跟這裡的一次性 git tag 是兩件事)

severity: minor

## 四、落點

**基本對齊,一處欄位重複宣告的形狀跟既有慣例不同(新發現)。**

`lands_in` 是這個 repo 已經在用的 frontmatter 欄位(`Projects/檢索訊號三件_計劃.md`、`每支檔有家_計劃.md`、`新增告警閘_計劃.md` 等 9 篇都有),既有用法一律**只在 frontmatter 宣告一次**、不在正文重複寫。凍結稿的 frontmatter 已經有:

引句:「lands_in:
  - Systems/design-loop
  - Systems/規格閘」

但正文第 212 行又重複寫了一次、格式還不一樣(frontmatter 是純節點名列表,正文是 `[[連結]]`+反引號+括號說明並列):

引句:「lands_in: [[Systems/design-loop]](閘的語意)、新開 `Systems/規格閘`(spec-gate 與條款檢查器的家)」

對照:`docs/lumos-toolchain-knowledge/Projects/檢索訊號三件_計劃.md:12-14`(`lands_in:` 只在 frontmatter 出現一次,正文沒有重複陳述)——這篇是唯一一份把 `lands_in` 同時寫兩處、兩種格式的計劃,屬於本專案自己記過的「知識同步散落會漏」那個形狀(一份資料兩個地方寫,之後只改一邊會漂移),但欄位本身、新開 `Systems/規格閘` 管 spec-gate 本體與條款檢查器、`design-loop` 只留閘的語意這個切法,跟 r1 本席已核可的落點理由(design-loop 已是長成包全部的巨型節點)沒有變,結構仍對齊。

severity: minor

---

不對齊共 3 條,其中 major 0 條(minor 3 條:`push-gate:unreviewed` 冒號複合值跟既有連字號命名不一致;`git tag pre-spec-gate` 回退錨與既有「錨」機制詞彙相鄰、無先例可對齊,標 ⚠ 判不準,建議實作時在文件裡明講兩者不是同一機制;`lands_in` 同時寫在 frontmatter 與正文兩處、格式不同,有漂移風險)。
