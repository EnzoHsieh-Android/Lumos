severity: clean

這是第 3 輪(末輪)審查,判的是這份 delta 有沒有跟專案既有做法(scripts/lumos 的 `_lens_*`/`_mainline_ref`、ci.yml 其他步驟對 BEFORE 的處理、doctor 給的既有寫法)長得不一樣。逐問回答如下,沒有發現需要擋的地方。

問1(分層與依賴方向,一致):ci.yml 的 code-loop gate 與 note-shape gate 兩步驟這次都只在 shell 端做「空字串→40 個 0」的純字串代換(`[ -n "$BEFORE" ] || BEFORE=0000000000000000000000000000000000000000`,ci.yml:105、128),真正的主線判斷、merge-base、要不要換空樹全部留在 `scripts/lumos` 的 `_lens_push_base`/`_mainline_ref`(scripts/lumos:28098-28162)算,三個呼叫點(node-home、note-shape、`_codeloop_guard_verdict`)共用同一支函式,shell 沒有重算 git 邏輯,也沒有跨層直呼 python 內部函式,依賴方向維持 shell → CLI(`python scripts/lumos <子指令> --diff`)→ 內部函式,跟既有分層一致。

問2(命名與錯誤處理,一致):兩個步驟的環境變數命名(`BEFORE`/`SHA`/`BRANCH`)、同一行 fallback 寫法、rc 判讀與 `::error::` 訊息風格都對齊,沒有各寫一套。doctor 給消費專案抄的單行建議(scripts/lumos:23891-23892)也同步補上語意相同的 GitHub Actions 表達式寫法 `${{ github.event.before || '0000000000000000000000000000000000000000' }}`;它跟 ci.yml 本身用 shell 變數不同,是因為 doctor 建議本來就是給人抄的單行 `- run:`,不能像 ci.yml 那樣先設 env 再用多行 shell——這個落差是既有慣例(上一版單行建議也沒有 env),不是這次新分岔出來的寫法,而且新增的測試 ⑥b(scripts/test_lumos.py 附近 `t_push_base_zero_or_missing`)有驗到這行文字确实出現。

問3(第二種做法是否還在,ci.yml 內一致;但 pre-push 仍留了一套獨立的):對整個 repo grep `4b825dc`、`EMPTY=` 確認 ci.yml 裡已經沒有殘留的舊寫法(先前那種 `EMPTY=4b825dc642...` + `case $BEFORE in 0*|"") ...` 的 shell 換空樹已經拿掉),code-loop gate 與 note-shape gate 兩步驟目前做法完全一致。ci.yml 裡還有一步「這次推送要跑哪個測試範圍」(ci.yml:30-40)自己用 `git cat-file -e "$BEFORE^{commit}"` 判斷要不要呼叫 `lumos pitfalls`,但它的失敗路徑是直接退回跑全套、不嘗試自己算出一個替代範圍,跟「換空樹」是不同性質的保守判斷,不在這次要修的「兩套做法」之列。真正還留著舊寫法的是 scripts/hooks/pre-push:它自己有一支 `pp_range_for()`(pre-push:34-45,靠 `git hash-object -t tree /dev/null` 算空樹、`git cat-file -e` 判本機找不找得到)以及另一段獨立的 `_hrange` 分岔點推導(pre-push:221-233,用 `git rev-list --not --remotes` 找不在任何遠端分支上的最早提交再往前一個),兩者都是在 shell 端自己算好範圍後,才把算好的 `_hrange`/`_range` 交給跟 CI 完全同名的 `home check --diff`、`note-shape --diff`(pre-push:236、247)。這正是 CLAUDE.md 這輪要收斂的「shell 換空樹」模式,而且目前只有 ci.yml 收斂進了 `_lens_push_base`,pre-push 這支还是自己一套。不過這支 hook 完全不在這份 diff 的改動範圍內、也不在本輪對照清單(`_lens_*`/`_mainline_ref`、ci.yml、doctor)裡,且檔內註解明講這是代碼審 r1 架構席已經核准、刻意跟另一段 `_range` 分開維護的既有設計(pre-push:219-220),不是這份 r3 delta 新引入或新造成的分歧,所以不算這份 diff 的擋點,列在這裡是給下一輪或另立 Issue 用的提醒,不計入本輪 major/minor。

不對齊共 0 條,其中 major 0 條。
