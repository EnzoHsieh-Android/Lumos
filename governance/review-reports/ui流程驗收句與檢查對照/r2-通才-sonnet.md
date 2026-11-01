severity: major

這次只做純讀,沒有建暫存目錄,也沒有刪任何檔。

## 逐節

- 前言與緣起、PRIOR-ART、RETIRE-IF:已讀,無 finding。
- 實測:見 F4。
- 做法 1 設定格式:見 F9。
- 做法 2 寫驗收句的程序:見 F7。
- 做法 3 流程裡標對應:已讀,無 finding。
- 做法 4 judge 記事實:見 F9、F10。
- 做法 5 推送檢查:見 F1、F2、F5、F8、F11。
- 做法 6 單向門怎麼認:見 F3。
- 做法 7 檢查數變少:已讀。`_e2e_fingerprint(root, base, …, allow_missing=True)` 現成,可以拿分岔點自己的 e2e 段重算,無 finding。
- 做法 8 舊項目只列出:已讀。放行時能印提醒的前提是紀錄有讀進來,列表只在讀得到紀錄的路徑出現,無 finding。
- 驗收條款 S1–S15:每一條做法都對得上條款。對不上的只有 F4 的過期引用,和做法 4 的預覽、做法 5 的條數上限沒有條款。
- 實務隱患:
  - 金流、對外送出、不可逆:無,因為只改判定、設定格式和讀本機紀錄,不碰付款、不送資料到外部。
  - 守衛面:命中,見 F1、F2、F5。
  - 資源:`_e2e_load_json` 的深度上限確實是 20(`scripts/lumos:40972`);紀錄單份上限 `E2E_RECORD_FILE_MAX` 是 2MB;spec 另設專用上限,講法一致,無 finding。
  - 併發:無,因為推送檢查是單次唯讀判定。
- 回退:見 F6。
- 落點、審計修正紀錄:見 F8。

## 驗證過的引用

- 存在且語意如 spec 所述:
  - `_e2e_judge_ui`(`scripts/lumos:40920`)
  - `_e2e_gate_body`、`_e2e_gate_full_note`、`_e2e_gate_need`、`_e2e_gate_mainline`
  - `_e2e_waiver_ok`(收 human 或 ai)
  - `_e2e_record_err`
  - `_e2e_norm`
  - `_cl_say_e2e_next`、`_cl_say_e2e_notes`(放行路徑只轉印含「提醒」的行)
  - `E2E_PATH_LIST_MAX = 200`
  - `_out_clean`
- `_e2e_judge_ui(e2e, steps)` 的簽名沒有 run 目錄或專案根。spec 說 judge 的輸入有這兩樣,實作要靠 steps.json 的絕對路徑,不是問題。
- 範本腳本每次嘗試的 debug 目錄就是 `ev/debug`,跟 spec 寫的一致。

## Findings

**F1. 新規則的「沒有 checks 欄」分支,會把「沒整套跑過」和「跑了但沒過」都講成「舊版 lumos 寫的」**

引句:「新流程 `checks` 是 null,或紀錄裡根本沒有 `checks` 欄(舊版 lumos 寫的)」

- 重現:
  - 新增一支新流程,只跑 `--case`、沒整套跑,提交了紀錄,此時 `runs` 是 null。
  - 或整套跑了但那支新流程第二次還是紅,此時 judge 只對通過的嘗試記 `checks`,失敗或沒跑到的流程沒有 `checks`。
  - 照 S5 字面,推送檢查印「紀錄是舊版 lumos 寫的,更新 lumos 後重跑」。
  - 但現行路徑會印的是「這次改動要整套驗收」或「整套結果是沒過」,方向正確。
- 壞處:新規則排在 `_e2e_gate_full_note` 前面,搶先印出誤導的原因,使用者去更新 lumos 而不是補整套或修紅燈。
- spec 沒定義 `runs` 為 null、`runs.result` 不是 pass、或流程在 `ran.flows` 之外時,新規則要不要先讓位給整套那條路。
- file: `scripts/lumos:42011-42030` 的 `_e2e_gate_full_note` 在 `runs` 不是物件時回 "",之後 `_e2e_gate_body` 印「這次改動要整套驗收」。這是現行正確的說法,新規則會蓋掉它。

severity: major
blocking: 是,照字面實作會對常見情境印出錯的處方,屬於會做出錯行為的 major。

**F2. 「AI 放行蓋不過」的理由,對 `checks: null` 這一支不成立**

引句:「AI 放行蓋不過——這幾條的成因是設定與流程內容,不是裝置狀態造成的誤擋,AI 自己補檢查、補驗收句就解得開」

- 重現:`checks: null` 的成因,spec 自己列了三種:
  - steps.json 沒有 `evidence.debug`(消費專案裡 vendored 的 `scripts/templates/android-e2e-run.sh` 比 lumos 舊)。
  - Maestro 太舊,`EVIDENCE` 為 false,`evidence.dir` 就是 None。
  - Maestro 改版讓 commands.json 讀不懂(實務隱患也承認)。
- 壞處:這三種都是工具或環境的問題,補檢查、補驗收句解不開。
  - 新流程因此只剩人放行一條路。
  - S12 規定擋下訊息的下一步是「改設定或流程再跑整套」,依這個處方做,會一直擋下去。
- 該分支需要自己的處方,例如更新 lumos 或範本腳本、升級 Maestro。
- file: `scripts/templates/android-e2e-run.sh:330` 的 `EVIDENCE = maestro_has_evidence_flags()`。
- file: `scripts/templates/android-e2e-run.sh:501` 寫入 `{"dir": ev if EVIDENCE else None}`。
- file: `scripts/lumos:31991` 把範本腳本列在 `lumos update` 發放清單,消費專案手上那份會落後。

severity: major
blocking: 是,理由和處方照字面實作都會錯。

**F3. 單向門的機械地板,spec 沒說類別名要轉換**

引句:「用規格閘的同一支掃描(`_door_keyword_hits`,含它的全形與零寬字元正規化)比對,只留 payment、external-send、prod-irreversible 三類的命中」

- 重現:`_door_keyword_hits` 回的是中文類名「金流、對外送出、不可逆、守衛面」,不是 payment 等英文鍵。我實跑「送出訂單」得到 `'對外送出'`。
- 壞處:照字面用英文鍵過濾會永遠留不下任何命中。
- 另外要把命中的中文名併回 `one_way` 的英文值,spec 沒寫。
- 還有:功能名、情境名、驗收句是分別掃還是串成一份文字,也沒寫;該函式以行為單位,串成多行就是多筆。
- file: `scripts/lumos:13974`(回傳值)、`scripts/lumos:13747`(`_DOOR_CLASS_ZH`)。

severity: minor
blocking: 否,屬實作細節沒寫清,不改變合約。

**F4. 實測段的條款編號是舊的**

引句:「中文 `name:` 的子目錄怎麼命名沒測(S12 實測)」

- 重現:現在的 S12 是「擋下訊息的下一步不應印整套重跑那一行」。
- 要手測的是 S14,而且 S14 已經沒有中文 `name:` 這一項。
- r2 把 judge 改成只讀唯一子目錄、不猜 `name:`,這件待測事項既沒搬進 S14,也沒被明說刪掉。
- 這不影響判定,因為 judge 已不依賴 `name:`。

severity: minor
blocking: 否,屬文件引用過期。

**F5. 首次導入 features 表的豁免,對沒有 flows 的新情境變成空洞為真**

引句:「情境底下的 flow 全是舊流程的,算舊情境」

- 重現:專案主線和分岔點都還沒有 features 表,這次推送一次加進整張表,其中一個新情境只列 visual(沒有 flows)。
  - 「全是舊流程」對空集合為真,這個情境算舊情境。
  - 做法 5 另一條說「只列截圖、效能或記憶體、沒有 flows 的新情境,`one_way` 照樣必填、單向門照樣要人點頭」。
  - 這兩段互相打架,字面實作會讓沒有 flows 的情境逃掉 `one_way`。
- 混合情境(有舊 flow 也有新 flow)的歸屬,spec 也沒定。
- S10 的第二個條件和這句同樣含糊。

severity: minor
blocking: 否,觸發條件窄(僅首次導入),但需要明講。

**F6. 回退段的專案層說法,對新情境不成立**

引句:「專案層:情境拿掉三個新鍵,就不做逐句對照;但新情境的 `one_way` 必填,拿掉會被擋(要撤也只能還原工具鏈)。」

- 重現:有 flows 的新情境拿掉 `accept` 一樣被擋(S6),不只是 `one_way`。
- 「不做逐句對照」只對舊情境成立,而舊情境本來就不對照。
- 結果是專案層沒有真正的回退路徑,只剩 `LUMOS_SKIP_ANDROID_E2E=1` 或還原工具鏈。

severity: minor
blocking: 否,屬文件精度。

**F7. 非單向門情境的「另派代理審」沒有任何機械守衛**

引句:「其他情境由另派的代理審即可。」

- 重現:新情境寫了 `accept`、`one_way: []`、標籤都對,但整個不寫 `accept_review`。
  - 推送檢查的七條擋下條件都不碰 `accept_review`:只有單向門才看 `by` 是不是 `human:`。
  - S13 只驗格式,沒有要求必填。
  - 這一關在實務隱患也沒列。
- 緣起裡 Enzo 同意「代理寫驗收句、另派代理審」,目前這步只是程序。

severity: minor
blocking: 否,spec 明說是程序不是機械擋,但漏列在隱患清單。

**F8. 審計修正紀錄漏記刪掉「不做」節**

引句:「r1(2026-10-31,4 席:正確性、邊界、整合、架構對齊,全 sonnet):41 條」

- 重現:差異把 r1 的「## 不做」整節刪了,審計修正紀錄裡沒有記。
- 被刪的三條是:不判斷檢查有沒有驗到重點、不做新畫面自動升代碼審、不管截圖門檻。
- 這是範圍邊界,留下的只有緣起裡提到的一條否決。
- 同一行說「minor 部分附理由放行」,但這份筆記裡沒有任何一條 minor 的理由,只有計數。

severity: minor
blocking: 否,屬紀錄一致性。

**F9. 做法 4 的欄位驗證範圍不清,逐句對照的流程鍵也沒說要正規化**

引句:「`_e2e_record_err` 同步驗這兩欄的型別(判定會讀的欄位在那裡驗,跟既有慣例一致)」

- 「這兩欄」指向不明:同一句前面講的是 `checks` 與 `checks_reason`,但 S4 只驗 `checks`、`count`、`labels`,`checks_reason` 沒有型別條款。
- `_e2e_record_err` 同時是寫入端(`_e2e_record_update`)的把關,新驗證寫錯會讓放行寫不進去。
- 逐句對照要把「情境的 flows」對到「紀錄裡的 flow 條目」。
  - 紀錄條目用 `e2e.flows` 的原字串。
  - 情境清單可以寫成 `./.maestro/a.yaml` 或 `.maestro/a.yaml`,設定檢查是兩邊正規化後才比的。
  - spec 只在新舊比對那條寫了 `_e2e_norm`,聯集查找沒寫。照字面實作會出現「A1 沒有檢查對到」的假擋。
- file: `scripts/lumos:41421`(`_e2e_case_results` 兩邊都用 `_e2e_norm` 對接)。

severity: minor
blocking: 否,屬實作時容易踩的缺漏。

**F10. label 前綴指向「不存在的情境」的檢查範圍沒限定**

引句:「label 的前綴指到一個新情境、但那個情境沒有這個 id,或指到根本不存在的情境」

- 重現:舊流程裡有 `驗收:舊功能.舊情境#A1`,這次推送刪掉了那個舊情境。
  - 前綴指到「根本不存在的情境」,被列出並擋下。
  - 這與 S10 所說舊流程不因此擋的方向矛盾。
- spec 沒說掃描範圍是只限新情境的 flows,還是紀錄裡所有 flow 的 labels。

severity: minor
blocking: 否,觸發需要同時刪情境,且擋下訊息會點名那個 label。

**F11. 多條擋下條件同時成立時,治理帳的 `gate_code` 記哪一個沒定**

引句:「這幾條各自一個擋下代碼,寫進治理帳的 `gate_code`(撤除條件要數)」

- 重現:同一次推送同時「新流程零檢查」和「新情境沒 `accept`」。
  - `_e2e_gate_block` 一次只丟一個 `gate_code`,spec 沒說取哪個、或是不是合成一筆。
  - RETIRE-IF 要數「因驗收句沒有檢查對到而擋下的次數」,按先到先記會少算。

severity: minor
blocking: 否,屬撤除條件的計數精度。

最嚴重 severity:major;blocking 共 2 條(F1、F2)。
