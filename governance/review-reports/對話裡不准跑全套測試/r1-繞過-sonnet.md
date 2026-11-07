severity: major

## F1 `-k` 與位置關鍵字只看「有沒有給」,不看選中多少,`-k t_` 照跑全套
severity: major
blocking: 是(spec 自己的 S1 就把 `-k`、位置關鍵字列為「不擋」,隨手就能跑出全套)
- spec 段落:〈做〉1、〈預期值表〉S1。
- 問題:關鍵字是子字串比對。每支測試名都以 `t_` 開頭,所以 `-k t_`、`-k _`、`-k t`、位置參數 `t` 會選中全部測試。這條路走單一程序、不切片,比預設切片還慢,約 8 分鐘。spec 只問有沒有帶關鍵字,完全不看選中數量。
- 佐證:file: `scripts/test_lumos.py:49772` 的篩選只有 `_args.keyword in t.__name__`,沒有數量上限。
- 佐證:file: `scripts/test_lumos.py:58` 的 `_keys_suite_select` 已經有「單一關鍵字選中超過三成就當太泛」的上限,而且那段註解說明這是「等於全套」的同一個問題。`--suite keys` 擋得住這種寫法,`-k` 擋不住。
- 修法:在 CLAUDECODE 下,關鍵字篩完後如果選中數超過總數的某個比例(例如三成,沿用 `cap`),就視為全套擋下。判斷放在篩選之後,不放在 main 前面。
- 天花板現在沒寫這一條。

## F2 判斷函式放在 `_isolate_environment()` 之前,字面上落在預設切片分流之後,無參數全套會漏過
severity: major
blocking: 是(預設的無參數全套就是被切片分流處理的那條路,放錯位置等於沒擋)
- spec 段落:〈做〉2「參數解析完、`_isolate_environment()` 之前呼叫」。
- 問題:main 的順序是參數解析、`if _fanout_wanted(_args): return _fanout_main(_args)`、然後才是 `_isolate_environment()`。無參數而且片數大於 1(預設 4)時,執行器會在切片分流那一行 return。照 spec 字面把判斷插在 `_isolate_environment()` 前面,無參數全套根本走不到它。
- 佐證:file: `scripts/test_lumos.py:49678` 是切片分流,`scripts/test_lumos.py:49680` 才是 `_isolate_environment()`,兩行相鄰。
- S3 的真子程序測試會抓到這個錯,但 spec 文字有歧義。應明寫「在 `_fanout_wanted` 之前」。
- 「判斷完把 CLAUDECODE 拿掉」也要在分流之前做,讓切片子程序與它們開的沙盒不繼承。
- 要補一條前置斷言,證明「預設片數 4、無 `LUMOS_FANOUT_CHILD`」的現場確實會走到切片分流,否則測試可能在 `LUMOS_TEST_SHARDS=1` 的環境下假綠。

## F3 擋下訊息把逃生門寫成現成指令,而且逃生門沒有任何紀錄
severity: major
blocking: 是(使用者的原話正是「你可以不斷繞過」,設計把繞法印在被擋的那一瞬間)
- spec 段落:〈做〉2 訊息第三段(印出 `LUMOS_ALLOW_FULL_SUITE=1`)、〈做〉3(不寫任何檔)、〈天花板〉2。
- 問題:急著跑全套的 AI 讀到 stderr 的最後一行就會照抄。〈天花板〉只寫「AI 自己也能設」,把它當事實,沒有任何緩解。這個擋法的效果因此取決於 AI 肯不肯停。
- 〈範圍〉隱患說「人在終端分頁手跑會被擋所以印逃生門」。人是少數,AI 是多數,訊息卻是照人的需求寫的。
- 修法:訊息只講子集的寫法與「要跑全套請使用者自己在終端機跑或交給推送閘」,不印變數名,變數名只留在手冊。或者要求逃生門帶一個理由字串,並且在 stderr 逐字回顯。
- 另外,逃生門 `LUMOS_PUSH_ATTEMPT=x` 和 `LUMOS_FANOUT_CHILD=1` 同樣是環境變數就能設的豁免,天花板也沒列。

## F4 RETIRE-IF 與 REVISIT 要量的數字,設計沒有留下任何可量的紀錄
severity: minor
blocking: 否(自我一致性問題,不影響擋的行為本身)
- spec 段落:RETIRE-IF、REVISIT:2026-12-08、〈不做〉3、〈做〉3。
- 問題:RETIRE-IF 的判準是「被擋下幾次」與「逃生門被用幾次」。REVISIT 也要看「逃生門被用了幾次」。設計卻明說不寫治理帳、不寫檔、逃生門只印一行。終端輸出不會留存,這個數字量不到。
- 引句:「逃生門是環境變數,AI 自己也能設;只印一行、不留帳。」
- 修法:至少要有一個不改工作目錄的計數去處(例如 `~/.lumos` 之類工作樹外的追加檔)。或者承認這條回頭條件改以人工回報為準。

## F5 `-k ''` 空字串與「沒帶 -k」的判準要跟現有切片分流用同一個謂詞
severity: minor
blocking: 否(要刻意打空字串才會踩到,但實作稍一鬆就留洞)
- spec 段落:〈做〉1「沒帶 `-k` 或位置關鍵字」。
- 問題:現有程式用真值判斷。`-k ''` 或位置參數 `''` 會被當成沒給,結果是全套照切片跑。如果判斷函式寫成 `args.keyword is None`,空字串會被當成「有帶」而放行。
- 佐證:file: `scripts/test_lumos.py:49399` 的 `_fanout_wanted` 用 `args.keyword or args.shard ...` 判斷,沒給與空字串等價。
- 修法:S1 加一列 `-k ''` 與位置參數 `''`,預期擋。判斷函式直接重用 `_fanout_wanted` 的謂詞,別另寫一套。

## F6 `--suite keys` 的三成上限是逐鍵算的,多鍵聯集沒有上限
severity: minor
blocking: 否(要刻意湊多個泛名才會踩到)
- spec 段落:〈做〉1「帶 `--suite` 不擋」、〈預期值表〉S1。
- 問題:每個關鍵字各自上限三成,聯集沒有。三個各 29% 的名字可以選中大半個全套,而且走單一程序。`--suite docs --graph` 也會選到兩百多支,實測約四分鐘,spec 同樣一律放行。
- 佐證:file: `scripts/test_lumos.py:72` 到 `:79` 逐鍵檢查 cap,最後取聯集。
- 修法:同 F1,在選完之後對最終選中數設上限。天花板要補上這兩條。

## F7 對話裡 `git push` 由推送前閘跑全套,spec 當正當豁免卻沒寫進天花板
severity: minor
blocking: 否(CLAUDE.md 與全域規則本來就要求全套交給推送閘,豁免方向正確,缺的是文件)
- spec 段落:〈做〉1(`LUMOS_PUSH_ATTEMPT` 豁免)、〈天花板〉。
- 問題:在對話裡下 `git push`,掛鉤會 export `LUMOS_PUSH_ATTEMPT` 再跑完整全套,仍會超過對話工具的上限,而且占住使用者機器。
- 佐證:file: `scripts/hooks/pre-push:393` 設 `LUMOS_PUSH_ATTEMPT`,`scripts/hooks/pre-push:975` 到 `:985` 起切片子程序跑測試。
- 修法:天花板補一行「對話裡 push 仍跑全套,由掛鉤與背景執行處理」。其他「不用順手也繞得過」的寫法也一併補進天花板:
  - `env -u CLAUDECODE ...`:本機實測有效,`env -u CLAUDECODE sh -c 'echo u=[$CLAUDECODE]'` 印空。
  - `CLAUDECODE=0` 或別的值:spec 只認 `== "1"`。
  - tmux、cron、ssh 這類脫離環境繼承的新程序。
  - 手設 `LUMOS_PUSH_ATTEMPT` 或 `LUMOS_FANOUT_CHILD`。
- `bash -lc` 不在這份清單裡:本機實測 `bash -lc` 後 `CLAUDECODE` 仍是 1,擋得到。

## F8 擋掉「只帶 --shard」與 `--ff -x`,跟掛鉤自己印的下一步相衝,會把正當用法推向逃生門
severity: major
blocking: 是(推送被擋後,掛鉤教的下一步在對話裡立刻被擋,直接把 AI 推向逃生門,讓 RETIRE-IF 的「用逃生門多於被擋」條件自動成立)
- spec 段落:〈做〉1「只帶 `--shard` 沒帶關鍵字也擋」、〈範圍〉隱患。
- 問題:推送前閘紅了之後,掛鉤逐字印出 `scripts/test_lumos.py --ff -x`,既沒有 `-k` 也沒有 `--suite`。照 spec,在對話裡這條會被擋。複現 CI 某一片紅的人,用 `--shard 3/4` 約兩分鐘就跑得完,也被擋。
- 佐證:file: `scripts/hooks/pre-push:1032` 與 `:1035` 印出「下一步」。
- 正當分片的需求被擋,只能走逃生門,擋下的訊息又教逃生門,兩邊的規則互相拉扯。
- 修法二選一:
  - (a) 在判斷函式裡,有上次紅過的快取而且帶 `-x`,或是帶 `--shard` 時放行。
  - (b) 改掛鉤印的指令,並在 spec 明寫掛鉤的提示要同步改。
- 沒有快取時 `--ff -x` 會退成全套單程序,仍該擋。

## 固定席逐條判
- 〈間接相依〉各節點的 ★INVARIANT★ 都綁在 `scripts/scenario_probe.py` 的行為,沒有一條在管測試執行器的入口:
  - `Systems/測試假綠形態`、`bound-tests-gate`、`lumos-cli-lifecycle`、`canary-audit`、`guard-kill`、`design-loop`、`lumos-cli-read` 都是這樣。
  - 判不影響的理由:這份設計只動 `scripts/test_lumos.py` 的 main 前段,沒碰 scenario_probe,也沒改任何合約文字。
- `bound-tests-gate` 的合約是對綁定測試逐支真跑。實際走的指令是 `.lumos/config.json:5` 的 `{python} scripts/test_lumos.py -k {method}`,有帶 `-k`,不被擋。不影響。
- 唯一要留意的是 `scripts/scenario_probe.py:1162`。它開巢狀 Claude 子程序前拿掉 `CLAUDECODE`,而 spec 讓執行器自己也拿掉。兩處互不衝突。
- 「`CLAUDECODE` 拿掉」可能影響別處讀它的程式。我只在 `scripts/test_lumos.py`、`scripts/lumos`、`scripts/hooks/*`、`scripts/scenario_probe.py` 這四處搜過,只有 scenario_probe 讀它。上述範圍外的程式沒查。

## 實務隱患鏡頭(spec 碰到的風險類)
- 守衛面:有。見 F1、F2、F3、F5、F6、F7、F8。
- 資源面(記憶體、時間):有。F1 的 `-k t_` 是單程序全跑,吃的記憶體比切片版還多。
- 正當用法被誤擋:有。見 F8。⚠ 自動迭代迴圈(每天 09:30 自動選題,在 headless Claude 底下跑)是否會合法地跑無參數全套,我沒查到來源,spec 也沒提。
- 金流、對外送出:無,spec 已排除,且我讀碼確認這段不碰網路。
- 不可逆:無,只改入口判斷,退提交即回原狀。
- 效能與記憶體:判斷函式只做環境變數與參數判斷,F1 的修法要在選完測試後才算數量,多一次 O(n) 掃描,可以接受。

總結:最高等級為 major,blocking 共 4 條
