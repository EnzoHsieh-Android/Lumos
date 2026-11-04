severity: major

審查範圍:逐節讀完凍結 spec(開頭欄位、白話、實測、做法 1 到 8、待決問題、驗收條款 S1 到 S13、實務隱患、回退、不做)。文件內部交叉引用的目標都存在:Projects 四篇計劃、Verification 的 `2026-10-31_無檢查流程實機放行`、Systems 三篇。檢查過 `scripts/lumos` 的 `_e2e_judge_ui`、`_e2e_gate_mainline`、`_e2e_gate_need`、`_e2e_gate_body`、`_e2e_case_err`、`_e2e_load_json`、`_e2e_record_err`、`PITFALL_CLASSES`,以及 `scripts/templates/android-e2e-run.sh`。我沒有裝置,Maestro 的 commands.json 實際形狀無法親驗,標 ⚠ 的是這類。

**固定席**
- `Systems/bound-tests-gate`(★INVARIANT★:code-loop 對固定席合約綁的測試逐支真跑):不影響。這份設計只動 android-e2e 的 judge、推送檢查與設定檢查,不碰 code-loop check 的測試真跑路徑。
- `Systems/規格閘`:不影響其行為。spec 只唯讀引用 `PITFALL_CLASSES` 詞表,但見 finding 10 與 15。

**做法 1(設定格式)**

1. 做法 1、S11:`accept: []`(鍵存在、清單是空的)沒有任何規則擋。
   - 引句:「text 空、by 不是 agent: 或 human: 開頭」
   - 壞在哪:S11 只驗每一項的內容,沒有驗清單非空。做法 5 的「沒有 accept」若實作成鍵不存在才算,新情境寫 `accept: []` 就過了設定檢查。做法 5 的逐句對照是對空集合逐句檢查,全數「已對到」,等於一句驗收句都不用寫就放行。
   - 佐證:file: `scripts/lumos:40597`(`_e2e_case_err` 對情境內其他鍵都用「非空」判,這三個新鍵 spec 沒定)。
severity: major
   - blocking: 是,照字面實作會讓「新情境要先寫驗收句」被空清單繞過。

2. 做法 1、5:只有 visual、stability、macrobench 而沒有 flows 的新情境,永遠過不了推送檢查。
   - 引句:「新情境的某一句,在這個情境所有 flow 的」
   - 壞在哪:`_e2e_case_err` 允許情境只列 visual、macrobench 或 stability,至少一樣即可。這種新情境依做法 5 必須有 `accept`,但 label 只存在於 flow 的 commands.json,情境沒有 flow,聯集是空的,每一句都「沒有檢查對到」。唯一的出路是 finding 1 的 `accept: []`,而那是個洞。
   - 佐證:file: `scripts/lumos:40597` 的 `kinds = ("flows", "visual", "macrobench", "stability")` 與「至少要列一樣要跑的東西」。
severity: major
   - blocking: 是,照字面實作會誤擋合法的非 UI 新情境,或逼人走空清單。

**做法 4(judge 記事實)**

3. 做法 4:「`<flow 的 name:>` 子目錄」要怎麼知道,spec 沒說,而且跟自己選的前提矛盾。
   - 引句:「靜態解析看不出,且 lumos 零依賴沒有 YAML 解析器」
   - 壞在哪:Q3 以「lumos 沒有 YAML 解析器」為由選讀執行紀錄。但做法 4 要讀 `<dir>/debug/<flow 的 name:>/commands.json`,judge 必須先從 flow 檔取得 `name:`。這件事需要解析 YAML,或用正則抓第一行。
     - flow 沒寫 `name:` 時 Maestro 的預設目錄名是什麼,spec 沒寫。
     - lumos 的 `_e2e_flow_name` 把 `.maestro/list.yaml` 變成 `.maestro__list`,跟 Maestro 的 `list` 很可能不同。
     - 中文或含 `/`、`..` 的 `name:` 怎麼取、怎麼防路徑穿越,都留給 S12。
   - 佐證:file: `scripts/lumos:40472`;file: `scripts/templates/android-e2e-run.sh:493`(每個 flow 每次嘗試各有獨立的 `--debug-output` 目錄,`debug/` 底下本來就只有這一支 flow 的子目錄,不需要 `name:` 反查)。
severity: major
   - blocking: 是,不訂規則,實作不是猜錯目錄(所有新流程記成 `checks: null` 被擋),就是對 `name:` 缺省的 flow 失效。

4. 做法 4:`runFlow` 引入的子流程、`repeat`、巢狀深度與 commands.json 大小,都沒有處理。⚠(commands.json 的實際巢狀形狀沒親驗)
   - 引句:「AI 類檢查(預設 optional、結果不穩定)不算」
   - 壞在哪:實測只探了「條件不成立的 runFlow → SKIPPED 且裡面不出現」。三個沒答的點:
     - 條件成立的 `runFlow`、`repeat` 裡的檢查,是巢狀在父指令底下,還是在另一個 name 子目錄?只掃最上層 list 的話,檢查全寫在子流程裡的新流程會被判 `count==0` 而擋;反過來,`repeat` 展開 N 次會讓 `count` 暴增。
     - 讀檔走 `_e2e_load_json`,它限深 20 層,超過回「巢狀太深」。commands.json 每層巢狀大約多 3 到 4 層 JSON,約 5 層 `repeat`、`runFlow` 就會被判成 `checks: null`、新流程被擋。這個 helper 也沒有檔案大小上限。
     - `labels` 清單沒說去重或設上限。`repeat` 內有 label 的檢查會把重複 label 寫成上千筆。單份查證紀錄上限是 2MB(`E2E_RECORD_FILE_MAX`),超過整份紀錄讀不懂、推送被擋。
   - 佐證:file: `scripts/lumos:40932`(`_e2e_load_json` 的 `_events_depth_ok(raw, 20)`);file: `scripts/lumos:42128`(`E2E_RECORD_FILE_MAX = 2 * 1024 * 1024`)。
severity: major
   - blocking: 是,用 runFlow 子流程或迴圈的合法新流程會被誤擋,或紀錄被撐爆。

5. 做法 4、5 與 S3 到 S5:舊 lumos 寫的紀錄裡 `checks` 欄不存在(不是 null),spec 沒定怎麼判,gate 也沒定怎麼驗型別。
   - 引句:「舊紀錄沒有這欄照舊判」
   - 壞在哪:spec 自己承認「舊版 lumos 讀到新鍵會靜默忽略」。若有人用舊版 lumos 跑 judge,紀錄的 `flow` 條目沒有 `checks`,指紋因 e2e 段含新鍵而對得上。S4(`count==0`)與 S5(`null`)都沒涵蓋「欄位不存在」,依字面實作很可能 `rec.get("checks")` 當 `None` 走 S5,或被當舊紀錄放過去。
     - 另外 `checks` 若不是物件、`count` 不是整數、`labels` 不是字串清單,spec 沒說要加進 `_e2e_record_err` 的型別檢查。現有慣例是「判定會讀到的欄位型別也在這裡驗」,不然 gate 會在判定內部丟 TypeError。
   - 佐證:file: `scripts/lumos:40866`(`_e2e_record_err` 的註解與型別檢查)。
severity: major
   - blocking: 是,欄位缺失與畸形值的 gate 行為未定,可能失效放行,也可能崩潰。

**做法 5(推送檢查判)**

6. 做法 5:兩個情境共用同一支 flow 時,另一個情境的 label 會被當成「多餘 label」誤擋。
   - 引句:「卻沒有這一句 →列出那個 label(打錯字會讓句子看似有人管)」
   - 重現:新情境 A 與舊情境 B 共用 `list.yaml`(`_e2e_features_err` 允許同一支 flow 出現在多個情境的 flows)。flow 裡有 `驗收:f.B#1` 與 `驗收:f.A#1` 兩個 label。
   - 壞在哪:對 A 做「flow 帶了 label 卻沒有這一句」時,B 的 label 是否算錯,spec 沒限定只看前綴為 `驗收:f.A#` 的 label。字面讀法會誤擋。S7 同樣寫「有 label 指到它沒有的句子」。反向也一樣:A 的 label 要寫在 B 也會跑的 flow 裡,B 的檢查沒對應,spec 沒定。
   - 佐證:file: `scripts/lumos:40597` 起的 `_e2e_case_err`,`flows` 只驗存在於整套清單,不驗獨佔。
severity: major
   - blocking: 是,共用 flow 是現行設計允許的合法用法,字面實作會誤擋。

7. 做法 5 與 S4 到 S8:新判定在 `_e2e_gate_body` 的哪個位置、waiver 與 `LUMOS_SKIP_ANDROID_E2E` 對它有沒有效,spec 沒說。
   - 引句:「用推送檢查既有的挑主線結果;主線判不出來時照那道判定原本的規則(判不清就擋)。」
   - 壞在哪:現行順序是 CI 或 SKIP 環境變數先結束,接著載入紀錄,然後 `waivers` 通過就直接 `waived`,再來才進 `_e2e_gate_full_note`,整套 pass 就 `_E2eGateStop` 放行。新判定放哪裡,結果完全不同:
     - 放在 waiver 之後:人放行一次就繞過全部新規則。
     - 放在 waiver 之前:沒有任何人工出口,關鍵字誤判單向門(實務隱患自己承認很常見)只能用 `LUMOS_SKIP_ANDROID_E2E=1` 關掉整道。
     - 放在 `_e2e_gate_full_note` 之後:整套 pass 會直接放行,新判定根本跑不到。
   - 佐證:file: `scripts/lumos:42076` 起的 `_e2e_gate_body` 與 `_e2e_gate_full_note`(`_e2e_gate_done("pass"…)` 會提早結束)。
severity: major
   - blocking: 是,位置決定這道守衛能不能被繞,spec 沒定,實作者只能猜。

8. 做法 5 與決策 d1:專案第一次引入 `features` 表時,所有既有情境都被當成「新情境」。
   - 引句:「既有的情境與流程照舊判,只在推送時列出還沒有驗收句或零檢查的舊項目,不擋」
   - 重現:主線的 e2e 段有 `flows` 但沒有 `features`(`_e2e_features_err` 對 `feats is None` 回 None,合法)。某分支新增 `features` 表,把既有 flow 分到情境裡。
   - 壞在哪:這些情境「主線與分岔點的 features 都沒有」,依字面全是新情境,全部要 `accept`、label 對照、單向門判斷,但底下的 flow 都是舊的,檔案根本沒動。這違反 d1 的不溯及既往。情境改名、功能改名也是同樣結果,spec 沒提。
   - 佐證:file: `scripts/lumos:40700` 附近 `_e2e_features_err` 的 `feats is None` 分支。
severity: major
   - blocking: 是,實作者要自己決定新舊,字面結果會大面積誤擋老專案。

9. 做法 5:「新流程」的判定沒說要先正規化路徑。
   - 引句:「當情境或流程在主線與分岔點已經存在時,不論有沒有」
   - 壞在哪:現有碼一律用 `_e2e_norm`(去空白、去結尾 `/`、去 `./`),`e2e.flows` 裡 `./.maestro/a.yaml` 與 `.maestro/a.yaml` 視為同一支。spec 沒要求,改寫 flows 的寫法就能讓舊流程在比對時變成「新流程」,被零檢查規則誤擋。
   - 佐證:file: `scripts/lumos:40463`。
severity: minor
   - blocking: 否,措辭精度,實作者順手用既有 helper 即可。

10. 做法 6 與 S8:單向門認定只比對情境名和驗收句 text,不看功能名,也沒說比對前要不要正規化。
    - 引句:「命中不可申辯,作者只能往嚴標」
    - 壞在哪:
      - 功能名 `billing`、情境名 `confirm`、驗收句「顯示確認」不會命中任何詞。
      - 規格閘自己的門掃描有 NFKC、去零寬字元的處理(`_DOOR_RULE_VERSION` 第 6 到 12 版),但 `_pitfall_scan_classes` 只是對原文做 `re.search`。若實作直接呼叫它,全形「ｓｅｎｄ」、「送​出」(夾零寬字元)都不命中。「不可申辯」的硬訊號就有一道很窄的縫。
    - 佐證:file: `scripts/lumos:59021`(`_pitfall_scan_classes`)。
severity: minor
    - blocking: 否,d2 已承認躲得掉、單人自用的威脅模型下不算 blocker。

11. 做法 5:主線版根本沒有 e2e 段的情況(第一次引入 E2E),新判定整段不適用,spec 沒提。
    - 引句:「主線判不出來時照那道判定原本的規則」
    - 壞在哪:`_e2e_gate_mainline` 在「主線版沒有 e2e 段」時直接 `_e2e_gate_done("not-required")`,後面的新判定一條都不會跑。第一次把 e2e 加進專案的分支,即使所有情境與流程都是新的,也零檢查放行。「主線判不出來」不包含這條路徑。
    - 佐證:file: `scripts/lumos:41922`(`_e2e_gate_mainline`)。
severity: minor
    - blocking: 否,可能是刻意取捨(引入分支還沒有主線可比),但 spec 沒寫,應補一句。

12. 做法 5:擋下訊息要列出項目與原因,數量與長度沒有上限。
    - 引句:「擋下訊息列出項目與原因」
    - 壞在哪:`accept` 條數、`text` 長度、label 條數都不設上限。其他清單都有上限(`E2E_PATH_LIST_MAX = 200`)。大量 `accept` 或 `labels` 會使訊息和 e2e 段(進指紋與 `_e2e_canon`)無限膨脹。label 與 text 是作者可控的文字,會進 AI 視野,要走 `_out_clean`,spec 沒提。
    - 佐證:file: `scripts/lumos:40481`。
severity: minor
    - blocking: 否,資源與回顯的防禦性細節。

**做法 7(檢查數變少只提醒)**

13. 做法 7、S10:對比的紀錄要去哪一棵樹找,spec 沒說清楚。
    - 引句:「分岔點沒有可比的紀錄,這次不比」
    - 壞在哪:「用分岔點那棵樹的 e2e 段算指紋、找 `.lumos/e2e-records/<指紋>.json`」沒說這檔是從分岔點的樹還是被推送提交的樹讀。
      - 若分岔點沒有 e2e 段(見 finding 11),指紋算不出來。
      - 若新流程的 `checks` 因 `repeat` 而數量不穩定,「變少」就會誤報。
      - 若該 flow 改名,也比不到。
    - 佐證:file: `scripts/lumos:41922`(base 的取得方式)。
severity: minor
    - blocking: 否,只影響提醒,不擋。

**待決問題、驗收條款**

14. 做法 1、2.4:人工點頭(`accept_review.by: human:`)寫在 e2e 段內,會使所有查證紀錄失效。
    - 引句:「e2e 段整段算進指紋,三個鍵改了,舊的通過紀錄自然失效、要重跑。」
    - 壞在哪:單向門情境必須由人簽 `accept_review`。人通常在代理跑完實機之後才簽,簽完修改 e2e 段,指紋變了,`_e2e_gate_need` 判成整套(`_e2e_canon` 不同就回 `"full"`),要為一次簽名重跑整套實機。順序上要先簽才能跑。spec 沒把這點寫進程序。
    - 佐證:file: `scripts/lumos:41775`(`_e2e_gate_need` 首段)。
severity: minor
    - blocking: 否,只是流程成本,不是正確性問題。

15. 開頭欄位 `pending_questions` 的 Q1、Q2 文字與已裁決衝突,而且引用未定義的設定。
    - 引句:「Q1、Q2 的題目文字是當時的建議,以裁定後的決策 d1(不溯及既往)、d2(單向門要人點頭)為準」
    - 壞在哪:Q1 的 `text` 寫著 `accept_required: true` 與「KDS 接上這版後就打開」,但這個鍵在整份 spec 沒有定義,S11 的格式檢查也不收。Q2 的 `risk` 欄位同樣不存在。〈待決問題〉一節只說「以 d1、d2 為準」,留下兩個未定義的詞,讀的人可能照題目文字去實作。
    - 佐證:file: `docs/lumos-toolchain-knowledge/Projects/UI流程驗收句與檢查對照_計劃.md`(凍結 spec 的開頭欄位)。
severity: minor
    - blocking: 否,文件精度。

**你列的極端情境,沒找到具體壞輸入的**
- 同一句被兩個檢查對到、一個 label 只能帶一個 id:不壞,聯集語意對。
- label 含空白、全形字、前綴大小寫、id 撞名:label 與 id 都是精確字串比對。偏差只會變成「沒有檢查對到」加上「帶了 label 卻沒有這一句」兩條擋下訊息,有被抓到。
- 第一次失敗第二次才過:做法 4 取通過那次。範本腳本每次嘗試各有獨立的 `.try1`、`.try2` 目錄,讀對。
- 中文 `name:` 子目錄命名:spec 自己承認沒測,併入 finding 3。

**實務隱患(風險類逐類)**
- 金流、對外送出、不可逆:無。spec 只改判定、推送檢查與設定格式,不碰付款、不送資料,拿掉新鍵就回到現狀,但詞表的語意邊界見 finding 10。
- 守衛面(推送檢查決定擋不擋):命中。壞法見 finding 1、2、5、6、7、8:有空洞放行(1、5、7),也有誤擋(2、6、8)。
- 並發:無。紀錄寫入沿用 `_e2e_record_update`,spec 沒新增併發寫入路徑。
- 資源與回顯(巢狀、大小、清單膨脹):命中,見 finding 4、12。
- 認證、快取、PII:無,這份設計不處理這些。

最嚴重 severity:major;blocking 共 8 條(finding 1 到 8),minor 共 7 條(finding 9 到 15)。
