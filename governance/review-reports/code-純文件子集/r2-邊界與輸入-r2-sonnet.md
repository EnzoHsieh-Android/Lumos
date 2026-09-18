severity: blocker

## F1 LUMOS_TEST_SHARDS 給非數字值,推送前測試整段變成「跑了個寂寞」卻回報成功

severity: blocker
blocking: yes

觀察到什麼:`_run_group`(這輪新抽出來、docs/light/full 三條路共用的執行函式)用 `for _i in $(seq 1 "$_shards")` 決定要開幾個子行程,`$_shards` 直接來自使用者可設的環境變數 `LUMOS_TEST_SHARDS`(`_shards="${LUMOS_TEST_SHARDS:-4}"`,scripts/hooks/pre-push:371),全程沒有任何數字合法性檢查。只要這個值不是合法整數,`seq` 直接失敗、標準輸出是空的,`for` 迴圈連一次都不會跑,`_pids` 是空陣列,後面的 `for _p in "${_pids[@]}"; do ...; done` 自然也不執行,`_bad=0`、`_any3=0`,函式回傳 0——跟「全部測試都綠」回傳的碼一模一樣。

怎麼重現(輸入→錯誤輸出):把 `_run_group` 原封不動抽出來單獨跑,子行程故意寫成「一定失敗」(`python3 -c "import sys; sys.exit(1)"`),只把 `_shards` 設成 `"abc"`:

```
$ bash /tmp/repro_run_group.sh
seq: invalid floating point argument: abc
REAL_run_group_rc=0 (每個子行程本來都會回 1=有紅,但 _shards=abc 讓迴圈連跑都沒跑)
```

`$_sdir` 底下連一個 log 檔都沒生出來——不是「測試都過」,是根本沒有任何測試被執行,但函式回傳值跟「全綠」完全無法區分。對照呼叫端:

```
  _grc=0; _run_group s ${_suite_args+"${_suite_args[@]}"} || _grc=$?
  [[ "$_grc" -ne 0 ]] && _rc=1      # 文件子集/全套選中 0 支也算紅(執行器那邊本來就這樣判)
```

`_grc=0` 時 `_rc` 完全不會被設成 1,推送直接放行,畫面上只有「推送前先跑全部測試…」這句話、沒有任何「0 支」或「算不出片數」的警示——使用者會以為測試真的跑過且全綠。

為什麼是 bug 而不是風格:這條路直接破壞這支掛鉤唯一的存在理由(推送前先跑測試把關)。文件裡「`--suite {docs,keys}` … 選中 0 個測試——視為失敗」那條防線(scripts/test_lumos.py 的 rc3 設計)只防得住「子集挑不到測試」,防不住「殼層根本沒把執行器叫起來」這種更上游的失效——本函式是這輪新抽出來、給 docs/light/full 三條路共用的核心邏輯,任何一條路都會被這個輸入吃死。`LUMOS_TEST_SHARDS` 不是隱藏內部變數,`t_prepush_docs_and_light_run_subset` 自己就示範拿它當正常旗標用(`env["LUMOS_TEST_SHARDS"] = "2"`),打錯字(例如複製貼上多一個字、環境變數殘留舊值)就會觸發,而且觸發後**沒有任何錯誤訊息**,是最危險的那種靜默失效——比「跑不完全套」更糟的是「假裝跑完全套」。

引句:「for _i in $(seq 1 "$_shards"); do」
引句:「env = dict(_os.environ); env["GIT_DIR"] = str(d / ".git"); env["LUMOS_TEST_SHARDS"] = "2"; env.update(env_extra)」
file: `scripts/hooks/pre-push:371`(`_shards="${LUMOS_TEST_SHARDS:-4}"`,原始值來源)
file: `scripts/hooks/pre-push:407-419`(`_run_group` 完整定義)
file: `/tmp/repro_run_group.sh`(本次重現腳本,對 `_run_group` 的原樣抽取)

補充:`_shards=0` 在這台(macOS/BSD `seq`)不是空跑而是重複跑兩次全套(`seq 1 0` 印出 `1` 再 `0`);GNU `seq`(多數 CI/Linux 開發機用的版本)遇到 FIRST>LAST 預設印空,行為跟 `_shards=abc` 一樣是「靜默 0 支」——這點沒有 Linux 環境可驗,只列非數字（"abc"）那條已經在本機（BSD seq）100% 可重現的路徑當主證據。

---

## F2 `_PP_TMP` 的 mktemp 沒有防呆,壞在跟同檔其他暫存檔完全不同的紀律上

severity: major
blocking: yes

觀察到什麼:這輪把「本次推送所有暫存檔的家」統一成一個目錄 `_PP_TMP`,直接用結果賦值,沒有任何失敗檢查:

```
_PP_TMP="$(mktemp -d "${TMPDIR:-/tmp}/lumos-prepush-XXXXXX")"   # 本次推送所有暫存檔的家,離開時整個清(r1 併發席:逐檔 rm 在 exit 1 / Ctrl-C 那條路會漏)
```

同一支檔案裡,舊有的 `impact_once` 對「同一種 mktemp 可能失敗」是有防呆的:`local _f; _f="$(mktemp "${TMPDIR:-/tmp}/lumos-prepush-impact-XXXXXX" 2>/dev/null || true)"` 接著 `[ -n "$_f" ] || return 0`——失敗就悄悄跳過,不留爛攤子。這輪新加的 `_PP_TMP` 沒有比照這個既有慣例,`set -u` 開著但沒有 `set -e`,`mktemp -d` 失敗時 `_PP_TMP` 直接變成空字串,腳本照跑。

怎麼重現(輸入→錯誤輸出):`TMPDIR` 指到一個唯讀目錄:

```
$ mkdir -p /tmp/ro-test && chmod 000 /tmp/ro-test
$ TMPDIR=/tmp/ro-test bash -c '_PP_TMP="$(mktemp -d "${TMPDIR:-/tmp}/lumos-prepush-XXXXXX")"; echo "rc=$? PP_TMP=[$_PP_TMP]"'
mktemp: mkdtemp failed on /tmp/ro-test/lumos-prepush-rnWvjn: Permission denied
rc=1 PP_TMP=[]
```

`_PP_TMP` 空掉之後,後面每一處 `"$_PP_TMP/…"` 全部變成指到檔案系統根目錄:

```
$ bash -c '_PP_TMP=""; mkdir -p "$_PP_TMP/shards"; echo "mkdir rc=$?"; : > "$_PP_TMP/sg-123.log"; echo "touch rc=$?"'
mkdir: /shards: Read-only file system
mkdir rc=1
bash: line 1: /shards: Read-only file system
touch rc=1
```

`_sdir="$_PP_TMP/shards"; mkdir -p "$_sdir"` 建不出目錄,後面每個子行程的 `> "$_sdir/$_pfx$_i.log"` 重導向全部失敗——但因為 bash 在重導向失敗時仍會記錄一個 PID、`wait` 回非 0 非 3(驗過是 1),`_bad=1`,`_run_group` 會回 1,`_rc=1`,最終還是會擋下推送(方向安全),但「擋下」訊息完全交代不出原因:`cat "$_sdir"/*.log > "$_TESTS_LOG"` 因為 `$_sdir`(`/shards`)根本不存在,glob 展不開、`$_TESTS_LOG` 是空檔;`grep -h "✗ " "$_TESTS_LOG"` 自然一支都列不出來。使用者看到的是「擋下:test_lumos.py 有紅,有測試沒過」+空白的失敗清單+一個指向空檔的路徑,完全查不出真正原因(是 TMPDIR 壞掉,不是測試真的紅)。

為什麼是 bug 而不是風格:同一支腳本裡,原本的紀律是「暫存檔失敗要防呆、要 fail-safe 講清楚」(impact_once 就是示範),這次把所有暫存檔集中到一個新變數卻沒延用這個紀律,是這輪重構時漏掉的邊界情況——不是我個人偏好的寫法問題,是「壞在哪裡使用者查不出來」的診斷斷裂,直接違反這支腳本自己的設計原則(擋下時要讓人看得懂為什麼)。

引句:「_PP_TMP="$(mktemp -d "${TMPDIR:-/tmp}/lumos-prepush-XXXXXX")"   # 本次推送所有暫存檔的家,離開時整個清(r1 併發席:逐檔 rm 在 exit 1 / Ctrl-C 那條路會漏)」
file: `scripts/hooks/pre-push:62`(`_PP_TMP` 賦值,無防呆)
file: `scripts/hooks/pre-push:49`(`impact_once` 裡對照組的防呆寫法)
file: `scripts/hooks/pre-push:402`(`_sdir="$_PP_TMP/shards"` 之後串聯崩壞的起點)

---

## F3 `--keys` 的值一旦剛好等於既有旗標字面(如 `-x`),整趟推送前測試被 argparse 吃掉、擋下訊息看不出真正原因

severity: major
blocking: yes

觀察到什麼:`affected_keys` 會把改到的程式檔的「檔名去副檔名」也當關鍵字塞進去(`_affected_test_keys` 的 `for f in code_files: ... _add(b.rsplit(".", 1)[0] ...)`),`_KEY_OK_RE = re.compile(r"[A-Za-z0-9_.-]{3,}")` 允許開頭是 `-` 的字串通過(字元類最後的 `-` 是字面連字號,對開頭位置沒有限制)。如果改到的程式檔恰好叫 `-x.py`(或任何跟 test_lumos.py 既有短旗標同名的檔名,如 `-k.py`),`_SUITE_KEYS` 就會是 `-x`,pre-push 把它整個丟給 `--keys "$_SUITE_KEYS"`。而 test_lumos.py 本來就定義了 `_p.add_argument("-x", "--exitfirst", action="store_true", ...)`——`--keys` 期待「下一個 token 當它的值」,但 argparse 認出 `-x` 是已註冊的旗標字面,拒絕把它當成 `--keys` 的值。

怎麼重現(輸入→錯誤輸出):

```
$ python3 scripts/test_lumos.py --list --suite keys --keys "-x"
usage: test_lumos.py [-h] [-k KEYWORD] [--list] [--keep-tmp] [-x] [--ff]
                     [--seed N] [--shard 第幾片/共幾片] [--json-summary 檔案]
                     [--suite {docs,keys}] [--keys 名字,名字]
                     [關鍵字]
test_lumos.py: error: argument --keys: expected one argument
(退出碼 2)
```

在 `_run_group` 裡,rc=2 不是 0 也不是 3,落進 `_bad=1` 那格,跟「真的有測試紅了」用同一個分支處理;呼叫端 `_krc=1`(非 0 非 3)→ `_rc=1` → 印「擋下:test_lumos.py 有紅,有測試沒過。紅的是這幾支:」再 `grep -h "✗ " "$_TESTS_LOG"`——但這份 log 裡裝的是 argparse 的 usage 說明,不會有任何一行 `✗ `,清單印出來是空的。使用者只會看到「有測試沒過」卻一支測試名字都看不到,得自己去翻 `$_TESTS_LOG` 才挖得出真正原因是「你的檔名撞到 -x 這個既有旗標」。

為什麼是 bug 而不是風格:這正是本輪要驗的「`--keys` 值含 `-` 開頭名字會被執行器當旗標」那個情境,而且是可以百分之百重現、非虛構的路徑(`-x`/`-k` 都是 test_lumos.py 真實定義過的短旗標)。`_KEY_OK_RE` 只管字元集合,完全沒管「這個 key 會不會剛好撞上執行器自己的旗標字面」,這是新功能(`--keys`/`affected_keys`)自己的輸入沒有跟它要餵給的下游(argparse)的既有介面做交叉檢查,屬於這輪新東西自己的邊界漏洞，不是外部環境問題。方向上還是會擋下推送(不會放過未驗證的程式碼),但診斷斷裂跟 F2 一樣——「有測試沒過」卻列不出任何測試名字,違反這支腳本自己反覆強調的「紅的時候要能查得出是哪支」的紀律(CI 那段特別寫了「不然只看得到『有片紅了』」)。

引句:「_p.add_argument("--keys", default=None, metavar="名字,名字",」
引句:「_p.add_argument("-x", "--exitfirst", action="store_true",」
file: `scripts/test_lumos.py`(`_KEY_OK_RE = re.compile(r"[A-Za-z0-9_.-]{3,}")`,允許 `-` 開頭)
file: `scripts/hooks/pre-push`(`_keys_args=(--suite keys --keys "$_SUITE_KEYS")` 那段,把未做旗標交叉檢查的字串直接傳給執行器)

---

## 驗過但沒發現問題的路徑(避免被誤判成漏查)

- `_docs_only_file` 對 `./`、`//`、大寫目錄(`Docs/`)：路徑一律來自 `git diff --name-only -z --no-renames` 的輸出,git 本身就會正規化(不會有 `./` 前綴、不會有重複斜線),而大小寫不同的目錄(如 `Docs/`)因為是逐字元比對 `path.startswith(w)`,不會被誤判成 `docs/`——後果是被歸類成「不是純文件」→ 退回全套,方向是保守（多跑不是少跑），不是安全漏洞。
- CI `sed -n 2p` 對 `suite_reason` 為空字串:實測 `suite_reason=""` 時 `sed -n 2p` 正確印出空字串,`why` 變數不會錯位或吃到下一行;而且 `_test_suite_for_range` 目前每個分支的 `reason` 都是非空字面字串,這個情境在現有程式碼路徑下也造不出來。
- `123.py` 這種純數字檔名:`_KEY_OK_RE` 會放行,但 `_keys_suite_select` 有「單一關鍵字選中超過三成測試就整個丟掉」的機制(`cap=0.3`),即使 `123` 這種短數字在測試原始碼裡到處出現,最壞也就是被丟掉印警告,不會造成漏跑或誤判成功。
- `_helper_sources_in` 對 `obj.foo(`、`print(` 誤抓:regex `\b(_?[a-z][a-z0-9_]*)\s*\(` 確實會把 `obj.foo(` 的 `foo` 抓出來(`.` 是非字元,`\b` 在它與 `f` 之間成立),如果模組剛好有一個同名的頂層函式會被誤當成呼叫到的輔助函式;但這只會讓某支測試「多算」一份輔助函式原始碼去比對文件路徑字樣,最壞結果是把該測試多算進文件子集(過度收錄,方向安全,不是漏測)。`print(`不會誤抓,因為 `globals().get("print")` 拿不到本模組定義的 callable。
