severity: major

# r3 整合-sonnet 席報告(整合與接手鏡頭)

範圍:照計劃做法 1 到 11 與條款 S1 到 S25 實際接 `scripts/lumos`,逐個接點開檔讀語意。已讀的接點:`cmd_note_shape`、`_note_shape_eval`、`_note_shape_report`、`_notelines_new`、`_notelines_regions`、`_drift_tree_env`、`_dispositions_check_test`、`_dispositions_split_test`、`_platform_test_index`、`_ns_skip_slot_extra`、`_gate_event_build`、`slot_parse`、doctor S16 到 S19。

## F1 「測試寫了沒提交」在名詞段與隱患段說擋、在做法 4 說只提醒,「差異」怎麼量也沒寫
severity: major
blocking: 是
引句:「推送時被檢查版本跟工作目錄的測試檔(同一套測試副檔名、排除 `docs/`、`governance/`)有差異(推的分支不是目前簽出的那條、測試檔改了沒提交)→ 這組這次只提醒不擋,訊息講原因。」
引句:「測試寫了沒提交就推送筆記,會被擋(第②道);這是本意(推上去沒有守衛)。」
file: `scripts/lumos:41244`(`_dispositions_check_test` 第②道只對 at_sha 的樹做 git grep,不看工作目錄差異)
file: `scripts/lumos:26138`(`_nodehome_reader` 對 HEAD 才用磁碟,其他提交走 git show,沒有現成的「測試檔差異」函式)
1. 兩段話互相打架:做法 4 說「測試檔改了沒提交」就只提醒;實務隱患與名詞段說「測試寫了沒提交」要擋。照字面,新增一個測試函式但還沒提交(測試檔是已追蹤、有修改)屬於前者,規則只提醒,第②道的本意(擋掉沒提交的測試)完全不發生。
2. 「有差異」用什麼指令量沒寫。`git diff --quiet <終點> -- <測試副檔名 pathspec>` 看不到未追蹤的新測試檔;`git status --porcelain` 才看得到。照前者實作:新建的未追蹤測試檔不算差異、第①道過、第②道不過,於是擋;已追蹤的有改動則只提醒。同一個「測試沒提交」場景因為檔案是新建還是修改而一擋一不擋,S13 與 S1 的夾具選哪一種,結果相反。
3. 比較的範圍(哪些副檔名、哪些根、跟 `_dispositions_check_test` 第②道的 pathspec 要不要同一組)沒指到可呼叫的共用函式。接手者得自己再寫一份 pathspec 組裝,而第②道那份是函式內的區域變數,取不出來。
4. 要補的:先決定本意。若本意是「沒提交的測試要擋」,「有差異就只提醒」應只對「推的分支不是目前簽出的那條」生效、不看未提交的改動(該情形下第②道本來就對終點的樹判,是對的);若本意是差異一律只提醒,隱患段與名詞段那兩句要改,並寫明用哪個指令量差異、未追蹤檔算不算。
未實測,依據是讀碼。

## F2 向 `_notelines_new` 要 rows 的參數沒寫,照預設會吞掉單行寫法的 summary
severity: major
blocking: 是
引句:「這組不靠格子的 `--slots` 容器,自己向 `_notelines_new` 要 rows。」
file: `scripts/lumos:27344`(`_notelines_new` 簽名:`mark` 為必填關鍵字、`keep_other=False`、`per_commit=True` 預設)
file: `scripts/lumos:27152`(`_notelines_regions`:`summary:` 這一行本身永遠標 other)
file: `scripts/lumos:28407`(`_note_shape_eval` 實際呼叫時傳 `keep_other=True`、`mark=_NOTE_SHAPE_GOLIVE_MARK`)
file: `scripts/lumos:26586`(`_nodehome_golive` 的 `mark=None` 退回每支檔有家自己的記號)
1. 計劃沒寫呼叫參數。最小實驗(臨時 repo,暫存一篇 `summary: "WHY: 單行寫法 [test:t_single]"` 加一行正文 `[test:t_body]`):
   - `_notelines_new(..., keep_other=False)` 回的 rows 只有行 6、7(正文),單行 summary 那一行(行 4)整個不在。
   - `keep_other=True` 才多出行 1 到 5(區塊 other),行 4 是 `summary: "WHY: 單行寫法 [test:t_single]"`。
2. 所以 S21「summary 是單行寫法也要抽到」只有傳 `keep_other=True` 才成立;預設值會讓 S21 紅,而且是靜默漏掉(名稱根本進不了抽取)。
3. 傳 `keep_other=True` 後 rows 會帶出整個開頭欄位(related、lands_in、decisions 的結構鍵行…),抽取必須自己限定只看「那一行是 `summary:` 單行值」或區塊 summary 的行,否則 `related`、`decisions` 內文裡寫的 `[test:` 字樣也會被抽。計劃沒講怎麼限定(要用 `_notelines_regions` 的哪個區塊、decisions 區塊的非結構行算不算正文)。
4. `mark` 沒寫:傳 None 時 `_nodehome_golive` 退回每支檔有家的上線點,`_notelines_new` 裡 `live_mark` 也變 None,逐提交的上線點判斷整個關掉;計劃只說「上線點沿用 note-shape 既有的」,沒說要傳 `_NOTE_SHAPE_GOLIVE_MARK`。
5. 另外:`_note_shape_eval` 已經呼叫過一次 `_notelines_new`(同一範圍、同一組參數),計劃另跑第二次,整段範圍的 rev-list、逐提交 diff 做兩遍,〈時間〉段沒算這筆。`_note_shape_eval(..., slots={})` 傳一個空容器就會把 `notes` 與 `old_by` 放回去(`scripts/lumos:28407` 往下兩行),不需要 `--slots` 旗標,不用第二次抽取;計劃把這條路排除的理由(「不靠 --slots 容器」)與程式不符:容器本身跟旗標無關,旗標只決定 `cmd_note_shape` 要不要建。
6. 要補的:寫明「用 `_note_shape_eval` 的 sink 取 rows,或第二次呼叫時傳 `keep_other=True, mark=_NOTE_SHAPE_GOLIVE_MARK, exclude_remote=True`」,以及單行 summary 與 decisions 區塊的取法。

## F3 1c 的「新寫」用什麼鍵比,照字面實作會漏掉最常見的作廢寫法,換個讀法又會誤擋舊帳
severity: major
blocking: 是
引句:「(1c)新寫的作廢條目掛著活測試,而且這一條用 `_ns_text_key` 正規化後在起點那一版整個知識庫找不到一樣的(只重排折行的不算新寫)→ 違規」
file: `scripts/lumos:28167`(`_ns_text_key(core)` 吃的是 `slot_parse(...)["core"]`,欄位已被剝掉)
file: `scripts/lumos:28189`(`_ns_superseded(line)`)
1. 最小實驗(載入 `scripts/lumos` 當模組):舊行 `RULE: 這條規則不能退 [依據:人] [since:2026-01-01] [retire:人裁] [until:2027-01-01] [test:t_x]`,新行是同一行尾端加 ` [status:superseded] [被取代:無 不用了]`。
   - `_ns_text_key(slot_parse(rest)["core"])` 兩者都是 `這條規則不能退`(相同)。
   - `_ns_text_key(整行)` 則不同(整行含欄位字樣)。
   - `_ns_superseded(新行)` 是 True,舊行 False。
2. 計劃寫「`_ns_text_key` 正規化後」,而這個函式的參數名與既有用法(`_ns_slot_key`)都是 core(欄位剝掉後的核心句)。照這個讀法實作:把既有的活條目改標作廢、`[test:]` 沒拿掉——這是撤除一條規則時最自然的改法——起點那一版有同核心句,判成「不是新寫」,不擋。1c 想擋的情境(rtb 12 條是舊條款被撤除)幾乎全是這種改標,等於只擋「憑空新寫一條就是作廢的」這種不會發生的寫法。
3. 換成整行比對:這次改標的行與起點不同,擋得到;但同時,起點就已經作廢而掛活測試的舊行(存量舊帳),任何人只改它的 `[confirmed:]` 或補一個欄位,整行鍵也變了,就被判新寫而擋——跟「存量只在 doctor 提醒」互相矛盾。
4. S11 與 S12 的夾具兩種讀法都過(S11 用全新句、S12 只折行),所以條款抓不出這個分歧;S24 同理。要補的是明寫比對規則,例如「同核心句的條目在起點是否已經標作廢:起點是活的、這次改標作廢 → 算新寫;起點已作廢 → 不算」,並加一條夾具(活條目改標作廢、`[test:]` 留著 → 擋;起點已作廢的舊行只改日期 → 不擋)。
5. 附帶:做法 1 說抽取「回每個名稱…是否作廢」,沒有回條目的核心句或鍵,1c 需要的鍵得另算(見 F5)。

## F4 借來的 `_dispositions_check_test` 有「驗不了」與「丟例外」兩條路,計劃都當成「指不到」或沒接
severity: major
blocking: 是
引句:「索引建不起來、或某平台的根不存在、掃不到任何測試方法 → 那個平台這次不查、印一行原因。」
file: `scripts/lumos:41244`(第②道:`git grep` rc 非 0 非 1 時回 `(False, "測試 … 無法對推送版本的樹驗證(git grep rc=…)")`;`subprocess.run(..., timeout=_disp_git_timeout())` 逾時拋 `TimeoutExpired`,函式內沒接)
file: `scripts/lumos:41209`(`_disp_git_timeout` 的說明明寫「超時往上拋…由每題的例外接手」)
file: `scripts/lumos:41377`(表態閘自己的呼叫端用 `try/except` 把例外接成「無法驗證」)
1. 做法 4 只列三種 fail-open:索引建不起來、根不存在、掃不到方法。第②道的另外兩種失敗沒列:
   - 回傳 `(False, "無法對推送版本的樹驗證…")`:呼叫端只拿到 `(bool, 字串)`,沒有結構化的「驗不了」旗標;照做法 5 的「指不到 → 違規」,這種情況會被當成「指不到」而擋,訊息還說「改成真的測試名」,但測試其實存在,是 git 沒跑成。
   - 逾時:`TimeoutExpired` 往上拋。表態閘有每題的 `try/except`;計劃沒要求新這組包 `try/except`,而 `cmd_note_shape` 本身沒有整體例外保護,未接的例外讓 Python 以 rc 1 結束,pre-push 掛鉤把它當擋下。跟檔頭說明「git 算不出來 → rc0(fail-open)」相反,也沒寫帳。
2. 其他既有慣例:格子那組(`_ns_slots_collected`)明確包了 `try/except`、印「這次沒跑完」、當作沒有;否定現況句提醒同理。新這組沒有對應句。S14 只涵蓋索引,沒有夾具涵蓋「單一名稱的第②道驗不了」與「逾時」。
3. 要補的:要求整組外層 `try/except Exception` 一律 fail-open 印一行(同 `_ns_slots_collected`);第②道回傳「無法對推送版本的樹驗證」那種原因的名稱,不算指不到、不進違規(要嘛包一層判斷,要嘛把 `_dispositions_check_test` 改成回三態);加 S14 的夾具。
未實測,依據是讀碼(逾時與 rc 128 要造 git 故障才重現)。

## F5 抽取函式的回傳形狀不夠接 1c、起點集合與空名稱
severity: minor
blocking: 否
引句:「回每個名稱與它出現的筆記、行號(新寫的那一行)、所在條目的前綴、是否作廢。」
file: `scripts/lumos:28216`(`_ns_slot_line_problems` 等既有比對用 `(前綴, 文字鍵, 連結集合)`)
1. 回傳欄位沒有條目的核心句或文字鍵,1c(做法 5 最後一點)要用 `_ns_text_key` 比起點,必須自己再算一次條目的核心句;正文行沒有前綴,`_ns_slot_key` 要求 `SYMBOL_RE`,正文行直接回 None,計劃沒說正文裡的作廢條目(計劃的條款行)用什麼鍵。
2. 沒有標「這個名稱在合約行或條款定義行上」的旗標。做法 1 說這兩種「在判存在時略過、在 1c 照查」,但回傳欄位沒有東西讓呼叫端分辨;做法 3 的起點集合又要「同一支抽取(不限新寫行)」,沒說起點集合要不要含合約行與條款行上的名稱。若抽取在內部就略過,起點集合少這兩種名稱,一個名稱從合約行搬到 WHY 行就被算成新加(搬行本來該不算新加,S2)。
3. S20「`[test:]` 方括號裡沒有任何名稱 → 擋」:空名稱沒有名稱可以扣起點集合,規則是「新加」才擋;一條舊的 `[test:]` 空行只被重排折行,仍在新寫行裡,照字面算新加而擋,跟「折行不算新加」衝突。要寫明空名稱用什麼判新:例如比對該條目在起點是否也有空的 test 欄位。
4. 起點知識庫有筆記不是 UTF-8 時,`_drift_tree_env` 把它建成讀不出的筆記(`_note_unreadable`);計劃沒說抽取遇到它怎麼辦,它上面的名稱就不在起點集合裡,搬走的名稱被誤判新加。

## F6 帳本 extra 合併、單次跳過與提交時的帳,形狀沒寫完
severity: minor
blocking: 否
引句:「`extra` 裡既有的違規種類欄照既有寫法再多列一項。」
file: `scripts/lumos:28375`(`_ns_slot_extra` 只產 `check: "slots"` 或 `"shape+slots"`)
file: `scripts/lumos:28089`(`_ns_skip_slot_extra` 在格子關掉時回 None、有格子時 sv 為空也回帶 `slots_lines: 0` 的字典)
file: `scripts/lumos:1147`(`_gate_event_build` 用 `ev.update(extra)`:鍵是頂層欄位)
1. 「違規種類欄」只有 `check` 一個,現有值是兩個字串,`kw` 只在有格子違規時才帶 extra(純形狀違規連 `check` 都沒有)。加第三種怎麼寫(`"test_refs"`?`"shape+slots+test_refs"`?只有這組違規時 `check` 是什麼?)沒寫;`check` 還是 gov 去重鍵的一部分(`scripts/lumos:7991` 附近),字串組法影響去重。
2. 單次跳過路徑:`extra = _ns_skip_slot_extra(root) if (staged and slots_flag) else None`,計劃要「不靠 `--slots`」,等於這行條件要改;`_ns_skip_slot_extra` 在 `smode == "off"` 時整個回 None,test_refs 的 extra 不能被格子關掉連帶丟掉。兩個 extra 怎麼併(任一為 None 時)沒寫。
3. 逃生口裡要建測試索引、批次讀起點知識庫,沒有時間上限(`_ns_skip_slot_extra` 只有 `try/except`),會讓「單次跳過」在大 repo 上變慢。
4. 提交時有 test_refs 提醒要不要寫一筆 warned 帳沒寫:格子與形狀的提醒走 `_note_shape_report` 會寫 warned;RETIRE-IF 以擋下為主,但若提交時每次提醒都寫 warned,帳本雜訊正是 `cmd_note_shape` 檔頭說明刻意避免的。

## F7 做法與名詞段對「無 platforms 時冒號」的描述跟 `_dispositions_split_test` 不符,S25 的觸發條件不明
severity: minor
blocking: 否
引句:「設定有 `platforms` 時可帶 `平台:` 前綴,沒有時整串當名稱。」
file: `scripts/lumos:40910`(`_dispositions_split_test`:沒開多平台而名稱含冒號 → `(None, "…沒開多平台…")`,不是當名稱)
file: `scripts/lumos:5169`(`resolve_test_refs` 才是「無 platforms 就整串當名稱」)
1. 判存在改借 `_dispositions_check_test`,語意是後者:legacy 專案寫 `[test:browser:登入]` 得到「沒開多平台」訊息,結果仍是指不到,但訊息與名詞段描述不同。
2. S25 的觸發寫「平台前綴沒定義」。呼叫端只拿到 `(False, 字串)`,要分辨「前綴沒定義」與「沒開多平台」得先自己呼叫 `_dispositions_split_test`(回 `(None, 原因)`);計劃沒寫,兩種情況是否都該提示 `[manual:…]` 也沒寫。
3. 另外 `_platform_test_index` 讀的是工作目錄的 `.lumos/config.json`(`load_platforms`),不是被檢查版本的設定;推的分支不是目前簽出時,平台與前綴以哪邊為準沒寫(做法 4 的「保險」只比測試檔,沒比設定)。

## r2 改法驗收摘要
- `_notelines_new` 作新寫行入口:可接,但參數沒寫清(F2)。
- 起點集合用 `_drift_tree_env`:簽名 `(root, where, vault_rel, override, deadline)` 可接,回傳 Env,全文用 `env_text(env, 路徑)` 取;`where=None`(空樹起點)時 `_nodehome_list` 回空,抽出空集合,可行。逾時與 git 失敗都回 None、無法區分,計劃只寫「超過就跳過」,可行。
- `_dispositions_check_test` 的 pidx 與 at_sha:pidx 用 `_platform_test_index(root)` 回的六元組整包傳入;at_sha 推送時用 `tip`、提交時傳 None,與表態閘呼叫端一致;但 `ev` 參數要求 `"test:"` 前綴的字串,計劃沒寫(接手者看函式就知道,記為小事)。失敗路徑見 F4。
- 補「類別.方法」:在 `scripts/test_lumos.py` 裡找不到任何寫 `test:類別.方法` 風格的表態證據斷言,補進第①道不會讓既有表態閘測試翻紅(已用 grep 查證,未實跑)。
- `slot_parse` 抽取:欄位名 `test-gone` 滿足 `_SLOT_KEY_RE` 的 1 到 12 字元與可含連字號,登記進 `_SLOT_KEYS` 就會被認得;反引號內與不成對反引號後的內容不抽,跟格子一致,可接。
- 擋只在推送:`cmd_note_shape` 的 `staged` 分支與推送分支已區分,可接;單次跳過在讀範圍前返回的描述與程式一致。
- doctor S20:`section(...)` 與 `warn_soft` 的用法照 S17 到 S19,位置在 S19 之後、`S8` 之前(程式裡 S16 到 S19 在 S8 前面),不落在 `t_doctor_soft_sections_truncate_by_default` 切的 `[S]` 到 `[E1]` 視窗內(該視窗是 Check S)。已讀,無 finding。

## 其餘已讀、無 finding 的節
- 範圍、回退、實務隱患(金流、對外送出、不可逆):已讀,無 finding。
- 條款 S1 到 S25 其餘條(S3、S4、S5、S6、S9、S10、S14 的索引部分、S15 到 S18):夾具都能用既有 note-shape 測試的臨時 repo 加 `.lumos/config.json` 的 `test_profile: python` 做出來,計劃沒另寫夾具細節但不構成歧義。

最高等級:major,blocking 共 4 條
