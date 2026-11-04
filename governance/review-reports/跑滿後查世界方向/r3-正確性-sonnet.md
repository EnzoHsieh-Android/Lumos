severity: major

外部審稿人第 3 輪(正確性席)。我逐節讀了 r3-snapshot.md,對照 `scripts/lumos` 的 `_cap_retro_check`(22399)、`_cap_retro_status`(22509)、`_cap_retro_next_lines`(22763)、`cmd_loop_cap_decision`(22797)、`cmd_loop_retro`(22851)、`cmd_loop_retro_stats`(22981)、`_loop_ts_key`(19357)、`_retro_text_ok`(22395)。也看了 `_secev_target_host`(10350)、`scripts/test_lumos.py` 的 `_cr_decide`/`_cr_retro_doc`(103441/103445)與 `_cap_real_cutoff`(50804),並實跑 Python 3.14 的 `urlsplit` 和 `_loop_ts_key` 的邊界值。

## 上一輪(r2)去向核對

- 正確性 c1(三種情況)、c2(統計來源)、c4(d1 措辭)、c5(測試釘常數、常數帶時區)、c8(同步點逐處列):這版在文字上補齊。我實測 README 和各手冊的行號,都對得上:`reference.md` 332/542/245/620、`05-設計審查迴圈.md` 22/23/33、`審查跑滿回顧_計劃.md` 98/134。
- c6(網址):`://` 後空白那個洞補了,但留下新的洞,見第 1 條。
- c7(提示面):只補了「已有人裁」分支和 `--template` 提示。`_cap_retro_record_block` 與處置閘第八步仍沒補,見第 7 條。
- c2 的「沒填」口徑:新引進的統計沒定義,見第 3 條。

## 逐條 finding

1. 網址檢查的例外處理範圍只涵蓋 `urlsplit`,`port` 在組鍵時才丟 ValueError,會吐堆疊。
引句:「`url` 去頭尾空白後用 `urllib.parse.urlsplit` 解(解不開、丟 ValueError,算這一項的錯,不丟例外)」
   - 輸入:兩項 source,`https://a.com:abc/x` 與 `https://b.com/y`,`verdict: direction-ok`,`point` 各夠 10 字。
   - 我實測:`urlsplit("http://a.com:abc/x")` 不丟例外,`hostname` 是 `a.com`,所以 spec 寫的「scheme 對、hostname 非空」都過。
   - 之後取 `.port` 才丟 `ValueError: Port could not be cast to integer value`。`http://a.com:99999` 同樣。
   - spec 把 `port` 放在「兩項以上時比」的鍵裡,而且只在 `urlsplit` 那句掛了「丟 ValueError 算這一項的錯」。照字面實作,`.port` 會在組鍵的地方、try 外面被讀。
   - 結果:`--check`、`--record` 吐 traceback,違反 S2 的「不丟例外」。
   - 同一個 `https://a.com:abc/x` 單獨出現在 undetermined(一項 source、不組鍵)會判過;出現在兩項以上卻會炸。同一個網址有兩種結果。
   - 對照:repo 自己的 `_secev_target_host` 在 try 裡主動讀 `u.port` 觸發這個例外,spec 借了它的取主機名,沒借這一行。
   - file: `scripts/lumos:10360`(`_secev_target_host`:`u = urlsplit(t)`、`_port = u.port` 一起放在 try 裡)
severity: major
blocking: 是——照字面實作會對一個合法形狀的輸入丟堆疊,直接違反 S2 明寫的「不丟例外」。

2. retro-stats 的世界查證統計讀的是 `不管` 情況下沒驗過的內容,和「不讀、不驗、不寫帳」自相矛盾。
引句:「`retro-stats` 的世界查證統計讀 `_cap_retro_status` 回的已驗回顧內容(跟它數族別、行動項同一個來源),不讀事件:每個迴圈只算一次(最新人裁之後那份回顧),只數最新人裁是 extra-round 的」
   - 對照第 59 行:「world_check 整段不讀、不驗、不寫帳,不論 version 是幾、裡面填了什麼」。
   - 這句只用「最新人裁是 extra-round」過濾。`不管`(人裁 ts 早於常數的 extra-round)也是 extra-round,也會進統計。
   - 輸入:合併當天前後仍在途的迴圈。人裁 `2026-11-04T22:00+08:00`,回顧在 11-06 才寫。
     - 回顧檔用新工具的 v2 骨架(內含 `world_check` 空殼)。
     - 第 1 點的提示又叫人「把查方向的結論寫進回顧的 world_check」,所以編排者照做。
     - 這個迴圈判 `不管`,`world_check` 整段沒驗。填 `"world_check": "已查,方向對"` 或 `"verdict": "對"` 都過 `--check`,也不寫 `world_verdict`。
   - 統計端 `data["world_check"]`:
     - 若是字串,`.get` 丟 AttributeError。
     - 這個例外落在 `cmd_loop_retro_stats` 逐迴圈的 `try` 裡(23002 讀 data、23009 `except`)。整個迴圈被改歸成「判不了(error)」,已記回顧的迴圈數被扣掉一個。
     - 若剛好是 `{"verdict": "direction-ok"}`,沒驗過就被數成「方向對」,而治理帳上沒有對應的 `world_verdict`。事件和統計對同一個迴圈說法不同。
   - 這正是 [[Systems/loop-retro]] WHY d7 防的「任何一處另判就會口徑分岔」。spec 沒有指名一支共用的「這筆人裁屬於要求/選填/不管」判定函式讓 `_cap_retro_check`、`--record`、`retro-stats` 一起呼叫,三處各自重算。
   - file: `scripts/lumos:23002`(統計只看 `key == "recorded"` 就取 data)、`scripts/lumos:22573`(`_cap_retro_status` 對 `不管` 一樣回 data)
severity: major
blocking: 是——一個真實在途的輸入會讓統計把已記回顧的迴圈改判 error,或數進沒驗過的結論,違反同一份 spec 的第 59 行。

3. 「沒填 L」沒有定義,迴圈在不同狀態下歸類不明。
引句:「印一段「世界查證結論(加開的迴圈):方向對 N、要換方向 M、判不準 K、沒填 L」」
   - `要求` 的迴圈只要是 `recorded`,`world_check` 就一定驗過,不可能「沒填」。
   - L 只能裝這幾類,spec 沒選:
     - `skipped`、`stale`、`none`(還沒寫回顧)
     - 不適用(沒有卷證)
     - 判 error
     - 前述 `不管` 的舊迴圈
   - 九、十月的舊 extra-round 迴圈全屬 `不管`,一旦算進 L,「沒填」永遠有一個灌水的底數,而且隨 `none` 迴圈寫完回顧而減少。
   - RETIRE-IF 用 N+M+K 當分母看「判不準過半」,L 不影響,所以只是量測口徑。
   - 但 S6 要求印出四個數,沒有口徑就寫不出會紅的測試。
   - file: `scripts/lumos:22981`(`cmd_loop_retro_stats` 現有 totals 表,state 與 key 的分法在 22995 起)
severity: minor
blocking: 否——只影響回頭看的量測,不影響放行與擋下。

4. 第 1 點的提示對 accept-risk 和舊迴圈講錯話,另一處的條件也沒寫死。
引句:「「已有人裁」那一支與 `cmd_loop_cap_decision` 記成 extra-round 成功後印的「繼續之前先寫跑滿回顧」都補一句「把查方向的結論寫進回顧的 world_check(還沒查就先查)」」
   - 「已有人裁」那一支的分支條件是 state 在 none/stale,不看 decision 種類。
     - `accept-risk` 的迴圈也會被叫去「還沒查就先查」,和〈不做〉的「不在 accept-risk 時強制」互相矛盾。
     - `不管` 的舊 extra-round 迴圈被叫去填一個工具不讀的欄位,正是第 2 條輸入的來源。
   - `cmd_loop_cap_decision` 那邊只說 extra-round 才印,同一條「已有人裁」分支沒有對應條件。
   - 「先上網查這條路的方向(至少兩個來源)」這句沒寫在 `if ask:` 底下。
     - 若實作成 `if ask` 之外,「可以停」的提示也會印「結論附在請人裁的訊息裡」,但那時根本沒請人裁。
     - 這和 [[Systems/loop-convergence-recording]] 的 PITFALL(「還沒有人裁而提示不是可以停或判到 cap-reached 才叫人記」)同一條邊界。
   - 「至少兩個來源」也和檢查的 undetermined 零來源不一致,提示沒給「判不準」的出口。
   - file: `scripts/lumos:22790`(「已有人裁」那條 `lines.append` 沒看 `dec`)、`scripts/lumos:22780`(`if st["decision"] is None:` 底下 `if ask:` 的位置)
severity: minor
blocking: 否——只是提示文字,檢查本身不受影響;但它導致第 2 條的輸入。

5. 生效常數晚於實際合併日時,已記回顧的迴圈會翻成過期,只有人工把關。
引句:「相容三:實作合併若晚於常數訂的日期,中間人裁加開的迴圈會被要求補 world_check;常數在合併前一刻再確認一次」
   - 常數是「實作合併日隔天零點」,寫在程式裡。寫程式當下並不知道合併日,要審 3 輪、推送前閘,日期通常會滑。
   - 常數 T 之後、合併前,用舊工具人裁並 `--record` 的迴圈,在新工具下:
     - `_cap_retro_status` 對指紋相符的回顧重驗,`不管` 變成 `要求`。
     - v1 回顧過不了檢查,`recorded` 翻成 `stale`,處置閘第八步變 ✗。
   - 補救靠編排者「合併前一刻再確認」,沒有測試、閘或 doctor 項目綁這件事。
   - 〈回退〉也不救它:拿掉驗法才會恢復,常數改不回去。
   - file: `scripts/lumos:22569`(`_cap_retro_status` 每次重驗 `recorded` 的回顧)、`scripts/lumos:22571`(不通過就改判 `stale`)
severity: minor
blocking: 否——spec 已自述這個風險並給人工步驟;缺的是機械綁定(例如測試斷言常數晚於本提交的提交時間)。

6. S5 與做法第 3 點對 `不管` 的 version 說法不一致。
引句:「world_check 整段不讀、不驗、不寫帳,不論 version 是幾、裡面填了什麼」
   - 做法第 3 點開頭是「`version` 收 1 或 2」。`不管` 的迴圈若 version 是 3、`"2"`、`2.0`、`true`,仍照舊被擋。
   - S5 寫「不論 version 是幾、world_check 填了什麼(含型別不對),應照舊過」。綁 S5 的測試若取 version 3,會和實作矛盾。
   - 兩處各說各話,實作者怎麼選,測試都能綠。
   - file: `scripts/lumos:22419`(現有 `v == 1` 的整數判斷,spec 改成 1 或 2)
severity: minor
blocking: 否——措辭層,把「不論 version 是幾」改成「version 是 1 或 2 時」即可。

7. r2 正確性第 7 條只補了一半:`canary record` 擋下訊息與處置閘第八步仍沒提 world_check。
引句:「`--template` 的 stderr 提示「編排者補 avoid 與 changes、填 completed_by」補上 world_check」
   - 新會談最先碰到的是 `canary record`(記新一輪)被擋,訊息「怎麼做:…」走 `_cap_retro_fix_cmd`,只講 `--template --write`。處置閘第八步同樣。
   - 查方向的結論只在原會談的對話裡,新會談看不到這一步,要等 `--check` 報缺才知道。
   - r2-intake 的 G6 只折了「已有人裁分支」和 `--template` 兩處,沒有交代這兩個擋下路徑為何不補。
   - file: `scripts/lumos:22694`(`cap-retro-missing` 的「怎麼做」)、`scripts/lumos:22736`(處置閘第八步印修法)
severity: minor
blocking: 否——`--check` 會逐欄列出缺什麼,不會放行;只是提示面不一致。

8. 網址檢查比 repo 既有的取主機名 helper 寬,且同頁寫法的天花板列得不全。
引句:「兩項以上時比「(scheme 小寫, hostname 小寫, port, 去掉結尾斜線的 path, query)」這組鍵」
   - `_secev_target_host` 明寫:授權段含反斜線、空白、百分比編碼就判不出來,理由是「各家 URL 解析對這幾種不一致」。
   - spec 只要求「`hostname` 不是空的」。`https://exa mple.com/a`、`https://a.com\x00/a` 這類主機名過檢查,而且和 `https://a.com/a` 算成不同來源。
   - 預設埠的同頁寫法也沒在天花板列到:`https://a.com:443/x` 和 `https://a.com/x` 的 port 一個是 443、一個是 None,算成兩個來源。〈天花板一〉只提 `www.` 和追蹤參數。
   - file: `scripts/lumos:10364`(`re.search(r"[\\%\s]", u.netloc)` 才是既有的寫法)
severity: minor
blocking: 否——格式檢查本來不保證真查過,屬已承認的天花板範圍;補一句列進天花板一或照 `_secev_target_host` 加一道即可。

## 各節已讀,無獨立 finding

- 〈問題與最小解〉〈不做〉〈回退〉:已讀。〈回退〉說「version 收 1 或 2 那段留著」只涵蓋部分回退;整支 revert 時,已記 v2 的回顧由舊工具判 `stale`,spec 的相容二已記此風險。
- 第 0 點(手冊)、第 5 點(同步點)、第 6 點(寫回)、S1、S3、S4、S7、S8:已讀。我開檔驗過 `reference.md` 332/542/245/620、`05-設計審查迴圈.md` 22/23/33、`templates.md` §9、README 兩份、`docs/指令參考.md`/`command-reference.md` 136/137,位置都存在。`skills/` 沒有釘「查不到就寫查了哪些詞」那句的測試,擴充不會撞既有測試。
- 三種情況的判定:
  - 多筆人裁:判斷只看最新一筆,`_cap_retro_status` 的最新人裁(22535)與 `cmd_loop_retro` 的最新人裁(22874)取法一致。
  - `ts` 邊界:實測 `_loop_ts_key` 對沒帶時區的日期回 None,對 `"2026-11-05T00:00:00+08:00 "`(帶尾空白)丟 ValueError 被內部接住,對非字串的真值丟 AttributeError。spec 的「先驗是字串再呼叫」寫對了。
  - 真實治理帳 29 筆 loop-retro 事件的 `ts` 全是 `+08:00` 完整格式,解不開的路不會誤傷既有迴圈。
  - 人裁後改回顧:常數只看人裁的 `ts`,與回顧內容無關,改檔只走既有的指紋失效,沒有新的翻轉路徑。
  - `world_verdict`:只在檢查通過時寫,值取常數本身,這條寫對了。

## 實務隱患逐類

- 併發:無新風險。`--record` 驗證與算指紋用同一份位元組。`--check` 與 `--record` 之間夾入新的人裁時,`_cap_retro_status` 以最新人裁重驗,不合就判 `stale`,寧擋不放。`accept-risk` 後同時被追加 `extra-round` 的順序,實測的結果仍是 `stale`(`要求` 不通過)。
- 效能:無。檢查對象被 `_RETRO_MAX_BYTES`(256KB)封頂;網址鍵用集合比對即可。壞項極多時問題清單逐條印出不封頂,這是既有欄位的同一行為。
- 資源:無。工具不上網、不開新檔。
- 回滾:見〈各節已讀〉的回退註記;第 5 條是常數與合併日的耦合,不屬回滾。

## 圖譜節點(逐條判)

- `Systems/loop-retro`:0 條合約,不受破壞。
  - WHY d7(五處共用同一支合格判定)被第 2 條的缺口碰到:spec 沒指名共用的情況判定函式,統計端另算。
  - WHY d2(起草獨立)不受影響。骨架在派工前就含 `world_check` 空殼,但派工詞的「只改下面列的欄位」讓起草者不動它,spec 另寫「派工前不寫進回顧檔」也成立。
- `Systems/loop-convergence-recording`:0 條合約。其 PITFALL(「人裁入口只放在 cap-reached 那段等於沒人看得到」)的條件邊界與第 4 條的 `if ask` 位置有關,否則不受影響。
- `Systems/每輪修補差異派工`:0 條合約。既有 `[不選:只在跑滿或卡關時才查]` 與新 WHY 的區分(修法 vs 方向、主觸發仍在第二輪)成立。不影響,因為它否決的是把查修法延到跑滿。
- 計劃 `Projects/跑滿後查世界方向_計劃`:d1 與正文、白話段觸發條件現在一致,r2 第 4 條已修好。

最嚴重等級 major,blocking 2 條。
