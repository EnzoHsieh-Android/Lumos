severity: minor

三問都答完,結論是結構沒走偏:沒有跨層直呼,也沒有新增第二份引號工具。有兩條命名或寫法上的小不一致。

**第 1 問:分層與依賴方向,跟鄰居一樣。**
- 新的重查指令放在掛鉤這一層。各閘把指令當 `pp_record_block` 的第 4 個參數交進去,擋下彙總之後由掛鉤自己印。
- 這個形狀跟既有的「擋不擋只看記憶體純量」一致:`_PP_BLOCKED`、`_PP_NBLK` 是純量,新增的 `_PP_FIRST_NEXT` 也是純量,而且沿用原有的 `${4:-}` 預設值寫法。
- 指令字串在掛鉤內組好,不向 lumos 要。這跟 `pp_cl_reason`(`scripts/hooks/pre-push:153`)寫明的「掛鉤要能配舊版 lumos 跑,所以不向 lumos 要」同一路線。
- 在 `scripts/lumos`,新增的作廢過濾放在既有函式裡,沒有新增呼叫層。
- 測試擴充既有的 `_ppc_run`(`scripts/test_lumos.py:82211`),新增參數 `hook_argv=()` 不影響舊呼叫。假 lumos 的新環境變數 `FAKE_PY_PATH`、`FAKE_PUSH_RANGE`、`FAKE_PITFALLS_JSON` 都照 `FAKE_*` 慣例。
引句:「[[ "$_PP_NBLK" -gt 1 ]] || _PP_FIRST_NEXT="${4:-}"」

**第 2 問:命名與錯誤處理,有兩條小不一致(Z1、Z2)。**
- 命名大多對齊:`pp_` 前綴、`_PP_*` 全域變數、`_cl_next` 對 `_cl_out` 與 `_cl_bl`、`_push_args` 對 `_hrange` 與 `_brange`。測試端的 `_ppc_*` 與 `t_prepush_*` 也對齊。
- 錯誤處理也對齊:印重查指令用 `[[ -z … ]] ||` 守住,沒有新增會讓掛鉤中途出錯的路徑。
- 不一致有兩處,見下面 Z1、Z2。
引句:「echo "下一步:$(pp_q "$PY") scripts/test_autonomous_loop.py${_AUTOLOOP_ARGS+ ${_AUTOLOOP_ARGS[*]}}"」

Z1:同一條「作廢的合約不算」的規則,在兩個地方各寫一次,切片方式也不同。
- `_impact_contract` 寫了兩處:一處把 `extract_contracts` 回傳的串列再過濾,一處用 `line.partition(":")[2]`。
- `_contract_key_matches` 又用 `s.partition(":")[2]`。
- 既有的 `_ns_superseded` 呼叫點都傳「前綴之後的 rest」,切法是 `rest`、`line[len("RULE:"):]`、`s[len(m.group(1)) + 1:]`,見 `scripts/lumos:4488`、`scripts/lumos:50323`、`scripts/lumos:51981`。
- 傳進去的內容語意一樣(都只讀 `[status:…]` 欄位),所以結構上沒走偏。
- 另外,`extract_contracts` 其他 20 個左右的呼叫點仍把作廢行算進去。這點圖譜 `派工鏡頭` 的 WHY 已寫明「不選:改 extract_contracts」,所以是有登記的取捨,不當缺陷。
引句:「invs = [x for x in invs if not _ns_superseded(x)]」
severity: minor
blocking: no

Z2:兩個測試紅的出口,新的「下一步」跟正上方已有的同一條指令重複,寫法也不同。
- `scripts/hooks/pre-push:984` 的上方(`scripts/hooks/pre-push:976-977`)已經印了「只重跑紅的那幾支」加縮排的 `$PY scripts/test_lumos.py --ff -x`,`$PY` 沒加引號。
- 新增那行用 `pp_q "$PY"` 把同一條指令再印一次。
- 新行是「標籤加指令同一行」,鄰居慣例是標籤一行、指令縮排獨立一行。
引句:「echo "       $PY scripts/test_lumos.py --ff -x"」
severity: minor
blocking: no

**第 3 問:`pp_q` 不是第二份,沒有第二種做法。**
- `scripts/hooks/` 底下沒有別的 bash 引號工具。我搜過 `printf %q`、`shlex`、`quote`,掛鉤腳本裡只有 `pp_q` 自己,另外兩支 `.py` 掛鉤(`bypass-ask-hook.py`、`check-graph-sync.py`)是拿 `shlex` 做解析,不是產生引號。
- `scripts/lumos` 有 Python 版 `_sh_quote`(約 468 行)和 28 處 `shlex.quote`,但掛鉤明講「維持薄殼:不在 hook 裡塞 python」(`scripts/hooks/pre-push:989`),又要能配舊版 lumos 跑。
- `pp_q` 是同一個語意在 bash 的對應版:安全字元集 `[A-Za-z0-9_./:@%+=,-]` 跟 `shlex.quote` 的一致。
- 註解寫明不用 `printf %q` 的理由(bash 3.2 在非 UTF-8 語系把中文跳脫成亂碼),不是無故另寫。我判它跟既有做法一致。
引句:「# 給人照抄的指令裡的一個參數:只含安全字元照原樣,其他整段包單引號。不用 printf %q:/bin/bash 3.2 在非 UTF-8 語系會把中文逐位元組跳脫成亂碼。」

其他可能的第二種做法我也查了,沒有:
- 重查指令走掛鉤自己印,沒有並行新增一條經 lumos 的輸出通道。
- 測試用既有的假 lumos 和 `_ppc_repo` 一類輔助函式,沒另建一套。

不對齊共 2 條,其中 major 0 條。

⚠ 交編排者的只有一點:Z1 若認為「同一條過濾規則寫在兩處」已算第二種做法,可升 major。我判 minor,理由是兩處都是在各自既有的掃描上補過濾,且圖譜已登記取捨。

被審材料:`/tmp/lumos-seat-work/code-推送被擋下一步/r3-code.patch`。我沒有改 repo,也沒有建任何暫存檔。
