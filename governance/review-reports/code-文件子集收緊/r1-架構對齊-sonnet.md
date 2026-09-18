severity: major

## F1 CI「自主迴圈測試」步驟用 if/else 整條指令複寫兩份,沒接上同檔案裡剛示範過的 `extra=""` 寫法(pre-push 那邊同一件事反而有照抄既有的陣列寫法)

severity: major
blocking: yes

引句:「if [ "$SUITE" = docs ]; then python scripts/test_autonomous_loop.py -k real_claude_md; else python scripts/test_autonomous_loop.py; fi」

file: `.github/workflows/ci.yml:47-56`(Full test suite 步驟,這次沒改,示範既有寫法)
file: `.github/workflows/ci.yml:85-90`(自主迴圈測試步驟,這次新加,另開一種寫法)
file: `scripts/hooks/pre-push:349-356`(同一份 patch 裡,pre-push 對同一個決策照抄了既有的陣列寫法)
file: `scripts/hooks/pre-push:403-406,445`(`_suite_args` 既有寫法:空陣列→條件賦值→`${arr+"${arr[@]}"}` 展開一次)
file: `scripts/hooks/pre-push:410-412,447-448`(`_keys_args`,同一套寫法的第二個實例)

觀察到什麼:
這份 patch 裡「依 `$SUITE` 是不是 docs 決定要不要多帶一個旗標」這件事出現了兩次——pre-push 一次、CI 一次——而兩邊選了不同的寫法。

pre-push 那邊(patch 內,scripts/hooks/pre-push:349-352):
```
_AUTOLOOP_ARGS=()
if [[ "$_SUITE_SEEN" -eq 1 && "$_SUITE_FULL" -eq 0 && "$_SUITE_LIGHT" -eq 0 ]]; then
  _AUTOLOOP_ARGS=(-k real_claude_md)
fi
```
呼叫時 `${_AUTOLOOP_ARGS+"${_AUTOLOOP_ARGS[@]}"}`(pre-push:356)。這跟本檔既有的 `_suite_args`(pre-push:403-406,呼叫見 445)、`_keys_args`(pre-push:410-412,呼叫見 447-448)是同一套「空陣列→條件塞值→`${arr+"${arr[@]}"}` 展開一次」的既有寫法,連命名習慣(`_XXX_ARGS`)都對得上。這一半沒問題。

CI 那邊(patch 內,ci.yml 新增的「自主迴圈測試」步驟)卻不是這樣寫,是整條指令在 if/else 兩邊各寫一次:
```
if [ "$SUITE" = docs ]; then python scripts/test_autonomous_loop.py -k real_claude_md; else python scripts/test_autonomous_loop.py; fi
```
而就在同一份 .github/workflows/ci.yml、往上數三個步驟的「Full test suite」步驟,做的是同一種事(依 `$SUITE` 決定要不要多帶一個旗標給 `test_lumos.py`),寫法是既有的 `extra=""` 變數:
```
extra=""
if [ "$SUITE" = docs ]; then extra="--suite docs"; echo "純文件推送:只跑文件子集(--suite docs),不跑全套"; fi
...
python scripts/test_lumos.py --shard "$i/4" $extra > ...
```
(ci.yml:53-56,這步這次沒改動,是既有寫法)。這批新加的「自主迴圈測試」步驟完全沒有沿用緊鄰在上面、同一份檔案裡的 `extra` 寫法,另外發明了一種「整條指令複寫兩份」的寫法。

怎麼重現:
對照 .github/workflows/ci.yml 第 47-56 行(Full test suite,舊寫法)跟第 85-90 行(自主迴圈測試,這次新加)。同一個檔案、同一個決策形狀(依 `$SUITE` 是否為 docs 決定加不加旗標),兩種不同寫法並存;再對照同一份 patch 裡 pre-push 那半反而照抄了本檔既有的陣列寫法(_suite_args/_keys_args),可以看出「CI 這邊另開一種寫法」不是因為找不到既有寫法可抄,是這次沒抄。

為什麼是不對齊,不是風格:
這不是「同一件事寫得比較長或比較短」的美觀問題。同一份改動裡,對同一個決策形狀(依 `$SUITE` 加不加旗標),本來已經有兩個可以直接照抄的既有寫法可用——ci.yml 自己往上三步的 `extra=""`,以及這份 patch 自己在 pre-push 那半剛示範過的 `_AUTOLOOP_ARGS` 陣列寫法——CI 這步卻兩個都沒抄,另開了「整條指令複寫兩份」的第三種寫法。以後有人要在 ci.yml 加第三個「依 `$SUITE` 加旗標」的步驟,會不知道該抄哪一種;而且複寫整條指令的寫法在旗標一多就會兩份一起漏改(extra/陣列寫法只要改一處),已經是「引入第二種做法」的典型情況。

## 其餘逐問對照(未計入不對齊,詳見驗過的路徑)

- Q1(`_AUTOLOOP_ARGS` vs `_suite_args`/`_keys_args`):對齊,見上面 F1 的第一段分析——pre-push 那半是抄對的,問題出在 CI 那半。
- Q3(`_docs_suite_select` 的「真 repo 根」正則是不是又一份清單):對齊,見驗過的路徑。
- Q4(`"t_ci_wait" not in names` 釘死具體名字,本檔有沒有先例):對齊,見驗過的路徑。

## 驗過的路徑

**Q1:pre-push 的 `_AUTOLOOP_ARGS`**——`scripts/hooks/pre-push:349-352,356` 跟本檔既有的 `_suite_args`(`pre-push:403-406`,呼叫見 `445`)、`_keys_args`(`pre-push:410-412`,呼叫見 `447-448`)是同一套「空陣列→條件賦值→`${arr+"${arr[@]}"}` 展開一次」寫法,連命名習慣都對得上,不是第二種做法。（真正對不齊的是 CI 那半,已寫成 F1。）

**Q3:`_docs_suite_select` 的「真 repo 根」正則不是又一份清單**。查了兩點:
1. 本檔(`scripts/test_lumos.py`)沒有一支共用的「取真 repo 根」輔助函式可以認——`GRAPHCTL`(`test_lumos.py:30`)只是「這支測試檔自己的路徑」這個常數,拿它組出 repo 根的寫法散在全檔幾十處,寫法本身就不只一種(`Path(GRAPHCTL).resolve().parent.parent`、`pathlib.Path(GRAPHCTL).resolve().parent.parent`、`_P(GRAPHCTL).resolve().parent.parent`、`Path(__file__).resolve().parent.parent` 都各自出現過,例如 `test_lumos.py:142,477,588,697,754,1404,3378,5612,6293,6451` 等)。既然全檔本來就沒有單一入口可以直接認,這次用正則列舉「本檔實際出現過的幾種寫法」不是新開了一份跟既有工具打對台的清單,是延續本函式自己既有的做法。
2. `rx_real` 這個變數名跟正則比對的作法在這次 diff 之前就存在——patch 裡被拿掉的舊版本身就有 `rx_real = _re.compile(r"parent\.parent|__file__|REPO_ROOT|Path\(GRAPHCTL\)")`(見 patch 第 99 行的 `-` 那行),這次只是把同一顆變數的規則收緊(從「隨便出現 `parent.parent` 或 `__file__` 字樣」收緊成「完整的 `(GRAPHCTL)...parent.parent` 或 `(__file__)...parent.parent` 或 `REPO_ROOT`」),不是引入新機制。另外 `test_lumos.py:31-33` 有一則明確留下的架構席 r1 裁定:「這個檔的慣例是 `_load_lumos_inproc()` 讀活的常數,不抄第二份」——這條裁定管的是 `_DOCS_ONLY_PATHS` 那種**資料清單**(本函式在 `test_lumos.py:91` 確實是讀活的模組常數,沒有抄成本檔字面量),跟 `rx_real` 這種比對**原始碼語法形狀**的正則是兩回事——語法形狀沒有活的常數可以讀,寫成正則本來就是本檔（也是本函式自己既有）的處理方式。

**Q4:`"t_ci_wait" not in names` 釘死具體名字有先例**。就在同一支函式 `t_runner_suite_flags` 裡,緊接在新加的 check 下面兩行,既有一條 `check("docs 子集不含跟文件無關的測試", "t_runner_exitfirst_and_failfirst" not in names and "t_guard_kill" not in names, "")`(`test_lumos.py:44232`,這次沒改),用的就是同一種「釘死具體測試名字、斷言它不在挑選結果裡」的寫法。這次新加的 `"t_ci_wait" not in names and "t_slim_gate" not in names`(`test_lumos.py:44227`)是照抄本函式自己既有的慣例,不是新寫法。

不對齊共 1 條,其中 major 1 條。
