severity: major

## F1 鎖內只重讀目標篇仍會依過期的鄰居狀態誤修 c3

severity: major

blocking: 是 — 不改，併發狀態變更後工具仍會把已不存在的 c3 當成有效發現並改寫驗證紀錄。

引句:「鎖內從磁碟重讀那一篇並重新解析」

file: `scripts/lumos:26058`

file: `scripts/lumos:620`

1. `_drift_c3_hit` 不只讀目標驗證紀錄，也從 `env.notes` 讀全部 `plan_refs` 計劃的狀態。
2. 會談 A 載入 env 後做鎖外準備；會談 B 先拿鎖，把相關計劃從 done 改回 doing；A 隨後拿鎖，但依 spec 只重讀驗證紀錄並換進舊 env。
3. A 仍從舊 env 看到計劃是 done，於是把驗證紀錄改離 pending；此時磁碟上的 c3 已不存在。
4. 鎖內必須重建整個 Env，或至少重讀所有依賴節點並重建索引；只換目標 `Note` 不足以完成重判。

## F2 同篇有兩個不同 c4 命中時不存在可完成的修復序列

severity: major

blocking: 是 — 不改，合法的 c4 發現會陷入每次只改一處、驗證又回滾的死路。

引句:「全部項目合計要剛好出現一次」

file: `scripts/lumos:26099`

1. 現況判定把整篇 `valid_under` 合起來檢查，一篇不論有幾個關鍵詞命中都只產生一筆 c4。
2. 例如兩項分別是「本次未提交」與「uncommitted build」；`--old 未提交 --new ...` 只會清掉第一項。
3. 寫後重判仍會得到同篇 c4，依 [S9] 必須回滾；第二項因此永遠沒有機會單獨修。
4. 若把「那一筆」解成原行文字而宣告成功，則會在 c4 仍存在時寫入成功帳，反而違反 [S9]。
5. 相同片段出現兩次也會先被「剛好出現一次」擋下；跨項一次替換又被換行禁令排除。

## F3 c3 接受 abandoned 等狀態卻一律記成由節點解決

severity: major

blocking: 是 — 不改，工具會把「放棄、過期、被取代」寫成「已解決」的假歷史。

引句:「合法值是驗證紀錄的合法狀態扣掉 pending」

file: `scripts/lumos:5248`

1. 驗證紀錄除 pending 外的合法值包含 `pass`、`stale`、`superseded`、`abandoned`。
2. spec 規定只要帶 `--by`，正文一律追加「由 `[[節點]]` 解決」。
3. `drift fix ... --kind c3 --status abandoned --by Projects/X` 因此會被接受，卻留下「由 X 解決」；`stale` 與 `superseded` 同樣不等於解決。
4. 實作必須依狀態選擇歷史文字，或只允許能支持「解決」語意的狀態搭配 `--by`。

## F4 c3 的 by 查找會接受同名歧義並寫回仍然歧義的連結

severity: major

blocking: 是 — 不改，狀態異動的來源連結會指錯節點或成為無法唯一解析的證據。

引句:「`--by` 找不到回 2。原本的正文不改(歷史說法保留)」

file: `scripts/lumos:666`

1. 現有 `Env.find` 遇到同 stem 多篇時只印警告，仍取第一篇，不會回傳找不到。
2. spec 又要求正文寫使用者原始輸入 `[[<節點>]]`，而不是已解析的完整圖譜相對路徑。
3. 若 `Projects/X.md` 與 `Verification/X.md` 同時存在，`--by X` 會通過檢查並寫入 `[[X]]`；這個連結仍然歧義，且所選第一篇依索引順序決定。
4. `--by` 必須拒絕多重命中，成功時寫回唯一解析後的 canonical 路徑。

## F5 既存無 related 表態會永久豁免後續新增的收尾計劃

severity: major

blocking: 是 — 不改，升級後既存 c2/c3 表態仍會吞掉本功能要重新列出的新關係。

引句:「舊表態:最新一筆沒記 `related` 的照舊對得上」

file: `scripts/lumos:27079`

file: `scripts/lumos:27129`

1. 現有表態紀錄沒有 `related`，鍵只有路徑、原文與種類。
2. c2 的原文通常只是 `status: open`；新增另一篇已收尾計劃的連結不會改這行，因此舊表態鍵仍命中。
3. spec 明訂無 `related` 的最新舊表態照舊有效，所以新計劃加入後不會重新列出，直接違反範圍第⑦項。
4. 只補工具鏈 17 筆與 rtb 2 筆沒有涵蓋其他已使用 `drift ack` 的消費專案；即使所有執行檔都已升級，舊資料仍永久保留這個洞。

## F6 JSONL 聯集合併無法維持最新一筆的時間順序

severity: major

blocking: 是 — 不改，多工作樹合併後表態是否生效會取決於合併方向，而不是實際表態先後。

引句:「同一個鍵(路徑+原文+種類)可能有好幾筆表態:★以最新一筆為準★」

file: `scripts/lumos:17669`

1. 既有 JSONL 聯集合併會先保留拉下來的遠端內容，再把本機獨有行追加到檔尾。
2. 本機獨有行即使實際較舊，合併後仍位於檔尾，會被新規則當成最新表態。
3. 例如遠端較新的表態記錄 `[A,B]`，本機較舊表態記錄 `[A]`；pull 後 `[A]` 被追加在尾端，現在的 `[A,B]` 會被錯誤重新列出。
4. 反向關係也能讓較舊的寬清單覆蓋較新的窄清單，進而漏掉計劃再次收尾。
5. 要使用 latest 語意，紀錄必須帶可比較的全序欄位並按它選擇；檔案物理行序不能同時承擔聯集合併與時間排序。

## F7 修復帳讀回失敗時會留下幽靈帳目

severity: major

blocking: 是 — 不改，失敗路徑會把筆記還原，卻留下宣稱修復成功的帳目。

引句:「帳寫不進去就把筆記還原成改前原文、回 2」

file: `scripts/lumos:8518`

1. `_jsonl_append_verified` 先以 append 寫入並關檔，之後才獨立重開讀回驗證。
2. 若 append 已成功但重開或讀取失敗，helper 回 2；已追加的 JSONL 行不會被移除。
3. spec 隨後把筆記還原成 `before`，但帳內仍保留該筆 `after_sha256`，形成「帳說已修、檔案實際未修」的幽靈紀錄。
4. 之後依修復帳回退或計算採用率都會讀到錯誤事實；失敗後需要可辨識的撤銷事件或不會先暴露正式帳目的提交協議。

## F8 新修復帳可以藉符號連結寫壞任意檔案

severity: major

blocking: 是 — 不改，執行一次修復即可把 JSON 追加到 repo 內外的非帳本檔案。

引句:「往 `governance/drift-fixes.jsonl`(常數 `_DRIFT_FIXES`,跟 `_DRIFT_ACKS` 放一起)追加一行」

file: `scripts/lumos:8518`

1. spec 指定直接沿用 `_jsonl_append_verified`；該 helper 的 `open(path, "a")` 沒有拒絕符號連結，也沒有驗證父目錄仍位於 repo。
2. 若投稿 repo 事先放置 `governance/drift-fixes.jsonl -> ../scripts/lumos`，執行 `drift fix` 會把 JSON 追加到主程式。
3. 讀回自驗也會沿同一連結找到 token，因此整個指令回成功，筆記改動與外部破壞一起留下。
4. 新帳本寫入前必須拒絕檔案及父目錄連結，並驗證解析後路徑仍是預期的 repo 內普通檔案。

## F9 guard settle 的現有鎖結構容不下新的鎖外日期查詢

severity: major

blocking: 是 — 不改，照現有結構接入日期查詢會讓 30 秒鎖被接手，形成並行寫入。

引句:「放在鎖外,因為寫入鎖 30 秒沒放就被當成死鎖接手」

file: `scripts/lumos:12195`

file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:19`

1. 現有 `cmd_guard_settle` 在讀狀態前就取得 `_vault_write_lock`，全部 settle 邏輯都在鎖內執行。
2. 第 3 節要求 pass 節點走第 2 節同一套日期規則；日期規則包含可能超過 30 秒的 `git log -G`。
3. 直接把共用 c1 流程接到現有 pass 分支，git 查詢會在鎖內執行；超過 30 秒後另一程序會把鎖當死鎖接手，兩邊同時寫。
4. 若單純把整個 settle 移到查詢後再拿鎖，又會破壞既有「從讀到寫整段持鎖」及狀態重判契約。
5. spec 必須定義兩階段流程：鎖外只做候選日期查詢；拿鎖後重讀守衛紀錄、家節點與狀態，重新判定仍是 pass+c1，再寫筆記與帳。

〈前言、依據、PRIOR-ART、RETIRE-IF〉已讀,無 finding

引句:「RETIRE-IF: 上線兩個月後任一成立就撤掉或重想」

〈第 5 節 結案 Issue 的回頭條件〉已讀,無 finding

引句:「用跟 E5 同一套判定列出它還留著的回頭條件行」

〈第 7 節 提示與同步〉已讀,無 finding

引句:「同步改的筆記與文件:Systems/存量漂移守衛」

〈合約候選〉已讀,無 finding

引句:「(設計審過閘後填。)」

〈審計修正紀錄〉已讀,無獨立 finding

引句:「鏡像核對(便宜席,材料含席報告目錄)」

## 實務隱患逐類結論

1. 守衛面誤擋或漏擋：有，F2、F5、F6。
2. 不可逆與回復：有，F7、F8。
3. 併發：有，F1、F6、F9。
4. 效能：無額外 finding；c1 查詢限定單一路徑且設計要求放在鎖外，c4 也只做目標檔的首次提交查詢，未發現隨圖譜筆記數擴張的重複 git 掃描。
5. 向後相容：有，F5、F6。
6. 資料正確性：有，F1、F2、F3、F4、F7。

最高為重大，共 9 條會讓實作者做錯決定或做出壞系統。