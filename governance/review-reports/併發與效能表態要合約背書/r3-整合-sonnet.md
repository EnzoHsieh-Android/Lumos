severity: major

r2 那批修法(`_codeloop_record_valid` 綁版本、配方身分雜湊、kill-log 補換行、兩個 try 包覆)方向站得住。

**N1**
severity: major
blocking: 是——照補救順序從零走,第二步就被擋下。
補救順序從寫測試直接跳到 kill-add --covers,漏了先寫 ★INVARIANT★ 合約行、再 guard bind 綁測試;kill-add 找不到合約行或合約沒綁測試都擋。
引句:「補救順序(提醒與技能文件照這個寫):寫次數或併發測試 →」
file: `scripts/lumos:12842` 合約沒綁測試就擋。
file: `scripts/lumos:12848` 配方從合約行的 [test:] 取 test。

**N2**
severity: major
blocking: 是——「補既有配方」照字面會被舊訊息擋下。
判準「其他欄位完全相同」;配方含 note、test、platform,沒逐字重打原 note 或 platform 就不同,仍印「先把舊的那條手動拿掉」;kill-log 4 筆都帶 note,是常態。判準要寫死:比 (invariant, file, old, new),note 與 platform 沒帶沿用已存值、帶了不同值才算不同。
引句:「改成「這次有帶 `--covers`、其他欄位完全相同」就只更新那條的 `covers`,印出更新前後,其餘情況照舊擋。」
file: `scripts/lumos:12848`

**N3**
severity: major
blocking: 是——一次環境性失敗就讓背書在該版本上永久算沒有,spec 沒給出路。
第 6 步把 abort、error、timed_out_weak、drifted、killed_unattributed 全部毒化;kill-log 只增,同 HEAD 重跑洗不掉;只能改碼造新版本。重現:環境壞掉跑一次得 abort,修好再跑得 killed,判 none。建議只讓 survived 毒化,其他非 killed 不貢獻強證據;若堅持全毒化要在天花板與提醒寫明。
引句:「涵蓋這一題的每一組,組內**每一筆**都要是 `killed` 且 `weak` 不是 true;任一筆不是 → none,原因「有一次不是強證據」」
file: `scripts/lumos:13132` abort。
file: `scripts/lumos:13172` survived。
file: `scripts/lumos:13199` 只 append。

**N4**
severity: major
blocking: 否——同步清單漏列,不影響實作行為,但文件會變錯、S14 驗收會漏。
漏列:`assets/stack-gate-zh.svg:3` 與 :61、`assets/review-layers-zh.svg:3` 與 :35、Systems/棧別提問表態閘 的 KEY 行與正文「刻意的天花板」段(`docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:91`)、Projects/對外說明親和化改寫 那句、`scripts/lumos:34823` docstring、Systems/reversibility-governance-ledger 的 kill-log 讀者段;reference.md 兩處吻合。
引句:「要同步改的位置(上線後舊說法會變錯的都列進來,共九處):」
file: `assets/stack-gate-zh.svg:3`
file: `assets/review-layers-zh.svg:35`

**N5**
severity: minor
blocking: 否——只影響提醒呈現。
pre-push 在 rc=0 時只轉含「提醒|受波及合約測試|表態閘」的行;補救步驟若多行,第二行起會被濾掉;警告要單行或每行帶「提醒」。
引句:「放進 `out["warnings"]`(不進 `problems`、不改 `blocked`、不改回傳碼),code-loop check 印成「提醒:」,附原因與補救步驟」
file: `scripts/hooks/pre-push:450`
file: `scripts/lumos:37874`

**N6**
severity: minor
blocking: 否——競態窗口很小。
現行 commit 在 worktree add 之前另跑 rev-parse,沙盒實際檢出的是 add 那刻的 HEAD;head_sha 應在沙盒內取。
引句:「那一組平台跑破壞測試時的完整 HEAD(存在每一筆自己身上,不是迴圈外的共用變數)」
file: `scripts/lumos:13090`
file: `scripts/lumos:13100`

**N7**
severity: minor
blocking: 否——只影響 RETIRE-IF 量測口徑。
補救流程逼重表態,--carry 帶 carried=True 的重複答案,gov 每筆事件每題算一次,分母被灌水;加總時要去掉 carried。
引句:「分母=上線後、被標題目、人工表態(不含自動記的未觸發)的事件」
file: `scripts/lumos:7059`
file: `scripts/lumos:37389`

逐類:既有讀者(gov 第 5 源 `scripts/lumos:7291`、表態段、`_kill_read_recipes`、guard list/trace、CI、--carry、validate)皆無害;併發無 finding;head_sha 格式與 `_codeloop_record_valid` 相容;slim 凍結與全域範本成立;kill-log 忽略清單屬實(`scripts/lumos:18250`)。

最嚴重 severity: major,blocking 共 3 條(N1、N2、N3)。
