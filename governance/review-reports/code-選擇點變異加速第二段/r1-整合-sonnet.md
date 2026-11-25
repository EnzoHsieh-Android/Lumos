severity: minor

先講結論：計劃的主要同步項都做了，四篇筆記 `lumos lint` 都是 0 問題，`[test:]` 綁定指到的測試全部存在。但有一處手冊沒跟上，還有幾處計劃文字與實作偏離對不上。

## 逐項核對

**1. 驗收條款與測試斷言**
- S1、S2、S3、S4、S8、S9 的測試輸入與預期，跟預期值表逐列對得上。
- S1 五案的名單由 `__mfail__` 設定，我逐案核對過，判定與呼叫順序都照表。
- S7 的數字 (40+2535+60 進位到 2700、剩 0 秒) 也對。
- S10 有幾處偏離，見 finding 1。

**2. 〈落點〉同步項**
- 前一份計劃〈做法〉1、3、5、〈舊否決比對〉、S3 條款與預期值表、S19 條款與預期值表，都有加〔已被…取代〕註記，說法與程式一致。
- `改動選擇點都要有需求守住_計劃` 的〈用詞〉殺掉判定那句已改。
- `_kill_merge_ready` docstring 已改。
- guard-kill 與規格閘各補了 WHY。
- 沒漏：這些項目都做了。

**3. 全 repo grep 舊說法**
- 筆記裡沒有殘留舊說法。
- 殘留在手冊與兩處小地方，見 finding 2、3。

**4. 新筆記行格式**
- guard-kill、規格閘的新 WHY 都有 `[出處:]` 和 `[因:]`，`[test:]` 都指到存在的測試。

**5. 實作偏離 ①–⑦**
- ① S10 條款字面沒跟著改，見 finding 1。
- ② 中斷只記 `merge_off`、不印：計劃〈做法〉3 的印字句沒寫例外，見 finding 4。
- ③ 舊帳讀成空字典：S9 預期值寫「當 none 與 0」，沒改成「空字典，每個平台當 none」，見 finding 4。
- ④ 計劃本來就寫 `kotlin`，不用同步。
- ⑤ S7 直接呼叫 `_kill_merge_ready` 驗，見 finding 5。
- ⑥⑦ 只動測試用的假 Gradle 和既有測試設定，不需同步到計劃。但計劃〈落點〉只列兩支要改的既有測試，實際改了三支 (多了 `t_choice_kill_merge_interrupt`)。

## Findings

**1. S10 條款字面與「對不到名字」那案的實際輸出不符**

引句：「各印一行 `⚠ <平台>:這次不合併(<原因>)`,`merge_off` 應 分別記 `指令過長`、`名稱檢查沒過`、`合併道不足 2 支`、`合併基準:對不到名字`」

- 前三案實際輸出跟條款一致。
- 第四案實際印的是既有那行 `⚠ kotlin-junit:1 支對不到結果檔裡的名字,這個平台組這次不合併`，不是條款寫的格式。
- 〈做法〉3 寫「既有字樣照留、不重複印」，條款與做法互相矛盾；測試照做法驗。
- 照條款字面去改測試或程式，會變成雙印或改掉既有字樣。
- 預期值表 S10 的來源欄還寫了沒定義的詞 `merge_base_why`，程式裡只有 `_CHOICE_MERGE_BASE_WHY`。
- file: `scripts/test_lumos.py:147609` 附近 `t_choice_kill_merge_off_reasons` 的第四案斷言 (函式內第二個 `check` 迴圈)。我讀的是 diff，行號是約數，用函式名找。
- blocking: 否，措辭與精度層級，做法與測試一致。

**2. 手冊還寫「這次跑 2 個以上壞法時」才合併**
- file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:18`
- 該行寫著「run_cmd 是帶模組的 Gradle 單元測試任務(…)而且這次跑 2 個以上壞法時,預設先把單支基準綠的測試合成一次呼叫…時限不夠量齊就不合併」。
- 現在一個壞法也合併，不合併時會印原因，手冊都沒提。
- `skills/lumos-code-loop/SKILL.md:16` 的 choice-kill 說明沒有「2 個」字樣，不需改。
- blocking: 否，說明過期，不會讓人做錯操作。

**3. 另外兩處「排序第一支」或「原樣交回」過期**
- file: `docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md:203`，S8 條款寫「帶排序第一支殺掉它的測試」。
- file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:55`，舊 WHY 寫「其餘配方原樣交回逐支迴圈本體」，現在有失敗時會先紅重排。
- 兩處都不在〈落點〉清單裡，判定語意沒變，只是說法過期。
- blocking: 否。

**4. 偏離 ②③ 沒回寫到計劃**
- 引句：「每個不合併的平台組印一行到標準錯誤,照既有格式」
- 〈做法〉3 的原因清單含 `中斷`，印字句沒寫例外。程式與 guard-kill 筆記都寫「中斷不印」。
- 引句：「讀沒有這兩欄的舊帳 應 當 none 與 0」
- 實作是 `merge_kind` 讀成空字典、`single_runs` 讀成 0。測試註解寫「空字典(都當 none)」，計劃沒改，之後讀帳的人可能把 `{}` 當成缺值。
- `merge_off` 記「中斷」沒有測試驗，中斷測試 `t_choice_kill_merge_interrupt` 沒查這個欄位。
- blocking: 否。

**5. S7 的 `t0` 接線沒有測試守**
- file: `scripts/lumos:79071` 附近，`_ChoiceKillRun` 建 `_KillMerge` 時傳 `t0=self.t0`。
- 我在 `/tmp` 的複本拿掉 `t0=self.t0` 後跑 `-k t_choice_kill_merge_budget_hint`，仍 5 passed。S7 測試自己建 `_KillMerge(..., t0=now-40)`，真正的接線沒被驗。
- 實際影響很小：不傳時 `t0` 用建構當下的時間，只少算建構前那幾秒。
- 同樣，原因 `基準量不齊` 及其「帶多大 `--max-seconds`」提示、`平台不穩或筆記未提交`、`指令形狀不支援`、`讀結果檔的模組不在`、`結果資料夾不在工作樹` 這幾條，沒有任何測試驗。
- 這些原因也不在 S1–S10 任何條款裡。
- blocking: 否，講不出會讓行為出錯的具體改壞，降為 minor。

**6. S2 預期值表寫 a、b、c、d，測試實際只有 a、b、c**
- 引句：「三案都照 a、b、c、d 原順序,跟 `--no-merge` 相同」
- 測試 `t_choice_kill_merge_failed_first` 的 S2 段用的是 `_CKM_TESTS` 三支，只有 S1 段用四支 `_CKM_T4`。
- blocking: 否。

## 圖譜鏡頭

固定席節點這次沒附，我自己讀了 guard-kill 的合約行，判斷如下。

- `★INVARIANT★ guard kill rc 優先序`：不受影響。新增的 `_single` 標記只在傳了選用參數時才加，不改 `verdict`，略過的列本來就不算進 rc。
- `★INVARIANT★ guard kill --json 模式 stdout 恰一行 JSON`：不受影響。`_single` 已加進 `--json` 輸出的排除鍵；新增的「這次不合併」那行與斷路器那行都印到 stderr。
- 殺傷力帳本寫入：不受影響。`_kill_log_rows` 是逐欄寫，不會帶出 `_single`。
- 規格閘的 `_GOV_FIELD_TYPES`：只新增鍵，舊事件缺欄時讀成空字典或 0，不破壞既有型別檢查。

總結：max severity 是 minor，blocking 共 0 條。

我的 `/tmp/lumos-seat-work/code-選擇點變異加速第二段/整合-sonnet/` 複本已刪除。
