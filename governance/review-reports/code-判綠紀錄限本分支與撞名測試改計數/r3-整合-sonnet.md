severity: major

## 發現

1. 回頭條件那支(`_drift_born_env_err`)這次改成認 promisor-only 的部分複製,但沒有任何測試或驗收條款管它。
severity: major
   blocking: 是
   引句:「if _git_partial_clone(root):」
   - file: `scripts/lumos:55684`,`_drift_born_env_err` 現在呼叫共用的 `_git_partial_clone`。修前是只查 `extensions.partialClone` 的內聯寫法,`6e10ae5b` 裡有兩處,`fe970227` 裡是零處。
   - 修前與修後的行為差異,用同一個只寫 `remote.origin.promisor=true` 與 `partialclonefilter` 的 repo 實測:
     - 修前(`6e10ae5b` 的 scripts/lumos):`_drift_born_env_err` 回 `None`,回頭條件照樣去讀舊版本。
     - 修後(`fe970227`):回「partial clone 讀舊版本會去網路抓,不讀」。
   - 把這一處改回舊寫法,再跑 `python3.14 scripts/test_lumos.py -k drift_born`,結果是 `26 passed, 0 failed`。`t_drift_born_unknown` 的③只設 `extensions.partialClone`,新舊寫法在那個案例行為相同。
   - 計劃 S1 到 S9 沒有任何一條涵蓋回頭條件那支。計劃〈回退〉只說拿掉 `_redbase_branch_rows` 的過濾與兩處 ref,沒提這支;〈實務隱患〉與 `lands_in` 也都沒提回頭條件(`lands_in` 缺 `Systems/存量漂移守衛`)。
   - 結果:下次有人把這支改回單看 extension,全套測試照綠,drift scan 又會在 promisor-only 的複製上去讀舊版本。
   - 最小補法:在 `t_drift_born_unknown` 的③後加一個只設 `remote.origin.promisor=true` 與 `partialclonefilter` 的案例,斷言 why 含 partial。
   - 歸因:有證據的修復回歸。修補提交 `d4bbaaea` 才開始改這支,測試缺口也從這次開始。行為本身沒壞,壞的是修補沒被保護。

2. 這次改動讓既有計劃筆記裡的兩句話變假,沒有改;新函式與回頭條件那支的行為變動也沒寫進任何 Systems 節點。
severity: minor
   blocking: 否
   引句:「d. repo 種類跟回頭條件那支 `_drift_born_env_err` 共用判法,第一次需要時問一次」
   - file: `docs/lumos-toolchain-knowledge/Projects/回頭條件寫下時就成立_計劃.md:101` 寫「partial clone 只看 `extensions.partialClone`,不看各 remote 的 `promisor` 設定」,第 51 行寫「partial clone(`git config extensions.partialClone` 有值」。兩句在 `6e10ae5b` 為真,在 `fe970227` 為假,diff 沒動這篇。
   - `_git_partial_clone` 全 repo 只有本計劃一篇提到。`Systems/存量漂移守衛.md` 沒講環境判不了的條件,`Systems/規格閘.md` 的 WHY 也沒講部分複製與淺複製的處理,三個月後的人只能去讀計劃本文。
   - 新函式放在 `scripts/lumos` 的 `_git_is_shallow` 旁邊(通用 git 輔助區),位置合理;檔案層級的家(`scripts/lumos`)也有。缺的是說明句。
   - 歸因:有證據的修復回歸。`git show` 兩版對照,第 101 行的文字不變,但程式從只看 extension 變成看三個設定。

3. 驗收條款 S8 說判不了治理帳有沒有被忽略、或 HEAD 解不出時「印一句說明」,程式不印,測試也沒驗。
severity: minor
   blocking: 否
   引句:「過濾應把那幾筆紀錄照舊算進來並印一句說明」
   - 程式只在 `ignored == "ignored"` 時才進 `_redbase_on_branch`,說明只在那裡印(`scripts/lumos:14496`);HEAD 解不出的路徑(第 14468 行 `ok` 為假)也不計入 `unsure`。計劃做法 1 e 也寫「b 以外」才印,所以是條款與計劃本文、程式不一致。
   - 重現:建一個帳被 `.gitignore` 忽略、帳裡有 `ref` 不同分支紀錄的 repo,呼叫 `_redbase_branch_rows(d, "甲", ignored=st)`。
     - `st="unknown"` 時回 1 筆,stderr 為空。
     - `st="ignored"` 且 `head_sha` 寫成字面 `HEAD` 時回 1 筆,stderr 為空。
   - `t_redbase_branch_rows_fallback_keeps` 對 unknown 與「還沒有提交的 HEAD」只斷言 shas,沒斷言說明。
   - 修法二選一:改條款,或讓 unknown 路徑印一句。
   - 歸因:有證據的原有漏查。同一支探針在 `6e10ae5b` 與 `fe970227` 輸出完全相同。

4. 三個設定「各自認定」只是文件說法,測試沒有逐個釘。
severity: minor
   blocking: 否
   引句:「新式部分複製只寫 remote.<名>.promisor 與 partialCloneFilter,沒有 extensions.partialClone:照樣認得」
   - 測試的 `pc2` 同時設了 promisor 與 partialclonefilter。真實 `git clone --filter` 也是兩個都寫,所以測試貼近真實。
   - 逐個改壞實測,`-k redbase_branch_rows_fallback` 與 `-k drift_born_unknown` 全綠:
     - M1:pattern 拿掉 `remote\..*\.promisor`。
     - M2:pattern 拿掉 `remote\..*\.partialclonefilter`。
     - M3:拿掉 `promisor` 不是 true 時略過的那段。
   - 計劃寫「三個設定各自認定」,但只有 extensions 那條與「兩個一起」被釘。
   - 補法:各補一個只有單一設定的案例,以及一個 `promisor=false` 的案例。
   - 歸因:有證據的修復回歸,新函式與測試都是 `d4bbaaea` 加的。

5. `_git_partial_clone` 會漏判沒有值的布林 `promisor`。
severity: minor
   blocking: 否
   引句:「if key.endswith(".promisor") and val not in ("true", "yes", "on", "1"):」
   - 重現:`.git/config` 寫 `[remote "origin"]` 底下單獨一行 `promisor`(無等號)。
     - `git config --get-regexp` 只印鍵,`val` 為空字串,函式回 `False`。
     - `git config --type=bool --get remote.origin.promisor` 回 `true`。
   - 真實 `git clone --filter` 會寫 `promisor = true`,所以只有手改設定才會踩到,可能性低。漏判的後果是回到會連遠端抓的路徑,也就是這個函式要擋的那一類。
   - 歸因:有證據的修復回歸。`_git_partial_clone` 是 `d4bbaaea` 新寫,修前沒有這個函式。

6. 規格閘 WHY 沒有把「這次改用 head_sha」跟上一行「不選記版本編號」對上。
severity: minor
   blocking: 否
   引句:「[不選:記寫入當下的版本編號跟測試首次提交比(壓提交後原提交不在、空殼與實作在檔案層分不出)]」
   - file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:51` 仍列這條不選。新的第 52 行用 head_sha 祖先判斷,只寫了代價,沒說為什麼這次可以用 head_sha(只在帳被忽略時用、沒有別的訊號、拿分支名補上)。
   - 計劃做法 4 第一點要求寫明這件事。說明只在計劃〈既有否決的對照〉,WHY 裡沒有。
   - 三個月後的人看到相鄰兩行互相矛盾,可能當成錯誤去掉 head_sha。
   - 歸因:有證據的原有漏查。

7. `_TG_LIT_PAT` 的註解前後兩句互相矛盾。
severity: minor
   blocking: 否
   引句:「跟剝註解那支 _C_STRIP_PAT 的主要差別:這裡要求字串收尾」
   - file: `scripts/lumos:49177` 同一段註解仍留「寫法同 _C_STRIP_PAT 的三引號那段」。`_C_STRIP_PAT` 的三引號收尾是 `(?:"""|\Z)`,會收沒收尾的字串,`_TG_LIT_PAT` 不會(見 `scripts/lumos:6786`)。
   - 新加的差別說明正確,但舊的「寫法同」沒刪,正好是計劃要消除的那種誤導。
   - 歸因:有證據的原有漏查。舊句早已存在,修補沒有改它。

## 已驗主張與證據

在 `/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/整合-sonnet/repo` 的 `fe970227` 上跑的結果:

- 全部綠:`-k spec_gate`(406)、`-k redbase`(194)、`-k tq_guard_cli_contract`(99)、`-k name_collision_scales`(4)、`-k tq_guard_string_comma_args`(24)、`-k gate_event`、`-k gov_readers`。
- 七篇被改的筆記 `lumos lint` 都是 0 問題。`lumos spec-trace` 顯示 S1、S2、S3、S4、S6、S7、S8、S9 共 8 條全綁、懸空 0。
- 改壞驗證:
  - `_TG_CONST_PAT` 拿掉三引號段,`t_tq_guard_string_comma_args` 紅在 S4 那條。
  - `_TitleIndex._join` 去掉快取,`t_name_collision_scales` 紅在②(515 個不同物件)。
  - 這支測試用 `id()` 數同一份,被回收的物件位址會重用,所以只偵測得到約一半的重算;1000 次全重用的機率很低,沒有構成失敗場景,不另列。
- 真實 `git clone --filter=blob:none`(git 2.39.2,伺服器不認 filter)只寫 `remote.origin.promisor=true` 與 `partialclonefilter=blob:none`,沒有 `extensions.partialClone`;`_git_partial_clone` 回 `True`,來源 repo 回 `False`。
- 寫入端與讀取端取分支名共用 `_redbase_branch_name`,同名 tag 與分離 HEAD 的行為跟計劃一致。留痕事件多的 `ref` 沒有被別的讀取端誤讀(`_codeloop_read_from_ledger` 只認 gate=code-loop)。
- 常數與預設值對得上:`_REDBASE_ANC_BUDGET_SEC` 是 10、`_REDBASE_ANC_CAP` 是 200,`_TG_LIMITS` 與 `test-quality-standard.md` 同步(`t_tq_guard_cli_contract` 綠)。
- 「改壞驗證通過」的案例只看原始結果是否紅,沒有替測試作者背書。

## 配對案例結果

- repair:
  - G1 只寫 promisor 的複製不連遠端。測試綠,但只證到「promisor 加 filter 一起」,逐個改壞見發現 4。
  - G1 回頭條件那支用同一個判斷。修前回 `None`,修後回訊息;測試無法分辨新舊寫法,見發現 1。
  - G2 帳被忽略時不算分岔點。`forks == []` 的斷言成立。
  - G3 分離 HEAD 與還沒有提交的 HEAD、G3 同名重開的前置斷言、G4 同名 tag 照樣對得上:綠。
- preserve:
  - 舊式 `extensions.partialClone` 照認:綠。
  - 帳進版控時不過濾(S7):綠。
  - 帳判不了時照舊算分岔點:綠,但不印說明,見發現 3。

## 三問

1. 原問題的修復效果:S1、S2、S6、S7、S9 對應的行為都有紅轉綠的測試。S6 的案例有「同名重開後那個提交已不是祖先」的前置斷言。
2. 修補處的正常、錯誤與相鄰呼叫路徑:正常路徑與錯誤路徑成立;相鄰的回頭條件那支是未驗證的缺口(發現 1、2)。
3. 新發現的案例在修前與修後:發現 1 修前回 `None`、修後回訊息;發現 3 兩版輸出相同;發現 5 在修前沒有這個函式。

## 未驗範圍

- 真實 blobless 或 treeless 的遠端複製與抓取只用設定加留記號的腳本代替。
- Windows、時鐘倒退、大 repo 沒有 commit-graph 都沒驗。
- 其他內聯判祖先的路徑(`_note_reread_own_fps`、`_codeloop_missing_commit`)判不了時的方向,沒有逐一核對。
- 全套測試約 8 分鐘,沒有跑。
- 我另一次改壞 `_TG_CONST_PAT` 時測試轉紅,留下一份 `gctl-run-*` 現場,沒能認出是哪一個;其他會談的同類目錄同時存在,所以沒有刪。已刪的是我自己建的 `gctl-run-knp8gx3r` 與四個 probe 暫存。我的臨時 repo 和探針腳本仍在 `/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/整合-sonnet/`,收貨後請編排者刪。

最嚴重等級是 major,blocking 共 1 條。
