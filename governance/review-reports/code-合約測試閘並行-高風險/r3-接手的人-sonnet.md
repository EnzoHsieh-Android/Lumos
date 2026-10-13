severity: minor

我沒有逐字重跑整份 diff 的測試,也沒有自己跑並行路徑。以下是讀 diff 和 repo 後的結論。

## Findings

### 1. `_run_bound_tests` 內的註解還在講舊行為:同批已開跑的子程序「成為孤兒」
severity: minor
blocking: 否
引句:「已開跑的子程序在自己的程序群組裡跑到自己的逾時為止(跟循序時按 Ctrl-C 一樣成為孤兒),不卡住前景。」
file: `scripts/lumos:48203`
1. 這句是 r2 的舊行為。r3 修補加了 `_BtProcs`、`_settle_and_reap`、`started` 參數,出錯或 Ctrl-C 時會把同批子程序整個程序群組收掉。
2. 同一段程式往下 20 行,`_settle_and_reap` 的註解寫的是「留下沒人收的子程序」是缺陷。計劃〈實務隱患〉、bound-tests-gate 的 WHY、S5 條款都寫「收掉不留孤兒」。這一句是 repo 內唯一還說會留孤兒的地方。
3. 三個月後的人讀這段註解,會以為並行出錯時孤兒是設計內行為,可能因此「簡化」掉 `_BtProcs`。
4. 歸因:有證據的修復回歸。修補差異只加了新機制,沒改這句,所以註解是修補遺漏的。
5. 查證:`grep -n "成為孤兒" scripts/lumos` 在修前 3daa00a8 和修後 54b01b1a 都命中同一行。修前它與程式一致,修後與程式矛盾。

### 2. REVISIT 取數指令能跑,但篩選口徑跟 RETIRE-IF 的「綠的支數」不是同一個數
severity: minor
blocking: 否
引句:「只取綠的支數 50 以上(同量級範圍,note 開頭是支數),跟上面的循序實測 176.5 秒對照」
1. 我在 repo 根實際跑了那一行指令,語法沒問題、能執行,目前輸出 `0 None`。這符合預期,因為還沒有帶 `secs_kind=wall` 的帳。
2. 帳上 `note` 開頭的數字是「綁定項目數」。例如 `'59 綠'` 對應的是 59 個項目,不是去重後的 51 支。基準 176.5 秒是 51 支去重後循序跑的值。
3. 所以「≥50」篩的是項目數。只要項目數達 50,而去重後只有 40 支,也會被算進「同量級」,拿來比 176.5 秒。重複綁定越多,牆上時間越偏短。
4. 指令也沒有限制 `kind == 'green'`。目前只因紅帳的 note 是 `N 紅/M`、N 通常小於 50 才碰巧被濾掉。
5. 照著做不會撞牆,只是對照口徑稍鬆。
6. 歸因:有證據的原有漏查,是計劃新寫的指令本身的問題,不是修補造成的。
7. 查證:`python3 -c "…"`(同計劃 REVISIT 那行)在修前修後都回 `0 None`。`bound-tests` 帳最近兩筆 note 都是 `59 綠`,但計劃量測段寫「實際跑 51 支」。

## 三問與已驗範圍(整合與知識同步鏡頭)

- **①原問題的修復效果**:我沒有重現 r2 的孤兒子程序,那是正確性席的範圍。文件這側,計劃〈實務隱患〉、S5、bound-tests-gate 的 WHY、`_kill_run` 的 `started` 說明、`_BtProcs` 與 `_settle_and_reap` 的註解,都與程式一致,例外是 finding 1 那一句。
- **②相鄰路徑**:`_kill_run` 的 `started=None` 預設值不影響 guard kill 與其他呼叫端,簽名向後相容。規格閘在 `scripts/lumos:7661` 呼叫 `_run_bound_tests`,結果只取前五欄,不依賴 secs,不受 secs 改成牆上時間影響。
- **③新發現案例的修前修後結果**:finding 1 在修前註解與程式一致,修後不一致。finding 2 前後相同。

## 已驗主張

1. 07 手冊的「只認 2 到 16 的整數;字串、小數含 `1.0`、布林、超出範圍、`bound_tests` 不是物件都提醒並當 1」,與 `_bound_tests_parallel` 一致。只有整數 1 與沒寫不出聲,`None` 也不出聲(`None` 是 07 沒寫到的細節)。
2. 06 手冊新增的指向「見安裝維運」存在,章節標題也對得上。
3. bound-tests-gate 的新舊段落:步驟 3 加了「(2026-10-13 補…)」,secs 欄位說明與 `secs_kind` 的程式一致,回頭看條件加了「只算帶 `secs_kind: wall`」,也一致。
4. 計劃〈回退〉:整段還原說「合併前壓成一個提交」,跟專案「功能壓成一個提交」的慣例一致。若分支內仍有合併提交,`git revert -n <起點>..HEAD` 會需要 `-m`。計劃以壓成單一提交為前提,所以不構成問題。
5. 〈回退〉說 `bound_tests.parallel` 拿掉或改成 1 就回到循序,與程式一致:沒寫、`None`、1 都回 1。
6. Grep 查 `bound_tests`、`bound-tests`:`ARCHITECTURE.md`、`CLAUDE.md`、`docs/command-reference.md` 只提到閘的名字,沒有講循序或 secs 的語意,沒有其他舊說法需要同步。

## 未驗範圍

- 並行路徑的執行行為(孤兒回收、`_settle_and_reap` 的計數)。
- 測試是否能翻紅。
- 「只改設定檔時風險分級是 light」這一句,我沒查到對應程式。
- bound-tests-gate 的 frontmatter `updated: 2026-10-06` 沒隨新增內容更新,這是風格層面的小事,沒有列為 finding。

## 圖譜鏡頭(固定席)

- **guard-kill**:`_kill_run` 只多了選用參數,預設行為不變。rc 優先序與 `--json` 純淨度這兩條 INVARIANT 沒被碰到,不破壞合約。
- **bound-tests-gate**:blocked 語意(紅、懸空、偽證據、bad-name、unproven 皆擋,無 run_cmd 或無固定席不擋)沒變,結果仍照原項目順序,去重鍵仍是 `(root, cmd)`。步驟 3 與耗時欄位的新說明和程式一致。不破壞合約。
- **design-loop、測試假綠形態、lumos-cli-read、lumos-cli-lifecycle**:diff 沒有碰這些節點的行為,不破壞合約。
- **其餘只列名的節點**(規格落成可驗收條件、雙向門放行等):它們經規格閘或修正關卡間接用到 `_run_bound_tests`。設定打開後判定語意不變,只有排程變動,不破壞。

總結:最高等級 minor
