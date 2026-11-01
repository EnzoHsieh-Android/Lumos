severity: major

審的是 r1-snapshot.md(凍結 spec)。三個 major、五個 minor。固定席(`Systems/bound-tests-gate`、`Systems/規格閘`)在結尾判。

交叉引用已核對:`[[Verification/2026-10-31_無檢查流程實機放行]]`、`[[Systems/規格閘]]`、`[[Systems/android-e2e-acceptance]]`、`Projects/截圖基準驗收流程_計劃`、`Projects/E2E紅燈現場與不穩帳_計劃`、`Projects/Android側UI測試綁圖譜工作流_計劃` 都在。內部引用「做法第 4 條」「第 6 條」、S12、`PITFALL_CLASSES` 也都在。`lumos macrobench --check-config` 合格回 0、不合格回 2,與 `scripts/lumos:70340` 的說明一致。

## 前置、緣起、PRIOR-ART、RETIRE-IF、實測
已讀,無 finding。

## 做法

**F1 新檢查的插入位置沒定,依現行判定順序,新情境與新流程會整個跳過逐句對照**
- 位置:做法第 5 條「推送檢查判,只對新開發的情境與流程」,和第 4 條「按功能跑的 `feature_runs` 同樣帶」。
- 問題:
  - 新情境或新流程一定改到 e2e 段,所以 `_e2e_gate_need` 第一個判斷就回 `("full", ["驗收設定(e2e 段)跟分岔點不一樣"])`。
  - 走到 `_e2e_gate_full_note`,整套 pass 時直接 `_e2e_gate_done("pass", …)` 丟 `_E2eGateStop` 放行。
  - 如果新規則實作在 `_e2e_gate_full_note` 之後,最常見的情況(新情境加整套通過)就不會執行。
  - `waived` 在 `_e2e_gate_body` 裡更早就返回。spec 沒說放行是否也蓋住新規則。
  - 新項目一律走整套,所以第 4 條要求 `feature_runs` 也帶 `checks`,推送檢查永遠不會讀它。`_e2e_case_results` 產的 items 只有 `{kind,name,result}`,spec 也沒定義 `checks` 掛在哪。
- 佐證:
  - file: `scripts/lumos:41779-41780`,`_e2e_gate_need` 第一個判斷回 full。
  - file: `scripts/lumos:42011-42034`,full 通過就 `_e2e_gate_done("pass")`。
  - file: `scripts/lumos:42045-42073`,`_e2e_gate_body` 順序為 waived、`_e2e_gate_full_note`、需要整套時的擋下、按功能判斷。
  - file: `scripts/lumos:41276-41290`,`_e2e_case_results` 的 items 欄位。
- 引句:「新流程在紀錄裡 `checks.count` 是 0 →「這支流程沒有任何檢查」。」
- 引句:「按功能跑的 `feature_runs` 同樣帶」
severity: major
- blocking: 是。照字面實作可能做出一個在最常見路徑上不執行的守衛,屬於漏掉合約。

**F2 單向門關鍵字表認不得一般 UI 驗收句,金流、不可逆畫面照樣躲過「要人點頭」**
- 位置:做法第 6 條、決策 d2、S8。
- 問題:
  - `PITFALL_CLASSES` 是為計劃散文寫的詞表,payment 類只有「金流、payment、stripe、billing、退款、refund、扣款」,不含 UI 句子最常用的詞。
  - 我用 `PITFALL_CLASSES` 原詞表逐字比對(同 `_PITFALL_COMPILED` 的編譯方式),下列句子全部回空,不算單向門:
    - 「點擊付款後顯示付款成功」
    - 「結帳完成顯示訂單編號」
    - 「使用者點擊支付按鈕」
    - 「轉帳成功」
    - 「儲值點數」
    - 「點確認刪除帳號後帳號消失」
    - 「按下發送後顯示已發送」
  - 有命中的只有「信用卡扣款成功」和「購物車 送出訂單」。
  - d2 只承認「寫得避開關鍵字就躲得掉」。這裡不是刻意閃避,是最自然的措辭就漏掉,實務隱患節只談了誤報多、沒談漏報。
  - 表另外沒有「刪除、發送、傳送」,但 S8 宣稱金流、對外送出、不可逆三類都會被認出。
  - 加詞要升 `_DOOR_RULE_VERSION`,並動到規格閘與 `pitfalls --check` 共用的表。spec 沒說要擴表,也沒說要另立一張。
- 佐證:
  - file: `scripts/lumos:36543-36548`,詞表內容。
  - file: `scripts/lumos:13745`,改表要升版號。
- 引句:「命中任一就是單向門(不取第四類 self-governance:那是工具鏈自己的守衛面,跟 App 功能無關);作者標了 `one_way` 也是。」
severity: major
- blocking: 是。S8 宣稱的覆蓋面實際漏掉主要用詞,金流類新情境可只靠代理審放行。

**F3 judge 找 `commands.json` 的目錄依「flow 的 `name:`」,但沒說怎麼取得,也沒說沒有 `name:` 的 flow 怎麼辦**
- 位置:做法第 4 條、實測、S3、S12。
- 問題:
  - 做法寫 judge 讀 `<dir>/debug/<flow 的 name:>/commands.json`。
  - judge 拿到的只有設定裡的 flow 路徑和 `steps.json`。lumos 零依賴、沒有 YAML 解析器(spec 自己用這點否決 Q3 的靜態解析),所以 judge 得自己 regex 讀 `name:`。spec 沒定義這段。
  - 實測探針有寫 `name: label_probe`。多數 Maestro flow 不寫 `name:`,此時子目錄怎麼命名 spec 沒測也沒定義。S12 只列了中文 `name:`。
  - 字面實作遇到沒 `name:` 的 flow 就找不到檔,記成 `checks: null`。按 S5,這些新流程全部被擋,擋下理由還是「讀不到執行紀錄」。
  - 範本腳本每支 flow 的每次嘗試都有獨立的 `ev` 目錄(`<run>/ui/<name>.try<N>`),裡面只會有那一次執行的紀錄。spec 沒用這個條件簡化成「在 `<ev>/debug` 底下找」,也沒定義找到多個或沒有時的行為。
  - 子流程(`runFlow: file`)的指令在 `commands.json` 是巢狀還是攤平,spec 沒寫。若只掃頂層,標在共用子流程裡的 label 會被算成不存在。S12 的實測清單沒列這項。
- 佐證:
  - file: `scripts/templates/android-e2e-run.sh:493-501`,`ev` 目錄與 `--debug-output` 的組法。
  - file: `scripts/lumos:40920-40947`,`_e2e_judge_ui` 現行沒讀 YAML,也沒帶出通過那次的 `evidence`。
- 引句:「從 steps.json 那次的 `evidence.dir` 讀 `<dir>/debug/<flow 的 name:>/commands.json`」
severity: major
- blocking: 是。照字面實作會把合格的新流程判成讀不到而擋下(誤擋),或掃漏巢狀指令而漏判。

**F4 檢查數的紀錄欄位沒有型別驗證,舊紀錄缺欄位的行為也沒定義**
- 位置:做法第 4、5 條、S3、S5。
- 問題:
  - `_e2e_record_err` 註明「判定會讀到的欄位型別也在這裡驗,不走到判定內部出錯」。spec 沒要求把 `checks` 納入。`_e2e_record_update` 也共用同一套檢查。
  - `checks` 若是字串、`count` 不是整數、`labels` 含非字串(紀錄是 git 樹裡的任意 JSON),新規則會丟例外,結果是 `evaluation_error` 的泛用擋下,不是「紀錄讀不懂」的指引。這是安全方向的失敗,所以只算 minor。
  - 第 5 條只定義了 `checks` 為 null 和 `count` 為 0。`checks` 欄位根本不存在(舊版 lumos 寫的、或 judge 沒補)沒有規則;第 7 條倒是有定義舊紀錄缺欄。
  - `accept` 的新格式驗證放在哪也沒說。`_macrobench_config` 和閘的 `_e2e_cfg_err` 是同一個函式;若只放 `--check-config` 專用路徑,閘對提交樹內沒驗過的 `accept`(例如不是清單)會直接崩潰。
- 佐證:
  - file: `scripts/lumos:40849-40876`,`_e2e_record_err`。
  - file: `scripts/lumos:41100-41133`,`_e2e_record_update`。
  - file: `scripts/lumos:41935,41952`,閘對主線版與被推送提交的 `_e2e_cfg_err`。
- 引句:「新流程 `checks` 是 null →「讀不到執行紀錄:<原因>」(不放行;Maestro 太舊沒帶旗標、不是用範本腳本跑的、檔不在都走這條)。」
severity: minor
- blocking: 否。失敗方向是擋,但行為與指引不明確,屬於 spec 精度。

**F5 單向門比對的範圍與輸出細節**
- 位置:做法第 6 條、S8。
- 問題:
  - 比對範圍是「情境名或任一驗收句的 `text`」,不含功能名。`billing.list` 這種功能名帶字、情境名泛用、驗收句沒寫關鍵字的情境不會命中。`state` 欄也不讀。
  - 現有的 `_pitfall_scan_classes` 直接對原文跑 regex,只回類別名,不回命中的字。門判定另有一套 NFKC 與去零寬字元的正規化。spec 要「印命中的類別與字」又說「硬訊號」,但沒說沿用哪一個比對函式。
  - 若直接呼叫現成函式,全形的「ＳＥＮＤ」、夾零寬字元的「送​出」比不到,也印不出命中的字。
- 佐證:
  - file: `scripts/lumos:59021-59026`,`_pitfall_scan_classes` 只回類名。
  - file: `scripts/lumos:13745`,正規化規則版本說明。
- 引句:「情境名或任一驗收句的 `text`,用規格閘的關鍵字表(`PITFALL_CLASSES`)只取 payment、external-send、prod-irreversible 三類比對」
severity: minor
- blocking: 否。範圍與輸出是精度問題,和 F2 的詞表缺口比是次要。

**F6 算數檢查的定義讓「零檢查」規則容易被繞過,純設定類流程會被強迫加檢查**
- 位置:做法第 4 條算數檢查、第 5 條新流程零檢查。
- 問題:
  - `extendedWaitUntil` 被算成檢查。登入、清資料這類只做前置的新 flow,常見寫法就是 `launchApp` 後接 `extendedWaitUntil`,所以 `count > 0` 輕易成立。
  - 反過來,純前置、沒有任何斷言的新 flow 會被擋,spec 沒有豁免。
  - `repeat`、`retry` 迴圈裡的斷言每次都記一筆,`count` 被灌大。第 7 條「從 5 個變 2 個」的比較會因迴圈次數而不穩。
  - 這個缺口在有 `accept` 的情境裡由 label 對照補上。不在有 `accept` 的情境裡的新流程(例如新流程掛在舊情境下)只剩這個 `count > 0` 防線。
- 佐證:spec 自己在算數檢查列出 extendedWaitUntil。
- 引句:「assertConditionCommand(assertVisible、assertNotVisible、extendedWaitUntil 都落在這)」
severity: minor
- blocking: 否。語意上的精度問題,spec 的「不做」節已聲明不判斷檢查有沒有驗到重點。

**F7 第 7 條「分岔點的紀錄」去哪棵樹讀、多常存在沒定義**
- 位置:做法第 7 條、S10。
- 問題:
  - 紀錄放在 `.lumos/e2e-records/<指紋>.json`。分岔點的紀錄通常在它之後才由「記錄 Android 端到端驗收」的提交加進樹,不一定在分岔點那個提交自己的樹裡。
  - spec 沒說讀分岔點樹、主線樹還是工作目錄。若讀分岔點那棵樹,多數情況會是「分岔點沒有可比的紀錄」,這條形同虛設。
  - 這一條不影響擋不擋,只是效益問題。
- 佐證:file: `scripts/lumos:41986-42010`,`_e2e_gate_load` 是從被推送提交的樹用 `_e2e_tree_json` 讀紀錄。
- 引句:「用分岔點那棵樹的 e2e 段算指紋、找 `.lumos/e2e-records/<指紋>.json`」
severity: minor
- blocking: 否。只提醒、不擋。

**F8 `accept_review` 沒綁驗收句內容,「human:」是自填字串**
- 位置:做法格式、第 2 條第 4 步、d2、S8。
- 問題:
  - `by` 只檢查前綴,`at` 只檢查日期格式,沒綁 `accept` 內容的雜湊。審完之後改了驗收句,只要 e2e 段變動會讓舊紀錄失效,但 `accept_review` 照舊有效,沒有「審的是這一版」的機械保證。
  - 寫驗收句的代理也能自己寫 `human:` 開頭,擋不了。信賴原則本來就不防刻意偽造,這裡只是把它寫進 spec 的「要人點頭」說法。
- 佐證:spec 自己的格式與 S8 只比對前綴。
- 引句:「`accept_review`:`{"by": "agent:<模型>" 或 "human:<名字>", "at": "YYYY-MM-DD"}`。」
severity: minor
- blocking: 否。程序性保證,spec 其他處已說明是程序不是機械擋。

## 待決問題、驗收條款、實務隱患、回退、不做
- 待決問題:已讀,無 finding。Q1、Q2 的題目文字已被 d1、d2 取代,spec 自己有註明。
- 驗收條款:S1 到 S13 與 F1 到 F3 的缺口有關。S4 到 S9 的測試名稱沒有一條覆蓋「閘在整套通過路徑上仍會執行新規則」,所以 F1 即使實作也測不出來。
- 實務隱患:
  - 本機驗收時與推送時主線不同:spec 的兩段分工站得住。judge 只記事實,與主線無關;推送時才依當下主線判新舊,不會因為中間合併過主線而判錯。
  - Maestro 改版:讀不懂記 `checks: null` 並擋新流程,方向正確。F3 的目錄命名問題會讓同樣的結果提早在沒改版時就發生。
  - 其他風險類(金流、對外送出、不可逆、守衛面)spec 已逐項回答,「已排除」三行不矛盾。
- 回退、不做:已讀,無 finding。

## 固定席判斷
- `Systems/bound-tests-gate`:不影響。該節點宣稱的是 code-loop check 對固定席合約綁的測試逐支真跑。這份設計只動 Android e2e 的 judge、推送檢查、設定格式,不碰這個閘。
- `Systems/規格閘`:不影響其行為,但有連帶影響。spec 引用 `PITFALL_CLASSES` 當單向門詞表。若為了解決 F2 去擴這張表,必須同步升 `_DOOR_RULE_VERSION`,也會改變規格閘與 `pitfalls --check` 的命中結果。

最嚴重 severity:major,blocking 共 3 條(F1、F2、F3)。
