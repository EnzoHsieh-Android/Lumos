severity: minor

總評:照 spec 逐條實作,S1、S2、S3、S4 的核心行為我都做得出來,翻紅斷言寫得出(S1 對範本行斷言 XX_BROKEN、S2 造格式壞配方與重複、S3 造缺 old 的配方跑真 guard kill、S4 兩個待填字樣各一輪)。以下是沒有擋路但會讓實作者猜或讓使用者再卡一次的地方。

## F1 列出格式沒有「合約片段」,同檔同原文、合約不同的兩條配方長得一模一樣
severity: minor
blocking: 否
引句:「每欄先截字(原文取前 30 個字元)再經 `_kill_show`(會帶引號、跳脫控制字元)」
佐證行: `scripts/lumos:13320`(P2 的 item 文字附「合約片段」;既有 t_guard_kill_rm 的 ra 與 rc_ 就是同檔、合約不同)
1. 列出行只有 短身分、檔、原文前 30 字、test、平台,沒有 invariant。P2 與 guard kill 結果行都附合約片段,唯獨這份列出沒有。
2. 輸入:一篇筆記裡兩條配方 file、old 相同、invariant 不同(身分不同,各自合法,t_guard_kill_rm 的 rc_ 與 ra 就是這形狀,只差 old)。列出後兩行只差 12 字元身分,使用者(rtb 那種「要移除自己寫錯的兩條」)分不出哪條是哪條合約的,只能回頭用 guard kill 的結果行對。
3. 建議加一欄 `合約 <invariant 前 30 字>`(同樣先截再 `_kill_show`),或在 spec 明寫刻意不放的理由。

## F2 S4 的「合法配方不會含」在本 repo 自己的原始碼上不成立,而且沒有放行出口
severity: minor
blocking: 否
引句:「kill-add 多擋的是範本待填字樣(合法配方不會含),不擋推送或提交」
佐證行: `scripts/lumos:13496`(範本的 `"--old", "'<照現在的程式填原文>'"` 就寫在 scripts/lumos 這支檔本身,實作後 `<照新原文改寫的壞法>` 也會在)
1. 要驗證 S1(範本 `--new` 不抄舊壞法)的殺傷力,最自然的配方就是 `--file scripts/lumos --old "'<照新原文改寫的壞法>'"`(或含 `<照現在的程式填原文>` 的那行)換回舊寫法。
2. 照 S4 字面這條配方的 `--old` 含待填字樣,kill-add 一律擋下回 2,沒有任何旗標可放行;本 repo 自己的合約(guard-kill 節點的 ★INVARIANT★)就綁不了這類殺傷力配方。
3. 影響小(只擋範本那幾行),但「合法配方不會含」是錯的;建議改成「--old 與 --new 整串等於待填字樣、或以引號包著的整欄就是待填字樣才擋」,或明記這個已知限制與撤除條件。

## F3 `--json` 濾掉「所有底線開頭的欄」會連人寫在配方裡的底線欄一起吃掉,跟「內容不變」互相矛盾
severity: minor
blocking: 否
引句:「`--json` 輸出前濾掉所有底線開頭的欄(含既有 `_logged`),`--json` 內容與既有 `recipe_id` 欄都不變」
佐證行: `scripts/lumos:13955`(現況只濾 `_logged`,其餘欄位用 `{**r, ...}` 原樣帶出)
1. 配方是人手寫的 JSON,kill-add 之外的手改可以帶任意欄位(例 `"_comment"`)。現況 `--json` 會把它原樣帶到結果裡;照 spec 改成濾所有底線欄後,這種欄位從 `--json` 消失,與 S3 的「各筆結果的欄位跟改動前相同」及上面這句「內容不變」不一致。
2. 另一端:配方若自帶 `_rid`,要靠「`_rid` 蓋在 `{**r}` 之後」才不被偽造,spec 只說「換成帶 `_rid` 的副本」,沒寫順序。
3. 建議:只濾 `_rid` 與 `_logged` 兩個確切鍵名(或改用不可能出現在配方裡的內部欄名),並寫明 `_rid` 一律以算出來的值覆蓋。測試加一條「配方自帶 `_foo`/`_rid` 時 `--json` 與改動前一致、結果行 id 仍是真的」。

## F4 要同步的文件清單不齊,而且最會讓照 P2 修的使用者再卡住的兩句訊息不在清單裡
severity: minor
blocking: 否
引句:「[[Systems/guard-kill]] 的 kill-rm 用法與範本說明;skill 的 `commands/06-代碼審與推送.md` 那一列與 `scripts/lumos` 裡 kill-rm 的 HELP_WHEN 與 argparse help」
佐證行: `scripts/lumos:13520`(另見 13546、13571;`skills/lumos-project-notes/reference.md:595`、`skills/lumos-project-notes/commands/INDEX.md:36`、`docs/lumos-toolchain-knowledge/Systems/guard-kill.md:70` 與 `:101`)
我 grep `kill-rm` 得到清單漏掉的地方:
1. `skills/lumos-project-notes/reference.md:595` 寫「`lumos guard kill-rm <node> --id <短身分>`」,`commands/INDEX.md:36` 也列 kill-rm;`--id` 變選填後這兩處過時。
2. `Systems/guard-kill.md` 有兩處(第 70 行用法、第 101 行 kill-rm 段落)都寫「移除前印…範本(原文留給人照現在的程式填)」,spec 只說「用法與範本說明」,沒點出兩處,實作者容易只改一處。
3. `cmd_guard_kill_rm` 的兩句擋下訊息:`--id` 格式不對(13520)與「沒有身分以 … 開頭」(13546)只叫人去看 doctor P2 段——而 spec 這次要解的正是「P2 不列、原文對得上的配方」。使用者給錯短身分時被導去 P2,P2 還是沒有,等於原問題照舊;應改指「不帶 --id 跑 `lumos guard kill-rm <節點>` 會列出全部」。
4. `_guard_kill_rm_locked` 結尾「下一步:照上面的範本填好原文 kill-add…」(13571)現在只提原文,`--new` 也要填;spec 沒列這句。
5. `cmd_guard_kill_rm` 的 docstring 也寫「rid=短身分 … 至少 8 個十六進位字元」,可順手改。

## F5 列出格式仍有幾處要實作者猜(測試寫不死)
severity: minor
blocking: 否
引句:「欄位缺就印 `(缺)`,不是字串就印 `(不是字串:<型別>)`;平台沒寫印 `(預設)`(不讀設定檔)」
佐證行: `scripts/lumos:12935`(`_kill_recipe_id` 的「欄位缺」判準是 `isinstance(..., str)`,沒分 key 不存在與值是 null)
1. `<型別>` 用 Python 型別名(`int`、`NoneType`、`list`、`bool`)還是 JSON 型別名(number、null、array)?S2 測試要斷言字樣,兩種都合 spec。
2. key 存在但值是 JSON null,算「缺」還是「不是字串:NoneType」?`platform` 是空字串 `""` 時算「沒寫」(guard kill 以 `r.get("platform") or ...` 當預設)還是印 `""`?
3. 同身分重複配方合成一行時,test、平台、原文取第一條還是其餘?(同身分只保證 invariant/file/old 相同,test 可不同,kill-rm 自己會逐條印。)spec 只說合成一行。
4. 原文被截到 30 字時沒有任何截斷記號(spec 不放 `…`),使用者看不出被截;且 file、test、平台是否也截(「每欄先截字」只給了原文的數字)?test 名可能很長。
5. 「`_kill_show(json 原樣的前 60 字)`」:json 原樣是 `json.dumps(elem, ensure_ascii=False)` 還是加 `sort_keys=True`(`_kill_recipe_id` 用 sort_keys、`_kill_rm_show` 也用)?不寫死,兩處輸出可能不一致。
6. 最後一句「移除:lumos guard kill-rm <節點的可貼寫法> --id <短身分>」的 `<短身分>` 是字面佔位字,還是第一條的真身分?建議明寫「字面佔位字」。

## 其他節
- 範圍、做法、條款、回退、審計修正紀錄:已讀,交叉核對無矛盾(範圍的四件事對得上做法四段與 S1–S4;回退四項對得上;審計修正紀錄 r1「20 條/blocking 5」與正文折入項一致)。引句核對:「revert 實作提交:範本回到抄舊壞法、kill-rm 回到 `--id` 必填、guard kill 結果行不附身分、kill-add 不擋待填字樣」。
- 實務隱患:已讀,既有測試的說法我查證屬實(t_guard_kill_rm 的 ②③⑥b 斷言 old 與 note 出現在完整內容,不碰範本的 --new;_kr_recipe 的 new 是 `XX_BROKEN = 1`,S1 只對範本那一行斷言即可)。
- 做法的 S3 部分:`_rid` 在分組前算好、`{**r, ...}` 帶上、`--json` 另濾,我核對 9 個組結果處皆為 `{**r, ...}` 或 `res = {**r, ...}`,可行;唯一前提是 F3。

最高等級:minor;blocking 共 0 條
