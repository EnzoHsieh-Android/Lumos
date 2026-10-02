severity: minor

# 代碼審 r3(末輪)通才席 — opus

審材:`r3-delta.patch`(第二輪修正差異,逐 hunk 讀完),上下文對照 `r3-snapshot.patch` 與 repo 真代碼(`scripts/lumos` 28600–28960、29004–29035、29221–29235;`_lens_git` 39244)。實驗一律在 `git clone --shared` 出來的臨時目錄 `scratchpad/code-tb-r3/opus-clone` 做,repo 沒動。

總結:這輪修正沒有引入 blocking 級的洞。三個被點名的接點:
- `_ns_tr_extra_merged` 兩個呼叫端(`_note_shape_report`、`_ns_skip_slot_extra`)都改成接回傳值 `ex = ...`;repo 與圖譜裡已經沒有 `_ns_tr_add_extra` 的殘留引用。**沒問題。**
- `st["out"]` 在 `ls-tree` 回 None 時設起:目前這個名稱照舊判不了(`undecidable`,會寫進快取,並印「判不了」那一行);後面的名稱走 `_out_of_time` 回 `skip`,不擋;同一次推送後面的筆記共用同一個 judge,所以也都不查。這跟計劃〈做法〉4「逾時或用完時剩下的名稱這次不查、印一行」一致,也有印出原因,**不是無聲放行**。代價是後面的名稱連第①道(工作目錄索引,便宜)也跳過,本來第①道就能判「指不到」的會變成不查。計劃對逾時已經接受這個取捨,`_lens_git` 只在逾時或 OSError(叫不起 git)時回 None(file: `scripts/lumos:39255`),所以不另外列成 finding。
- `_ns_tr_collect` 是原樣搬出來,行為沒變。

找到兩條 minor,都在 `_ns_tr_is_new` 和它的測試。

## F1 帳本 `new` 的「整字比對」把 `.`、`:`、`-` 也當字界,也沒有把名稱用同一套規矩正規化,第二輪修的同一類誤判還有幾種寫法沒收掉
severity: minor
blocking: 否
引句:「pat = re.compile(r"(?<![\w])" + re.escape(nm) + r"(?![\w])") if nm else None」
file: `scripts/lumos:28785`(`_ns_tr_is_new`)
file: `scripts/lumos:28643`(`_test_names_of`:名稱只在平台前綴那一處正規化冒號,並去掉包住名稱的反引號)

1. **字界太寬(誤中)**:`\w` 不含 `.`、`:`、`-`,所以一個名稱只要剛好是同一條裡另一個名稱的「最後一段」,就會被當成也出現在那一行。我用真實的筆記全文走完整流程(`_ns_test_ref_lines` → `_test_names_of` → `_ns_tr_is_new`),摘要區塊從第 5 行起:
   - A:第 5 行(舊)`WHY:一句 [test:test_x]`,第 6 行(新)`接續 [test:FooTest.test_x]` → `test_x` 的 new 是 **True**,應該是 False(第 6 行的 `FooTest.test_x` 前面是 `.`,算成字界)。
   - D:第 5 行(舊)`[test:t_p]`,第 6 行(新)`[test:ios:t_p]` → `t_p` 的 new 是 **True**,應該是 False。
   - E:第 5 行(新)`[test:should-work]`,第 6 行(舊)`[test:work]` → `work` 的 new 是 **True**,應該是 False。
2. **只正規化原文、沒正規化名稱(漏中後退回整條)**:`_norm` 把原文**每一個** `\s*[:：]\s*` 都換成 `:`,但 `_test_names_of` 只正規化平台前綴那一處,名稱裡面的冒號與空白、前綴後面的反引號都留著。兩邊對不上就退回整條的行,等於回到修正前的行為:
   - B:第 5 行(舊)``[test:`given a: then b`]``(Kotlin 反引號名稱),第 6 行(新)→ 名稱 `given a: then b`,原文正規化後是 `given a:then b`,比對不到,退回整條,new 是 **True**。
   - C:第 5 行(舊)``[test:android: `my test`]``,第 6 行(新)→ 名稱 `android:my test`,原文正規化後是 ``android:`my test` ``,比對不到,退回整條,new 是 **True**。
3. 影響範圍:`new` 只進治理帳的 `extra.test_refs.items[].new`(`scripts/lumos` 裡讀 `info["new"]` 的只有 `_ns_tr_extra`),不影響擋或放。被拉偏的是 RETIRE-IF 第②條「名稱全在舊行上」的比例,誤差方向是把舊行算成新行,所以撤除條件比較不容易觸發。
4. 重現(在臨時 clone 跑,五個案例全部印 new=True):`python3.14 scratchpad/code-tb-r3/probe_isnew.py scratchpad/code-tb-r3/opus-clone/scripts/lumos`
5. 建議(用一條統一規則,不要逐個補字元):不要再拿正則去原文找名稱,改成把 span 裡每一行各自做 `slot_parse` 加 `_test_names_of`(`test` 與 `test-gone` 兩個鍵都看),名稱**在那一行的名稱清單裡**才算命中。這樣產生名稱跟找名稱用的是同一支切分,上面五種寫法都會自動對齊。同一族的測試要補 A 到 E 這幾種寫法,只補 `_` 子字串與全形冒號兩種不夠。

## F2 「列不出子模組清單就停掉剩下的名稱」那句新提醒沒有被測試釘住,刪掉它測試照樣全綠
severity: minor
blocking: 否
引句:「self.st["notes"].append("列推送版本子模組清單的 git 逾時或叫不起來,剩下的名稱這次不查")」
file: `scripts/test_lumos.py:64154`

1. 斷言用 `any("子模組" in x for x in st["notes"])`,但 `_NsTrJudge._judge` 對同一個名稱本來就會寫一行 `test_only_wd:判不了(列不出推送版本的子模組清單),不擋`,這行也含「子模組」。所以新加的那句(告訴人「剩下的名稱這次不查」)不管在不在,這條斷言都會過。
2. 翻紅驗證:在臨時 clone 只刪掉那行 `notes.append`,清掉 `__pycache__` 後跑 `python3.14 scripts/test_lumos.py -k t_note_shape_test_refs_git_fail_and_guard`,結果「2 passed, 0 failed」。
3. 這條斷言也只看 `st["out"] is True` 這個旗標,沒有驗「之後的名稱真的回 `skip`、不再叫 git」這個使用者看得到的行為。
4. 建議:斷言改比對「剩下的名稱這次不查」這幾個字;再補一個 judge 呼叫第二個名稱,斷言結果是 `("skip", …)`,而且 `_lens_git` 沒有再被呼叫。

## 另外確認過、沒問題的
- `_ns_tr_is_new` 的翻紅:把那行改回 `nm in lines[i - 1]` 以後,`t_note_shape_test_refs_line_attribution` 的 ④⑤ 會變紅(4 passed、2 failed),新斷言不是空轉。
- `_ns_tr_extra_merged` 的 ④:改回直接修改傳入的字典,`src` 就會變,斷言會紅;放在 ③ 前面,也不會動到 ③ 用的 `ev`。
- 正則特殊字元:有 `re.escape`。名稱前面緊接中文字時,Python 的 `\w` 把中文字當成字元,`search` 會往後找到 `[test:` 後面那一處,不會漏。`WHY:`、`https://` 這類原文冒號被正規化也不會讓名稱錯位,因為只是在行內搜尋,不靠位置。
- 三支被改的測試在臨時 clone 都綠(6/2/4 passed)。

## 圖譜鏡頭(固定席)
- `Systems/lumos-cli-read` ★INVARIANT★(search 預設排除 superseded、不排除 stale):這份差異沒動 search。不受影響。
- `Systems/design-loop` ★INVARIANT★(處置閘第五步):沒動處置閘或 loop 記帳。不受影響。
- `Systems/測試假綠形態` ★INVARIANT★(還原翻紅釘要配前置斷言,證明被測那條路真的有走到):`_ns_tr_is_new` ④⑤ 與 `_ns_tr_extra_merged` ④ 都是直接呼叫,一定走得到;`git_fail` ① 用 `r[0] == "undecidable"` 加原因,證明確實走到 ls-tree 那條路。合約本身成立,但 ① 對「提醒那一行」的釘子是空的,見 F2。
- `Systems/筆記內容閘`、`Systems/bound-tests-gate`、`Systems/每支檔有家`、`Systems/pitfalls-code-loop`、`Systems/loop-convergence-recording`:差異沒有改變它們宣稱的行為;兩支被改的檔都有家;圖譜裡沒有指向舊名 `_ns_tr_add_extra` 的引用。
- `Issues/code-loop守衛main-direct盲區`:跟這份差異無關。
- 計劃〈實作紀錄〉r2 那段跟這輪的代碼一致,〈做法〉4 的逾時語意也跟 `st["out"]` 的新行為一致。

最高等級:minor,blocking 共 0 條
