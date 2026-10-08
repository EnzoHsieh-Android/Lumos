severity: minor

# 架構對齊審查 r1(筆記測試綁定要存在)

## 三問

### 1. 分層與依賴方向:對齊
- 新規則組放在 `cmd_note_shape` 與 `_note_shape_report` 之間,跟否定現況句那組、格子那組同區。接線順序一樣:`prepare/mode → eval → collected → report(帶 tr=)`(對照 `scripts/lumos:29097-29109`,`_ns_slots_prepare` 在 28040、`_ns_slots_collected` 在 28063)。
- 設定讀取 `_note_shape_test_refs_parse` / `_ns_test_refs_mode` 是 `_note_shape_slots_parse` / `_ns_slots_mode`(28157、28178)的同形複本。鄰居本身就有 slots、negation 兩份同形複本,這是既有慣例,不判不一致。
- 第①道直接呼叫 `_platform_test_index`(12889)與 `_classify_test_refs`(40730),是推送前合約測試閘與修正關卡已經共用的函式。note-shape 讀工作目錄索引是跨層,但 patch 註解與 `cmd_note_shape` docstring 都明講是唯一例外,並有 `_ns_tr_guard` 兜底。已有書面理由,不判 major。
- `_test_in_tree` 從表態閘 `_dispositions_check_test`(41237 一帶)抽出來,表態閘改成呼叫它,單向依賴,沒有反向或循環。逾時照舊丟 `TimeoutExpired`,表態閘外層行為不變。
- doctor S20 掛在 S19 之後、同樣 `warn_soft` 軟段、不計入問題數,位置紀律跟 S16-S19 一致(對照 `scripts/lumos:2539-2549`)。

### 2. 命名與錯誤處理:大致對齊,有兩處小差異
- 命名:`_ns_tr_*` 對應 `_ns_slots_*`,`_doctor_test_ref_lines` 對應 `_doctor_fact_recheck_lines`(3696),`_ns_tr_extra` 對應 `_ns_slot_extra`(28412)。共用的 `_test_names_of` 沒有 `_ns_` 前綴,因為 doctor 也用,跟 `_slot_vals`(3558)同理,可接受。
- fail-open:`_ns_test_refs_collected` 的 try/except 印「提醒:…這次沒查(例外類別名),不影響其他檢查」到 stderr,跟 `_ns_slots_collected`(28063)同句式。doctor S20 的 `except` 走 `ok("…跳過(…)")`,跟 S18 同寫法(2529-2535)。對齊。
- 不一致處見 F1(帳的結構欄位)、F2(讀全文的方式)。

### 3. 第二種做法
- `_NsTrJudge` 用類別裝狀態:不算第二種做法。同檔已有 `_NotelinesNet`(27433)、`_NodehomeSide`(26101)、`_Drift*` 一組類別,而且 docstring 明寫「比照 `_NotelinesNet` 的寫法」。鄰居並非多半用閉包。
- `_test_names_of` 的名稱切分:跟 `invariant_test_refs`(5193)、`resolve_test_refs`(5202)部分重複。見 F3,判 minor 並標 ⚠。
- doctor S20 讀全文:跟 S16-S19 不一致。見 F2。
- 沒有新設定讀法、沒有新帳本檔。帳是寫既有的 note-shape 事件,多一個 `extra.test_refs`。

## F1 只有測試綁定違規時,治理帳的 extra 沒有 `check` 鍵
severity: minor
blocking: 否
引句:「ex["test_refs"] = _ns_tr_extra(trmode, trviol, trinfo)」
file: `scripts/lumos:28147`(`_ns_skip_slot_extra` 同款;`_note_shape_report` 在 patch 的 `ex = _ns_slot_extra(sviol, ...) if sviol else {}` 之後)
1. 鄰居的 extra 一律帶 `check` 欄位作為分類鍵:格子是 `"slots"` 或 `"shape+slots"`(`_ns_slot_extra`,28412-28419),否定現況句與 tag-hints 也都是 `{"check": ...}`(28005)。
2. 新組在「沒有格子違規」時 `ex` 是 `{}`,只塞 `test_refs`,沒有 `check`。讀帳的人要靠有沒有 `test_refs` 鍵反推,正是格子那組當年註明不要的「從字樣反推」做法。
3. 三種都有時 `check` 也只反映格子與形狀,看不出測試綁定。
4. 建議:`check` 的值納入 `"test_refs"`(或至少 tr-only 時補 `check: "test_refs"`)。

## F2 doctor S20 自己 read_text 讀全文,沒走 `env_text`
severity: minor
blocking: 否
引句:「text = (env.vault / rel).read_text(encoding="utf-8-sig")」
file: `scripts/lumos:716`(`env_text` 定義;用例 30968、31012、32236)
1. 檔裡已有「Env 全文存取」的共用函式 `env_text(env, rel)`:記憶體 Env(`Env.from_texts`)走記憶體,一般 Env 讀磁碟,讀不到回 None。
2. S16-S19 一律從 `env.notes` 的 Note 物件與 `_slot_summary_entries(env, …)` / `_note_summary_entries` 取摘要條目,不自己開檔。S20 因為要掃正文行必須要全文,但應該用 `env_text`,而不是新寫一份 try/except 讀檔。
3. 後果:S20 對記憶體 Env 會靜默跳過每一篇(`except Exception: continue`),跟鄰居行為不同。
4. 注意:鄰居 2266、2383 一帶的 doctor 舊段也有直接 `(env.vault / rel).read_text`,所以 doctor 內部本身不完全一致。我把它判 minor、不判 major。

## F3 ⚠ `_test_names_of` 的逗號與前綴切分跟既有 `invariant_test_refs` / `resolve_test_refs` 是兩份
severity: minor
blocking: 否
引句:「半形或全形逗號切開、去空白與空項、去掉包住名稱的反引號」
file: `scripts/lumos:5193`
1. 既有的切法:`invariant_test_refs` 用 `TEST_REF_RE`(4769)抽 `[test:…]` 後只切半形逗號;`resolve_test_refs` 再切 `平台:名稱` 前綴並對未定義前綴丟 `ValueError`。
2. 新寫的 `_test_names_of` 從 `slot_parse` 的欄位取值,另外寫了全形逗號、反引號、前綴(`_NS_TR_PREFIX_RE`)的切分與正規化,最後 `_NsTrJudge._plat` 再把名稱包成合成字串 `[test:{nm}]` 餵回 `resolve_test_refs`,等於切一次、再組回去、再切一次。
3. 輸入來源不同(`slot_parse` 欄位對正則抽取),而且新增了全形逗號與反引號容忍,不是單純複製,所以不判 major。
4. 鄰居本身也不一致:`slot_parse` 欄位與 `TEST_REF_RE` 這兩條路在檔裡並存(格子表的 `test` 鍵由 `slot_parse` 讀,合約行由 `TEST_REF_RE` 讀)。標 ⚠ 交編排者:要不要把全形逗號與反引號容忍回收進 `invariant_test_refs`,讓兩邊共用一套切分。

## F4 測試綁定借用格子的 `slots` 容器當「碰到的筆記」載體
severity: minor
blocking: 否
引句:「box = slots if slots is not None else {}   # 測試綁定要碰到的筆記」
file: `scripts/lumos:28040`(`_ns_slots_prepare`:容器有沒有 `mark2` 決定格子跑不跑)
1. 鄰居的容器語意:`_ns_slots_prepare` 回傳的容器非 None 就代表「這次要跑格子」,`_note_shape_eval` 以此為開關並往裡塞 `notes`。
2. 新碼在格子不跑時也傳一個空容器給 `_note_shape_eval(slots=box)`,再從 `box["notes"]` 取筆記。結構上能運作,patch 註解也說明了「不帶 mark2 時格子不跑」。但同一個參數現在承擔兩種意思,後來改格子開關邏輯的人容易踩到。
3. 建議:用獨立參數(例如 `notes_out=`),或在 `_note_shape_eval` 註解裡把兩種語意寫清楚。結構對,所以只列 minor。

不對齊共 4 條,其中 major 0 條
