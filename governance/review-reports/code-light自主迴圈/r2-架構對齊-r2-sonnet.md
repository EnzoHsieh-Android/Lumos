severity: clean

## 三問逐答

### Q1:`_keys_mentioned` 放在 lumos、執行器用 `_load_lumos_inproc()` 拿——跟本檔先前的 `_DOCS_ONLY_PATHS` 一不一致?

一致。r2-snapshot.patch 裡 `scripts/test_lumos.py` 新增的寫法是:
引句:「    _mentioned = _load_lumos_inproc()._keys_mentioned   # 整字比對只有一份定義(在 lumos;推送前掛鉤那邊也用它)」

跟同檔既有的 `_DOCS_ONLY_PATHS` 讀法同一套模板——`scripts/test_lumos.py:91` `paths = tuple(_load_lumos_inproc()._DOCS_ONLY_PATHS)`,連同一行上方 `scripts/test_lumos.py:31-33` 的註解都直接點名這是本檔的慣例(「這個檔的慣例是 `_load_lumos_inproc()` 讀活的常數,不抄第二份」)。兩處都是:常數/函式的單一定義留在 `scripts/lumos`,`test_lumos.py` 透過 `_load_lumos_inproc()`(定義於 `scripts/test_lumos.py:225`,inproc import 活模組,不 subprocess 也不抄副本)取用,不另刻一份。沒有第二種做法、沒有跨層直呼、沒有繞過既有入口。

### Q2:`_autoloop_full_for` 寫死 `scripts/test_autonomous_loop.py` 路徑——lumos 裡其他地方怎麼指這支檔?

一致(全 repo 都用字面路徑字串,沒有另一支「找這支檔」的工具可借)。`scripts/lumos:22377` `f = Path(repo_root) / "scripts" / "test_autonomous_loop.py"`。對照:
- `scripts/lumos:16599`(`ANCHOR_FILES` 清單)本來就把它寫成字面字串 `"scripts/test_autonomous_loop.py"`,用法是 `f = repo_root / rel`(`scripts/lumos:18078`),跟新函式同一種「相對路徑字面值 + repo_root 拼」寫法,只是把單一字串換成兩段 `/` 而已(等價,屬風格差異,不判)。
- `scripts/hooks/pre-push:359,362`(既有、非這批改動)一樣是 `"$REPO_ROOT/scripts/test_autonomous_loop.py"` 字面路徑。
- `scripts/test_lumos.py:9202,15676,15739,33844` 等多處也都是字面字串 `"scripts/test_autonomous_loop.py"`。

沒有任何一處是透過某個「找這支檔」的共用函式取得路徑,所以 `_autoloop_full_for` 自己拼字面路徑不是另立一套、不是繞過既有入口——本來就沒有那個入口可用,現有做法本身就是逐處寫死。

### Q3:pitfalls JSON 欄位命名 `autoloop_full` 跟既有 `suite`/`suite_graph`/`light_ok` 一致嗎?掛鉤讀 JSON 用 `grep -q '"x": *true'` 跟既有讀法一致嗎?

讀法:一致。`scripts/hooks/pre-push:255` 新增:
引句:「    printf '%s' "$pf_json" | grep -q '"autoloop_full": *true' && _AUTOLOOP_FULL=1」
跟同檔既有三種布林欄位讀法同一個模板——`scripts/hooks/pre-push:223` `grep -q '"tier": *"high"'`、`:227` `grep -q '"suite_graph": *true'`、`:251` `grep -q '"light_ok": *true'`——都是 `printf '%s' "$pf_json" | grep -q '"<欄位>": *<值>'`,沒有另開一套解法(唯一例外是 `affected_keys` 那個陣列欄位改用 `$PY -c 'import json...'` 解析,那是既有分工:布林用 grep、非純量值用真 JSON parse,新欄位是布林,跟著 grep 這條路走是對的)。

命名:欄位命名本身不算「第二種做法/跨層直呼/繞過入口」這類 major 範疇(這批判準明講風格不列),但附帶記一句供參考:`suite`/`suite_reason`/`suite_graph`(`scripts/lumos:22529` 同一個 dict)三者是 `_test_suite_for_range()` 回傳、描述「lumos 自己這次要跑 docs 還是 full」;`light_ok` 描述「small-change 閘擴散可信不可信」;新 `autoloop_full` 描述的是第三件事(自主迴圈那支測試自己要不要整支跑),語意上跟前三者本來就不是同一組判斷,不掛 `suite_` 前綴、也沒有沿用 `_ok` 後綴,是合理的第三類命名,不構成「同一組欄位卻取了不一致的名字」。

## 不對齊共 0 條,其中 major 0 條

## 驗過的路徑

- Q1:對照 `scripts/test_lumos.py:31-33`(_DOCS_ONLY_PATHS 慣例註解)、`:71`、`:91`、`:225`(`_load_lumos_inproc` 定義)。
- Q2:對照 `scripts/lumos:16597-16599`(ANCHOR_FILES)、`:18077-18078`(cmd_anchor_approve 取路徑寫法)、`:22377`(`_autoloop_full_for`);`scripts/hooks/pre-push:359,362`;`scripts/test_lumos.py:9202,15676,15739,33840-33844,35718`(既有多處字面路徑,全 repo grep `test_autonomous_loop` 逐一過)。
- Q3:對照 `scripts/hooks/pre-push:221-255`(pf_json 全部讀法逐行過一次:tier/suite/suite_graph/light_ok/autoloop_full/stack_questions_applicable);`scripts/lumos:22300-22380`(`_test_suite_for_range`、`_keys_mentioned`、`_autoloop_full_for` 三個函式與回傳 dict 的欄位組成)、`:22517-22530`、`:22584-22597`(兩處組裝輸出 dict 的位置,r2-delta.patch 對這兩處的改動一致)。
- 額外核過:全 repo grep `(?<![A-Za-z0-9_])` 這個整字比對正則的寫法有沒有第二份沒被收編——`scripts/lumos:25864` 另有一處(呼叫者反查/lens 功能,跟測試選取無關、不在本次改動範圍內),`_keys_mentioned` 註解只宣稱是「測試執行器 --suite keys 與推送前自主迴圈判斷」的唯一定義,沒有誇大成全 repo 唯一,不算失實。
