severity: minor

我逐 hunk 讀完整份 diff,沒找到 blocker 或 major。下面 6 條都是 minor,blocking 都是否。

我本機沒有 ast-grep,所以需要 ast-grep 的 S1、S4 兩支測試沒法跑。`lint_new.include_test_paths` 那組(`t_lint_new_include_test_paths`)8 項已跑過,全綠。

**1. 型錄編號檢查把決策表的 `D-n` 也當成型錄編號**
severity: minor
blocking: 否
file: `configs/ast-grep/kotlin-android/check.py:109-114`(patch 第 109-114 行)
引句:「main = text if cut < 0 else text[:cut]」
`catalog_ids` 只在「## 待查證」前截斷,範圍連「## 情境決策表」都吃進去,`D-1`、`D-10` 這類列編號就混進編號集合。
重現:用 python3.14 載入 check.py 後,`catalog_ids()` 回 531 個編號,其中含 `D-1`、`D-10`、`D-11`、`D-12`、`D-13`。`message_problems([{...,"message":"[D-1] x;改用 y"}], ids)` 回 `[]`,也就是不報錯。
後果:規則訊息寫 `[D-1]` 會過 S2「訊息要引用型錄裡真的有的編號」這道檢查,但 `D-1` 不是規則編號。
修法:改在「## 情境決策表」前截斷(`catalog_problems` 已用 `i_dt` 這樣切)。

**2. 祖先目錄樣本的掃描失敗被悄悄吞掉**
severity: minor
blocking: 否
file: `configs/ast-grep/kotlin-android/check.py:315`
引句:「for (i, f) in scan(sg, cfg, TEST_ONLY_ANCESTOR) or []:」
`scan` 失敗會回 `None`(returncode 不是 0 或 1,或設定檔壞掉)。`or []` 把它當成零命中,祖先目錄那道檢查就空過。
對照:同函式上面壞例、好例的掃描失敗有報 `跑不起來`,這裡沒有,處理不一致。
修法:`None` 時同樣加一條 problem。

**3. 新增的各道檢查有一半沒有「改壞就紅」的測試**
severity: minor
(自行降級,見下)
blocking: 否
file: `scripts/test_lumos.py`(`t_kotlin_rulepack_samples` 與 `t_kotlin_catalog_rows_wired`)
引句:「dup.write_text("id: kt-dup-probe\nlanguage: kotlin\nseverity: error\nmessage: '[API-3] 探針;改用 launch'\nrule:\n  pattern: probeOnly()\n", encoding="utf-8")」
我在測試函式範圍內逐字 grep 這些檢查的失敗訊息,都是 0 筆:
- `id 重複`:這個「dup」探針的 id 是唯一的 `kt-dup-probe`,根本沒重複任何 id。
- `好例至少要兩段`、`缺好例樣本`
- `缺 samples/ancestor`
- `形狀類要有`
- `沒有被任何決策表`
- 型錄裡有指向暫存區路徑
- `觸發字不准空`
- 載入條數對不上(`got != want or skipped`)
具體改壞:把 `check()` 裡 `if dup:` 整段刪掉,或把 `good_cases(good) < 2` 條件拿掉,測試仍然全綠。
這違反使用者記憶裡的「每道檢查各改壞一次」。
降級說明:`check()` 內的那幾道本機無 ast-grep,沒法當場翻紅,所以按規則自降一級,從 major 降到 minor。

**4. 樣本歸屬用第一個叫 bad 或 good 的路徑段判斷**
severity: minor
blocking: 否
file: `configs/ast-grep/kotlin-android/check.py:289-290`
引句:「owner = parts[parts.index(kind) + 1] if kind in parts and parts.index(kind) + 1 < len(parts) else ""」
`parts` 來自 ast-grep 回傳的完整路徑,`index` 取第一個匹配的段。
失敗情境:repo 放在像 `/Users/x/good/...` 或 `/work/bad/...` 的目錄下,owner 會變成那個目錄的下一層,所有規則都報「壞例只命中 0 處」,並且好例誤報檢查也被架空。
修法:用 `parts.index("samples")` 之後的那一段,或把路徑轉成相對於 `HERE / "samples"` 再切。

**5. 只掃測試碼的規則判定太鬆**
severity: minor
blocking: 否
file: `configs/ast-grep/kotlin-android/check.py:104-105`
引句:「"test_only": bool(re.search(r"^files:.*src/(test|androidTest|testFixtures)", doc, re.M | re.S)」
`.*` 加 `re.S` 會跨過 `files:` 區塊,一路掃到整份規則文件。
失敗情境:規則 `files: ['**/app/**']` 加上 `ignores: ['**/src/test/**']`,後面的 `src/test` 會讓它被判成只掃測試碼的規則。
後果:祖先目錄樣本檢查會對它誤報。
修法:先抽出 `files:` 區塊(第二個正規式已經在做),再只對那段比對。

**6. 樣本目錄排除條件在消費專案也會生效,而測試說明寫的不是這樣**
severity: minor
blocking: 否
file: `scripts/lumos`(`_stack_changed_ok`)
引句:「_RULEPACK_SAMPLE_RE = re.compile(r"configs/ast-grep/[^/]+/samples/")」
測試 docstring 寫「消費專案裡長得像的路徑照掃」,但程式只比對路徑形狀,沒有區分是不是本 repo。
失敗情境:消費專案自己有 `configs/ast-grep/<x>/samples/*.kt` 的正式碼,會被整批排除出風險分級、棧別題和新增告警閘。
測試只驗了 `app/samples/bad/X.kt` 這種不同層的路徑,沒驗同形狀的路徑。
修法:要嘛接受這個範圍並把註解改實話,要嘛用設定開關限定。

**逐角度結論**
- 被刪行為:只換掉 `_stack_changed_ok` 的測試排除那一行。預設空集合時等價於舊行為,其他呼叫端(`scripts/lumos` 第 61831、61840、61847、65924 行附近)都傳位置參數 `vend_skip`,第三個參數不影響它們,沒有呼叫端被弄壞。
- 設定值 `frozenset` 沒有被 JSON 輸出,我追過 `cfg` 的使用處,沒有序列化問題。
- 重用:型錄表格解析沒有可重用的既有函式,不報。
- 慣例:`_stack_changed_ok` 的 docstring 與圖譜節點宣稱一致,我沒找到可逐字引用且違反的規則,不列。

**總結**:邏輯本身沒有會做出錯行為的缺陷;主要缺口是型錄編號集合混入 `D-n`,以及新增檢查約有一半沒有逐項改壞的測試。
