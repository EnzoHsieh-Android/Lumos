severity: major

我逐節讀完 r2-snapshot.md,並在臨時目錄用 Python 3.14 匯入 `scripts/lumos` 實測了 `_loop_ts_key`、`_retro_text_ok`、`_esc_clean` 和 `urllib.parse.urlsplit`。實測用的臨時目錄已刪。

1. `world_verdict` 沒有寫帳的值域,法定的 `ts` 之前那條路徑會把沒驗過的任意內容寫進版控治理帳。
   引句:「`--record` 寫的治理帳事件多帶 `world_verdict`(沒填就不帶)」
severity: major
   blocking: 是,spec 沒寫「只寫驗過、去空白後屬於三個常數的值」,照字面實作就會寫進任意值。
   - 重現一:人裁早於生效日、version 1 的回顧檔,spec 規定整段 world_check 不驗。在這個檔裡加 `"world_check": {"verdict": ["x"]}`,或一個 200KB 的字串,再跑 `--record`。
     - 「沒填就不帶」只說沒填,沒說填了不合格怎麼辦,所以這個值會被原樣寫進帳。
     - 寫入端是 `_gate_event` 裡的普通 `f.write`(file: `scripts/lumos:1855`),沒有大小上限,也沒有原子性保證。`_gate_event_fit` 只截特定清單。
     - `retro-stats` 之後數三種結論時,list 型的值拿來當鍵會直接炸。
     - 版控帳是追加制,寫進去就收不回來。
   - 重現二:合格路徑也有同一個洞。`verdict` 寫成 `" undetermined "`,檢查時去空白會過,但 spec 沒說寫帳要寫去空白後的值。寫成原樣的話,`retro-stats` 的精確比對會漏數,「判不準」的提醒也不會印。
   - 重現三:accept-risk 搭「空骨架」,`verdict` 是 `"   "`。算沒填,但寫不寫、寫什麼 spec 沒說。
   - 現有事件欄位全是定長的小欄位(file: `scripts/lumos:22972`);這個欄位是第一個自由長度的。
   - spec 要補的是:只在檢查通過、而且 `strip()` 後屬於 `_RETRO_WORLD_VERDICTS` 時才寫,寫的是那個常數本身。

2. 做法第 3 點最後一條,和前面「不要求時整段不驗」自相矛盾。
   引句:「最新一筆人裁是 accept-risk、或不要求時:`world_check` 省略、`null`、`{}`、空骨架」
severity: major
   blocking: 是,測試作者無法同時滿足這兩句,S5 和這一條會互相打架。
   - 第 56 行與 S5 說:人裁早於生效日的 version 1「整段 world_check 不驗」。
   - 第 60 行同一句又把「不要求時」算進去,並說「不是這幾種而且不是物件算型別錯;有填就照上面驗」。
   - 照第 60 行,在 version 1、人裁早於生效日的回顧檔裡放 `"world_check": "abc"`,會被判型別錯。照第 56 行與 S5 則照過。
   - 舊迴圈要回溯被擋還是不擋,這兩句答案相反。第 60 行應該只管 accept-risk。

3. 網址正規化沒寫「解析失敗」的出路,而最自然的實作(`urlsplit`)會丟例外。
   引句:「型別不對逐欄列出,不丟堆疊」
severity: major
   blocking: 否 ⚠,取決於實作用不用 `urlsplit`,但 spec 沒有這條路徑。
   - 實測 `urlsplit("https://example.com：8080/x")`(全形冒號)、`urlsplit("http://a.com／path")`(全形斜線)、`urlsplit("http://a.com＃x")`(全形井號)都丟 `ValueError: netloc … contains invalid characters under NFKC normalization`。
   - `urlsplit("http://[abc")` 丟 `ValueError: Invalid IPv6 URL`。
   - 中文環境下 AI 摘來的網址帶全形標點很常見。
   - `_cap_retro_check` 在 `canary record`(file: `scripts/lumos:22663`)、處置閘(file: `scripts/lumos:22715`)等路徑上沒有 try,只有 `retro-stats` 的掃描有包(file: `scripts/lumos:22645`)。
   - 一個壞網址會讓 `canary record` 噴堆疊。檔案指紋沒變,`_cap_retro_status` 每次重驗都會再炸。
   - spec 要補一句:網址解不開就當成該項 url 的一條錯,不丟例外。

4. 「`://` 後面不是空的」擋不住沒有主機名的網址。
   引句:「scheme 不分大小寫是 http 或 https、而且 `://` 後面不是空的」
severity: minor
   blocking: 否,這條規則本意是擋掉空殼網址,現在有洞但不傷資料。
   - 下列字串去空白後 `://` 後面都非空,全部會過:`http:///x`、`http://#a`、`http://?q`、`http://@`、`http://:80`、`http://\u200b`、`http://%20`。
   - 用 `urlsplit(...).hostname` 驗證,前幾個都是 `None`,最後一個是零寬字元。
   - 兩個 `http:///a` 與 `http:///b` 互不相同,可滿足 direction-ok 的「兩項」。
   - 判準應改成「解析後主機名非空」。

5. 「互不相同」的正規化規則不足以界定「同一頁」,而且步驟沒釘死,測試無法釘。
   引句:「正規化(scheme 與主機名轉小寫、去掉 `#` 之後、去掉結尾斜線)後要互不相同(用集合比)」
severity: minor
   blocking: 否,規則本身是自洽的,但邊界會漂。
   - 結尾斜線沒說去一個還是全部。`http://a.com//` 全去會等於 `http://a.com`,只去一個則不等於。
   - 順序也沒說。`http://a.com/#` 先去 `#` 再去斜線,與先去斜線再去 `#`,結果不同。
   - 下列寫法都算「互不相同」:`https://a.com/x` 對 `https://a.com:443/x`、`http://a.com` 對 `http://a.com.`(結尾點)、`http://User@a.com` 對 `http://a.com`、`http://例え.jp` 對 `http://xn--r8jz45g.jp`(IDN 對 punycode)、`/x?1` 對 `/x?2`。
   - 若只想擋「抄兩次同一條」,這些可以不管,但 spec 要明寫界線並各釘一支測試。
   - 「主機名轉小寫」是整個 netloc 轉還是只轉 hostname,也沒說。`urlsplit` 的 `.netloc` 保留大小寫。

6. 生效常數覆寫值若格式不對(例如日期字串),spec 沒寫行為。
   引句:「生效常數照 `_cap_real_cutoff` 的寫法讓測試能改(環境變數覆寫,只給測試用)」
severity: minor
   blocking: 否,只有手滑設環境變數才會踩到。
   - 同門的覆寫(`LUMOS_PANEL_RETIRE_CUTOFF`)用的是純日期字串 `"2026-08-26"`,以字串前綴比較(file: `scripts/lumos:18839`)。
   - 新常數要求帶時區的完整時間戳,而且用 `_loop_ts_key` 解。實測 `_loop_ts_key("2026-11-05")` 回傳 `None`(naive 一律不猜)。
   - 於是 `ts_key >= None` 會是 `TypeError`,而這支檢查沒有 try。
   - 若覆寫值本身解不開,應定義成 fail-closed(一律要求)、並在訊息裡講明。
   - 這個環境變數在正式程式裡也讀得到,不只在測試。
   - 順帶確認:ts 等於常數時用「不早於」,算要求,和 S5 一致。`_loop_ts_key` 對 `0`、`[]`、`{}`、`None` 回 None,對 `5`、`1.5`、`b"x"` 丟例外。spec 已寫「先驗是字串再呼叫」,這條沒問題。

7. `_retro_text_ok` 對全標點和零寬字元放行,所以「字數」擋不住占位內容。
   引句:「字數口徑跟同一支檢查裡 `why_cap`、`avoid` 一樣用 `_retro_text_ok`,不另用 `_real_chars`」
severity: minor
   blocking: 否,既有欄位一樣,但這次是新增的「必查」欄,影響到保底的可信度。
   - 實測 `_retro_text_ok("!!!!",4)`、`("。。。。",4)`、`("....",4)`、`("\u200b"*4,4)` 全回 `True`,`("-"*20,20)` 為 `True`。
   - 純空白會被 strip 擋掉,包括全形空白。零寬空白 U+200B 不被 `str.strip()` 當空白。
   - 結果是:`queries:["----"]`、`point:"----------"`、`note:"-"*20`、`verdict:"undetermined"`、`sources:[]` 可以整份通過。
   - spec 在「不做」第一條已接受「格式對不等於真的查過」,所以這條不傷天花板的宣告。
   - 要不要在新欄多要求「至少含一個字母或漢字」,是設計取捨,該寫進決策。

8. undetermined 是最便宜的通關路徑,而 RETIRE-IF 把它算成這道關有效的證據。
   引句:「是 undetermined 時可以沒有來源(查不到就照實寫,note 裡講查了什麼、為什麼沒有)」
severity: minor
   blocking: 否,不會讓機制出錯,但會讓撤除條件失效。
   - 要通過只需:一條 4 字 query、一段 20 字 note、`sources: []`。
   - RETIRE-IF 寫「世界查證結論是『要換方向』或『判不準』的次數為 0」才撤。偷懶一律填 undetermined,這個次數永遠不為 0,撤除條件永遠不成立,即使這道關沒有改變任何決定。
   - 做法第 4 點的 `retro-stats` 段也沒按人裁分開數:accept-risk 的 change-direction 也被併進「要換方向 M」,而 RETIRE-IF 只看加開的迴圈。
   - 同一迴圈多次 `--record`(改檔重記)是按最新一筆數還是每筆數,也沒說,重記會灌水。
   - RETIRE-IF 該改成按「extra-round 的迴圈,最新 recorded 一筆」數 change-direction,並把 undetermined 的占比單獨列為警訊。

9. 骨架裡的空殼 source 在 undetermined 情境下會直接擋掉填寫者,而且 spec 沒講錯誤訊息怎麼指引。
   引句:「`"sources": [{"url": "", "point": ""}], "verdict": "", "note": ""`」
severity: minor
   blocking: 否,這是使用順手性,不影響正確性。
   - S3 的情境是「sources 是空的」。但 `--template` 發出的骨架本身是一項空殼 source。
   - 填寫者選 undetermined 卻忘了刪那一項,spec 規定「每一項 source」都驗,會得到 `url`、`point` 逐欄不合格。
   - 在 extra-round 路徑上,骨架放著不動、在 accept-risk 路徑上算「空骨架」照過,兩邊行為不一致。
   - 錯誤訊息要講「沒有來源就把 sources 改成 `[]`」。
   - 「空骨架」的定義「每格去空白後都是空字串」也沒說缺 key、`null`、`sources:[{}]` 算不算空。對 accept-risk 來說這會決定過或不過,需要各釘一支測試。

其他逐項回應:
- version 型別:已讀,無 finding。`True`、`2.0`、`"2"` 仍被擋;`bool` 是 `int` 的子類,spec 要保留那條 `not isinstance(v, bool)`,現有碼第 22419 行有。
- 骨架寫入(`--template --write`):已讀,無 finding。現有 `O_EXCL` 不覆寫,和第 56 行的修法措辭一致。
- 併發:無。`--record` 對同一份 `raw` 先驗再算指紋,新增欄位沒有改變這個結構;跨會談同時 `--record` 是既有行為,新欄位不增加風險。
- 效能與資源:無。回顧檔有 256KB 上限(r1 b8 已放行),集合比較是 O(n),新增驗證只掃一遍。
- 回滾:無新增問題。第 87 行說已寫成 version 2 的回顧「檢查照收」,但 RETIRE-IF 說「改回只提醒」,和「拿掉 world_check 的驗法」是兩種回退,措辭不一致,不影響實作。
- 其他節(名詞、問題與最小解、不做、驗收條款 S1、S3、S7、S8、實務隱患):已讀,無 finding。

最嚴重的是 major,共 9 條(major 3、minor 6),其中 blocking 2 條(第 1、2 條)。
