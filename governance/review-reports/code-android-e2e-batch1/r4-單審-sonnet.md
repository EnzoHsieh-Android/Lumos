severity: minor

## F1 字典鍵裡不同的孤立代理字元換成 U+FFFD 後撞鍵,靜默丟資料
severity: minor
blocking: 否

引句:「return {_e2e_fix_surrogates(k): _e2e_fix_surrogates(x) for k, x in v.items()}」

- 位置:`scripts/lumos:40573`(`_e2e_fix_surrogates` 的 dict 分支),呼叫者是 `scripts/lumos:40684` 的 `_e2e_record_update`。
- 失敗場景:紀錄裡有兩個鍵只差在不同的孤立代理字元,例如 `"a\ud800"` 與 `"a\ud801"`。兩個鍵都變成 `"a\ufffd"`,後者蓋掉前者,整份寫回後少一筆,沒有任何提示。
- 實際影響很低:紀錄的 schema 欄位固定,人寫的 waivers 是 list 內的 dict、鍵由工具定義。要發生得有人手改出這種鍵,而且這個欄位本來就是壞資料。這條只是標出不可逆的邊界,不是會在正常使用中發生的缺陷。
- 重現(修後 8eea52f7):對 `{"a\ud800":1,"a\ud801":2}` 呼叫 `_e2e_fix_surrogates`,得到 `{'a\ufffd': 2}`。
- 歸因:未判定。修前(aba0d9cd)根本沒有這個函式,舊行為是完全不處理,遇到孤立代理字元會整支崩潰。所以這是新增行為的一個極端邊角,不能算回歸,也沒有修前的對照結果。

## 三問

**① 原問題的修復效果有何行為證據?**
- claim:紀錄裡有孤立代理字元時,judge 照樣寫回、不崩,其他放行理由原樣保留。
- input:`t_android_e2e_judge_dirty_tree` 新增的情境,把紀錄的 `壞字` 換成 `壞\ud800字`。
- expected:rc 0,`waivers[1].reason == "壞\ufffd字"`,`waivers[0]` 的換行與 tab 保留。
- case_source:behavior-cases.json 的 G1 repair 與 preserve。
- before:在 aba0d9cd 的 lumos 上套用 8eea52f7 的測試檔,跑 `python3.14 scripts/test_lumos.py -k android_e2e_judge_dirty_tree`。結果是 `8 passed, 1 failed`,rc 1,`UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800'`,錯誤出在 `_bytes_atomic`。
- after:在 8eea52f7 上同一個命令,結果是 `9 passed, 0 failed`。
- comparison:同一個輸入,修前崩潰,修後通過。這是有證據的修復,也證明新測試抓得到原錯誤。
- preserve 的 waivers 換行與 tab 斷言在修前修後都過。
- 另外我自己跑的:輸入 `{"x":"\ud83d\ude00","e":"","l":["\udc00"]}`,成對代理字元已被 json.loads 合成 😀 並保留,空字串保留,list 內的孤立代理字元變成 �。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 只有 `scrub=False` 這條走新函式,唯一呼叫者是 `_e2e_record_update`(`scripts/lumos:40684`)。
- `scrub=True` 的兩個呼叫者(`scripts/lumos:40587`、`scripts/lumos:40618`)與 `steps.json` 的讀取(`scripts/lumos:40722`)都沒改。
- 遞迴深度已由前面的 `_events_depth_ok(raw, 20)` 限制,所以深層巢狀不會爆遞迴。
- 讀改寫的錯誤路徑(讀不懂就不寫)沒動。
- `_lumos_config_at_ref` 加 `rel` 參數的 docstring 修改只動文字。`kill_group` 的 docstring 與檔頭註解也只是文字,內容和程式實際行為一致(寬限結束後補 KILL)。

**③ 新發現的案例在修前、修後各是什麼結果?**
- 唯一新發現是 F1,修前沒有這個函式,所以沒有對照結果,歸因未判定。

總結:最嚴重是 minor,F1 字典鍵撞鍵;blocking 共 0 條。

**未驗範圍**
- 沒有跑 `-k` 的 macrobench、role_card、arch_target 全套。
- 沒有驗範本腳本的實機行為,本輪對 sh 腳本只改了說明文字。

我留下的 /tmp 現場是 `/tmp/lumos-seat-work/code-android-e2e-batch1/單審-sonnet/r4`。這個 clone 我已檢出回 aba0d9cd 後又切回原狀,沒有保留需要的資料,交由編排者刪除。測試沒有留下 gctl-run-* 現場。
