severity: major

這份設計大體是照既有合併快篩的架構擴充,新函式放在 `_choice_merge_*` / `_kill_merge_*` 那一層,順序機制也沿用既有的名單。不一致集中在兩處:加引號寫法的描述,以及事件行名稱比對。另有幾條 minor。本次只讀材料與既有程式碼,沒有執行任何測試或指令。

## 1. 分層與依賴方向

大致一致,但有兩處偏離。

- **函式分工(一致)**:
  - `_choice_merge_events(tail, names)` 是純函式,放在 `_choice_merge_*` 這組,和 `_choice_merge_classify`、`_choice_merge_facts` 同類。file: `scripts/lumos:28869`
  - 排序仍由 `_kill_merge_failed_first` 負責,只多吃 `merge_back`,沒有另立排序機制。file: `scripts/lumos:29241`
  - 呼叫方向仍是 `_kill_merge_iter` → `_kill_merge_screen`(寫 `c.merge_failed`)→ `_kill_merge_failed_first`(讀它),和現況一致。file: `scripts/lumos:29161`、`scripts/lumos:29238`

- **`_kill_merge_ready` 不再是純判斷(偏離)**:現在它的 docstring 寫明「其他幾道只算字串與路徑」。file: `scripts/lumos:28950`
  - 計劃讓它在時限門前寫檔,等於在判斷函式裡加了副作用。
  - 既有慣例是副作用放獨立 helper,例如 `_choice_merge_clear`。file: `scripts/lumos:28980`
  - 時限門擋下時,檔案已經寫了卻沒被用到,雖然無害,但和「時限門排最後是因為前面都不碰外界」的設計意圖相反。

- **直接取 `os.path.dirname(c.wt)`(偏離)**:這等於依賴 `_isolated_worktree` 內部的目錄結構(`parent/wt`)。file: `scripts/lumos:28088`
  - 既有做法是由該 helper 自己在 `parent` 裡寫標記檔,結構知識不外洩。file: `scripts/lumos:28123`
  - 計劃還得為此改既有測試的 `wt` 形狀,這就是耦合的症狀。

- **「跑到測試」的判斷分在兩處(偏離)**:`_choice_merge_classify` 已經在讀 `tail`(用 `_CHOICE_MERGE_SYSKILL_RE`),原因字串也由它產生。file: `scripts/lumos:28877`
  - 計劃卻在 `_kill_merge_screen` 事後把「逾時」覆寫成「逾時(跑到測試後掛住)」並改 `counts`。
  - 這讓原因決定權分散在 classify 和 screen 兩處。

severity: minor
blocking: 否
引句:「`_kill_merge_ready` 先算路徑(不寫檔)拿去做指令過長判斷;其餘條件都過、時限門之前才寫檔」

severity: minor
blocking: 否
引句:「classify 回 `unclean`、原因「逾時」、而且事件「跑到測試」→ 交斷路器時計數改成不計、原因改成「逾時(跑到測試後掛住)」」

## 2. 命名與錯誤處理

命名大致一致,錯誤處理有一處不同。

- **命名(一致)**:
  - `_CHOICE_MERGE_INIT` 符合同組 `_CHOICE_MERGE_*` 常數的前綴。file: `scripts/lumos:28737`
  - `_choice_merge_events` 符合 `_choice_merge_*` 函式前綴。
  - `c.merge_back` 與 `c.merge_failed`、`c.merge_need` 同屬 `merge_` 前綴。
  - `sh["init"]` 與既有的短鍵 `s/e/seg/eq/parts/task/pdir/rdir/tq` 同風格。file: `scripts/lumos:28766`
  - 測試用假 Gradle 的 `__events__` 與 `__merge__`、`__msleep__` 同風格。file: `scripts/test_lumos.py:146259`
  - `merge_back` 這個詞本身不太直觀(實際是「排後面的名單」),但屬風格問題,不列為不一致。

- **寫檔失敗靜默退化(minor)**:
  - 計劃寫「寫入失敗(OSError)→ `sh["init"]` 是 None、照常合併」,沒有印任何字。
  - 既有合併快篩每一條退化路徑都會印一行,例如 `_kill_merge_off` 一律印到 stderr。file: `scripts/lumos:28933`
  - 另一個先例是 `_isolated_worktree` 寫保留標記失敗時 `except OSError: pass`,也是靜默。file: `scripts/lumos:28123`
  - 靜默處理有先例,但本案的退化會改變整個快篩的行為:沒有事件就退回舊順序,逾時照舊計數。這比寫標記檔失敗的影響大。
  - 〈實務隱患〉已承認「專案自己設了 testLogging.events 蓋掉事件」這種沒有事件的退化,計劃也沒說要印字。

- **事件行解析沒指定常數(minor)**:鄰居把輸出特徵寫成模組層級的編譯 regex(`_CHOICE_MERGE_SYSKILL_RE`、`_KILL_COMPILE_RE`)。file: `scripts/lumos:28750`
  - 本案的事件行判斷只用文字描述「以 ` > ` 切開」,沒說是否用 module-level 常數。
  - 這屬實作細節,先標 ⚠ 請編排者留意。

severity: minor
blocking: 否
引句:「寫入失敗(OSError)→ `sh["init"]` 是 None、照常合併(指令變短,過長判斷仍成立)」

## 3. 第二種做法

有一條 major(加引號)和一條 minor(名稱比對),排序機制沒有第二套。

- **加引號:雙引號與 `list2cmdline` 不同(major,⚠ 措辭有歧義)**:
  - 計劃寫「路徑照 `_IS_WIN` 用雙引號或 `shlex.quote`」。
  - 既有的 helper 是 `_run_cmd_expand`:非 Windows 用 `_shlex.quote`,Windows 用 `_sp.list2cmdline([x])`(有空白才包雙引號,註解說明「cmd.exe 不認單引號,跟 `{python}` 同一套」)。file: `scripts/lumos:28076`
  - 若「雙引號」指手寫包一層 `"…"`,就是第二套加引號寫法,和 `list2cmdline` 對含引號、尾端反斜線的處理不同。
  - 若指的就是 `list2cmdline`,則只是措辭不精確,但 spec 仍應寫成「沿用 `_run_cmd_expand` 那套」,不然實作者很容易手寫。
  - 這個插入點正好在 `_choice_merge_cmd` 內,而這支函式已經用 `_run_cmd_expand` 處理所有片段。file: `scripts/lumos:28796`

- **名稱對到:多出一套規則(minor)**:
  - 既有的是 `_choice_merge_fullname`(完整類別名,`$` 換 `.`、去參數尾巴)加 `_choice_merge_hits`(f 等於 m,或 f 以 `.m` 結尾),這是單向比對。file: `scripts/lumos:28817`、`scripts/lumos:28826`
  - 計劃另寫了一套:類別只取最後一個 `.` 之後的字,對到時加上「m 以 `.f` 結尾」的反向比對。
  - 這是並存的第二種「事件名 ↔ 測試名」比對規則。計劃沒說明為何不能重用 `_choice_merge_fullname` 的正規化。
  - 實作上很容易把 `$`、去參數尾巴這幾步又寫一遍。
  - 若單純解析 stdout 需要簡短類別名,至少應註明與 `_choice_merge_hits` 的差異,並說明為何兩邊不統一。

- **排序機制(一致)**:沿用 `_kill_merge_failed_first`,只多一份名單。計劃明寫「只改順序、不判任何事」。

- **寫暫存檔(一致)**:檔案寫在隔離工作樹的上層暫存資料夾,與 `_isolated_worktree` 寫保留標記的位置和方式相同。file: `scripts/lumos:28123`
  - 寫法是 `open(..., encoding="utf-8")` 加 `except OSError`,沒有另一套原子寫入的新做法。

severity: major
blocking: 是
引句:「路徑照 `_IS_WIN` 用雙引號或 `shlex.quote`」

severity: minor
blocking: 否
引句:「類別先把 `$` 換成 `.`、再取最後一個 `.` 之後的字;測試名去掉參數尾巴(第一個 `(` 或 `[` 起)」

## 4. 落點

落點比前三段少了規格閘,也漏了舊計劃的被取代註記,兩條都是 minor。

- **只列 guard-kill,少了規格閘(minor)**:
  - 前三段的 `lands_in` 都是 guard-kill 加規格閘。
  - 第三段明確把 `merge_why`、`merge_trips`、`merge_reopen` 的說明寫進規格閘。
  - 第四段新增的 `merge_why` 字樣「逾時(跑到測試後掛住)」是治理帳欄位的新值。
  - 計劃自己寫「`merge_why` 的新字樣是既有欄位的新值,讀者照字串讀」。
  - 既然前一段把該欄位的說明放在規格閘,這個新字樣也該登記到規格閘那篇,至少補一句。
  - 第四段只動 guard-kill 這支檔本身並沒有錯,但「欄位值的登記處」應與前三段一致。

- **缺「同一提交改的既有句子」(minor)**:前三段計劃都有此節,列出被取代的舊句子並加〔已被取代〕或〔部分被取代〕註記。
  - 第四段卻沒有。
  - 第三段〈做法〉2 與 `_CHOICE_MERGE_BREAKER` 的註解寫「只數逾時、讀不出…」。file: `scripts/lumos:28740`
  - 這些在第四段後變成「逾時且沒開始跑測試才計」,屬於部分被取代。
  - 第三段 S3 / S5 也提到逾時計數,同樣會有語意變動。

- **guard-kill 節點本身**:參考資料顯示該節點「沒寫負責範圍」。第四段沿用它並不算不一致,但可能是下次一併處理的點。

severity: minor
blocking: 否
引句:「`merge_why` 的新字樣是既有欄位的新值,讀者照字串讀」

severity: minor
blocking: 否
引句:「[[Systems/guard-kill]]:合併呼叫帶事件初始化腳本、沒跑乾淨照事件排序、跑到測試的逾時不計斷路器。」

不對齊共 6 條,其中 major 1 條(加引號用雙引號而非 `list2cmdline`,措辭有歧義,標 ⚠ 交編排者確認原意)。其餘 5 條 minor,都不阻擋。
