# r3 收貨紀錄(編排者)

派出七席:五席 Claude(正確性/邊界/整合/併發資源/架構對齊,sonnet)先派;兩席外家 Codex(找洞 gpt-6-astra、否決 gpt-5.6-terra)
等 Codex 帳號用量恢復(22:02)才派——第二輪時兩席撞到用量上限沒有產出。七席收齊之前正式工作目錄不動、報告先存在工作目錄外;
修正先在工作目錄外的一份複製 repo 裡做,七席收齊才搬回來。
存報告時的兩件事(都不改內容):
- 背景通知在傳送時會把 < > & 轉成 &lt; &gt; &amp;,存檔時還原成原字元——架構對齊席原始輸出查過是 `>`(它自己的輸出紀錄裡 `count("[[") > 1` 出現 5 次、`&gt;` 0 次);
- 整合席第一行多了一個標題,把檔級 severity 擠到第三行,退回該席只拿掉標題重交(內容逐字相同)。
七份報告 quote-check 全數錨定;refcheck 的 missing 全是審查員在暫存區自造的重現檔路徑或反引號裡的指令。
外家兩席 22:02 派出、各跑 11 分鐘,都有產出。

## 前兩輪 18 條的驗收

Claude 五席一致判 F1–F14、F16–F18 修到。F15(大小寫):邊界席判「修出新洞」(→ 本輪 F22)、併發資源席判「修到但另開新洞」(→ 本輪 F23)。
外家找洞席:F6 修出新洞(→ F31)、F13 沒修到(→ F32)、F17 沒修到(→ F26/F33)。外家否決席:F1/F2 修出新洞(→ F24)、F9 修出新洞(→ F35)、F13 修出新洞(→ F32)。

## 去重後的發現(本輪)

| id | 等級 | 一句話 | 哪幾席抓到 |
|---|---|---|---|
| F19 | major | 「一個值裡兩個以上連結」讀的一側(lint)只認兩種寫法、寫的一側認全部——兩套規則 | 架構對齊 F20 |
| F20 | blocker | 格式檢查器的「零條豁免」剝太寬:「blocker 0 台」「major 0/1 條已修復」「blocker 0day」都被剝掉,夾帶的等級溜過 | 正確性 F20、外家找洞 F19、外家否決 F19 |
| F21 | major | about_code 的 Windows 反斜線寫法永遠「找不到」 | 邊界 F19 |
| F22 | major | about_code 比對鍵不折大小寫:舊的大小寫錯字項造成重複、而且刪不掉 | 邊界 F20 |
| F23 | major | 目錄讀不到檔名清單時,大小寫檢查被當成「寫對了」放行 | 併發資源 F19 |
| F24 | blocker | 工具自裝檔跳過只比路徑、不比內容、也不確認真的裝過——專案自己同名的 hook 或改過的工具檔都逃過風險掃描 | 併發資源 F20、外家否決 F20 |
| F25 | major | 同一篇筆記同時被好幾個程序寫:固定暫存檔名互搶噴錯、回報成功的被蓋掉 | 併發資源 F21 |
| F26 | minor | about_code 的 symlink 別名被當成另一支檔:疊出重複、用別名加進去的用別名刪不掉 | 正確性 F19、外家找洞 F22 |
| F27 | minor | `[a]` 沒有逗號,擋下訊息卻說「看不懂逗號」 | 正確性 F21 |
| F28 | minor | about_code 的路徑正規化跟工具自裝檔判別各寫一份 | 架構對齊 F19 |
| F29 | minor | 排序加分那一側讀 about_code 只剝 ./、不解 .. | 整合 F19 |
| F30 | minor | new verification 回掛被擋時,擋下訊息蓋掉「新筆記已建好」 | 整合 F20 |
| F31 | major | 單一值轉清單時含雙引號的舊連結被重新加引號改壞;寫完的自我檢查只驗新項 | 外家找洞 F20 |
| F32 | major | 同一行清單的檢查還有兩種繞法:`[[Systems/A], Systems/B]`、引號內前導空白 | 外家找洞 F21、外家否決 F21 |
| F33 | minor | remove 同一支檔寫了兩種寫法時只拿掉一筆 | 外家找洞 F23 |
| F34 | minor | 「清單=來源受版控的檔」那支測試在消費專案裡跑會假紅 | 外家找洞 F24 |
| F35 | major | 安裝照目錄全抄(含來源沒進版控的檔),跳過清單卻只列受版控的檔 | 外家否決 F22 |

## 編排者機械重現(修改前的程式,205ee0f8;暫存 repo)

| id | 怎麼重現 | 結果 |
|---|---|---|
| F19 | parse_frontmatter 讀 `related: [[Systems/A]],  [[Systems/B]]` 的 lint;同一個值餵 _list_scalar_value | HIT:讀側 lint 回 [],寫側丟 ValueError |
| F20 | report-normalize 讀「總結:有 blocker 0 台原型機…」「總結:最高 severity major 0/1 條已修復…」「總結: blocker 0day exploit」 | HIT:三種都判「已是正規化格式」 |
| F21 | append about_code 'src\a.ts'(src/a.ts 存在) | HIT:rc2「找不到」 |
| F22 | `about_code: SRC/A.TS` 後 append src/a.ts,再 remove src/a.ts 兩次 | HIT:兩筆並存;第二次 remove rc2「沒有 src/a.ts」 |
| F23 | chmod 111 src 後 append src/SUB/a.ts(磁碟上是 src/sub/a.ts) | HIT:rc0 存進錯字大小寫 |
| F24 | 讀碼:_is_vendored_path 只做 `_posix_norm(rel) in _VENDORED_ALL`,沒有看內容、也沒有看是不是裝過 | HIT(讀碼即可確認) |
| F25 | 六個程序同時 append 同一篇 | HIT:六個全部 FileNotFoundError(暫存檔名互搶)、一項都沒寫進去 |
| F26 | repo 有 real/a.ts 與 link→real;`about_code: link/a.ts` 後 append link/a.ts;另一篇 append link/a.ts 後 remove link/a.ts | HIT:第一種 rc0「多了一項 real/a.ts」;第二種 rc2「沒有 link/a.ts」 |
| F27 | `tags: [a]` 後 append b | HIT:訊息講「看不懂同一行裡的逗號」 |
| F28 | 讀碼:_about_code_norm 與 _is_vendored_path 各自 posixpath.normpath(… replace("\\", "/")) | HIT |
| F29 | 讀碼:_impact_mark_about 的 _norm 是 removeprefix("./"),不含 normpath | HIT |
| F30 | Systems 筆記 verified_by 寫成同一行清單,跑 new verification X --systems | HIT:rc2 只印擋下,沒有「筆記建好了」 |
| F31 | edit_fm_append 對 `related: '[[Systems/API "v2"]]'` 加一項 | HIT:舊項讀回來變成 `[[Systems/API \"v2\"]]`,指不到原本那篇 |
| F32 | edit_fm_append 對 `related: [[Systems/A], Systems/B]`、`about_code: " [src/a.ts, src/b.ts]"` | HIT:兩種都沒擋 |
| F33 | `about_code:` 兩項 `src/../src/a.ts`、`src/a.ts`,remove src/a.ts | HIT:只拿掉一筆 |
| F34 | 讀碼:repo = 測試檔上兩層 + git ls-files;反向驗證拿掉來源限定後,模擬消費專案跑它翻紅 | HIT |
| F35 | 讀碼:安裝端 `toolkit += [... base.rglob("*") if p.is_file()]` | HIT |

## 判讀(判準是編排者自己想的,不照席位給的)

- F19:清單欄位的一項只能是一個連結或一個值,讀寫共用 `_multi_link_value`;只用在清單欄位(散文欄位講到兩個連結是正常的)。
  放寬前先盤點:工具鏈與三個消費專案的開頭欄位零篇會因此新翻紅。
- F20:零條豁免只認「等級字後面 0 條」;另外編排者自己抓到(O3)總結句的判斷原本不限行首,內文講到「總結句」就被誤擋——
  正確性席這份報告本身就被擋了兩行。改成只認行首(可帶標題、清單、引用、編號、粗體記號);不在行首的照一般規則檢查。
- F21–F23、F26:about_code「指的是哪一支檔」統一成一個比對鍵(檔案還在就看磁碟上的真實位置,不在了才看字面),
  append 去重與 remove 找項共用;讀不到目錄就擋。
- F24:安裝/更新時記內容指紋,只跳過內容對得上的工具檔;沒有指紋清單一支都不跳。第一輪收尾時我把這條列成「以後再看」,
  第三輪被判重大,照規則折(code 迴圈重大一律折)。邊界:清單本身在專案裡,防不了刻意連清單一起改——寫進事故筆記附回頭條件。
- F25:根因是舊程式(暫存檔名固定、讀改寫不上鎖,原本註記「單機 CLI 不上鎖 accepted」);這輪的新用法讓它更容易撞到,
  而且實測比席位說的更嚴重(六個全噴錯)。暫存檔名照既有 mkstemp 先例改成每次不同;set/append/remove 在同一個筆記庫上排隊。
  其他寫入指令還沒套鎖,寫進事故筆記附回頭條件。
- F31:原本那一項有引號就照原樣搬;append/remove 寫完的自我檢查補「原本其他每一項都還在」。
- F32:判斷前先去空白;單一連結要「整個值恰好是一個連結」才豁免,跟讀的一側索引連結共用同一個判斷(_SINGLE_WIKILINK_RE)。
- F33:remove 對同一支檔的每一種寫法都拿掉。F34:照既有 `_need_src` 做法只在工具鏈本體跑,並加進消費端模擬回歸。
- F35:安裝只複製精確清單上的檔;授權檔頭測試跟著改用同一份清單。
- code 迴圈:輪內有 blocker 與 major,accepted 必須是空的——十七條全折。
- ★三輪上限★:這是高風險分級的第三輪(上限 3 輪)。這輪的修正本身還沒有經過全新一輪審查——要不要開第四輪交給人裁,
  在那之前不做 code-loop pass、不推送。

## 編排者自己抓到的(不是席位發現,不進處置清單)

- O3(收貨時):見 F20 那段。
- O4(派人之前):about_code 大小寫逐層比對把「只差 Unicode 寫法的同一個檔」當成大小寫寫錯擋下(é 一個字 vs e 加重音)。
  已在凍結第三輪材料之前修進 205ee0f8,本輪快照含這個修法。
