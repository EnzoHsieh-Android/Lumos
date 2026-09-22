severity: blocker

## F1 逾期合約已被列成「另有 N 條逾期」,S15 結尾卻印「沒有逾期或快到期的預告合約」,自相矛盾

severity: major
blocking: yes

`run_doctor` 新增了 `_gover_other`(碰不到的逾期合約清單)並用 `warn_soft` 印出來,但 S15 段落結尾那個「全都沒事」的 ok 訊息只檢查 `_gover` 和 `_gsoon`,沒有一併檢查 `_gover_other`:

引句:「if _gover_other:」
引句:「if not _gover and not _gsoon:」

重現:在臨時 vault 建一篇 `Systems/Pay.md`(`about_code: [scripts/pay.py]`),`guard plan` 一條逾期合約,`--touched-from` 給一個不含 `scripts/pay.py` 的清單(例如空檔或只含 `scripts/unrelated.py`),跑:
```
python3 scripts/lumos --vault <vault> doctor --ci --touched-from <touched.txt>
```
實測輸出(節錄自我在 /tmp 臨時 vault 跑出來的真結果):
```
⚠ 另有 1 條逾期的預告合約,但這次改動沒碰到它們(不擋這次推送):
    • 退費那條逾期了(負責人 enzo,最遲 2026-09-19);Verification/...
建議: 推送前的閘只擋你這次碰到的...
✓ 沒有逾期或快到期的預告合約
```
前一句剛講「還有一條逾期」,下一句立刻講「沒有逾期」。這不是風格問題:doctor 的輸出是給人(或下一個讀圖譜的 AI)判斷現況用的,結尾的 `ok()` 訊息是唯一會被掃過去、當「全都乾淨」訊號讀的那一行,兩句話矛盾會讓人誤信「沒事」。
不影響 exit code(退出碼仍照 `_gover` 正確判斷),所以不是 blocker,但這是這次新增邏輯自己漏接既有收尾檢查造成的,新加的三支測試都只驗退出碼與清單內容,沒有人驗過這行收尾訊息,漏網。

## F2 `about_code` 跟推送清單只做「一字不差」比對,沒有正規化——`./` 前綴、結尾斜線、大小寫、資料夾寫法全部比對失敗,逾期合約永遠判成「沒碰到」

severity: blocker
blocking: yes

`_guard_touches` 算「有沒有碰到」用的是純字串集合交集,沒有做任何路徑正規化:

引句:「files = [str(x).strip() for x in as_list(hn.fields.get("about_code")) if str(x).strip()]」

重現(四種都在臨時 vault 實測過,結果一致):功能節點 `about_code` 寫成 `./scripts/pay.py`(或 `scripts/`、`Scripts/Pay.py`、`scripts/pay.py/`),`--touched-from` 給 `scripts/pay.py`(這是 `git diff --name-only` 真正會吐出來的樣子,不會帶 `./` 前綴):
```
$ echo "scripts/pay.py" > touched.txt
$ python3 scripts/lumos --vault <vault> doctor --ci --touched-from touched.txt
rc=0
⚠ 另有 1 條逾期的預告合約,但這次改動沒碰到它們(不擋這次推送):
    • 測試逾期(負責人 enzo,最遲 2026-09-19);...
```
四種寫法(`./scripts/pay.py`、`scripts/`、`Scripts/Pay.py`、`scripts/pay.py/`)全部得到同樣結果:rc=0,判成「沒碰到」,即使 `scripts/pay.py` 真的被改了。

為什麼是 bug 不是風格:這支功能的唯一賣點就是「靠 about_code 精準算出有沒有碰到」(commit 訊息:「算不出某條跟哪些檔有關時,本機放行、交給 CI 擋,列表會講明為什麼算不出來」)。但這裡不是「算不出來」——是**算出了錯的答案卻裝成正常**:沒有印出「格式對不上」之類的警語,列表裡就是安安靜靜地把它歸進「沒碰到」那一堆,跟真的沒碰到的合約長得一模一樣。`about_code` 的寫法本來就沒有強制規範(這個 repo 自己的 `Systems/*.md` 也能看到 `./` 前綴混用),只要家節點用 `./` 開頭寫(很自然的相對路徑寫法),這條本機收窄機制就對那個家節點永久失效——不是失效一次,是只要沒人發現,永遠都判不出碰到,本機這道閘形同虛設(CI 那邊沒有這個旗標,仍然會擋,但本機端完全喪失設計初衷)。三支新測試裡 `about_code` 跟 `--touched-from` 給的字串都寫得一模一樣,沒人測過任何路徑寫法差異,漏網。

## F3 `guards:` 欄位若手改成兩個以上的值,只有第一個會被拿去算「有沒有碰到」,第二個家節點被完全忽略

severity: major
blocking: yes

`_guard_touches` 呼叫既有的 `_guard_home_of` 取得守衛節點指回的功能節點,但那支只取清單第一個元素:

引句:「home = _guard_home_of(gn)」

重現:手改一個守衛節點的 `guards:` 從一個值變兩個(`Systems/A`、`Systems/B`),`A` 的 `about_code` 是 `scripts/a_only.py`、`B` 的是 `scripts/b_only.py`。`--touched-from` 只給 `scripts/b_only.py`(真的碰到 B 管的檔):
```
$ echo "scripts/b_only.py" > touched.txt
$ python3 scripts/lumos --vault <vault> doctor --ci --touched-from touched.txt
rc=0
⚠ 另有 1 條逾期的預告合約,但這次改動沒碰到它們(不擋這次推送):
    • 多家守衛測試...
```
實際上這次推送真的碰到 `scripts/b_only.py`,卻被判成沒碰到——因為只看了 `guards:` 第一項(`Systems/A`),`Systems/B` 整篇連同它的 `about_code` 直接被丟掉,不是「算不出來」而是「算了一半就當算完了」,而且不像 F2 那樣至少列表項目本身沒有異常提示。`_guard_home_of` 的型別檢查(`isinstance(g, list)`)本身就暗示 `guards:` 設計上是支援清單的,這支新函式沒有照這個假設處理多值情形。目前 `guard plan` CLI 永遠只寫一個值,所以要出現這個情境需要手改檔案,但 CLAUDE.md 與這個 repo 的討論脈絡本來就承認手改欄位是常見情境(guard-kill.md 的 RULE 行也提到「規則只認節點身上有 guards 欄位…手寫 status: pending 的人不該被拖進整套規則」,顯示手改是預期會發生的路徑)。

## F4(非阻擋,行為紀律)一篇功能節點掛兩條逾期合約時,只要碰到其中任一支檔,兩條都會被判成「碰到」,即使第二條合約其實跟你改的檔完全無關

severity: minor
blocking: no

引句:「靠守衛節點→家節點→about_code 兩跳算交集」

重現:`Systems/Pay.md` 的 `about_code` 同時列 `scripts/pay.py` 與 `scripts/ship.py`,底下掛兩條逾期合約(「第一條逾期」「第二條逾期」)。`--touched-from` 只給 `scripts/pay.py`:
```
⚠ 有 2 條預告的合約已經逾期(不准延期,只能做完或棄置):
    • 第一條逾期(...);你這次改到 scripts/pay.py
    • 第二條逾期(...);你這次改到 scripts/pay.py
```
兩條都被擋,即使「第二條逾期」實際上可能跟 `ship.py` 那部分邏輯有關、跟這次真正改的 `pay.py`無關。這是演算法本身的設計粒度(交集算在「整篇家節點管哪些檔」而不是「每條合約各自管哪些檔」),不是程式碼跟自己文件矛盾的錯誤,所以不算 blocking,但這代表「本機只擋你這次碰到的」這句話的精確度,取決於同一篇家節點底下有沒有混放多條不相干的合約——家節點切得越粗,收窄的效果越差,值得記一筆,不確定作者有沒有意識到粒度是「每篇家節點」而不是「每條合約」。派工單三支新測試裡沒有任何一支測過「同一個家節點掛兩條合約,只碰其中一條所管的檔」這個情境。

## F5(非阻擋)`_TOUCHED_F` 暫存檔沒有放進 `_PP_TMP`、不受既有的訊號安全 trap 保護,但實測正常路徑與訊號中斷都沒有真的洩漏

severity: minor
blocking: no

引句:「_f="$(mktemp "${TMPDIR:-/tmp}/lumos-prepush-touched-XXXXXX" 2>/dev/null || true)"」

`pp-push` 既有機制專門為了「被擋下或收到訊號時暫存檔會在 $TMPDIR 累積」這個問題建了 `_PP_TMP` 目錄 + `trap '...; rm -rf "$_PP_TMP"' EXIT INT TERM`(`scripts/hooks/pre-push:95-100`,未改動的既有程式碼),註解明講「本次推送所有暫存檔的家,離開時整個清」。但這次新增的 `pp_touched_file()` 建的暫存檔是直接建在 `$TMPDIR` 底下、不在 `$_PP_TMP` 裡面,不受那個 trap 保護——結構上確實跟既有的「所有暫存檔都收進 `_PP_TMP`」慣例不一致。

實測:寫了一支注入 `sleep 3` 的 pre-push 副本(只在 /tmp 跑,沒碰正式 repo),在 `_TOUCHED_F` 建好、還沒清掉的窗口送 `SIGTERM`:0.2 秒後檔案跟行程都還在,但因為既有 trap 本身沒有呼叫 `exit`,腳本收到訊號後會執行 trap 再繼續往下跑,最後還是會跑到 `doctor` 判定式裡「擋下才 rm / 沒擋也 rm」的既有清理行,約 1.5–1.9 秒內就自己清掉了——沒有觀察到真正永久洩漏。會不會真洩漏取決於 bash 既有 trap 設計本身收不收訊號後 exit,而那段 trap 是既有程式碼、不在這份 diff 裡,所以我把這條記成「結構上沒跟既有慣例一致、但這次實測沒有證出真的洩漏」,不算擋。

## 我實際跑過的路徑(沒寫進上面五條的,列在這裡)

- ①空檔、純空白行、路徑前後空白、重複路徑、含中文檔名(`scripts/付款.py`)、含 `..`(`../scripts/付款.py`)、絕對路徑(`/abs/scripts/付款.py`)混在同一份清單:全部正確去空白/去重/忽略雜訊,精準比對到中文路徑那一行,沒有 crash。
- ①非 UTF-8 內容(夾雜 `\xff\xfe\x00`、UTF-16 代理對字節)、無讀取權限(`chmod 000`)、檔案不存在:非 UTF-8 用 `errors="replace"` 不會炸、且不會誤配對;無權限與不存在都正確落到「讀不到就回 None(=CI 模式,全擋)」那條路,rc=1,符合文件裡「打不開是我們自己的問題,不該因此少擋一條」的宣稱。
- ⑤`guards:` 指到不存在的節點名(`Systems/NotExist`)、指到自己(守衛節點自己的 relpath):兩種都正確落到「找不到節點/沒寫 about_code」分支,本機放行且訊息講清楚為什麼,沒有 crash 或無限遞迴。
- ⑥新分支(remote 沒有這個 ref,用全零 sha)、force-push 後本地缺 remote 物件、一次推兩個 ref(`feat-a`+`feat-b`,分別動不同檔,驗證聯集正確只擋碰到那條)、推送刪除 ref(local_sha 全零)混在同一批 stdin:全部在真的 git repo(建在 /tmp,不是 lumos-toolchain 本體)跑完整支 `scripts/hooks/pre-push`,行為符合預期,沒有 crash。
- ⑦「被擋下那條路」與「doctor 判過但沒有 vault」兩條路都會執行到 `rm -f "$_TOUCHED_F"`(前者在 if 內、後者在 if 外的無條件行),兩種路徑實測都有清掉。
