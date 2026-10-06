severity: clean

## 鏡頭 1 修正差異的正確性:已讀無 finding
- 減號判斷只比開頭一個字元。合約片段中間有減號(例 "a-b"、"上限-1")、平台名正常(例 "ios")都不會被擋。實跑 _kill_cmd_arg:'a -b' 回 'a -b'(已引號),'-'、'--'、'-1' 回 None。
- 回 None 後的分支:platform 分支 want 為 None 走「kill-rm 後改用合約綁的平台重新 kill-add{unsafe}」,通順;unbound 分支 inv 或 plat 為 None 走「要讓推送閘也守它就手動 guard bind{unsafe};或 kill-rm …」,通順。兩條都不貼未處理的字(scripts/lumos:15068-15084 一帶)。
- 其他字實跑:空字串回 "''"(有引號,貼上是空參數,非注入);純空白回 "'  '";"~"、"~root" 回帶引號的 '~'(shlex 已引,不會被展開);" -x"(前導空白)回 "' -x'",argparse 視為位置參數;Unicode 減號與破折號不是 ASCII '-',argparse 不當選項。無新洞。
- 過寬擋(無害):含空白的 "-x 上限"、"-1" 在 argparse 其實當位置參數收,現在也不印指令。後果只是改印文字說明,不出錯,不標。
- 同類未處理(範圍外、既有):_kill_node_arg 對 "-" 開頭的節點名沒擋;但 rel 一律在 Systems/、Projects/ 這類子目錄下,實際到不了。
- unsafe 文字「合約片段或平台名含控制字元或以減號開頭」在 platform 分支只會是平台名觸發,文字略寬但不誤導。
引句:「return None if _path_special_chars(s) or s.startswith("-") else _sh_quote(s)」
引句:「unsafe = "(合約片段或平台名含控制字元或以減號開頭,不印可貼的指令)"」

## 鏡頭 2 測試:已讀無 finding
- 跑 -k kill_add_warns_test_not_bound:22 passed;-k doctor_kill_test_not_bound:11 passed。
- 突變:在臨時目錄複本把 `or s.startswith("-")` 拿掉,新增兩格(⑮合約片段減號開頭、⑮平台名減號開頭)都翻紅,輸出可見 `lumos guard bind Systems/L -x Foo` 與 `--platform -p` 被印出。新增的兩格有咬力,舊格不受影響(⑭ 的 pd 多加 "-p" 平台不影響 bad/esc 斷言)。
引句:「("平台名減號開頭", {"invariant": "上限", "test": "Foo", "platform": "-p"}」
引句:「pd = {"multiplatform": True, "default_platform": "py", "platforms": {"py": {}, bad: {}, esc: {}, "-p": {}}}」

## 鏡頭 3 圖譜:已讀無 finding
- guard-kill.md 的兩條 INVARIANT 管 guard kill 的 rc 優先序與 --json 純淨度;本修正只改提醒文字的產生(_kill_cmd_arg 與 _kill_binding_msg),不碰 guard kill 的 rc 或 stdout,不影響。
- lumos-cli-read / lifecycle / design-loop / 測試假綠形態 的合約各管 search、re-inject、處置閘、翻紅釘;修正與其無關。翻紅釘一條,本次測試已實測還原即紅且前置斷言(msg 非空)成立,符合。
- 其餘 RISK 與超限節點只列名,未見牽連。
引句:「kill-add、guard audit 定位與 doctor 對回合約行共用這一支」

## 鏡頭 4 角色卡
未附卡,略過。

總結:修正在 _kill_cmd_arg 的減號判斷正確、各分支文字通順、測試實測還原即紅;試過空字串、純空白、~、中間減號、Unicode 減號都沒新洞,無 finding。
