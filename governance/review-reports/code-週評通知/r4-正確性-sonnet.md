severity: minor

第 4 輪找到兩個小問題。判斷邏輯、MSG 讀取時機和「判定為否不印 MSG」都成立,我沒有找到能讓判定出錯的輸入。

## 1. 儀器事故時總結行不在行首,錨定後 log 變「無結果」,退路也不送(be-api-compat:對 log 格式的舊讀法不相容)
severity: minor
blocking: 否
引句:「  local line; line="$(grep -E '^[0-9]+/[0-9]+ 個情境 Claude 自己敲對了' "$LOGDIR/probe-$TODAY.log" | tail -1 || true)」
file: `scripts/scenario_probe.py:1632`

1. 輸入:探針因 `fatal` 或 `bad`(skills 事故)結束。
2. 路徑:主程式把 `summ["line"]` 改成「儀器例外: …;整批不能下結論。 0/8 個情境 …」再印出。總結行從行首被推到句中,行首錨 `^[0-9]+/[0-9]+` 抓不到。
3. 壞處一:log 寫「情境探針結果:無結果」。事故這次最需要看的結果被藏起來,而且計劃 S5 寫的「log 記錄錨在行首的總結行」在這條路徑上不成立。
4. 壞處二:沒有判定行時,舊規則的退路也不送 LINE。這要在 `weekly_alert` 丟例外、`weekly_alert_line` 回 None 時才會發生,所以到得了的機會很窄,標 ⚠。
5. 有判定行時,「週評通知:是」加 MSG 仍會送 LINE,所以通知本身沒丟。
6. 重現:把 `run_probe` 抽到沙盒,假探針輸出 `儀器例外: x；整批不能下結論。 0/8 個情境 Claude 自己敲對了 lumos 指令`,其餘照 `t_autoloop_probe_alert_follows_verdict` 的做法。
   - 沒有判定行:返回碼 0、log「無結果」、LINE 為空。
   - 加判定行和 MSG 行:log 仍是「無結果」,LINE 會送。
7. 測試缺口:S5 的假探針輸出永遠以 `N/M` 開頭,沒有「總結行被儀器例外前綴推離行首」這組,所以錨定的修補沒被這條路徑翻紅。
8. 歸因:有證據的修復回歸。
   - 查證命令:`git show cc137467:governance/autonomous-loop.sh | grep -n "個情境"`,該版 grep 未錨行首,會抓到整行。
   - 結果:修前這條路徑 `pp != tt` 會送 LINE,修後是「無結果」。這是依 grep 與 `sed` 的程式行為判斷,沒有另外跑修前版本。
9. 修法方向:grep 改成 `^([^M].*。 )?[0-9]+/[0-9]+ 個情境`,或把儀器例外前綴移到總結行之後,維持 `summarize_results` docstring 說的「第一行固定以 p/n 開頭」。

## 2. 同一週重跑「只留最後一列」與實作不一致
severity: minor
blocking: 否
引句:「        if (not g or r.get("grader") != g or s == this.get("seed") or s in seen or not r.get("ids")」
file: `scripts/scenario_probe.py:1257`

1. 輸入:W40 第一次跑 conclusive 且 a 沒過,重跑那列是 `fatal`。
2. 路徑:`_baseline_weeks` 先判斷事故,`seen.add(s)` 在過濾之後。W40 的最後一列被 `continue` 略過,`s` 沒進 `seen`,第一次跑的那列就當成 W40 收進基準。
3. 壞處:docstring 和計劃都說「同一週有多列只留最後一列」。實際上最後一列是事故時會退回較早的列,被當成「上一次出現」。
4. 重現:W37、W38、W39 各 8/8,W40 第一次跑 `failed=["a"]`、`ids=["a","d"]`,W40 重跑 `fatal=True`、`ids=[]`,W41 8/8,W42 `failed=["a"]`。
5. 結果:`_baseline_weeks` 回 W37 到 W41,`weekly_alert` 回「同一題連續兩次出現都沒過:a」。照文字讀應該是 W40 整週不算,a 的上一次出現是 W37。
6. 是否算錯有爭議:退回 conclusive 的較早列也說得通。但文字和行為得二選一對齊,目前沒有測試釘住任何一邊。
7. 歸因:未判定。查證方式是上述的 `_baseline_weeks`,r4 以前就是這個過濾順序,不是這輪修補造成的。

## 三問
- **①原問題的修復效果**:三個 behavior_cases 都有直接證據,但有一個例外,見下方「另有一事」。
  - 判定為否不印 MSG:`main` 以 `alert.startswith("週評通知:是")` 守住,測試的「否」那組斷言沒有 MSG 行。
  - 沒判定行時雜散 MSG 不送:`msg` 只在 `[ -n "$verdict" ]` 內才讀 MSG,`8/8` 加 `MSG:hello` 那組測試能抓到。
  - 總結行錨行首:一般情況下 MSG 行不再被抓成總結行。例外就是 finding 1。
- **②修補處的相鄰路徑**:正常路徑、判定為否路徑、MSG 與總結行互相干擾的路徑都成立。儀器事故路徑退步,即 finding 1。
- **③同一案例修前修後**:finding 1 的案例,修前(未錨定)退路會送 LINE、log 抓得到整行,修後退路不送、log「無結果」。

另有一事:除了上面兩條,我沒再找到分支翻不紅的測試。逐項看過的有 `_is_weekly_row` 的 arm、runs、passed 非整數與缺 total,`_baseline_weeks` 的 ids、事故與同週,基準週數 `< 3` 的邊界,以及 Trigger A 的「取最近一次」。各項都有測試對應,看起來能翻紅。這只是讀測試和程式比對的判斷,我沒有把這些分支改壞再跑測試。

總結:最高等級 minor
