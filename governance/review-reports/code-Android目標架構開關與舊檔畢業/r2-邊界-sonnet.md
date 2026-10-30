severity: major

這是背景工作完成的通知,不是使用者回覆。該指令只是我已讀過結果的 `tail`,沒有新內容。我的臨時目錄已用字面絕對路徑刪除,沒有程序開著它。

## Findings

### 1
severity: major
blocking: 是

「清單元素必須是字串」的守衛沒有任何測試。

引句:「if not isinstance(files, list) or not all(isinstance(x, str) for x in files):」

- **輸入**:起點版 `.lumos/arch-legacy.json` 內容是 `{"files":["app/Domain/A.py",1]}`,分支改了 `app/Domain/A.py`。
- **現況行為**:`_arch_legacy_at` 判成 unreadable,清單不起作用,`pitfalls` 正常輸出(rc 0)。
- **改壞**:把該行改成只剩 `if not isinstance(files, list):`。下一行 `{nfc(x) for x in files}` 對整數 1 丟 `TypeError: normalize() argument 2 must be str, not int`。
- **重現(改壞版)**:`lumos pitfalls --diff <base>..HEAD --repo <repo> --json` 回 rc 1,stderr 末行是該 TypeError,stdout 沒有 JSON。`_arch_legacy_apply` 在推送前分級路徑沒有 try 包住。
- **測試不紅**:改壞版跑 `scripts/test_lumos.py -k arch_target`,結果 `178 passed, 0 failed`。測試只有 H 案 `{"files": "not-a-list"}` 驗外層型別。
- **影響**:一份含數字或 null 的清單,會讓推送前分級整個崩潰,而不是退回「清單不起作用」。
- file: `scripts/test_lumos.py:15815`(H 案)、`scripts/lumos:57430`
- 歸因:有證據的原有漏查。該行與 H 案在修前 `006c398b` 就一樣(兩版 grep 都找到),修補沒碰它。
- 兩版查證:修前與修後的原始碼該行相同,只有 `not-a-list` 這一個測試輸入。

### 2
severity: minor
blocking: 否

「頂端版宣告有警告就不畢業」那半個條件沒有測試。

引句:「return legacy, h_legacy, (legacy - h_legacy if h_rules == rules and not h_warns else set())」

- 把 `and not h_warns` 拿掉後,`-k arch_target` 仍是 178 passed。
- 測試 B 只用「換成另一條有效宣告」,讓 `h_rules != rules`。
- 沒有測「規則相同、警告不同」的輸入。
- 風險只在放寬到多審的方向,所以列 minor。
- 歸因:有證據的原有漏查。修前的 `_arch_legacy_apply` 內嵌同一條件 `h_rules == rules and not h_warns`。

### 3
severity: minor
blocking: 否

沒有宣告、只有舊檔清單時,doctor 摘要行沒有測試。

引句:「        return [], [], leg_list, leg_probs」

- 把這行改成 `return [], [], [], []` 後,`-k arch_target` 仍是 178 passed。
- `t_arch_target_legacy_doctor_lines` 只用有宣告的 repo,沒有「清單在、宣告沒有」的 doctor 案例。
- 歸因:有證據的修復新增行為。修前的 `_arch_legacy_doctor_line` 本來就不看宣告是否存在,新行為是修補才加的。這是新增的覆蓋缺口,不是回歸。

## 固定席逐條判定

- **`Systems/arch-alignment-lens`(家)**:不影響已宣稱的行為。起點版宣告仍是唯一的規則來源,畢業只在「宣告一字不改」時放行,方向是審得更多。
- **`pitfalls-code-loop`(家,RISK)**:不影響。分級與分流結果,在我跑過的輸入上與預期一致。Finding 1 的崩潰只出現在被改壞的版本。
- **`lumos-cli-read`、`design-loop`、`guard-kill`、`測試假綠形態`(INVARIANT)**:不影響。diff 沒碰 `search`、處置閘、guard kill 的邏輯。「測試假綠」那條要求的現場前置斷言,與 Finding 1、2、3 同類,但這幾處缺的是守衛測試,不是修復還原釘。
- **`Issues/code-loop守衛main-direct盲區`、`reversibility-governance-ledger`**:不影響。本案不碰帳本與 main-direct 守衛。
- **「超出上限,只列名」的節點**:未逐條判,未驗範圍。

## 極端輸入實跑

以下都在固定版 `44b0044` 上跑。

| 輸入 | 結果 |
|---|---|
| 空清單 | 全照目標審 |
| 一支 | 正確 |
| 重複項 | 正確,只算一次 |
| 開頭 BOM | 正確 |
| 檔名含空白與方括號 | 照字面比對,正確 |
| NFD 寫法的清單項 | 與 NFC 檔名認得是同一支 |
| 非 UTF-8 | unreadable,不崩 |
| 含數字元素 | unreadable,不崩(見 Finding 1 的守衛) |
| 清單是目錄或符號連結 | 讀不懂,不崩 |
| 頂端清單是 `{"files": null}`、`{}` 或頂層陣列 | 不畢業 |
| 頂端整份清單刪掉 | 全畢業 |
| `./` 開頭或目錄項 | 不命中,doctor 算「已不存在」 |
| 5 萬行清單加 61 條宣告的 doctor | 1.75 秒 |
| 2 萬支檔乘 61 條規則的 split | 0.71 秒 |
| 宣告第一條是 `**` → `none` | 清單項被算成「沒被判給」,符合預期 |
| `_lens_git` 全部回 None | 印「讀不到」,不印「讀不懂」 |

## 三問

**① 原問題的修復效果有何行為證據?**

- **未判定**。以下兩個案例,修前 `006c398b` 與修後 `e31302e3` 的結果完全相同:
  - **I 案**:範圍起點 `c1` 有清單、範圍是 `c1..c2`。命令是 `lumos pitfalls --diff c1..c2 --json`,兩版 targets 都是 `{'Systems/N': ['app/Domain/A.py']}`。
  - **J 案**:清單寫 NFD、檔案是 NFC。同樣的命令,兩版 targets 都是 None。
- 我沒有重現出修前的錯,所以無法證明修補改變了這兩個行為。
- G2、G3、G4 的修前行為沒有另存,我也沒另跑 `code-loop check`,同樣未判定。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**

- 呼叫端接成新的單一回傳值,沒有遺漏:`_arch_legacy_apply` 的三個呼叫點都改成單值接收。
- `_arch_target_doctor_lines` 在 `scripts` 下只剩 `run_doctor` 一個呼叫者,而且已改成接四個值。
- doctor 的錯誤路徑成立,但有一個小回歸。舊檔清單檢查原本有自己的 try/except,現在併進 `_arch_target_doctor_lines`。任一段出錯,另一段的結果會一起被丟掉。我沒找到能在舊檔清單那段丟例外的輸入,所以只是耦合變緊,不是已知故障。
- 沒有宣告也沒有清單的專案,修前 doctor 的 git 呼叫是 `show`、`cat-file`、`show`、`cat-file`。修後多了一次無條件的 `ls-files -z`。
- 在 16532 支檔的 repo,這次呼叫約 0.02 秒。我給不出具體失敗場景,所以不立 finding。
- doctor 沒有多印任何東西(回 `([], [], [], [])`)。

**③ 新發現的同一案例在修前、修後各是什麼結果?**

- Finding 1 的改壞實驗只做在修後版,但守衛程式碼與唯一的測試輸入在兩版相同,所以兩版的行為視為相同。
- Finding 2、3 沒有逐版另跑,只在修後版驗了「改壞後 178 項照綠」。

**未驗範圍**

- 沒跑 `code-loop check` 的 K 案(沒有宣告時不印說明行)。
- 沒測 git 逾時。
- 沒測幾千支改動檔加清單的端到端 `pitfalls`。

最嚴重等級為 major
