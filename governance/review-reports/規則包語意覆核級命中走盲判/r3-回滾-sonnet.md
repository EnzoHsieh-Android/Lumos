severity: major

審查範圍:第 3 版修訂稿。照「回滾」席立場,把〈回退〉節當辯詞逐句開檔對照。
〈回退〉節逐句判定:
- 「舊版照未知題號略過」:讀側成立。`_dispositions_verdict` 只照 `meta` 的適用題逐題取 `disp.get(qid)`,多出來的 `kt-rule-hits` 沒人讀。
- 寫側不成立:`_dispositions_validate` 會拒未知題號(見 F8)。
- 「舊版照缺欄略過」:成立。事件沒有 `role`,`_kt_bj_event_ok` 直接回 False。
- 「退回後自檢只對語意覆核級排除」:成立。
- 「已回流的誤報樣本留著也無害」:不成立(見 F4)。

## F1 「工具沒裝就擋」跟既有先例相反,而且擋下後沒有出口
severity: major
blocking: 是——擋下後作者無路可走(命中算不出來就無從回答 `fp`,也沒有放行檔),屬於會卡死推送的擋停。
- spec 位置:範圍 2「算不出來(工具沒裝、git 失敗)丟無法驗證」,驗收 S10「ast-grep 沒裝 → 無法驗證、擋」。
- 問題:範圍 3 的最後一條說逾時、例外「全照表態閘既有規則」,但「工具沒裝」在既有規則裡是只提醒、記一筆 fail-open 帳、不擋。這一題是外部工具相依,命中算不出來時就沒有 `seg` 可答,範圍 3 又說「不寫放行檔」。
- 後果:CI、新 clone、沒裝 ast-grep 或規則包路徑不存在的機器,只要消費專案宣告了規則包、這次改動有 `.kt`,每次推送都被擋,而且無解。
- 逃生口:只剩把 `stack_questions.gate` 設成 off(整道表態閘全關),或刪掉 lint.json 的宣告。這違反〈回退〉節「消費專案不用收拾」。
- 內部不一致:spec 一邊說「照表態閘與情境題既有的逾時規則」,另一邊對工具沒裝選了相反做法,卻沒有拿出理由。
引句:「算不出來(工具沒裝、git 失敗)丟無法驗證」
- 佐證:file: `scripts/lumos:73663` 情境題對「環境不可用」寫明「照新增告警閘「工具沒裝」的先例只提醒、記一筆 fail-open 帳、不擋」。
- 佐證:file: `scripts/lumos:42405` 新增告警閘把 `env` 類 undone 與 `hard_undone` 分開處理,env 不擋。

## F2 引用的設定鍵 `stack_questions.mode(warn/off)` 不存在,這一題沒有單題關掉的開關
severity: major
blocking: 是——〈回退〉與誤擋處置所依賴的「warn/off」開關是不存在的,實際上沒有單題降級的辦法。
- spec 位置:範圍 3 最後一條。
引句:「`stack_questions.mode`(warn/off)、逾時 fail-open 全照表態閘既有規則,本案不另寫讀法」
- 問題:實際的設定鍵是 `.lumos/config.json` 的 `stack_questions.gate`,值只有 `all`、`high-only`、`off`。`mode` 只是內部讀出來的字典鍵,沒有 `warn` 這個值。
- 後果:
  - 上線後發現這題擋錯,消費專案沒有「只把這題降成只提醒」的辦法。
  - `off` 會連 kt 全部效能題一起關。
  - `high-only` 只是依 tier 決定要不要擋,不是單題開關。
  - 要回滾只能退提交或動 lint.json,spec 沒給中間檔。
- 佐證:file: `scripts/lumos:38916` `_STACK_QUESTIONS_GATE_VALUES = ("all", "high-only", "off")`。
- 佐證:file: `scripts/lumos:38922` 讀設定那支的註解寫明「鍵叫 mode 不叫 gate」是為了避開治理閘名漂移掃描,對使用者的設定鍵仍是 `gate`。

## F3 誤報樣本的輸出路徑太扁平,測試類規則的樣本永遠不會命中,回測會假過
severity: major
blocking: 是——`--fp-regress` 會永遠印出「仍命中 0」,把規則改鬆也不會被抓到,等於回測失效。
- spec 位置:範圍 5 第一條與範圍 1。
引句:「各寫成 `<輸出目錄>/<規則 id>/review-fp-<seg>.kt`」
- 問題:規則包既有的誤報樣本放在 `samples/good/<id>/src/main/kotlin/review-fp-*.kt` 或 `src/test/kotlin/...`。
- 問題:`rules-review/testing.yml` 與 `rules-hints/testing.yml` 的 `files:` 限定 `**/src/test*/**` 等路徑。
- 後果:扁平寫到 `<id>/review-fp-<seg>.kt` 的檔,測試類規則根本掃不到,回測會假過。
- 缺口:spec 沒有說樣本要不要還原原專案的 src 子路徑,材料裡也沒有記原檔路徑。
- 佐證:file: `configs/ast-grep/kotlin-android/rules-review/testing.yml:5`。
- 佐證:`find samples -name 'review-fp-*'` 的現有檔全在 `src/{main,test}/kotlin/` 底下。
- 佐證:file: `configs/ast-grep/kotlin-android/check.py:704` `_sample_owner` 只取 `parts[2]`,所以扁平路徑不會報錯,只會靜靜地不命中。

## F4 〈回退〉說樣本「留著也無害」,但帳只追加、樣本刪了會復活,錯收的樣本還會遮掉真命中
severity: major
blocking: 是——〈回退〉節宣稱的收拾辦法行不通。
- spec 位置:〈回退〉節。
引句:「已回流的誤報樣本是規則包好例,留著也無害」
- 問題一:兩處排除不是無害。
  - 對語意覆核級,`check.py` 把 `review-fp-` 樣本整個排除在好例誤報之外(第 754 行)。
  - `good_cases` 也不數它(第 716 行)。
  - 抽查跟作者是同一家模型,真問題被判 `false` 並收成樣本後,規則的好例檢查就把這個命中視為已知誤報。
- 問題二:收拾辦法本身不成立。
  - 唯一的收拾是手動刪檔。
  - 但範圍 5 的 `--fp-samples` 是從治理帳重新匯出,帳只追加、撤不掉。
  - 下次匯出會把刪掉的檔重新生出來。
  - spec 沒有「墓碑」或排除清單。
- 問題三:〈回退〉只講了提示級目錄要刪,沒講語意覆核級已回流的樣本,也沒講退回後這些樣本會讓 `--fp-regress` 以外的哪些東西失真。
- 佐證:file: `configs/ast-grep/kotlin-android/check.py:743`(`review_ids` 只含 `rules-review`)與 `:754`(排除條件)。
- 佐證:第 725 行(檢查規則數)之後的流程完全不看 `review-fp-` 檔本身。

## F5 申請命中的適用性怎麼進 `stack_questions_meta` 沒寫,合併分支的重算路徑用的是 `--no-lint`
severity: major
blocking: 是——⚠這題在實作時有可能漏題。判準:最常見的情境(把 main 合進分支再推)走的重算路徑跳過 lint,若適用性靠 lint 命令算,該路徑會靜默漏掉這一題。
- spec 位置:範圍 3 與用詞「命中題」。
引句:「只在這次改動有規則命中時適用」
- 問題:適用性要靠重跑 ast-grep 才知道,但現行表態閘的適用題來自 `pitfalls --json` 的 `stack_questions_meta`。
- 問題:`code-loop check` 在 `_nr != diff_range`(把主線合進分支)時,會用 `pitfalls --diff <範圍> --no-lint --json` 重算 `disp_data`。
- spec 沒說:
  - `kt-rule-hits` 要不要登記進 `_STACK_QUESTION_SPECS`(`_dispositions_validate` 與 `_backing_mark` 都靠它認題號,認不得會回「不是題目表裡的 id」)。
  - `--no-lint` 路徑下這一題要怎麼出現。
- 後果:適用性靠 lint 算,則 `--no-lint` 路徑裡這題不會出現,表態核對就整題跳過。
- 佐證:file: `scripts/lumos:74731`。
- 佐證:file: `scripts/lumos:72996` `_dispositions_validate` 以 `_stack_spec_by_id` 認題號。

## F6 新增的 `rule_hits` 欄位沒登記進治理帳欄位型別表
severity: minor
blocking: 否——只影響統計與帳的健壯性。
- spec 位置:範圍 4 第二條、範圍 6。
- 問題:`lumos gov` 讀帳時用 `_GOV_FIELD_TYPES` 驗每個欄位的型別,表頭註解寫「新增 mapper 用到的欄位時一起補進來」。
- 問題:`_gov_row` 也是白名單式 mapper,`rule_hits` 若不進 mapper,範圍 6 的統計讀不到。
- 問題:spec 沒提這兩處,新的統計只能整筆信任帳。形狀壞的一行(例如 `rule_hits` 不是 list)會直接丟例外或被吞掉。
- 佐證:file: `scripts/lumos:17501` 到 `:17511`(欄位表與註解)與 `:17575` 以下(`_gov_row`)。
- 回滾面:舊版的 `gov --stats` 把 `kt-rule-hits` 當一般題列進「做到了 N」,不會當掉,但數字是作者答的 `fp/risk` 混成「做到了」。

## F7 已經另外宣告提示級設定的專案會被兩道閘各擋一次
severity: minor
blocking: 否——是重複擋停,而不是漏擋,兩邊各有出口。
- spec 位置:範圍 7 與範圍 2「不讀放行檔」。
- 問題:file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:198` 現行建議是「要用就另加一條宣告指向它」(`sgconfig-hints.yml`)。
- 後果:這種專案同一筆命中會在新增告警閘被擋一次(出口是放行檔),再被命中題擋一次(出口是答 `fp`)。
- 缺口:spec 沒說兩邊如何對帳,也沒有「已有放行的不再要求交代」。
- 回滾面:退回後這些專案的放行與 `fp` 答案各留在不同帳,沒有對照。

## F8 〈回退〉的「未知題號略過」只對讀側成立,寫側會拒絕
severity: minor
blocking: 否——只影響退回後重用舊檔的作者,有明確錯誤訊息可手動修。
- spec 位置:〈回退〉節與實務隱患「已排除:不可逆」。
引句:「舊版不認 `kt-rule-hits` 題(未知題號照表態閘既有規則略過)」
- 佐證:file: `scripts/lumos:72996` 到 `:73000` `_dispositions_validate` 對不在題表的題號回「不是題目表裡的 id」,寫表態整份被拒。
- 後果:退回後若作者拿含 `kt-rule-hits` 的表態檔重送,會被拒,要手改掉那題。
- 讀側確認成立:`--carry` 只照 `meta` 帶題,不會把 `kt-rule-hits` 帶進舊版樣板。

## F9 作者交代沒有任何撤回與排除機制,為了通過被迫寫的 `fp` 會進統計
severity: minor
blocking: 否——spec 在〈不做〉明說不做推翻,屬已知取捨,但〈回退〉要交代清楚。
- spec 位置:〈不做〉第 4 條與範圍 6。
引句:「不做人複查指令、不做推翻:抽查結果只提醒,推翻沒有對象。」
- 問題:因為誤擋的唯一出口是答 `fp`,工具本身算錯(弱比對換身分、改檔名視為新增、F1 的環境問題)時,作者被迫寫的 `fp` 與 `risk` 會原樣進 `gov --stats`。
- 後果:fp 比例會被灌高,「改形狀候選」(fp 八成以上)與「升擋候選」(fp 一成以下)的判斷都被污染。帳只追加,事後沒有排除標記。
- 缺口:RETIRE-IF 第二條(抽查推翻比例連續八週超過三成)也會被同一批被迫答案污染。

## 實務隱患鏡頭
- 金流:無,不碰付款,spec 已排除,同意。
- 對外送出:無,只讀本機檔、跑本機 ast-grep。
- 不可逆:有。治理帳的答案與抽查紀錄只追加、撤不掉(見 F4、F9);誤報樣本匯出後的刪除會被下次匯出還原(F4)。spec 把「不可逆」判為已排除,理由「退提交即回原狀」只涵蓋程式,不涵蓋帳與樣本。
- 守衛面:有,spec 已承認並走完整設計審,同意。補充:新增外部工具相依(F1)與單題無開關(F2)是這次守衛面的新增風險。
- 資源:20 秒預算(`_DISP_BUDGET`)與情境題共用,新增 2 份設定 × 2 份快照的 ast-grep 掃描,逾時會 fail-open 連累情境題核對。spec 有提預算、沒量。⚠

## 固定席(節點宣稱的行為或合約會不會被破壞)
- 〔棧別提問表態閘〕不影響既有行為。新題只多一個題號,讀側忽略未知題號,不動 `kt-situation` 的形狀。例外:無法驗證擋下與環境不可用 fail-open 的先例,這份 spec 的 S10 與之相反(F1)。
- 〔pitfalls-code-loop〕不影響。盲判事件新增 `rule_hits` 欄,舊讀端靠缺 `role` 略過,已核對成立。
- 〔kotlin規則包〕不影響已有合約。好例排除範圍若擴到提示級,要依 F3、F4 修樣本路徑與回收辦法。
- 〔linter精選目錄〕不影響,但範本措辭要處理 F7 的重複宣告。

總結:最高等級為 major,blocking 共 5 條
