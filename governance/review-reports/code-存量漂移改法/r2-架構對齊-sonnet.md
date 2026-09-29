severity: minor

## 問 1 分層與依賴方向
對齊。新函式都放在 drift 區段(`_drift_jsonl_parse` 在「表態」節,`_drift_sh`/`_drift_phys`/`_drift_deps`/`_drift_c4_yaml_err` 在 fix 節),命名前綴 `_drift_` 與同區段鄰居一致。依賴方向:drift 往下呼叫 guard(`_guard_raw_git_path`、`_guard_pass_home`、`_guard_formal_line`),guard 區段沒有反過來呼叫 drift——`awk NR<26000 && /_drift_/` 只命中 doctor 與 history(1267、2224、2262、4937),都是上層消費者,不是 guard。
file: `scripts/lumos:12244`(guard 註解「drift 往下呼叫 guard,guard 不呼叫 drift」與實況相符)
file: `scripts/lumos:26361`
修復帳寫入沿用 `_jsonl_append_verified`(`scripts/lumos:27578`),沒另造寫帳原語。
`.lumos/lint-waivers.json` 新增項的欄位(key/rule 空/file 空/reason/by/ts)與 `cmd_lint_waive` 走 `_lint_waivers_add(repo_root, key, "", "", note, who)` 產生的形狀一致,理由字串也是 lint-waive 的 --note 寫法。
file: `scripts/lumos:21674`

## 問 2 命名與錯誤處理
對齊。`_drift_placeholder_err`/`_drift_c4_yaml_err`/`_drift_ack_args_err` 都是「回錯誤字串或 None」,由呼叫端印「擋下:…」到 stderr 並 return 2,與 `cmd_drift_ack` 及其他 cmd 的擋下慣例相同。`_drift_c4_yaml_err` 直接用既有 `_yaml_plain_ok`,沒有另寫一套判定。
file: `scripts/lumos:14642`
file: `scripts/lumos:27447`(擋下訊息格式、rc 2)

## 問 3 第二種做法
沒有跨層直呼,沒有新增依賴;有兩處「鄰居已有近似工具、又長一支」,結構對,列 minor。

## F1 `_drift_sh` 與既有 `_sh_quote` 同功能並存,且與內聯 shlex.quote 是第三種寫法
severity: minor
blocking: 否
引句:「不直接全部 shlex.quote:它把中文也當危險字元,圖譜裡幾乎每條提示都會被包上引號。」
file: `scripts/lumos:34530`(`_sh_quote`,docstring 寫「路徑含空白或中文時照樣貼得上去」,即既有做法是全部 shlex.quote)
file: `scripts/lumos:1037`、`scripts/lumos:11229`、`scripts/lumos:19421`(其他印給人照貼的指令都是內聯 `import shlex as _shlex` 後直接 `_shlex.quote`)
1. 專案原本的「照貼指令加引號」= 一律 shlex.quote(內聯或 `_sh_quote`);`_drift_sh` 新增白名單(含 CJK 原樣、其餘才 quote)的第二種規則。
2. 理由(中文不想被包引號)在 docstring 交代了,但同專案別處照貼的中文路徑都被包引號,沒有先統一。⚠ 判為可接受的局部差異還是該收斂成同一支,取決於是否要讓 `_sh_quote` 也改;未在此判。

## F2 `_drift_phys` 是逐層 NFC 比對 iterdir 的第三份寫法
severity: minor
blocking: 否
引句:「逐層找 NFC 相同的名字,找不到就回原路徑讓呼叫端照常報錯。」
file: `scripts/lumos:9788`(`{nfc(q.name): q.name for q in proj.iterdir()}`)
file: `scripts/lumos:9885`(`any(nfc(q.name) == want for q in parent.iterdir())`)
file: `scripts/lumos:12167`(`_guard_raw_git_path`,對 git ls-files 比 NFC,不同域)
1. `_guard_raw_git_path` 是 git 側、`_drift_phys` 是檔案系統側,不是同一功能,不算重複。
2. 但檔案系統側「以 NFC 比 iterdir 名稱」在 9788、9885 已有兩份內聯版本,`_drift_phys` 是第三份(逐層版),沒有共用。

## 其他點名項目
- `_drift_one_line`、`_drift_placeholder_err`、`_drift_deps`、`_drift_ack_args_err`:檔內沒有同功能既有函式(`_FOLD_RO_PLACEHOLDER_RE` 在 `scripts/lumos:31429` 是另一種用途的正則),不列。
- `_drift_jsonl_parse`:專案內讀 jsonl 多為內聯 `splitlines()` + `json.loads`(`scripts/lumos:6148`、`scripts/lumos:7828`、`scripts/lumos:9803`),沒有既有共用讀帳函式可對照;此函式改用只在 `\n` 切行並在 docstring 說明原因,不算第二種做法。

不對齊共 2 條,其中 major 0 條
最高等級:minor
