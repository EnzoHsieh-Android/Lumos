# r3 收貨紀錄(2026-10-14,6 席)

- 六份席報告(正確性、邊界、整合、回滾、通才、架構對齊,皆 sonnet)原樣存檔;quote-check 全數錨定。
- 編號照各報告裡以 `severity:` 行開頭的 finding 順序(第一行檔級 severity 不算):正確性 正1–正6、邊界 邊1–邊13、整合 整1–整9、回滾 回1–回5、通才 通1–通7、架構對齊 架1–架6,共 46 條;blocking 合計 16(正 1、邊 9、整 2、回 2、通 2、架 0,取自各報告總結句)。46 條全數折入,無放行、無重現不到。

## 判讀

46 條集中在六個根因,依根因一次改,不逐點補:

1. 提交編號的形狀(正3、邊1、通3、架4):只收 40 或 64 碼完整編號,照 `_lens_full_sha` 解,解出必須等於輸入;以第一個冒號切。
2. 路徑與讀取(正2、邊3、邊4、邊5、邊6、邊7、整5、通4、架1、架3):提交那條路新增正規 posix 相對路徑規則、vault 用路徑自己的 slug、`ls-tree` 只收一般 blob、內容借 `_nodehome_cat_blobs_capped`、新代碼 `spec_too_large`;工作樹那條路明寫不動。
3. 會談目錄與提交兩邊的存在判斷(正1、正4、邊9、邊10、整8、通5):程式檔照會談目錄判、另列只在提交裡的;連結節點與落點分三種;用詞改「會談目錄」。
4. 文法由誰判、掛鉤輸出(正5、正6、邊2、邊11、邊12、邊13、整2、整3、回3、通7、架2、架5、架6):讀計劃收斂成一支;lumos 回 `spec_source` 等欄位,掛鉤只讀;計劃版說明行、`_fail_note` 加參數;spec_* 記 ok 加 note;五個代碼都寫成新增。
5. 快照與提交沒綁在一起、先提交的前提不實(整6、通1、通2):新子命令 `lumos spec-freeze` 用暫存 index 建不掛分支的提交並寫出快照;rN-dispatch.json 記 `spec_commit`。
6. 分發、回退與說法同步(整1、整4、整7、整9、回1、回2、回4、回5、邊8、通6):版本錯開寫明;回退加全域 lumos 與 update 覆寫;撤 REVISIT/RETIRE-IF;要改的說法列全;lands_in 改;S5 改假 `git` 外包腳本;審計紀錄加註前兩輪做法已撤回。

## 逐條

| 編號 | 一句問題 | 怎麼折 |
|---|---|---|
| 正1 | 程式檔存在用提交判、impact 用會談目錄算,新增的檔得到零節點還寫「找得到」 | 做法 5:存在照會談目錄判,只在提交裡有的另列一行「沒算牽連」;條款 S6 |
| 正2 | 路徑沒要求是 blob,目錄、符號連結會被當計劃讀;超過 1MB 沒代碼 | 做法 3:`ls-tree` 只收 100644/100755 blob,其餘 `spec_missing`;新代碼 `spec_too_large`;條款 S4 |
| 正3 | 短編號被同名分支搶走、只收小寫、撞號與 64 碼與逾時沒定義 | 做法 1:只收 40/64 碼、不分大小寫、解出須等於輸入、逾時歸 `spec_rev_missing`;條款 S2 |
| 正4 | 不存在的節點全標「主線還沒有」、「主線」用詞不準、vault 取 `slugs[0]`、「相同檢查」不實 | 做法 6 分三種並改用「會談目錄」;做法 2 vault 用路徑自己的 slug、工作樹那條路明寫不動;條款 S5、S7、S10 |
| 正5 | 絕對路徑落在 `spec_outside_repo`,繞法只掛 `spec_missing`;說明行是範圍措辭 | 做法 8:兩個代碼都加繞法;另寫計劃版 `SPEC_FAIL_NOTE`,`{what}` 用 `_clean_field`;條款 S13 |
| 正6 | 掛鉤說不解析,卻要判寫法記 note | 做法 7、8:lumos `--json` 帶 `spec_source`,掛鉤只讀;條款 S12 |
| 邊1 | 十六進位會被同名 ref 搶走,「無歧義」不成立 | 同正3,做法 1 只收完整編號並驗等於輸入;實務隱患改寫 |
| 邊2 | 掛鉤不解析與 S3、S6 矛盾;`_dispatch_lens_spec_with_arch` 另讀檔讓架構段消失 | 做法 4 讀計劃收斂成一支、外層讀一次傳進內層;做法 8 掛鉤只讀欄位;條款 S8、S12 |
| 邊3 | 空路徑、多冒號、`./`、中段 `./`、64 碼、NFD 都沒定義期望 | 做法 1 以第一個冒號切;做法 2 字串規則逐項列、`./` 也擋、NFD 不處理且夾具只用 NFC;條款 S3 |
| 邊4 | 目錄與符號連結被當計劃讀,封閉代碼表沒對應 | 同正2,做法 3;條款 S4 |
| 邊5 | 「同值上限」不存在,超限代碼與 rc 沒列 | 做法 3:上限 1MB 只在提交那條、剛好 1MB 照讀、`spec_too_large` rc 2;做法 2 明寫工作樹那條沒有上限、不動;條款 S4、S10 |
| 邊6 | 「相同的檢查」不是現況,會誤動工作樹那條路 | 做法 2:改寫成提交那條新增的規則,工作樹那條一律不動;條款 S10 |
| 邊7 | 選哪個 vault 沒定義 | 做法 2:用路徑自己的 slug,會談目錄沒有就 `no_knowledge`;條款 S3、S5 |
| 邊8 | 假 `_lens_git` 證明不了只在會談 repo 跑 git | 條款 S9 改成 PATH 前置假 `git` 外包腳本記 `-C` 與工作目錄,涵蓋子行程 |
| 邊9 | S1 測試層次沒定,端到端會依全域 lumos 版本紅綠不定;夾具檔要在會談目錄 | 驗收條款拆 lumos 層與掛鉤層、不跑端到端;S1 寫明程式檔與節點在會談目錄都有 |
| 邊10 | 「主線還沒有」沒有機械定義、分不出死連結;落點段互相矛盾;在 main 上測不出差別 | 做法 6 三種分法(用 `ls-tree` 判提交裡有沒有)、落點同樣分;測試搭法要求會談目錄停在不含該提交的分支;條款 S7 |
| 邊11 | 事件 kind 沒定,錯的編號會拉高錯誤數;逾時蓋掉 note | 做法 8:spec_* 記 ok 加 note、`no_knowledge` 記 error,逾時那筆不帶字首、RETIRE-IF 不計;條款 S12–S14 |
| 邊12 | 三個代碼不是沿用;rc 沒寫;逾時與大小檢查失敗歸哪個代碼;S2 應拆兩層 | 做法 7:五個代碼都寫成新增、rc 2/3 列明、逾時歸 `spec_rev_missing` 或 `spec_missing`;條款分兩層 |
| 邊13 | 路徑含空白整行不匹配、靜默 | 做法 9:spec-freeze 遇路徑含空白就拒絕,做法 12 寫明不改 `SPEC_RE`;條款 S18 |
| 整1 | 要一起改的說法沒列全 | 做法 11 列全:design-loop SKILL、reference、templates 兩處、project-notes reference、commands/05、Systems/design-loop、`--spec` 說明與 docstring、掛鉤檔頭與說明行、codex-harness 代碼列舉 |
| 整2 | 掛鉤自述不解析卻要分辨寫法,違反掛鉤薄殼裁定 | 同正6,做法 8;檔頭補一句 |
| 整3 | 代碼不是沿用、種數與既有測試要改;工作樹失敗 kind 從 ok 變 error | 做法 7 寫成新增、種數改十一;做法 8 spec_* 記 ok;條款 S10、S11、S13 |
| 整4 | lands_in 留著 hook信任邊界、漏 templates.md 的家與 design-loop;沒有結構化決策 | lands_in 拿掉 Systems/hook信任邊界,加 Systems/派工鏡頭、Systems/每輪修補差異派工、Systems/design-loop;`decision-add` 記 d1 |
| 整5 | 「跟工作樹那條路相同」不實(工作樹收絕對路徑、無上限) | 同邊6,做法 2 |
| 整6 | 「先提交」沒有出處,也沒防用到舊輪的提交 | 做法 9 新增 spec-freeze,每輪產生提交與快照,快照與提交一定一致;rN-dispatch.json 記 `spec_commit`;附加段印 blob;條款 S15 |
| 整7 | Codex 編排照範本寫什麼也不會發生、沒有說明 | 做法 10:範本標明只對 Claude 編排有效,codex-harness 天生限制補一句 |
| 整8 | 分支新節點怎麼判、「主線」用詞、節點讀舊版、架構段讀 HEAD | 同邊10,做法 6;節點版本寫進附加段頭與實務隱患,另立 REVISIT |
| 整9 | 審計紀錄殘留「標作廢」等相反句子 | 審計修正紀錄在 r1、r2 之後加註「前兩輪做法已整類撤回,舊裁定照舊成立」(原兩行不改字) |
| 回1 | 新舊錯開時看不出來,會跟當晚一樣靜默放空 | 做法 10:範本只叫人用 spec-freeze,它與掛鉤叫的都是全域 lumos,產得出那一行即全域認得;寫明三種組合;用專案內那支的殘餘情況立 REVISIT |
| 回2 | 回退只退掛鉤、漏全域 lumos,update 誰最後跑誰贏 | 回退第 2、3 步:全域 lumos 先退並核對,再各專案 update,最後核對掛鉤指紋,寫回時的處理 |
| 回3 | 舊掛鉤配新 lumos 失敗時靜默 | 做法 10 寫明:只少 note 與說明行、不報錯 |
| 回4 | 舊 lumos 配 `--arch-target` 失敗會白跑兩次 | 實務隱患加「過渡期多一次呼叫」一條 |
| 回5 | 回退後 REVISIT 與 RETIRE-IF 指向不存在的機制;note 讀端 | 回退第 5 步:撤掉或標 `[closed:]`,回退前 grep 確認沒有讀端解析 note 字首 |
| 通1 | 提交編號與凍結快照沒綁在一起,沿用舊輪編號不會被發現 | 同整6,spec-freeze 從提交寫快照、dispatch.json 記 `spec_commit`、lumos 印 `spec_blob`;條款 S15 |
| 通2 | 「凍結快照本來就要先提交」前提錯,強制先提交撞提交前檢查;沒評估暫存 index 退路 | 採用通才席提的暫存 index 加 `commit-tree`:做法 9;條款 S16–S18;工作樹清單比對寫進決策的不選 |
| 通3 | 收 7–40 碼與代碼審完整編號不一致 | 同正3,做法 1 |
| 通4 | 「相同的檢查」不屬實、多 slug 沒寫 | 同邊6、邊7,做法 2 |
| 通5 | 程式檔存在改了,impact 與落點仍讀會談目錄,新檔空手而回 | 同正1,做法 5、6;條款 S6、S7 |
| 通6 | S5 抓不到繞過 `_lens_git` 的 git 呼叫 | 同邊8,條款 S9 |
| 通7 | 掛鉤不解析與記帳矛盾;新代碼進白名單;1MB 沒代碼 | 做法 7、8;`spec_too_large` 新增 |
| 架1 | 自組有上限的提交讀法,沒借 `_nodehome_cat_blobs_capped` | 做法 3:借它讀並說明理由;它不走 `_lens_git`,所以條款 S9 改用假 `git`(選架構席的 b) |
| 架2 | 掛鉤與 lumos 對文法的邊界重複;`_fail_note` 簽名沒交代 | 做法 8:掛鉤只讀 `spec_source`;`_fail_note(r, rng, repo, spec=None)` |
| 架3 | 「相同檢查」不實;三個代碼是新增 | 同邊6;做法 7 寫成新增、改種數與 `LENS_FAIL_REASONS` |
| 架4 | 沒指名借 `_lens_full_sha` 與既有十六進位正規式 | 做法 1 指名 `_lens_full_sha` 與 `_LENS_SHA_RE`(帶 `--end-of-options`);提交裡檔的存在改用 `ls-tree`,一次帶多個路徑 |
| 架5 | 讀計劃有內外兩份,文法會有兩個解析點 | 同邊2,做法 4 共用讀計劃函式 |
| 架6 | 成功也呼叫 `mark` 是新用法,失敗 kind 沒講 | 做法 8:寫明對 `mark` 慣例的有限破例、note 固定字首、spec_* 記 ok 的理由 |

## 補不出來、留給實作

- 決策 d1 的 `alternatives_considered` 與 `trade_offs`:`lumos decision-add` 只收 `--context` 與 `--why`,這兩欄照 lumos-project-notes reference.md「白名單外的 frontmatter 寫入走手動 Edit」補進 d1。
- rN-dispatch.json 是編排者照範本手寫的(lumos 只在 `seat-check --dispatch` 讀它),`spec_commit` 欄由範本要求寫入;seat-check 要不要核對這一欄不在本計劃範圍。
- 讀計劃共用函式的名字(暫名 `_dispatch_lens_read_spec`)與 `cmd_dispatch_lens_spec` 新增的選填參數名,實作時定。
- skills 底下的 SKILL.md、reference.md、commands/05 沒有 Systems 節點把它們列進 about_code(`lumos impact --file` 查不到家);它們是手冊不是程式檔,只有 templates.md 有家(Systems/每輪修補差異派工),已加進 lands_in。

refuted-set:none。
