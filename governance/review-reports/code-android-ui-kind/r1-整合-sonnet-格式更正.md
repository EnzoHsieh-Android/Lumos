severity: major

兩個 major 都是我實際跑過的,結果寫在各條。其餘固定席節點(lumos-cli-read、測試假綠形態、design-loop、guard-kill、lifecycle 等)我判不影響:diff 在 `scripts/lumos` 只動 `_VENDORED_TREE_FILES` 多一行,沒碰它們的行為。

## 1. 範本整份貼進 queries.sql 後,重跑腳本只截到註解,查詢本體丟掉
severity: major
blocking: 是
引句:「-- 效能:往下走子區段時直接查 slice 表(trace_processor 對自己的表過濾快,查中間結果會變成平方級);」
file: `scripts/templates/android-receipt-rerun.sh:14`(解析用的正規表達式 `^-- \[(Q\d+)\] (.+?)\n(.*?;)\s*$`,搭配 re.S|re.M)
file: `scripts/templates/android-ui-attribution.sql:17`(註解行以 ASCII `;` 結尾)

- 照 SKILL.md 做的步驟:「把專案的 `scripts/templates/android-ui-attribution.sql` 裡的 `__PROCESS__` 換成 App 套件名……兩條都照標頭格式寫進 `queries.sql`」。範本檔頭也寫「複製進收據的 queries.sql 時,上面加一行 -- [Qn]…」。
- 照做就是把整份範本(含檔頭註解)貼在 `-- [Qn]` 標頭下面。
- `rerun.sh` 取 SQL 本體用的是「第一個以 `;` 結尾的行」。第 17 行註解剛好以 `;` 結尾,所以它被當成 SQL 的結尾。
- 重現:我把範本換掉 `__PROCESS__`,前面加 `-- [Q1] session=c trace=t1 requires=- expect=f100:compose_ns=5`,套用同一個正規表達式。解析出的 Q1 本體只到那行註解,`'WITH' in sql` 為 False。
- 後果:標頭數等於解析條數,所以不會回 2。trace_processor 拿到一份只有註解的 SQL,沒有輸出列,每條歸因 expect 都報 `BAD`(rc1)。接手者會誤判成「量測不符」,而不是「收據寫錯」。
- 兩種修法:拿掉第 17 行結尾的 `;`,或在 skill 寫明只貼 `WITH` 之後。
- 整份範本沒有任何測試把它餵進 rerun.sh,所以沒人發現。

## 2. 範本用 `--` 寫 SPDX,授權守衛測試會紅,推送會被擋
severity: major
blocking: 是
引句:「-- SPDX-License-Identifier: MIT」
file: `scripts/test_lumos.py:53797`(`_spdx = re.compile(r"^#\s*SPDX-License-Identifier:\s*MIT\s*$")`,只認 `#` 開頭)

- 重現:`python3.14 scripts/test_lumos.py -k vendored`,輸出 `✗ 授權/KEY2: 每支會被複製進消費專案的檔都帶 SPDX 標示 ['scripts/templates/android-ui-attribution.sql']`,最後 `FAILED t_license_headers_travel_with_vendored_files`,88 通過 1 失敗。
- 這條測試綁在「授權與歸屬」節點的 ★INVARIANT★ 上:被複製的檔至少要有 SPDX 註解行。
- bound-tests-gate 會逐支真跑它,所以 pre-push 與 CI 都會擋。
- 計劃 S6 只說「登記在工具組複製清單」並綁 `t_android_ui_attribution_vendored`。這支測試通過,但沒覆蓋授權守衛。
- 修法二選一:守衛測試認 `--` 註解(改測試檔要先簽名);或範本改用該測試認得的形式。
- 另一個提醒:`t_android_ui_attribution_vendored` 的 docstring 寫「skill 要指到它」,但斷言沒檢查 SKILL.md 有提到範本路徑(見第 4 條)。

## 3. skill 的管線類名單比範本和計劃少一個 traversal
severity: minor
blocking: 否
引句:「`pipeline`(兩種寫法共用的畫面管線:input、animation、measure、layout、draw)」
file: `scripts/templates/android-ui-attribution.sql:245`(`name IN ('traversal', 'measure', 'layout', 'animation', 'input', ...)`)

- 計劃的四類表與 S8 都列 `traversal`,skill 沒列。
- 場景:接手者在 Trace 看到佔比很大的 `traversal`,對 skill 的名單找不到它,可能懷疑它算「其他」。
- 其餘四類名單、「看長最多不看最大」、只看主執行緒,三處都一致。

## 4. skill 沒有測試守著它真的指到範本和 queries.sql 格式
severity: minor
blocking: 否
引句:「歸因查詢範本要登記在工具組複製清單,才會跟其他範本一起進消費專案;skill 要指到它。」
file: `scripts/test_lumos.py`(`t_android_ui_attribution_vendored`,斷言只有清單登記和檔案存在)

- skill 的路徑目前寫對了,但改名或搬檔時沒有任何東西會紅。
- skill 步驟 1 也沒提 `expect` 要寫 `f<幀起點>:compose_ns=…`。這只寫在範本檔頭,skill 只說「照標頭格式」。接手者不開範本檔頭就不知道第一欄鍵的規則。

## 已核對過、沒問題的項目
- `lumos compose-metrics --audit`、`metrics_dir` 指到 `*-module.json` 那層:對得上 `scripts/lumos:39073`、`39177`、`39222`。
- `lumos macrobench` 存在。
- `Compose:recomposeCount` 門檻寫法與現有讀檔程式相容。
- 範本已登記進 `_VENDORED_TREE_FILES`,「消費專案裝了工具組後該路徑存在」成立。
- `t_android_ui_attribution_*` 6 支全綠,`t_vendored_file_list_matches_what_install_ships` 通過。
- `rerun.sh` 認得第一欄 `'f'||ts` 這種字串鍵,範本輸出格式接得上。

我跑測試留下的兩個暫存現場,已用字面絕對路徑刪掉。

總結:最高嚴重度 major
