severity: major

# 代碼審第 2 輪・正確性-opus

實驗環境:`git clone --shared` 到 `kcc-r2-work-正確性-opus/repo`(73bc8aff),探針腳本在 `kcc-r2-work-正確性-opus/probe/`(h.py 重用測試檔的 `_krc_cell`/`_kr_lum`,每格同時跑判斷函式與真的 `lumos guard kill --json`)。macOS、git 2.39.2、Python 3.14.6。區分大小寫的情境用 `hdiutil create -fs "Case-sensitive APFS"` 掛一顆磁碟映像,把 TMPDIR 指過去(repo 與 guard kill 的暫存工作樹都在上面),等同 Linux。基準:`-k kill_recipe_check_matches_guard_kill` 63 passed、`-k doctor_kill_recipe_drift` 27 passed。

## F1 unrestorable 在數原文之前判,原文對不上或讀不成 UTF-8 時跟 guard kill 判不一樣,提醒還寫「壞法套得上」
severity: major
blocking: 是
引句:「if _kill_pathspec(file) not in modes:」
file: `scripts/lumos:13264`
file: `scripts/lumos:13913`
file: `scripts/lumos:13922`

1. guard kill 的順序是:開檔 → 數 `old` → 次數不是 1 就判 drifted、`continue`(13913–13916)→ 次數是 1 才寫入、跑測試 → 最後才 `git checkout -- <file>` 還原(13922)。所以「還原會失敗」只有在原文恰好一次、而且讀得成 UTF-8 時才會發生。
2. `_kill_judge_file` 卻把還原檢查放在讀檔、數原文前面。路徑還原不回去、原文又已經對不上時,判斷函式回 unrestorable,guard kill 實際判 drifted,或者因為讀檔出錯直接當掉(rc1)。
3. 重現(probe/p1.py):
   ```
   == A1 結尾斜線 + 原文 0 次
      judge: unrestorable | 這樣寫路徑還原會失敗(…),改寫成 "prod.py"
      guard kill: rc=2 verdict=drifted detail=old 命中 0 次(需恰 1——配方漂移,重寫)
   == A2 ../wt/prod.py + 原文多次
      judge: unrestorable | …
      guard kill: rc=2 verdict=drifted detail=old 命中 2 次(需恰 1——配方漂移,重寫)
   == A3 結尾斜線 + 非 UTF-8
      judge: unrestorable | …
      guard kill: rc=1 … UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff …
   ```
4. kill-add 的提醒會講錯話(probe/p6.py,`--file prod.py/ --old "LIMIT = 42"`):
   `⚠ 提醒:"prod.py/" 壞法套得上,但這樣寫路徑還原會失敗(…),改寫成 "prod.py";guard kill 會判 error、同組後面的配方不跑。…`
   其實壞法根本套不上(原文 0 次)。使用者照這句只把路徑改成 `prod.py`、原文不動,重新 kill-add 之後還是 drifted。真正的問題(原文對不上)被這句蓋掉了。
   同一個提醒分支的引句:「msg = f"{f} 壞法套得上,但{res['detail']};guard kill 會判 error、同組後面的配方不跑。{fix}"」
5. 同一類順序問題:`new` 沒寫或不是字串時,guard kill 只有在原文恰好一次、要寫入時才會碰到 `r["new"]`(13919)。原文對不上的話,guard kill 判 drifted,判斷函式則判 malformed(probe/p7.py:G1 缺 new + 原文 0 次 → judge malformed / guard kill drifted;G2 new=5 也一樣)。docstring 寫「malformed=…或程式出錯」,但這種輸入 guard kill 並不會出錯。
6. 測試沒釘到:對照表裡標 unrestorable 的格子全都用預設的 `old="LIMIT = 5"`(恰好一次),沒有任何一格同時是「還原不回去」又「原文對不上」。
7. 修法方向:把 `_kill_pathspec` 這一關搬到 `n == 1` 之後(順序變成讀檔 → undecodable → 次數 → 還原);`new` 的型別檢查也放到次數判完之後再看,或在 malformed 那邊明寫只在原文恰好一次時才成立。對照表補「結尾斜線+原文 0 次」「../wt/+非 UTF-8」「缺 new+原文 0 次」三格。

## F2 test 欄不是字串時,判斷函式判 malformed,guard kill 卻照跑
severity: major
blocking: 是
引句:「bad = [f"{k} 沒寫或不是字串" for k in ("file", "old", "new", "test") if not isinstance(r.get(k), str)]」
file: `scripts/lumos:12920`
file: `scripts/lumos:13885`
file: `scripts/lumos:13886`

1. guard kill 判 test 名的寫法是 `_kill_method_name(r.get("test", ""), …)`,先 `str(test or "")` 再拿白名單 `^[A-Za-z_][A-Za-z0-9_]*$|^[\w .]+$` 比。數字 `5` 會變成 `"5"`,布林 `true` 會變成 `"True"`,兩個都符合第二段白名單,guard kill 會照常跑 baseline、套壞法。
2. 這輪新加的 `_kill_bad_fields` 規定 test 一定要是字串,所以這兩種輸入會被判 malformed。
3. 重現(probe/p1.py):
   ```
   == B1 test=5
      judge: malformed | 配方欄位格式不對(test 沒寫或不是字串)
      guard kill: rc=1 verdict=survived detail= whole-suite
   == B2 test=true
      judge: malformed | 配方欄位格式不對(test 沒寫或不是字串)
      guard kill: rc=1 verdict=survived …
   ```
   判斷函式說「guard kill 會拒跑」,實際上 guard kill 照跑還出了判定,屬於誤報。
4. 修法方向:test 不放進「要是字串」的清單,改成跟 guard kill 用同一個式子判:`_KILL_METHOD_OK_RE.fullmatch(_kill_method_name(r.get("test", ""), mp) or "")`。缺欄或 null 時這個式子本來就會變成空字串、被擋下,不必另外要求型別。對照表補 test=5 一格。

## F3 `_kill_alias` 拿「工作目錄裡這個名字存不存在」當作「檔案系統不分大小寫」的證據,在區分大小寫的檔案系統上會誤判
severity: major
blocking: 是
引句:「if not os.path.lexists(os.path.join(str(top), *pth[1:], name)):」
file: `scripts/lumos:13057`

1. 這支函式本來要回答的是:檔案系統把這個名字跟提交裡的某個名字當成同一支檔嗎?它實際問的卻是:工作目錄裡有沒有一支剛好叫這個字面的檔?在 Linux 或區分大小寫的 APFS 上,只要工作目錄有一支「未提交的大小寫改名」或「未追蹤的大小寫變體」,`lexists` 就成立,接著用 casefold 對到提交裡的另一支檔,判成 unrestorable,還叫人「改寫成」提交裡舊的那個名字。guard kill 的工作樹是從 HEAD 檢出、檔案系統又區分大小寫,根本開不到這個名字,判 drifted。
2. 重現(probe/p4.py,TMPDIR 指到區分大小寫的 APFS 映像):
   ```
   == D1 區分大小寫 FS:工作目錄把 prod.py 改名 Prod.py 未提交,配方寫 Prod.py
      judge: unrestorable | 這樣寫路徑還原會失敗(…),改寫成 "prod.py"
      guard kill: rc=2 verdict=drifted detail=file 開不了: [Errno 2] No such file or directory: '…/wt/Prod.py'
   == D2 區分大小寫 FS:未追蹤的 Prod.py 跟提交裡的 prod.py 並存
      judge: unrestorable | … 改寫成 "prod.py"
      guard kill: rc=2 verdict=drifted detail=file 開不了: …
   == D0 區分大小寫 FS:對照 PROD.py(工作目錄沒有)
      judge: missing | 不存在          ← 跟 guard kill 對得上
   ```
   D1 的建議還是反的:開發者正要把檔名改成 `Prod.py`,工具卻叫他把配方改回 `prod.py`,一提交就失配。
3. 測試沒釘到:對照表「大小寫跟提交裡不同」那一格的期望值寫成 `lambda root: "unrestorable" if os.path.exists(root / "PROD.py") else "missing"`,判準同樣是「工作目錄有沒有這支檔」,跟函式本身的假設是同一個。所以在 Linux CI 上它只會跑到 missing 那一支,永遠驗不到 D1/D2 的形狀。
4. 修法方向:對到候選名之後,再確認「字面名」跟「候選名」在檔案系統上是不是同一個實體,例如 `os.path.lexists(top/cand) and os.path.samestat(os.lstat(literal), os.lstat(top/cand))`。在不分大小寫的檔案系統上兩者 lstat 會是同一個 inode,照樣走別名;在區分大小寫的檔案系統上,改名(候選名已不存在)與並存(inode 不同)都不會被當成別名。

## F4 `_kill_pathspec` 拿「消掉 `.`/`..` 後的字面在不在 modes 裡」當作 git 還原成不成功,跟 git 真正的 pathspec 規則有落差,兩個方向都會判錯
severity: major
blocking: 是
引句:「return unicodedata.normalize("NFC", lit) if sys.platform == "darwin" else lit」
file: `scripts/lumos:13074`
file: `scripts/lumos:13264`

1. `git checkout -- <file>` 吃的是 pathspec,不是字面路徑。資料夾前綴、萬用字元、開頭冒號的 magic 寫法,以及 `core.precomposeunicode` 設定,都會改變它對到什麼。`_kill_pathspec(file) not in modes` 只認「提交裡有一支一模一樣的檔」,以下四種情況都對不上(probe/p2.py、p3.py、p5.py):
   ```
   == C1 x/../sub:字面是資料夾、實體是檔(x → deep/inner 的資料夾連結,deep/sub 是檔、sub/ 是資料夾)
      judge: unrestorable | … 改寫成 "deep/sub"
      guard kill: rc=1 verdict=survived              ← checkout -- sub 還原整個資料夾,成功
   == C2 s?c/x.py:連結名帶 ?(s?c → src)
      judge: unrestorable | … 改寫成 "src/x.py"
      guard kill: rc=1 verdict=survived              ← 萬用字元對到 src/x.py,還原成功
   == C4 :x.py(冒號開頭、頂層沒有 x.py)
      judge: ok |
      guard kill: rc=2 verdict=error detail=revert 失敗——後續同組配方作廢防污染   ← 漏報
   == E1 NFD 寫法、core.precomposeunicode=false
      judge: ok |
      guard kill: rc=2 verdict=error detail=revert 失敗——後續同組配方作廢防污染   ← 漏報
   ```
2. C4 與 E1 是漏報:判斷函式說沒問題,guard kill 卻在還原時失敗,同組後面的配方也全部作廢。E1 說明 docstring 寫的「macOS 上 git 把參數轉成組合寫法」其實要看 repo 設定,不是只看平台。`git init` 在 macOS 預設會寫成 true,但手動關掉、或從別處複製來的 repo 就不一定。
3. 這幾種輸入都偏刁鑽(要有連結加 `..`、萬用字元、冒號開頭的檔名或非預設設定),實務上很少碰到,所以標成不擋推送。但依共同規則,判斷函式跟真跑 guard kill 判得不一樣就算 major。
4. 修法方向(二選一):(a) 改成直接問 git,把 pathspec 規則交還給 git 自己算,例如在平台的 repo 頂跑 `git -C <top> ls-files --error-unmatch --with-tree=HEAD -- <file>`,一次涵蓋資料夾前綴、萬用字元、magic、precompose 與 `..` 超出 repo 頂;(b) 保留自己算,但至少也接受「在 dirs 裡」(資料夾前綴),precompose 改讀 `git config core.precomposeunicode`,並在計劃〈實作紀錄〉明寫萬用字元與冒號 magic 不在模擬範圍內,補一格對照把邊界釘住。

## F5 設定檔讀不了、配方又全是格式不對的時候,P2 不提設定檔,標題改說「原文對不上程式」
severity: minor
blocking: 否
引句:「return {"cfg_err": st["ctx"]["cfg_err"] if st["cfg"] else None, "items": st["items"], "total": st["total"]}」
file: `scripts/lumos:13338`

1. 只有當某條配方真的走到 cfg 那一步時,`st["cfg"]` 才會變成 True。格式不對的配方在讀設定之前就先回 malformed 了。所以只要配方全是格式不對的,`cfg_err` 就會回 None,doctor 改走 `elif _p2["items"]` 那一支。
2. 重現(probe/p8.py:`.lumos/config.json` 寫 `{bad`,唯一一條配方是 `{"file": 5}`):P2 只印「第 1 條配方欄位格式不對(…)」,標題是「有 1 條殺傷力配方的原文對不上程式(guard kill 跑到會判 drifted 或擋下…)」,整段完全沒提設定檔讀不了。可是 guard kill 跑這篇時,會先在「擋下:設定檔讀不了」那裡整篇拒跑。
3. 結果是使用者修好配方、再跑一次 doctor,才會第一次看到設定檔壞了,要多跑一輪。修法:有讀過設定(`st["ctx"]` 不是 None)而且 `ctx["cfg_err"]` 有值,就一律回報 cfg_err,不必看有沒有配方走到 cfg。

## 已驗、沒發現問題的部分(不算 finding)
- doctor Check T 的保護:設定正常時 `t_check = bound`,迴圈內容一字未改;收尾條件多出的 `not (bound and t_skipped)` 在 `t_skipped=False` 時恆為真,輸出跟改之前一樣。`pdata/split/methods_for/hay_for` 在 1657–1680 行以外沒有別處用到,跳過時不會出現 NameError。
- `_kill_pathspec` 的字面規則:`./sub//./p.py`、`sub/../sub/p.py`、`zz/../prod.py`、`[id]/p.py`(Next.js 式,git 先比字面)、檔名帶反斜線(非 Windows)、開頭冒號但頂層剛好有同名檔(`:prod.py`),判斷函式跟 guard kill 都對得上。
- 不分大小寫的 APFS 上,別名是連結、別名是資料夾、別名在中間層(`SRC/x.py`),兩邊都判 unrestorable/error,對得上。NFD 寫法配預設 precompose 也對得上。
- malformed 的 test 名白名單:跟 guard kill 共用 `_kill_method_name` 與 `_KILL_METHOD_OK_RE`,多平台前綴和 Kotlin 反引號的處理一樣(差別只在 F2 的型別預檢)。
- 設定檔讀不了時 P2 逐條走:格式不對的配方不管排在前面或後面都會列出來;`--ci` 會記 check-p2,沒有逐條記錄時也照樣補一筆節點空白的事件。

最高等級:major
