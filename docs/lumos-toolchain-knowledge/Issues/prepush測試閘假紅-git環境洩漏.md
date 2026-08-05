---
type: issue
status: resolved
created: 2026-08-01
updated: 2026-08-01
tags:
  - type/issue
  - status/resolved
summary: |-
  FLAG:TECHNICAL
  DECISION:①薄殼(install.sh/uninstall.sh)改用純 bash 參數展開取目錄,不呼叫外部 `dirname`——這是交付給別人跑的工具,少一個外部依賴是實打實的可攜性,且把系統目錄加回測試 PATH 會破壞該測試「證明沒寫死 python」的前提 ②GIT_DIR 那條併案保留,清在 test_lumos.py 唯一進入點而非幾十個呼叫點各自清(分支簿記天生會漏)
  KEY:★真因(第二次診斷才對)★=`install.sh` 薄殼呼叫外部 `dirname`,而測試把 PATH 縮到只有 python3 stub + `bash`/`git` 所在目錄;互動 shell 的 `git` 在 `/usr/bin`(有 dirname)、hook 底下的 `git` 在 CommandLineTools(沒有)→ 同一份碼在兩種環境一綠一紅。修法=薄殼改用純 bash 參數展開 `${SOURCE%/*}`,零外部依賴
  KEY:★第一次診斷是錯的,留著當教訓★——先押 `GIT_DIR` 洩漏,實測把 GIT_DIR 指向本 repo 確實讓 65 條翻紅,「機制成立」就當成「找到真因」;修完再推,還是紅三條。**一個假說能重現出更嚴重的症狀,不代表它是眼前這個症狀的原因**
  KEY:★而且那個假說的前提也是錯的★:`git push` 並不會把 `GIT_DIR` export 給 hook——反證是每次 pre-push 跑完 repo 都沒被污染,而我手動設 `GIT_DIR` 跑的那兩次★把 127 筆測試 fixture commit 寫進了本 repo 的 main★(834→1029),得 reset 到乾淨基底重貼內容才救回來。env-strip 的修法保留(它正好防住我自己造成的這種傷害),但★不得宣稱它修的是 hook 環境★
  KEY:★這是「閘一直在給假紅」的事故,不是單純的 flaky★——一個持續給假紅的閘,下一次就會被人用 `--no-verify` waive 掉,等於閘自己把自己關了
aliases:
  - dirname
---
# prepush測試閘假紅-git環境洩漏

> ★檔名保留第一次（錯的）診斷用詞，刻意不改★——「git環境洩漏」是最初押錯的假說，真因見下方〈真因（第二次診斷）〉。留著檔名是為了讓「我曾經診斷錯」這件事在檔案清單上就看得到，而不是事後被無痕修掉。

## 症狀

同一個 commit、同一棵工作樹：

- 人手跑 `python3 scripts/test_lumos.py` → **2039 passed / 0 failed**
- 由 `git push` 觸發 pre-push hook 跑同一支 → **紅 3~5 條，而且每次紅的條數不一樣**

hook 只印輸出尾段，看不到紅的是哪幾條；`/tmp/lumos-prepush-tests.log` 又會被套件裡「測試 pre-push hook 本身」的測試覆寫，所以第一時間拿不到失敗清單。

## ★第一次診斷是錯的（留著當教訓，不刪）★

先押的假說是「`git push` 把 `GIT_DIR` export 給 hook，hook 傳給測試進程，測試自己 `git init` 的臨時 repo 被 `GIT_DIR` 覆蓋 cwd 推斷」。

實測：把 `GIT_DIR` 指向本 repo 再跑整套 → 紅的條數從 3 **暴增到 65**；套修法後同一環境 → 2039 passed / 0 failed。看起來機制完全成立，於是當成找到真因、修完就推。

**還是紅三條。**

★教訓★：**一個假說能重現出「更嚴重」的症狀，不代表它是眼前這個症狀的原因。** 65 ≠ 3 這個數字對不上就是訊號，當時被「機制講得通」蓋過去了。正確的收斂條件是「用假說解釋得了觀察到的**那三條**」，不是「假說能造出一堆紅」。

★而且那個假說的前提本身也是錯的★：`git push` **並不會**把 `GIT_DIR` export 給 hook。反證很直接——每次 pre-push 跑完，repo 都沒有被污染；而我為了「驗證機制」手動設 `GIT_DIR` 跑的那兩次，**把 127 筆測試 fixture 的 commit 寫進了本 repo 的 main**（祖先數 834 → 1029），最後得把 main reset 到乾淨基底、再把內容重貼上去才救回來。

★教訓之二★：**為了驗證一個「環境會被污染」的假說，我直接在真 repo 上製造了那個污染。** 該做的是在拋棄式的 clone 上跑。env-strip 的修法保留（它恰好防住我自己造成的這種傷害，也是真的加固），但**不得宣稱它修的是 hook 環境**——它防的是「有人手動設了 `GIT_DIR` 才跑測試」。

## 真因（第二次診斷）

拿到失敗清單才看得出來（hook 只印尾段，得直接讀 `/tmp/lumos-prepush-tests.log`）：

```
✗ 模擬 Windows 安裝(PATH 只有 python3)rc0
  .../pkg/install.sh: line 35: dirname: command not found
```

- `slim/install.sh`（交付給接手者的薄殼）呼叫**外部** `dirname` 來定位自己所在目錄。
- 對應測試刻意把 `PATH` 縮到只有「自製 python3 stub」+「`bash`/`git` 所在目錄」，好證明 shim 沒有寫死 `python`。
- **互動 shell 的 `git` 在 `/usr/bin`**（那裡有 `dirname`）→ 綠；**hook 底下的 `git` 在 `/Library/Developer/CommandLineTools/usr/bin`**（那裡沒有 `dirname`）→ 紅。

同一份碼、同一棵樹，綠或紅取決於**那台機器的 `git` 裝在哪個目錄**。

## 修法與選型理由

`slim/install.sh` 與 `slim/uninstall.sh` 改用純 bash 參數展開取目錄（`${1%/*}`，處理「無斜線」與「根目錄」兩個邊界），**不再呼叫外部 `dirname`**。

**為什麼修碼而不是把 `dirname` 的目錄加進測試 PATH**：這支薄殼是要在**別人機器**上跑的一次性交接工具，PATH 被縮小的情境真實存在（容器最小映像、CI 乾淨 shell、使用者自訂 PATH）；少一個外部依賴是實打實的可攜性。而把系統目錄加回 PATH 反而會破壞這條測試原本的前提——那些目錄可能藏著 `python`，測試正是要證明沒寫死 `python`。

**GIT_DIR 那條的修法（併案保留）**：`scripts/test_lumos.py` 的 `main()` 開頭 pop 掉 `GIT_DIR` / `GIT_WORK_TREE` / `GIT_INDEX_FILE` / `GIT_PREFIX` / `GIT_COMMON_DIR` / `GIT_OBJECT_DIRECTORY` / `GIT_ALTERNATE_OBJECT_DIRECTORIES`。清在唯一進入點而非幾十個呼叫點各自清——後者是分支簿記，天生會漏。清掉的是「測試該用哪個 repo」的外部注入，不是任何斷言，**是加嚴不是放寬**。

## 回歸釘

- `t_slim_install_windows_shim_*`（既有）：把薄殼改回 `dirname`、用 hook 型 PATH（`git` 解析到 CommandLineTools）跑，三條斷言確實翻紅；改回純 bash 展開後轉綠。**非稻草人。**
- `t_suite_strips_git_env_from_hook_invocation`（新增，對應 GIT_DIR 那條）：用被污染的 env spawn 子進程跑一條 git 重的測試，斷言 rc0；把 `environ.pop` 換成 `pass` 會連同 `codeloop_guard_prepush` 的兩條斷言一起翻紅。


## 影響評估（誠實）

- **這道閘假紅多久了不確定**。取決於這台機器上 `git` 何時變成解析到 CommandLineTools,沒有紀錄可查。
- **只在「`git` 不在 `/usr/bin`」的機器上發作**——所以別台機器可能從來沒看過這個紅,也因此更容易被當成 flaky。
- **可能的下游影響**：過去若有人在 pre-push 紅的時候選了 `--no-verify`，那次 push 等於沒過測試閘。
- **本次不擴大回溯**：修法本身已讓閘可信，回溯稽核是另一個題目。
