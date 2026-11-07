severity: major

三問都以 patch 與 `block-fullsuite` 工作樹的既有檔對照。分層、錯誤處理跟鄰居一致;不一致處集中在家目錄寫檔、理由判法與子程序環境,共 5 條。沒有實跑測試,全是讀碼比對。

## 問 1:分層與依賴方向

`main` 這段跟既有進入點一致,掛鉤函式的放法也一致,本問沒有不對齊。

- **`main` 的位置**:新判斷接在參數驗證之後、`_fanout_wanted` 與 `_isolate_environment()` 之前(patch 的 `_chat_full_suite_block(_args, _chat_snap)` 那段)。這跟既有「在唯一進入點清外部注入」的先例同層。先例是 `scripts/test_lumos.py:49351` 的 `_isolate_environment` 與 `main` 裡清 `GIT_*`、`PYTHON_COLORS=0` 那兩段。
- **用的工具一致**:`import os as _os_env` 的別名沿用,擋下走 `print(..., file=sys.stderr); return 2`,跟同函式的參數錯誤一樣。
- **分層方向對**:判斷只依賴 `args` 與環境快照,沒有跨層直呼 `scripts/lumos`。
- **掛鉤函式**:`pp_red_names`、`pp_red_hint`、`pp_red_next` 用 `pp_` 前綴、`$1` 收 log 路徑、`local _x` 命名,在 `{ ... } >&2` 紅燈區塊裡被呼叫。這跟 `scripts/hooks/pre-push:877` 的 `pp_keep_log` 與 `:130` 的 `pp_q` 同款;`pp_red_next` 也沿用 `pp_q "$PY"` 的既有寫法。

## 問 2:命名與錯誤處理

結構對,有兩處小不一致。

**finding 1**
severity: minor
blocking: 否
- `_CHAT_GUARD_ENV` 與 `_chat_full_suite_block` 把 `LUMOS_FANOUT_CHILD` 寫成字面字串,但同檔已有 `_FANOUT_CHILD_ENV` 這個常數。鄰居 `_fanout_wanted` 就是讀那個常數。同一個標記名字現在有兩處來源。
- 引句:「_CHAT_GUARD_ENV = ("CLAUDECODE", "LUMOS_PUSH_ATTEMPT", "LUMOS_FANOUT_CHILD", "LUMOS_ALLOW_FULL_SUITE")」
- 既有佐證:`scripts/test_lumos.py:49470`(`_FANOUT_CHILD_ENV = "LUMOS_FANOUT_CHILD"`),`:49524` 的 `_fanout_wanted` 讀它。

**finding 2**
severity: minor
blocking: 否
- 新函式插在 `pp_keep_log` 與它上面的說明註解之間。原註解「測試紅時把要給人看的 log 搬到暫存資料夾外…」現在貼在 `pp_red_names` 上方的新註解前面。`pp_keep_log` 本身沒了註解。鄰居的慣例是說明緊貼函式。
- 引句:「# ★紅燈提示逐支給 -k★(Projects/對話裡不准跑全套測試_計劃 做 5):對話裡不帶篩選條件會被執行器擋,」
- 既有佐證:`scripts/hooks/pre-push:877`(`pp_keep_log` 與它的註解原本相鄰)。

其餘錯誤處理一致:擋下訊息以「擋下:」開頭、印 stderr、回 2,跟既有參數錯誤一樣。測試名 `t_runner_*`、`t_prepush_*` 與 docstring 以 `[[Projects/…]]` 開頭的寫法也沒問題。

## 問 3:第二種做法

計劃寫的兩個理由,我查證如下:

- **「測試總檔單獨裝進消費專案時不保證有 `scripts/lumos`」不成立。**
  - `scripts/test_lumos.py:240` 的 `_load_lumos_inproc` 在檔內被呼叫 868 次。
  - 同檔 `:71`、`:91`、`:104` 在 runner 層、`--suite docs` 選測試時就會載入它。測試總檔本來就依賴 `GRAPHCTL`。
- **「執行器一啟動就要判,載入那支大檔要多花時間」部分成立。** 目前只有 `--suite docs` 在選測試時才載入它。這個理由撐得起「啟動路徑不 import」,撐不起「連信任檢查都不要」。

**finding 3**
severity: major
blocking: 是
- ⚠ 家目錄寫檔另起了一套做法。
- 新的 `_chat_guard_log` 直接 `Path.home()/.cache/lumos/full-suite-guard` 加 `mkdir(parents=True)`,再用普通 `open(..., "a")` 追加。
- 既有每個寫 `~/.cache/lumos` 的地方都先過 `_mkdir_trusted_under_home` 與 `_trusted_private_dir`,檔案用 `O_NOFOLLOW`、`O_NONBLOCK`、0600 開,並確認是自己的一般檔。這樣 `~/.cache/lumos` 被換成別人的 symlink 時才擋得住。
- 新寫法兩樣都沒有,會跟著 symlink 寫到別處,也不收斂。
- 兩個理由都不撐這個差異:消費專案那半不成立;啟動速度那半頂多支持「不 import 整支 lumos」,但不必連信任檢查都不要。
- 引句:「        d = _Pg.home() / ".cache" / "lumos" / "full-suite-guard"」
- 既有佐證:`scripts/lumos:62016`(`_drift_m1_ledger_miss`,同樣是「追加一行 jsonl」的用途),`:70037` 的 `_trusted_private_dir`,`:70117` 的 `_mkdir_trusted_under_home`。

**finding 4**
severity: minor
blocking: 否
- ⚠ 逃生門理由判法另抄了一份,沒有雙邊一致的守衛。
- 規則字面跟 `scripts/lumos:41861` 的 `lint-waive --note` 一樣:去空白至少 10 字,加上 `[^\W_]` 實字。計劃的依據表也只寫「既有程式」。
- 計劃對「不借寫入函式」寫了理由,對「另抄判法」沒寫。
- 結構上不是跨層直呼,所以標 minor。真要降到零,可以加一支測試用 `_load_lumos_inproc` 對同一組輸入比對兩邊的結果。
- 引句:「    return bool(reason) and len(_re_r.sub(r"\s", "", reason)) >= 10 and bool(_re_r.search(r"[^\W_]", reason))」
- 既有佐證:`scripts/lumos:41861`。

**finding 5**
severity: minor
blocking: 否
- ⚠ 子程序測試的環境組法與鄰居不同。
- 既有執行器子程序測試走 `_fan_box` 與 `_fan_run`:把執行器複製進沙盒,環境從 `os.environ` 扣掉兩個標記。
- 新的 `t_runner_chat_full_suite_block_process` 另手組 `env` 字典,直接對真檔開子程序。
- 計劃有寫理由:要從頭組環境,免得繼承推送前閘與切片標記。這個理由成立,所以不是 major。但它是第二種組法,沒有共用 helper。
- 引句:「    env = {"PATH": _o.environ.get("PATH", ""), "HOME": str(home), "TMPDIR": str(tmp), "CLAUDECODE": "1"}」
- 既有佐證:`scripts/test_lumos.py:30763`(`_fan_box`)、`:30780`(`_fan_run`)。

從掛鉤切函式出來測:新測試用 `re.finditer` 切出三個函式後在 bash 真跑,沒有另抄一份。這跟鄰居從掛鉤原文取字串的做法同向(`scripts/test_lumos.py:21188`、`:53080`、`:64695`)。唯一差別是沒呼叫 `_need_src`,不列條。

不對齊共 5 條,其中 major 1 條
