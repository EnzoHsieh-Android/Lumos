# r3 收貨紀錄(型錄接電要附證據)

- 四席交回後一次存檔,取自逐字稿。通才三、證據可信三全數錨定;正確性三 5 句有 1 句錨不到(第 2 條引句裡包了「」被截斷),那條與通才三 i2 同一件事,下表機械重現;架構對齊三的引句沒加「」,退回只改格式重交。編號:通才三 i、正確性三 j、證據可信三 k、架構對齊三 l。

| id | 席 | 原報 | 一句 | 重現 | 處置 |
|---|---|---|---|---|---|
| i1 | 通才三 | major | 12 列壞寫法欄沒有反引號段、19 列只有帶「…」的佔位,照字面寫不出合格的〔真跑〕樣本 | HIT:python 數到候選 168 列裡 12 列無反引號(UI-44、UI-45、UI-46、UI-64、UI-84、UI-86、UI-88、UI-92、UI-95、ARCH-81、ARCH-84、DATA-50) | 折:樣本要含「去掉佔位後長度 8 以上的反引號段」裡最長那段;沒有這種段的列樣本自擬,理由以「壞寫法欄沒有可抄的程式碼」開頭,自檢兩條路各驗(M1) |
| i2 | 通才三 | minor | 55 列「批四(現成規則)」沒說怎麼處理 | HIT:python 數到 55 列 | 折:新比對只管有候選的列;沒有候選的列照舊值不動(M5) |
| i3 | 通才三 | minor | 一個標籤多個候選怎麼合;compose-rules 檢查名用 kebab 還是 Pascal | HIT:讀快照與 check.py _B4_CR | 折:任一候選擋得到該標籤就算;檢查欄照型錄寫法(compose-rules 用 kebab)(M8) |
| i4 | 通才三 | minor | 環境行、編號不在主表、〔查證〕理由這幾道沒有改壞案例 | HIT:讀預期值表 | 折:預期值表補三列 |
| j1 | 正確性三 | major | 同 i1,另反引號段太短(1、2 字)比對沒意義 | HIT:同 i1;UI-87 最短段 `X` | 折:同 i1(長度 8 下限) |
| j2 | 正確性三 | major | 同 i2,照字面會報 55 個不一致或改壞資料 | HIT:同 i2;此條引句錨不到,以 i2 的機械重現採信 | 折:同 i2 |
| j3 | 正確性三 | minor | 通電批次值的語法:括號內分號、「批一、批四」拿掉後懸空頓號、前面有別的子段 | HIT:python 去重 10 種寫法 | 折:寫明用 `批四\([^)]*\)` 抽、拿掉時連同相鄰頓號、值變空才寫未接、其他子段保留(M6) |
| j4 | 正確性三 | minor | 環境行套件段驗不了 | HIT:讀快照 | 折:只驗開頭、日期、AGP、Gradle 四段,其餘照抄不驗,寫進〈天花板〉 |
| j5 | 正確性三 | minor | 候選要自己重抽(標籤,碼) | HIT:check.py batch4_expected_tags 只回標籤 | 折:新增回傳(標籤,碼)的函式,batch4_expected_tags 改呼叫它(M8) |
| k1 | 證據可信三 | major | 判定與等級沒綁:擋得到配 Hint 或沒報也過;升級前後等級寫哪個沒定 | HIT:讀快照範圍 3 | 折:等級記檢查原本等級(升級前);擋得到只准配 Fatal、Error、Warning 或 detekt,擋不到配等級寫什麼都行但理由必寫(M2) |
| k2 | 證據可信三 | major | detekt 套不上 lint 的等級;推送前那條是 CLI 不是 Gradle | HIT:Systems/linter精選目錄 的推送前命令、configs/detekt/compose.yml | 折:compose-rules 標籤照推送前的 CLI 命令跑(`--build-upon-default-config --disable-default-rulesets --config configs/detekt/compose.yml` 加外掛),報出就算擋得到(新增告警閘擋任何新告警),等級寫 detekt(M3) |
| k3 | 證據可信三 | major | 「外層函式或類別」讓樣本可以補會觸發檢查的呼叫端(UI-11、PERF-1、TEST-25);import 選哪個沒定(ARCH-28) | HIT:pilot.md 這幾列的變體 | 折:樣本裡除了 package、import、註解、空行、只有括號的行、與開區塊的宣告行(不含 = 與呼叫),每一行都要出現在壞寫法欄裡;import 照壞寫法欄寫的類別選,沒寫的選 androidx(M4) |
| k4 | 證據可信三 | minor | 真跑的 lint 區塊跟範本不同(baseline、checkDependencies);失敗怎麼判 | HIT:Systems/linter精選目錄 範本段 | 折:真跑照範本 lint 區塊但不用 baseline;以報告逐筆讀,不看任務 rc |
| k5 | 證據可信三 | minor | 缺依賴時型別解析不到會靜默不報 | HIT:Systems/linter精選目錄 寫 detekt 沒型別時靜默;pilot 依賴偏離段 | 折:〈天花板〉補;理由「沒報」時記樣本用到的依賴 |
| l1 | 架構對齊三 | minor | 樣本檔名「以編號開頭」會撞名(UI-2 對 UI-24) | HIT:check.py situation_samples 整名取 | 折:整名 `<編號>.kt.txt` |
| l2 | 架構對齊三 | minor | 切節寫法會變第三份 | HIT:check.py _abbr_table、_pending_table | 折:抽一個共用切節函式,三處共用 |
| l3 | 架構對齊三 | minor | 主表實測欄舊「實跑命中」句會跟判定表矛盾 | HIT:型錄 STATE-5 實測欄 | 折:判成擋不到而實測欄寫實跑命中的列,那句改成這次真跑結果 |
| l4 | 架構對齊三 | minor | 〈統計〉沒有新節的計數 | HIT:check.py stats_problems | 折:〈統計〉加「接電證據 N 筆」,接進 stats_problems |

--refuted-set none。

## 依根因分組

- M1 樣本可抄的原文(i1、j1)
- M2 判定與等級一致(k1)
- M3 detekt 的定義(k2)
- M4 樣本只准外殼(k3)
- M5 沒有候選的列(i2、j2)
- M6 通電批次語法(j3)
- M7 真跑設定與天花板(k4、k5、j4)
- M8 候選抽取與彙總(i3、j5)
- 格式與鄰居(l1 到 l4、i4)

## 先查世界

- PRIOR-ART:M4——lint 測試框架的樣本就是被測的原始碼本身,檢查器作者不在樣本裡另加觸發條件(https://googlesamples.github.io/android-custom-lint-rules/api-guide.html 〈Testing〉);採用「樣本每一行都要出自壞寫法欄,只准加外殼」的機械規則。
- PRIOR-ART:M3——compose-rules 以 detekt 外掛載入(https://mrmans0n.github.io/compose-rules/detekt/),推送前的命令與設定檔照 [[Systems/linter精選目錄]] 與 `configs/detekt/compose.yml`;detekt 的任務失敗看 `build.maxIssues`,不看等級(https://detekt.dev/docs/introduction/configurations/)。
- PRIOR-ART:M1、M2、M5 到 M8——專案既有寫法(型錄欄位、check.py 既有函式),沒有要另查的。

## 跑滿三輪

標準級上限 3 輪到了;本輪全部折入、處置閘過就出設計迴圈,不加開第四輪。理由:三輪 blocking 從 13、7 降到 6,這輪的 major 全是補真跑定義的細節(沒有翻掉換形狀的方向),而且都寫成了自檢會機械驗的規則;實作後還有代碼審與改壞測試。這個決定由編排者依使用者授權(「你自己簽核」「沒錯，你一樣有我的授權，目標是完成這些」)做。
