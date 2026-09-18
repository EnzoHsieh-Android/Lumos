severity: major

## F1 「governance/」被整個列進純文件白名單,連 anchor-baseline.json 自己的防竄改測試都被跳過

severity: major
blocking: yes

觀察到什麼:`_DOCS_ONLY_PATHS` 把整個 `governance/` 目錄前綴(配 `.json`/`.jsonl` 副檔名)都算「純文件」。但 `governance/` 底下不是只有帳本/卷證這種純資料——`governance/anchor-baseline.json` 是「裁判防竄改」的簽名檔本身(scripts/lumos `_ANCHOR_BASELINE_REL`,被 `anchor verify`/doctor Check ⑨ 讀進去跟磁碟上的 hook 檔案雜湊比對)。只要一次推送只動這一支檔,`_test_suite_for_range` 判定的路徑就是「非文件清單全空 → suite: docs」,pre-push 與 CI 都只跑文件子集,不跑全套。

引句:「                    "docs/", "assets/", "diagrams/", "governance/")」

引句:「# 兩層白名單都要過才算純文件:★路徑★在 _DOCS_ONLY_PATHS 裡(不在的——scripts/、skills/、.github/、slim/…——一律跑全套;」

怎麼重現(輸入→輸出):
1. 實際在本機跑過(唯讀查證,沒改任何東西):`python3 scripts/test_lumos.py --list --suite docs | grep -i anchor`,結果只有 `t_prepush_blocks_uncommitted_anchor_baseline` 一支;真正驗「baseline 內容跟碼一致/竄改會被抓」的 `t_anchor`(approve/verify/改檔判紅)與 `t_anchor_files_match_baseline`(★ANCHOR_FILES 與 baseline 鍵集合必須相等★)、`t_anchor_covers_all_auto_running_hooks` 全部**不在**文件子集裡(全套是 1021 支、文件子集是 209 支)。
2. 攻擊路徑四件:
   - 不可信輸入:一筆只改 `governance/anchor-baseline.json` 的推送(例如把某支 hook 的錨點鍵整個刪掉,或把雜湊改成未來要換上的惡意版本的雜湊)。
   - 誰能送:任何有推送權限、繞不過(或還沒被)人審的分支(這條規則本身就是唯一的自動閘,CLAUDE.md 定義的兩道自動防線就是 pre-push 與 CI)。
   - 機制怎麼處理:`_test_suite_for_range` 只看路徑+副檔名(不看內容、不看這支 json 實際上是不是「安全機制的一部分」),整份非文件清單為空 → `suite=docs`;pre-push 與 CI 兩邊都改成只跑 `--suite docs`(209 支),完全跳過上面那三支測試。
   - 造成的後果:doctor Check ⑨(`add("anchor-baseline", ...)`,scripts/lumos ~17881-17897)本身也救不回來——它只逐一比對 baseline **裡面現有的鍵**跟磁碟雜湊,鍵被整支刪掉時,迴圈裡根本沒有這一項可比,不會判 degraded,只會印「N 個錨點,全符」(N 變小,沒人講)。整條防線裡唯一會抓「baseline 鍵集合是不是被動過手腳」的,就是被跳過的那支 `t_anchor_files_match_baseline`。這支推送本身 pre-push 綠、CI 綠,完全沒有任何訊號。之後另一次推送真的去改那支 hook 檔的內容(那次因為動到 `scripts/hooks/...` 不是文件,`suite=full`,t_anchor_files_match_baseline 會跑)——但如果第一次那筆已經把鍵刪掉或把雜湊換成新版本的雜湊,`anchor verify`/doctor 對那支檔根本不再檢查(鍵沒了)或直接比對成功(雜湊已經先量好了),兩層防線在關鍵那一步都失效。

為什麼是 bug 不是風格:這不是「measured 但偏好不同」的問題——`governance/` 這個路徑前綴同時裝著兩種東西:①純粹紀錄用的帳本/卷證(rel-cascade、review-reports、backlog-archive.jsonl,這些真的不需要測)、②functionally 被讀進去當設定/防線的檔案(anchor-baseline.json,甚至 `governance/code-loop/<branch>.json` 這種代碼審過閘留痕)。這批改動把整個目錄當同一類對待,直接讓「防竄改」機制自己最關鍵的一致性測試,在改到它自己時反而被跳過——這正是原始碼裡自己講的「fail-safe 是多跑不是少跑」的設計初衷被自己的白名單違反的具體案例,而且是可以機械重現的(不需要猜測,上面 `--list --suite docs` 的結果就是證據)。

file: `scripts/lumos:16609`(`_ANCHOR_BASELINE_REL = "governance/anchor-baseline.json"`)
file: `scripts/lumos:17881-17897`(doctor Check ⑨,只逐鍵比對、不驗鍵集合)
file: `scripts/test_lumos.py:32030`(`t_anchor_files_match_baseline`,唯一驗鍵集合一致的測試,已機械確認被文件子集排除)


## F2 (推論)`governance/code-loop/<branch>.json` 代碼審留痕同樣落在純文件白名單裡

severity: minor
blocking: no

觀察到什麼:代碼審過閘後的留痕檔 `governance/code-loop/<branch>.json`(scripts/lumos 有 `_write governance/code-loop/<branch>.json` 一類邏輯)同樣是 `governance/` 前綴 + `.json`,單獨改它也會被算成「純文件」而跳過全套。

引句:「                    "docs/", "assets/", "diagrams/", "governance/")」

攻擊路徑(推論,沒有實際重現,只是同一形狀的延伸):這支檔案本身不是拿來擋東西用的(pre-push 讀留痕主要是 `bound_tests_gate`/`spec-gate`那條路,不是靠 test suite 去驗留痕真偽),真正防竄改的是「留痕綁 sha」與 pre-push 另外會查的 marker 檔存不存在、有沒有對應的 canary 記帳——這套本來就不是靠 test_lumos.py 全套去驗證的機制,單獨改這支檔案本來就不會動到全套裡的哪支測試(不像 F1 那樣有一支現成的、被跳過的專門測試)。標成推論、severity minor:沒有像 F1 那樣找到一支「本來會抓、現在被跳過」的具體測試,只是同一個白名單形狀下同一類檔案,寫出來給下一輪參考,不構成本輪要擋的理由。


## F3 已看,無:`--keys` 值的字元集合(argparse/bash 誤讀)

severity: minor
blocking: no

已看的路徑:`_KEY_OK_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{2,}")`(scripts/lumos)要求關鍵字第一個字元是 `[A-Za-z0-9_]`,不能是 `-` 或 `.` 開頭;之後每個候選字串都要整串符合 `_KEY_OK_RE.fullmatch`(`_add` 函式裡),不符合的直接丟掉不進清單。pre-push 端把 `_SUITE_KEYS` 用逗號接起來、當成**單一個** `--keys` 的值傳給執行器(`_keys_args=(--suite keys --keys "$_SUITE_KEYS")`,有加雙引號),不會被 shell 斷詞成多個 argv;執行器那邊 `--keys` 的值本身是不是以 `-` 開頭不影響 argparse 解析(`--keys` 後面吃一個值,不管值裡有什麼字元,argparse 都當成該旗標的值,不會被重新解析成旗標)——`_KEY_OK_RE` 擋掉 `-` 開頭反而是多一層保險而非必要,但也沒有反效果。`_keys_suite_select` 裡用 `_re.escape(k)` 組正則,`.`/`-` 這種正則特殊字元也不會被當成正則語法誤讀。三個環節(shell 斷詞、argparse 解析、正則組裝)都查過,沒找到可利用的洞。


## F4 已看,無:TMPDIR / mktemp -d 權限

severity: minor
blocking: no

`_PP_TMP="$(mktemp -d "${TMPDIR:-/tmp}/lumos-prepush-XXXXXX" ...)"`——`mktemp -d` 預設建出來的目錄權限是 0700(僅擁有者),檔名尾碼 XXXXXX 由 mktemp 亂數展開、原子建立,不是先猜測路徑再建立,沒有典型的 tmp 競態(TOCTOU/符號連結攻擊)空間。建不出來會 `exit 1` 擋下並講清楚(不是靜默退回根目錄),這正是這批改動自己修正的項目(r2 邊界席原本抓到的洞)。TMPDIR 本身雖然由推送者環境給,但推送者本來就是在自己機器上跑 pre-push,對自己機器的 TMPDIR 有多大影響力,不構成新的攻擊面(同一個人本來就能對自己的推送做任何事)。


## F5 已看,無:`LUMOS_TEST_SHARDS` 非數字改串行是不是反向關閘

severity: minor
blocking: no

`_shards` 校驗:`[[ "$_shards" =~ ^[0-9]+$ && "$_shards" -ge 1 ]] || _shards=1` 只決定**要不要切片**(平行度),不影響 `_suite_mode`/`_suite_args`(docs/keys/full)的判定——那組判定完全由 `_SUITE_SEEN`/`_SUITE_FULL`/`_SUITE_LIGHT`(來自 pitfalls 與 spec-gate 的結果)決定,跟 `LUMOS_TEST_SHARDS` 是不同變數、不同計算路徑。`run_group` 在 `_shards<=1` 時只是把 `"$@"`(也就是已經決定好的 `--suite docs`/`--suite keys ...`/什麼都不帶=全套)串行跑一次,不會因為切片數異常就「偷偷跑得比原本判定的範圍還少」。用環境變數把片數關掉頂多是讓同一個範圍跑得比較慢(串行而非平行),不會讓不該省的全套變成子集。


## F6 已看,無:`.lumos/config.json` 的 `node_home.ignore` 讓程式檔不算程式檔

severity: minor
blocking: no

`.lumos/` 這個路徑不在 `_DOCS_ONLY_PATHS` 裡(白名單只有 `README.md`/`docs/`/`assets/`/`diagrams/`/`governance/` 這幾類),所以只要 `.lumos/config.json` 本身被改動,它自己就會落在 `non_docs` 清單裡,讓 `_test_suite_for_range` 直接判 `suite: full`。就算攻擊者不改 `.lumos/config.json`(用之前就已經在圖譜裡核准過的 ignore 設定),而是讓被忽略的那支「實際上有惡意行為」的檔案被判成非程式檔——這條路徑反而讓它在 `_test_suite_for_range` 的 `code` 清單裡消失,`light_ok = len(code) == len(non_docs)` 因此變假(該檔仍算在 `non_docs` 裡、但不算進 `code` 裡,兩邊長度對不上),`light_ok` 假就永遠進不了「light」分支,仍然強制跑全套。這條路徑檢查完是自我防禦(ignore 掉的檔反而更容易觸發全套),不是漏洞。


## F7 已看,無:`_PP_TMP` 暫存目錄清掉之前 log 內容(密鑰/個資)

severity: minor
blocking: no

`trap 'impact_done; rm -rf "$_PP_TMP"' EXIT INT TERM` 涵蓋正常結束、Ctrl-C(INT)、TERM 訊號;唯一涵蓋不到的是 SIGKILL(-9)——這是 shell trap 機制本身的天花板(任何用 trap 做清理的腳本都一樣),不是這批改動新引入的洞,而且就算被 SIGKILL 留下,目錄權限是 mktemp 預設的 0700(僅目前使用者可讀),裡面存的是 spec-gate 輸出與測試 log,不是密鑰本身;跟改動前(舊版把測試 log 放在 `mktemp -d`/`$_TESTS_LOG`)比,暴露面沒有變大。已看,無新增風險。


## 覆蓋範圍說明
逐類檢查(依派工詞六類):①不可信輸入→危險操作(F3/F4/F5/F6,已看無;F1/F2 屬這類但重點在「該跑的驗證被跳過」而非注入)②登入權限:改動不涉及任何認證/授權機制,已看,無適用面③密鑰個資:F7,已看無④加密傳輸:改動全在本機 shell/Python 執行與 GitHub Actions 內部檔案讀寫,沒有新的網路傳輸路徑,已看,無⑤執行邊界:F1(major,實測證據)、F2(推論,minor)——這是本輪真正的攻擊面,已詳細驗證⑥行動端:無,不適用。
