severity: major

## 複核

①「推送前只比條款指紋,正文事後塞金流敘述、條款不動照樣放行」——**關上了**。`_spec_gate_push_check` 在比對 `clause_sha` 之前先呼叫 `now = _door_judge(env, n, text)`,若整個門重判不再是 two-way 就直接擋(`bad.append(... "留痕時是雙向門,現在判成單向門" ...)`),不是只比指紋。新測試 `t_prepush_spec_gate_door_rejudged` 實測「留痕後正文塞 Stripe 扣款敘述」會被擋,我用手跑也重現同樣行為(見下方 F1 的實驗,同一條 `_door_judge` 路徑)。

②「實務隱患節裡引用塊(>)的已排除行被當真」——**關上了**。`_door_exclusions` 對 `_h2_section_lines(text, _HAZARD_H2_RE)` 回傳的每一行,先 `if ln.lstrip().startswith(">"): continue`,引用塊行不進 `found`/`linenos`,測試 `t_spec_gate_引用塊已排除不算`(list 裡有這支)驗過。

③「新開的 `_plan_all_links` 跟既有 `_plan_system_links` 重複」——**關上了**。現在全檔只有一支 `_plan_system_links(note, text=None, systems_only=True)`,`_regress_sources`(line 5235)沿用舊語意呼叫 `_plan_system_links(note)`(不傳 text,只收 Systems 前綴),`_door_linked_signals`(line 4868)與 `_spec_gate_push_check`(line 5561)改傳 `text=..., systems_only=False` 收全部節點。確認沒有第二套平行實作。

④「實作提交只動程式檔時推送前查不到計劃」——**關上了**。`_spec_gate_push_check` 在 `code` 非空時反查 `about_code` 列了該檔的 Systems 節點,再用該節點找 `lands_in`/`related`/正文連結指向它的 doing 計劃。測試 `t_prepush_spec_gate_code_home` 我實跑過(`python3 scripts/test_lumos.py -k t_prepush_spec_gate_code_home` → `1 passed, 0 failed`),行為與宣稱一致。

但③的合併函式本身帶了一個新洞,見 F1。

## F1 `_plan_system_links(text=...)` 沒有走 `_visible_lines`,fence/引用塊裡的範例連結被當真連結,反把雙向門硬打成單向門

severity: major
blocking: yes

`_plan_system_links` 合併之後(scripts/lumos,約 line 5247-5263),`text=` 分支直接對整份原始文字跑 `WIKILINK_RE.findall(text)`,完全沒有經過本專案「全檔唯一的 fence 判定」`_visible_lines`:

引句:「links += [link_target(m) for m in WIKILINK_RE.findall(text)]」

同一支檔案裡,凡是需要判斷「這行算不算數」的地方都刻意繞開圍欄與引用塊——`_door_exclusions` 明講「引用塊行不算」,`_door_judge` 的關鍵字掃描也是 `for no, ln in _visible_lines(text.splitlines())`。但 `_plan_system_links(text=...)` 被 `_door_linked_signals`(門判定訊號 2)與 `_spec_gate_push_check` 的「落點被碰到」反查直接拿去用,兩處都沒有二次過濾圍欄。

引句:「for lk in _plan_system_links(note, text=text, systems_only=False):」

結果:計劃正文裡只要出現一段「示範怎麼寫 wikilink 語法」的圍欄程式碼,裡面的 `[[Systems/X]]` 會被當成真連結,連到帶 ★IRREVERSIBLE★/★CHECKPOINT★ 合約或 risk/ 標籤的節點時,會把本來該過的雙向門硬判成單向門。

怎麼重現(我在 /tmp/seat-r2-reviewer 這個唯讀 worktree 裡手跑,沒有動到正式 repo):
1. 建一份 doing 計劃,四類已排除行齊全、沒有其他任何單向門訊號,唯一「風險內容」是一段示範語法的圍欄程式碼:
```
這是說明如何寫連結語法的範例(給下一個人看怎麼寫 wikilink,不是真的連過去):

​```
- [[Systems/Risky]]
​```

- [S1] 系統應回 200 [test:t_red]

## 實務隱患
- 已排除:金流:這份計劃不碰任何收費或扣款的流程
- 已排除:對外送出:不寄信不推播不呼叫外部服務
- 已排除:不可逆:只改本機檔案,改壞了重跑一次就回來
- 已排除:守衛面:不碰任何閘或掛鉤的判定
```
2. `Systems/Risky.md` 帶 `KEY:★IRREVERSIBLE★ 上架後撤不回`(這節點跟計劃正文完全無關,只是被圍欄範例提到)。
3. 跑 `lumos spec-gate Projects/甲_計劃 --no-run`,輸出:
```
[spec-gate] 門: 單向門(連到 Systems/Risky(★IRREVERSIBLE★))
```
四類已排除行明明齊全、也沒有真的連結,卻因為圍欄裡的範例文字被判成單向門。我另外用 `_visible_lines` 直接驗證同一段文字:圍欄內的 `[[Systems/Risky]]` 那一行根本不在「可見行」清單裡(`any("[[Systems/Risky]]" in ln for _no, ln in vis)` 回 `False`),證明這是 `_plan_system_links(text=...)` 沒套用可見行過濾造成,不是我編的邊界案例。

為什麼是 bug 不是風格:這條函式的 docstring 自己寫「★全檔唯一的「計劃連到誰」★」,意在取代掉舊的重複實作(複核③),但合併時把「圍欄/引用塊不算」這條本專案到處在用的規則弄丟了,造成語意跟同一支檔案裡其他判斷(`_door_exclusions`、PITFALL 關鍵字掃描)不一致。方向雖然是「多判單向門」不是「漏判雙向門」,不會被拿來繞過閘,但它會讓完全合格的雙向門計劃被平白打回單向門、逼進設計審——這正好是這整批 PR 要交付的「雙向門免審快速路徑」失效的具體案例,而且沒有任何測試涵蓋(`t_spec_gate_door_signals`/`t_spec_gate_skips_exclusion_lines` 等測試都沒有在計劃正文放過圍欄或引用塊裡的 `[[…]]`)。同樣的洞也存在於 `_spec_gate_push_check` 用 `_plan_system_links(text=ptxt, systems_only=False)` 找「落點被碰到的 doing 計劃」那一段,會把示範用的圍欄連結也算進「被碰到」,造成不必要的推送前重查(方向一樣是多做而不是漏做,但同一顆函式,建議一併修)。
