severity: major

### F1 「不審的行」的圍欄門檻寫成四個反引號,跟同一篇裡剛引用的 `_visible_lines` 實際門檻(三個)自相矛盾,等於另開一套圍欄判定

severity: major
blocking: 是 —— 若照字面實作,「不審的行」這條規則會需要一個「4 個以上反引號/波浪號才算圍欄」的判準,而 `scripts/lumos` 全檔唯一的圍欄判定 `_visible_lines`(scripts/lumos:3231 起,關鍵行 scripts/lumos:3262 `s.startswith(("```", "~~~"))`,只吃跟 CommonMark 一致的「3 個以上」)不認這個門檻;同一段第 58 行也正確引用 `_visible_lines` 為「三個以上」。這正是 `_visible_lines` 自己的說明(scripts/lumos:3231 docstring)點名要防的那種事故形狀——各處各寫一份圍欄判定、門檻不一致,曾經真的吃過虧(幽靈圖譜邊、假合約佐證、整段散文被吞)。第 61 行、第 116 行([S4])目前是「引用同一支函式,卻附一個那支函式不認的數字」,不是單純用詞誤差,而是在文件裡種下「第二種圍欄判準」的種子。
引句:「圍欄記號行(`_visible_lines` 認的那種,含四個以上反引號與波浪號)」
file: `governance/review-reports/筆記內容審/r3-work.md:61`

---

## 四問逐答

**1. 分層與依賴方向**
第二層的設計沒有直呼第一層(`_note_shape_eval`)內部邏輯,而是走「先抽共用函式、兩層都呼叫它」(r3-work.md:52-57),上線點與範圍截斷也是對既有函式加參數而非另寫一份(r3-work.md:59,「上線點函式與截斷函式加『看哪支掛鉤』參數」)。這個方向跟 `scripts/lumos` 既有「單一實作源」的慣例一致,例如 `_visible_lines` 本身就是為了收斂「各處自寫圍欄判定」而抽出的共用函式(scripts/lumos:3231 docstring)、`_nodehome_cat_blobs`(scripts/lumos:22801)也是同樣性質的收斂,且它的說明明講「第四輪架構席:第三輪另寫了一套 cat-file --batch 解析」(scripts/lumos:16974)曾經被抓過同型問題;本篇對 `_nodehome_cat_blobs` 的引用(r3-work.md:77,「用一次列目錄加一次批次讀檔(`_nodehome_cat_blobs` 那種讀法)」)是正確重用,不是繞過。分層本身沒有問題,問題出在 F1:同一段文字一邊說「走 `_visible_lines`」、一邊給了它不認的門檻,若照字面實作等於在第二層私下多開一條判準,違反了這條依賴方向要守的「單一實作源」原則。

**2. 命名與錯誤處理**
子命令、旗標與事件種類都是沿用既有家族命名,沒看到自造一套的跡象:`prepare/record/check/skip` 四段式跟既有 `home check`、`note-shape --diff`、`code-loop check` 並排(r3-work.md:92,已用 `scripts/hooks/pre-push:236,247,309` 的實際順序 home check → note-shape → code-loop check 核對過,note-audit 卡進 code-loop check 之前跟現有順序不衝突);`note_audit.gate` 的 block/warn/off 三態與「從被檢查版本讀、非 block 時 doctor 印一行」照抄 `note_shape.gate` 的既有讀法(比對 scripts/lumos:23480 `_note_shape 設定(從被檢查的版本讀,照 _nodehome_config 的快照讀法)`,與 docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:42 的放行文字同一形狀);`_KNOWN_GATES` 登記閘名(r3-work.md:78)也是既有機制(scripts/lumos:6599)。判定者模型常數把 Codex 那邊指到既有的 `_CODEX_SEAT_MODEL`(scripts/lumos:17858)而不是另開一個,claude 側新開 `opus` 一個字串常數,命名風格跟既有 `_DOOR_RULE_VERSION`/`_SMALL_CHANGE_RULE_VERSION` 這類「規則版本常數 + 測試釘住,manual 補實驗」的模式(scripts/lumos:5398、5409,搭配既有 `[manual:]` 標記慣例 scripts/lumos:3815)吻合,S14 用 `[manual:]` 綁「改版本要重跑小實驗」不是自創語法。`decision-amend --field --text` 的旗標形狀跟既有 `decision-supersede note match --by --ended`(scripts/lumos:32199-32203)、`decision-add note content --decided --context --why`(scripts/lumos:32218-32223)同一種「positional 定位節點/決策、flag 帶要改的內容」寫法,沒有另開一套。「不改代碼審簿記豁免、改用順序」這條的收尾動作——判定檔提交後讓留痕失效、重跑 `code-loop pass --note` 補回——不是新發明,`scripts/lumos:30381` 已經有「審查留痕重跑 `lumos code-loop pass --note \"…\"`」這句既有提示,本篇只是多了一個觸發它的場景,沒有另開一條補救路。唯一的命名/定義層級不一致是 F1 那條(「`_visible_lines` 認的那種」卻附錯數字),但因為它會導致實際判斷邏輯分岔而不只是文字用詞問題,已計入 major,這裡不重複記 minor。

**3. 第二種做法**
本篇對照的四個既有形狀(PRIOR-ART①-④)引用得住:①借第一層的新增行算法並抽成共用函式(已於問 1 核對);②判定檔存法本篇老實承認是新存法,並比對過治理帳 jsonl、放行檔兩種既有存法為什麼不適用(r3-work.md:70),另外新補了跟 `loop replay --freeze`/`--golden`(scripts/lumos:579、32013-32016 確認真實存在,做的是「凍結判定、之後拿去比對」)的對照,並講清楚防竄改為什麼刻意不借——這條理由(防竄改不在防疏忽的範圍內,見第 0 節)站得住,不是含糊帶過;③留痕閘的推送前查詢/CI 標紅/skip 出口對齊 `Systems/pitfalls-code-loop`,跟既有 note-shape 掛鉤方式一致;④設定讀法對齊 `note_shape.gate`,已在問 2 核對。r2 新加的五項裡,範本檔載入、模型常數、check 排序、簿記豁免改用順序,四項都在問 1、問 2 驗過是重用既有形狀,沒有另開一條路;`decision-amend` 的遠端追蹤參照 reflog 新鮮度判法在既有 `scripts/lumos` 裡找不到直接先例(`_pull_source_or_abort` scripts/lumos:17021 做的是「當場 pull」而非「檢查 reflog 新鮮度」,是不同問題),但這是全新指令要解的全新問題,沒有既有機制可借也沒有繞過既有機制——不構成「第二種做法」,只是「新做法」,兩者在這份審查的判準下不同(⚠ 若日後要嚴格判斷這條 fetch 新鮮度邏輯要不要收斂成共用函式,留給併發/正確性席比較合適,這裡不確定要不要開 finding,故不開)。唯一實質的第二種做法風險是 F1:對「圍欄記號行」引用 `_visible_lines` 卻附一個它不認的門檻,若字面實作,判斷邏輯就會跟共用函式分岔。

**4. 落點**
新家 `Systems/筆記內容審`(r3-work.md:57)與 `Systems/筆記內容閘`負責範圍的改寫(「不管第二層的判定與紀錄,但『哪些筆記行算新寫的』共用函式歸這裡」)跟該節點目前的 frontmatter 對得上:`docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:6` 現在寫的是「不管推送前 AI 審查員(第二層計劃)」,本篇要把它收窄成「共用函式歸這裡、其餘歸第二層」,方向一致,不是把第二層的東西誤放進第一層的家,也沒有把第一層的東西(range/golive 函式)誤搬進新家——上線點與範圍起點兩支函式的家維持 `Systems/每支檔有家`(r3-work.md:57),跟 `Systems/筆記內容閘.md:40`「範圍、上線點、合併的算法本身的家是 Systems/每支檔有家」一致。沒有發現落點問題。

不對齊共 1 條,其中 major 1 條
