severity: major

資源併發鏡頭:新的字串字面正規式本身沒問題,但它前面那層剝註解會讓一部分句子名永遠掃不到。兩道閘裡「選到多支就弱證據」的防護,對這次要支援的測試棧也不存在。

## F1 剝註解不認字串,句子名裡的 `//` 與 `/*` 會讓整條測試或後面的測試消失
severity: major
blocking: 是(照 spec 實作,含 URL 或萬用字元的句子名會靜默掃不到,綁定判成懸空)

- spec 位置:做法 2 與〈實務隱患〉守衛面,「c-style 註解照舊先剝」。
- 問題:`_strip_test_comments` 先把 `//[^\n]*` 與 `/\*.*?\*/` 整段刪掉,而且不認字串邊界。標題是任意句子之後,標題裡出現 `//` 或 `/*` 很常見,例如 URL 或 `GET /api/*`。
  - 標題含 `//`:該行從那裡起被刪,標題收不到結尾引號,這支測試不被收進集合。
  - 標題含 `/*`:從那裡一路刪到檔內下一個 `*/`(任何 JSDoc 都算),中間所有測試一起消失。
- 具體例,我用現行兩條剝法加 spec 的字面正規式實測。輸入檔:
  1. `it('開啟 http://localhost:3000 首頁', …)`
  2. `it('GET /api/* 回 200', …)`
  3. `it('下單後 按鈕會停用', …)`
  4. 一行 `/** 說明 */`
  5. `it('結帳', …)`
  - 預期:收到 4 支。照 spec 得到:只剩 `['結帳']`。第 1 支被 `//` 吃掉,第 2、3 支被 `/*` 到 `*/` 吃掉。
  - S1、S2、S3 的範例標題都不含這兩種字元,測不出來。
- 佐證:
  引句:「c-style 註解照舊先剝;字串裡的假呼叫不另處理」
  ``file: `scripts/lumos:6264` `` `_strip_test_comments` 對 `c-style` 的實作。JEST、PLAYWRIGHT、DART 三條 profile 都是 `c-style`,見 `scripts/lumos:5805`、`scripts/lumos:5821`、`scripts/lumos:5866` 附近。
- 修法方向:這三家改用字串感知的單趟剝法。一個正規式交替,把字串字面與註解都吃進去,字串原樣放回、只刪註解,這樣也是線性。再加一條驗收條款:標題含 `//` 或 `/*` 時,後面的測試照樣收得到。

## F2 「選到兩支以上判弱證據」的防護,對 Jest、Vitest、Playwright、Dart 不存在,兩道閘都一樣
severity: major
blocking: 是(spec 的假綠防線建在不存在的機制上,RETIRE-IF 計的假綠也會因此量不到)

- spec 位置:做法 4 最後一點。
- 問題:spec 說「既有的篩到幾支判法會把選到兩支以上判成弱證據」。我讀碼,這不成立:
  - `_ran_count` 只對有 `count_re` 的 profile 讀得出支數。`_RAN_EVIDENCE` 裡只有 `python` 帶 `count_re`。`node-jest` 只有 `re`,`node-vitest`、`playwright`、`dart` 連 `_RAN_EVIDENCE` 項目都沒有,所以全回 `(None, False)`。
  - `_spec_gate_verdict` 只有在 `n >= 2` 時才給弱證據。`n` 是 None 時直接走「只印有沒有跑過」,綠就是綠。
  - 推送前合約測試閘(`_run_bound_tests` 之後)完全不呼叫 `_ran_count` 或 `_spec_gate_declared`。
  - 子字串篩選從識別字名變成句子名後才真正危險:`-t '登入'` 會選中所有含「登入」的測試。Jest 的 `-t` 比的是「describe 鏈加標題」,`_spec_gate_declared` 只數標題,抓不到跨 describe 邊界的匹配。
- 具體例:
  - 條款綁 `登入`,程式裡有 `it('登入後 看得到訂單')` 與 `it('登入失敗 顯示錯誤')`。
  - 預期:判弱證據或懸空。
  - 照 spec 得到:`-t '登入'` 跑 2 支,全綠就報綠,只有一格綁定的東西實際在驗另一批測試。
  - 同一個篩選若選到幾百支(Playwright 的 `-g` 是子字串),會整批跑,撞上單支 180 秒的逾時,被判成紅,資源花在不相干的測試上。
  - S5 只測前半標題判懸空,S13 到 S15 只測展開字串,沒有一條涵蓋「篩選選到多支」。
- 佐證:
  引句:「會把選到兩支以上判成弱證據」
  ``file: `scripts/lumos:54256` `` 起的 `_RAN_EVIDENCE`,只有 `python` 項目帶 `count_re`。
  ``file: `scripts/lumos:54280` `` 的 `_ran_count` 讀不到支數時回 `(None, False)`。
  ``file: `scripts/lumos:8815` `` 的 `_spec_gate_verdict` 以 `n is not None` 為前提。
  ``file: `scripts/lumos:54725` `` 附近的推送前閘路徑沒有呼叫上面三支。
- 修法方向:`name_filter` 為 `regex` 或 `plain` 的平台,執行前先用已有的 `_spec_gate_declared` 做靜態檢查(含 describe 鏈)。名字被兩支以上宣告包含就判弱證據,兩道閘都做。這個靜態檢查不依賴輸出格式。另補一條驗收條款:造兩支標題互為子字串的測試,斷言不報綠。

## F3 效能驗收只量新正規式,量不到真正慢的那一層
severity: minor
blocking: 否(不改只是漏掉真問題,不會做出壞行為)

- spec 位置:〈實務隱患〉效能。
- 問題:
  - 驗收是拿全是未閉合引號的檔量掃描時間。我實測 spec 描述的字面正規式(三種引號、`\\.` 還原、不含 `${` 的反引號)在 80 萬到 100 萬字元的各種壞輸入上都是線性,最慢 0.07 秒。這個驗收通過是必然的,沒有資訊量。
  - 真正會慢的是前面的剝註解。`/\*.*?\*/` 遇到多個沒有結尾 `*/` 的 `/*`,每個起點都掃到檔尾,是二次方。實測 `it('GET /api/vN/* …')` 一行一個、檔內沒有 `*/`:2000 行約 0.7 秒,4000 行 2.9 秒,8000 行(約 480KB)11.3 秒,1MB 約 50 秒。
  - 這層每次健檢、推送前、殘留索引(`_residual_test_files`)都會再跑一次。
  - Playwright profile 沒有檔名錨(`file_name_match`),會掃整個 repo 所有 `.ts/.tsx/.js/.jsx`。`CODE_SKIP_DIRS` 不含 `.next`、`coverage`、`out`,建置產物也會被掃。
- 佐證:
  引句:「實作後拿 1MB、全是未閉合引號的測試檔量一次掃描時間」
  ``file: `scripts/lumos:5608` `` 的 `CODE_SKIP_DIRS`,以及 ``file: `scripts/lumos:5805` `` 的 playwright 項目(沒有檔名錨)。
- 修法方向:F1 的字串感知單趟剝法同時解掉二次方。量測輸入改成「大檔加大量 `/*` 且無 `*/`」,並對 Playwright profile 補量 repo 全掃的總時間。

## F4 原本因懸空而不會真跑的綁定,上線後每條都起一次測試工具,spec 沒交代耗時
severity: minor
blocking: 否(行為正確,是推送前閘的時間預算沒人算)

- spec 位置:做法 4 與〈實務隱患〉。
- 問題:
  - 前端示範的 15 條條款原本全懸空,推送前閘判紅後直接略過,不會真的去跑。
  - 改成可綁之後,每條展開成不同指令,去重鍵是「根目錄加展開後指令」,所以是 15 次獨立的 `npx playwright test -g …` 或 `npx jest -t …`。
  - `bound_tests.parallel` 預設是 1,每次冷啟動(Playwright 還可能帶起 `webServer`),單支上限 180 秒。
  - 最壞時序:15 次乘每次數十秒,序列跑完是數分鐘到十幾分鐘,而 spec 對這個沒有任何預期值或提示。
- 佐證:``file: `scripts/lumos:54388` `` 起的 `_run_bound_tests` 與 ``file: `scripts/lumos:54142` `` 的 `_bound_tests_parallel`。
- 修法方向:在「懸空變可綁」的上線說明或 `attr_hint` 補一句耗時預期與 `bound_tests.parallel` 的用法。F2 的靜態檢查通過後,低風險推送可考慮對 `regex` 與 `plain` 平台不重複起進程(此點可不做)。

## 已讀,無 finding
- 做法 1(`_test_name_ok`):200 字上限與字元集本身不吃資源。
- 做法 3:最多 15 行的上限正確。
- 做法 5:`_apply_test_overrides` 不新增子程序。
- 做法 6 歸檔與 `guard trace` 的邊界改法:
  - `cmd_archive` 把所有存活守衛名併成一個交替正規式去掃每篇驗證紀錄。
  - 我用 1500 個長中文名實測,每篇約 18KB 的紀錄要 82 毫秒。
  - 這個量級在手動指令下可接受,不標。
- 子程序回收:沿用 `_kill_run` 與 `_BtProcs` 的既有機制,spec 沒有新增開子程序的路徑。
- 威脅模型:只考慮單人、AI 依序操作,多程序同時寫的問題不報。

風險類:
- 守衛面:F2 屬於,假綠的來源是放寬名稱後篩選選到多支。
- 舊帳相容:無,舊識別字名的展開不受影響(`ident` 路徑不變)。
- 在途分支:無。
- 與其他會談的交界:無,只動 `scripts/lumos`。

最嚴重 severity:major;blocking 共 2 條(F1、F2)。
