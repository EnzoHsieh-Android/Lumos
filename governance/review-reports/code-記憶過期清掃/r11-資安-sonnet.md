severity: major

## 發現1

severity: major

引句:「不管卡在哪一步,開場一定有一句出聲,不會被外層逾時砍到完全沒聲音。」

觀察到什麼:

`_watchdog()` 算自己要等多久,用的是 `_outer_budget() * 0.85`——這是一個**從 `_watchdog()` 被呼叫那一刻才開始算的全新時鐘**,完全沒扣掉「呼叫它之前這支 process 已經花掉的時間」。而 `main()` 是被 `scripts/hooks/claude/_hookevent.py` 的 `guard()` 包住呼叫的,`guard()` 在呼叫 `main()`**之前**會先跑 `_root_from_cwd()`——它自己就帶一個 3 秒的逾時上限(`_hookevent.py` 第 96-105 行,`subprocess.run(["git", "rev-parse", ...], timeout=3)`),註解也承認這是為了防「git 卡住時會先把預算吃完」設的最壞情況上限。

換句話說:`_watchdog()` 的「0.85 外層」跟 `_inner_budget()` 的算法不是同一套邏輯——`_inner_budget()` 有明確記錄並扣除「這支 hook 到目前為止已經花掉的時間」(見它自己的註解:「已耗時間自己算,不靠呼叫端記得傳」),但 `_watchdog()` 完全沒有做這件事,而是把 `_root_from_cwd()` 那最壞 3 秒直接晾在外面,沒有算進 0.85 這個比例裡。這正是 `_inner_budget()` 註解裡自己講過的那個坑——「這正是這批改動宣稱要修掉的問題,只是換個地方重新發生」——只是這次是在新加的看門層重演一次。

實測(用真正的呼叫方式,`main()` 由 `_hookevent.guard()` 包住呼叫,`--budget 12 --quiet`,模擬 `_root_from_cwd()` 落在它自己文件說的最壞情況 2.9 秒,記憶目錄放一個 FIFO 讓子行程卡在 `os.open()`,逼看門層跑滿 10.2 秒才逾時):

```
python3 /tmp/test_root_overhead2.py <帶一個 evil.md FIFO 的記憶目錄>
```
輸出:
```
{"hookSpecificOutput": {... "additionalContext": "...這輪清掃超過 10 秒還沒跑完,被停掉了——結果完全沒出來...."}}
TOTAL WALL TIME: 13.18s (registered external timeout = 12s)
exceeded 12s external budget: True
```

也就是說:從這支 hook 真正開始跑,到它自己終於印出「超時沒跑完」那句話,總共花了 13.18 秒——超過背景裡講的、Claude Code 外層註冊的 12 秒逾時。

會造成什麼:如果 Claude Code 自己的外層真的在 12 秒準時對整條行程樹送出 SIGTERM/SIGKILL(這正是「外層逾時 12 秒」這句話的意思),那麼在上面這個情境下,這支 hook 會在**它自己都還沒來得及跑到印出那句「超時沒跑完」之前**就被外層砍掉——整支(外層看門 + 子行程)跑超過 12 秒,而且對話裡完全沒印出任何東西,直接推翻 `_watchdog()` 文件字面上寫的保證(「不管卡在哪一步,開場一定有一句出聲,不會被外層逾時砍到完全沒聲音」)。

要注意:觸發條件裡「記憶目錄放 FIFO 讓子行程卡住」是攻擊者可以做到的(跟符號連結/硬連結攻擊同一個能力等級,前幾輪已經把那些當成有效威脅在防);但「`git rev-parse --show-toplevel` 卡到 3 秒」這一半不是靠記憶檔內容觸發的,是環境/系統條件(大 repo、慢碟、網路掛載的 .git)。可是這個最壞情況是程式碼自己承認、自己特地留 3 秒上限去防的真實情境("最壞態原本設 10 秒......git 卡住時會先把預算吃完"),不是我發明的極端假設——它跟一個攻擊者能觸發的卡住(FIFO/任何繞過 deadline 檢查的單步驟卡住)疊在一起,就會讓整支 hook 真的可能超時不出聲,直接打臉這一輪要修的核心宣稱。

建議怎麼修:`_watchdog()` 的逾時上限要用「從整支 process 真正開始的那一刻」算起的剩餘時間,而不是「呼叫 `_watchdog()` 那一刻」算起;最直接的做法是把 `guard()` 呼叫 `main()` 之前的那段時間也算進去(例如把 process 啟動時刻記下來,`_watchdog()` 用 `外層預算 - 到現在為止真正耗掉的時間` 而不是固定比例乘一個全新時鐘),或者把 `_root_from_cwd()` 的逾時也內縮進同一個總預算裡,別讓它是額外白吃的 3 秒。

## 發現2

severity: minor

引句:「這一層只負責計時——子行程在時間內沒跑完就停掉它」

觀察到什麼:`_watchdog()` 逾時後靠 `subprocess.run(..., timeout=limit)` 內部的 `TimeoutExpired` 處理去停子行程,那個機制只對**直接子行程**送 SIGKILL,不會連著子行程自己再往下開的孫行程一起收掉。如果被停掉的子行程當下正卡在它自己叫出來的孫行程(這支程式裡唯一會開孫行程的地方是 `_git()`,例如 `git fetch`),孫行程會變成孤兒(PPID 變成 1)繼續跑,不受這支 hook 的 12 秒逾時約束。

實測(直接呼叫 `_watchdog()`,用一支會自己再 fork 一個 `sleep 30` 孫行程、然後 `wait()` 等它的假子行程模擬 `_git()` 卡在 fetch 上的情境):

```
ms._watchdog(True, Path("."), 2.0, cmd=[sys.executable, "-c",
    "import subprocess,time,os; p=subprocess.Popen(['sleep','30']); ... ; p.wait()"])
```
watchdog 在 2.01 秒正確返回、印出「超時沒跑完」;但事後檢查:
```
enzo   860   0.0  0.0 ...  ??  SN  ...  sleep 30
recorded grandchild pid: 860
CONFIRMED: grandchild pid 860 is STILL ALIVE (orphaned) after watchdog killed its parent
PID  PPID STAT COMMAND
860     1  SN  sleep 30
```
PPID 已經變成 1,證實孫行程在直接子行程被砍掉之後確實還活著、繼續跑。

會造成什麼:每次觸發這條路徑,理論上會在系統裡留下一個不受這支 hook 自己逾時約束的殘留行程,持續佔用資源(這裡是網路連線/等待)直到它自己結束或被系統其他機制回收。

不過在這次審查給定的威脅前提下(攻擊者只能讓 .md 內容落地,不能碰 git remote 設定、env、repo 圖譜),目前程式碼裡**唯一**會開出孫行程的路徑是 `_git()`,而它自己的 `subprocess.run` 逾時是用 `_budget_left()`(封頂在 `0.7×外層預算` 那條線附近),比看門層的 `0.85×外層預算` 更早到期——正常情況下 `_git()` 自己的逾時會先把 git 收掉,看門層根本沒機會對還在等 git 的子行程開刀。而且那次 fetch 打的是這個 repo 真正設定好的 remote,攻擊者控制不到讓它掛住的那一端(不能改 git config/env)。所以雖然「看門層砍不掉整棵樹」這件事本身是真的洞,但要單靠記憶檔內容把它逼出來、留下真正的孤兒行程,目前沒有找到路徑——算縱深防禦不足,不是可直接靠惡意記憶檔觸發的洞。

建議怎麼修:`_watchdog()` 停子行程時改用行程群組(例如 `start_new_session=True` 開子行程、逾時時 `os.killpg` 整組收掉),連根拔起而不是只砍直接子行程;這樣以後不管未來加了什麼會開孫行程的檢查型別,都不會重新踩到這個坑。

## 已確認

- 記憶目錄放一支 FIFO(named pipe)讓子行程卡在 `os.open()` 阻塞讀取:用真實呼叫方式(`--budget 12 --quiet --dir <含 FIFO 的目錄>`)實跑,10.33 秒內看門層正確逾時、印出「超時沒跑完」且帶安全框,沒有殘留行程——這個情境下(沒有額外疊加 `_root_from_cwd()` 變慢)整支確實在 12 秒內出聲,行為符合處置的宣稱。
- `_LINKED_REF` 排除 `[` 與換行、長度上限 200 那個修正:32000 個字元的未閉合 `[[` 在 1 秒內比完(對照組確認正常的 `[[連結]]` 照樣抓得到),不再是 r10 那條平方級 72 秒的回歸。
- 圖譜衝突/影子副本排到逐條檢查雜訊前面的修正:`tally.lines[0:0] = front` 確實讓衝突段落排在最前面,不會被大量「驗不了」雜訊擠出 80 行的注入視窗。
- 看門層把子行程輸出原樣轉印(`print(r.stdout, end="")`)不會繞過注入框:子行程無論 quiet 或手動模式,`_emit()` 都是先呼叫 `_frame_injected()` 框好才 `print()`,看門層只是把已經框好的那段文字轉印一次,沒有再暴露一段未框的原始內容;逾時分支也是走同一支 `_emit()`,同樣有框。
- `python3 scripts/test_lumos.py -k memory_sweep` 全套 59 項(含這輪新增的 ㉕㉖㉗)全部通過,0.9 秒跑完。
