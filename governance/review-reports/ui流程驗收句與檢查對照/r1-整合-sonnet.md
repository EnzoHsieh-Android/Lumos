severity: major

說明:規格逐節讀完。內部連結 `Projects/Android端到端驗收_計劃`、`Android側UI測試綁圖譜工作流_計劃`、`E2E紅燈現場與不穩帳_計劃`、`截圖基準驗收流程_計劃`、`Systems/android-e2e-acceptance`、`Systems/bound-tests-gate`、`Systems/規格閘`、`Verification/2026-10-31_無檢查流程實機放行` 目標都存在,無斷鏈。固定席 `bound-tests-gate`:這份設計只新增 `t_android_e2e_*` 測試,不改它的 ★INVARIANT★(code-loop check 對固定席合約綁的測試逐支真跑)。判不影響。固定席 `規格閘`:設計重用 `PITFALL_CLASSES`,見 F6,對規格閘本身行為不影響,但對它的「兩條路共用詞表」筆記有牽連。

**F1 做法 5 沒說新判定接在 `_e2e_gate_body` 哪個階段。新情境與新流程一定走整套那條路,spec 讓按功能跑也帶 `checks` 是死欄位。「舊項目只列出」「檢查數變少」的印出行在放行路徑沒有出口。**
引句:「用推送檢查既有的挑主線結果;主線判不出來時照那道判定原本的規則(判不清就擋)。」
- 新情境或新流程會改變 e2e 段,`_e2e_gate_need` 因此一律回 "full"(與分岔點的 e2e 段不同就要整套)。所以只有整套紀錄的 `runs.blocks.ui` 會被讀,`_e2e_gate_by_feature` 讀的 `feature_runs.items` 只有 kind/name/result,用不到 `checks`。
- file: `scripts/lumos:41775`(`_e2e_gate_need` 開頭比 `_e2e_canon`)
- file: `scripts/lumos:41837`(`_e2e_gate_by_feature` 只看 items)
- 整套通過時 `_e2e_gate_full_note` 直接 `_e2e_gate_done("pass")` 丟例外結束。要擋就得在它前面、`_e2e_gate_load` 之後插入,spec 沒寫插在哪。file: `scripts/lumos:42011`
- `_cl_say_e2e_notes` 只處理 ci、skipped-env、pass-by-feature。"pass" 狀態不印提醒,`_codeloop_e2e_step` 也不寫帳。spec 要求推送時列出舊情境、舊流程和檢查數變少,放行時沒有出口。file: `scripts/lumos:68512`、`scripts/lumos:67844`
- 提醒行還得以「提醒」開頭,pre-push 放行路徑才會轉印。
severity: major
blocking: 是,字面實作要嘛擋不到,要嘛列出的清單印不出來,屬漏掉合約。

**F2 d2「單向門要人點頭」「命中不可申辯」只在判定本體內成立,三個既有出口可以整個繞過,spec 沒提。**
引句:「命中不可申辯,作者只能往嚴標。」
- `_e2e_gate_body` 裡 `_e2e_waiver_ok` 為真就直接 "waived",排在所有新判定前面。`by` 可以是 `ai`,沒有互動終端時會自動記成 AI 放行,只在推送時列為「待人看」。
- 另有 `LUMOS_SKIP_ANDROID_E2E=1` 和 `_in_ci()`(第一版 CI 不判)。三者都在 `accept_review.by` 檢查之前就返回。
- 單向門(金流、對外送出)情境因此可以靠 AI 放行通過,人不需要點頭。「人點頭」只是 `human:<名字>` 這個自填字串,實質把關在放行與逃逸。spec 沒寫放行是否涵蓋新規則,也沒寫單向門情境能不能被 AI 放行。
- file: `scripts/lumos:42064`(waiver 先返回)、`scripts/lumos:42036`(`_e2e_gate_escape`)、`scripts/lumos:41713`(`_e2e_waiver_ok` 接受 ai)
severity: major
blocking: 是,d2 的合約在 spec 字面實作下有三條繞路,spec 沒聲明是否接受。

**F3 `checks` 欄不進 `_e2e_record_err`,與既有 WHY「判定讀到的欄位型別在寫入端與判定端同一套驗」衝突。紀錄裡的自由文字 label 也沒有消毒與大小處理。**
引句:「把算數的檢查記進查證紀錄 `runs.blocks.ui` 那支 flow 的新欄位」
- `_e2e_record_err` 只驗 `runs.result`、`runs.ran`、`feature_runs.items`,完全不看 `runs.blocks`。現行判定也從未讀 `blocks`(`_e2e_runs_missing` 只讀 `ran`)。
- 手改或舊版寫的紀錄,`checks.labels` 型別不對時,推送檢查會在內部丟 TypeError。被 `_e2e_gate_evaluate` 接成 `evaluation_error` 擋下,訊息叫人設 `LUMOS_SKIP_ANDROID_E2E=1` 繞過,而不是「修好或刪掉紀錄」。
- file: `scripts/lumos:40849`
- label 來自 flow 檔經 `commands.json`,進擋下訊息要走 `_e2e_gate_out` 的 `_out_clean`。spec 沒要求,而 `Systems/android-e2e-acceptance` 有一條由 AST 掃描守的「外來文字出口」WHY。
- `E2E_RECORD_FILE_MAX` 是 2MB,labels 清單沒有上限。
severity: major
blocking: 是,漏掉既有紀錄驗證合約,並造成誤導性擋下訊息。

**F4 judge 要讀 `<dir>/debug/<flow 的 name:>/commands.json`,但 lumos 零依賴沒有 YAML 解析器,flow 名也有三種不同規則,spec 沒寫怎麼對應。**
引句:「每支 flow 通過的那次嘗試,從 steps.json 那次的 `evidence.dir` 讀 `<dir>/debug/<flow 的 name:>/commands.json`」
- lumos 自己的 flow「名」是 `_e2e_flow_name`:相對路徑去副檔名、`/` 換 `__`,連字號保留,例如 `.maestro__smoke-05-x`。
- Maestro 的子目錄名是 flow 檔頭 `name:` 的值。派工要求規定它是「檔名去副檔名轉底線」(`smoke_05_x`),兩者不同。
- 派工要求自己承認「name↔檔名一致性沒有機械守衛」,`name:` 缺漏或寫錯時子目錄名就對不上。
- spec 沒說靠什麼讀 `name:`(與 Q3「沒有 YAML 解析器」矛盾)。也沒說替代做法,例如每次嘗試的 `<ev>/debug/` 底下只有一個子目錄,可以直接取。中文 `name:` 的命名還留在 S12 沒測。
- 對不上的後果是 `checks: null`,新流程被 S5 擋下,而且很難診斷。
- file: `scripts/lumos:40472`
- file: `scripts/templates/android-e2e-run.sh:495`(`ev` 是每次嘗試一個目錄)
- file: `skills/lumos-project-notes/reference.md:1217`
severity: major
blocking: 是,新流程可能因為名字對不上被誤擋。

**F5 新規則的擋下訊息會沿用「整套跑,跑完提交紀錄再推」的處方,而這處方解不開它們。**
引句:「對新的項目,下面任一成立就擋,擋下訊息列出項目與原因:」
- `_cl_say_e2e_next` 對未識別的 `rep` 走 `_cl_say_e2e_full`,印 `E2E_RUN_CMD` 整套重跑。「新情境要先寫驗收句」「A2 沒有檢查對到」「單向門要 human」靠重跑不會變綠,要改設定或 flow。
- 還會附上「確定是誤擋才放行」的 waive 指令,鼓勵放行。
- 治理帳事件的 `gate_code` 目前只在逾時與內部錯誤時有值,`note` 截到 200 字。RETIRE-IF 要的「因驗收句沒對到而擋下的次數」無法機械統計。spec 沒定義新的 `gate_code`。
- file: `scripts/lumos:68478`、`scripts/lumos:67851`
severity: major
blocking: 是,字面實作會印出錯誤處方,而撤除條件也量不到。

**F6 單向門詞表 `PITFALL_CLASSES` 覆蓋不到 Android 常見的金流與不可逆詞,d2 的前提不成立。**
引句:「用規格閘的關鍵字表(`PITFALL_CLASSES`)只取 payment、external-send、prod-irreversible 三類比對」
- 實跑該詞表(用 case-insensitive 編譯過的正規式):「付款成功後顯示收據」、「結帳」、「刪除帳號後資料消失」、「點數兌換」全部零命中。「使用者按送出訂單」、「訂單送出」命中 external-send。
- spec 的實務隱患只承認「誤報多」這一個方向,沒承認漏報:金流情境用「付款」寫驗收句就不用人點頭。
- 這張詞表在規格閘已被兩條路共用,筆記 PITFALL 寫明改它要同步改 `pitfalls --check`,改了要升 `_DOOR_RULE_VERSION`。Android 閘是第三個消費者。詞表一改,已存在情境是否需要 human 會無聲翻轉,卻不影響指紋。
- 規格閘的筆記沒被列進需要更新的節點。
- file: `scripts/lumos:36543`
- file: `scripts/lumos:13745`
- file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:138`
severity: major
blocking: 是,d2「金流要人點頭」在字面實作下漏掉主要用詞。

**F7 做法 7(檢查數變少)的紀錄來源沒講清楚,多半會是「找不到,不比」。**
引句:「用分岔點那棵樹的 e2e 段算指紋、找 `.lumos/e2e-records/<指紋>.json`」
- 現有 `_e2e_gate_fps` 算 `fp_base` 用的是被推送提交的 e2e 段(`sel`)。spec 要的是分岔點自己的 e2e 段,必須另寫一次指紋計算。
- 沒說從哪個樹讀:分岔點的樹、主線樹或工作目錄。
- 分岔點那版要有人跑過驗收並把紀錄提交進主線,否則大多數情況印「不比」。
- file: `scripts/lumos:41945`
severity: minor
blocking: 否,只是提醒,但實作者會在這裡猜。

**F8 `lands_in` 與需改的 skill 段落沒有逐項列出。**
引句:「寫驗收句的程序**(寫進 lumos-android-evidence 與產 flow 的派工要求,是程序不是機械擋)」**
- `Systems/lumos-cli-write` 的 about_code 列了 skills 檔,所以勉強算家。但它的內容是圖譜寫入原語,與本案無關。
- `Systems/macrobenchmark-adapter` 有「e2e 段格式由 --check-config 驗」的 WHY,沒進 lands_in。
- 要改的 skill 段落沒列:`skills/lumos-android-evidence/SKILL.md:49` 的 cases 鍵說明、reference.md〈產 maestro UI flow 的派工要求〉的第 1 段(斷言)與第 4 段(完成判準)。
- 同一節第 5 段「斷言被刪掉不會有任何機械檢查翻紅」在本案落地後變成不實,spec 沒列要改。
- 另外,`Systems/規格閘.md` 的 PITFALL 也要補第三個消費者(見 F6)。
severity: minor
blocking: 否,文件精度。

**F9 `E2E_SCHEMA` 不升,舊版 lumos 讀到新鍵靜默忽略,新規則在舊機器上等於不存在。**
引句:「舊版 lumos 讀到新鍵會靜默忽略」
- spec 自己承認這件事,卻沒有版本閘或警告。紀錄 schema 仍是 1(`E2E_SCHEMA = 1`),舊版 lumos 讀到 `checks` 也不會被擋。
- file: `scripts/lumos:40433`
severity: minor
blocking: 否,lumos 以 symlink 分發,漂移機率低。

**F10 回退與實務隱患的敘述與做法 5 互相矛盾。**
引句:「不可逆:拿掉三個新鍵就回到現在的行為;查證紀錄只多 `checks` 一欄,舊紀錄沒有這欄照舊判」
- 做法 5 與 S4、S5 對新流程的零檢查、`checks: null` 的擋法,不依賴任何新鍵,所有採用 E2E 的專案都受影響。
- 例如 Maestro 太舊、沒有 `--debug-output` 旗標的專案,新增任何 flow 都會被擋,沒有 opt-in。
- 回退「專案層」那段也寫「零檢查只對新流程擋」,兩處自相矛盾。
severity: minor
blocking: 否,文件自洽問題,行為已由 d1 和 S5 明定。

**F11 「算數的檢查」定義尚未定稿,S1–S3 的判定依據仰賴 S12 的第 0 步實測。**
引句:「assertTrue 與 assertNotVisible 的實際指令名在實作第 0 步實測後寫進這節(S12)」
- 這是 spec 自己承認的未完成項,S12 是 manual 綁定,沒有機械守衛。
- 該指令集本身就是判定核心。
severity: minor
blocking: 否,已標明待實測。

總結:最嚴重 severity 為 major;blocking 共 6 條(F1–F6)。
