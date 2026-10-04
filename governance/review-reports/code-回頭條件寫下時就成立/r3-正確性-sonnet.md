severity: clean

沒有 finding。走過的輸入與結論如下。

## 走過的輸入(正確性)

(a) 「整份回 None」會不會誤殺正常輸出。實跑 git 2.43,把 `git log --no-show-signature --follow [--first-parent] --format=%H --name-status -z` 的原始位元組看過:
- 空輸出:toks 為空,回 [],不是 None。
- 只有一個提交(A):「sha\0\nA\0path\0」→ 解得出。
- 改名 R100(新舊兩個路徑)、刪除 D、修改 M:都符合 `[A-Z]\d*`,位置照 n 取。複製 C、類型變更 T、未合併 U 同樣符合。
- 沒有檔案列的合併提交(不帶 --first-parent):sha 後直接接下一個 sha,兩個都符合 SHA 規則,不碰 None 那一行。
- 路徑看起來像 40 碼十六進位:路徑是被 R/C/一般狀態列「依位置」吃掉的,不會被當成 sha 認,沒有新增的誤判面。路徑首尾換行被 strip 是舊行為,這輪沒改。
- log.diffMerges=dense-combined / first-parent 設定加上 --follow:實測輸出仍是單字母狀態(M),不產生 MM。只有手動加 --cc / -c 才出 MM,而這條 git log 沒帶那兩個旗標、也不隨設定帶出,所以走不到。
- 簽章提交(用假 gpg 程式實做出 gpgsig 提交,設 log.showSignature=true):確認 gpg 訊息會進 stdout、黏在 sha 前面,同一個 \0 片段變成「訊息\nsha」,fullmatch 失敗 → 現在回 None(修法目的);加 --no-show-signature 後輸出乾淨。`git show -s --format=%cs` 同樣會夾訊息,加旗標後乾淨。

(b) `--no-show-signature` 是 git 2.10 起的旗標,對 log、show 都有;放在 `--follow`、`--first-parent` 之前或之後都是一般選項,沒有順序問題。本機 2.43 實測可用。

(c) `_note_status_seq` 在 scripts/lumos 只有 `_note_flip`(約 29949 行)一個呼叫端:`seq is None` 時 strict 回 None、不嚴格回 False,本來就有處理。`_DriftBornHistory._text` 在 `pairs is None` 時回 ("err", "git 讀不出這篇的歷史"),也本來就有。`_git_commit_date` 回 None 時,輸出端(約 35515 行)用 `born.get('date') or '日期讀不出'`,有接。

(d) 新測試:
- ⑤ 用合成原始位元組,修法被還原(跳過而非回 None)會得到非 None,翻紅。
- ⑥ 檢查 log、show 的 git 呼叫引數都含 `--no-show-signature`,拿掉任一處就翻紅;前置:集合要剛好等於 {"log","show"},證明兩種呼叫都真的跑到。
- ⑧ 把 `_lens_git` 換成夾了 gpg 訊息的輸出,還原「不是日期形狀就回 None」會翻紅。
- ⑦ 單獨看在沒簽章提交的測試庫裡本來就會過,還原修法也不會翻紅(它只能靠 ⑥⑧ 守);另外 ⑥ 設的 log.showSignature 在沒有簽章提交的庫裡不產生任何效果,測試實際守的是「呼叫引數」而不是「端到端行為」。這是測試強度的備註,不是會讓現場出錯的輸入,所以不標 finding。
- `python3.14 scripts/test_lumos.py -k note_versions` 9 支全綠。

## 固定席判定

- lumos-cli-read:這份差異新增的 git 呼叫都是 log、show 的唯讀呼叫,沒有寫治理帳,不影響。
- bound-tests-gate:改動在 scripts/lumos 與 test_lumos.py,沒動綁定測試的對照表,不影響。
- guard-kill:沒碰守衛與殺傷力流程,不影響。
- 授權與歸屬:沒碰,不影響。
- 測試假綠形態:⑤⑥⑧ 有還原就翻紅且 ⑥ 有前置(集合剛好是 log 與 show);⑦ 較弱(見上),不構成違反 INVARIANT,因為它的配對 ⑧ 是真的紅綠釘。
- lumos-cli-lifecycle:沒新增指令與生命週期階段,不影響。
- design-loop、pitfalls-code-loop:沒改流程文字與閘,不影響。
- Systems/存量漂移守衛:「判不了就明講 unknown、不猜」的方向一致,新增的 None 路徑落在已有的 "git 讀不出這篇的歷史"。
- Systems/筆記內容審:`_note_flip` 對 None 本來就有分支;嚴格模式變成判不了(符合「不能當沒翻轉」的原則),不嚴格模式回 False(舊行為)。
- 注意點:不嚴格模式下 None→False 代表「這一篇不當候選」,與之前 git log 失敗時一致,沒有新增語義。

總結:最高等級 clean
