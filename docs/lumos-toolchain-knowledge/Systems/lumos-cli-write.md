---
type: system
status: done
created: 2026-06-26
updated: 2026-10-15
self_audit: claude-fable/2026-08-24
tags:
  - type/system
  - status/done
  - scope/node-content
related:
  - "[[Systems/lumos-cli-read]]"
  - "[[Systems/lumos-cli-lifecycle]]"
  - "[[Verification/2026-08-11_T1_remove_list項移除]]"
  - "[[Systems/check-u-overgeneralization]]"
  - "[[Projects/工具分類_計劃]]"
  - "[[Projects/過期鎖安全接手_計劃]]"
summary: |-
  WHY:`lumos summary-line <節點> "<舊片段>" "<新片段>"` 改摘要裡的一行:片段比對照 guard bind(對到多處就擋、列候選、--nth 指定),續行條目不支援,換完只剩空白就拿掉那一行(摘要不得變空),寫入照 atomic_write_verify、同一次把 updated 改成今天 [出處:2026-10-06 [[Projects/改摘要單行的指令_計劃]];rtb 第三輪提案 D1] [因:摘要沒有指令可改,只能手改開頭欄位;rtb 這輪手改 10 次全是同一行改一小段] [test:t_summary_line_replace] [test:t_summary_line_ambiguous]
  WHY:`lumos updated-sync <節點>… | --stale` 把筆記開頭 updated 改成今天,一篇一篇走 cmd_set;doctor U 段列出 updated 早於 git 上那篇最後一次提交日期的筆記(`_updated_stale_notes`,讀 git_last_change_dates),只提醒不擋;不在提交時自動改 [出處:2026-10-06 [[Projects/提交時自動更新筆記日期_計劃]];Enzo 先裁提交時自動改、設計審 r1 後改裁健檢列出加一鍵修] [因:提交時自動改會讓設計審整檔指紋失效、消掉翻案提醒、多會談共用工作目錄時帶進半成品] [test:t_doctor_updated_stale] [test:t_updated_sync_stale]
  PITFALL:git_last_change_dates 原本拿未解析的圖譜路徑跟解析過的專案根算相對路徑,macOS 暫存目錄(/var → /private/var)或任何經符號連結的圖譜會讓整張日期表靜默變空;它在本案之前沒有呼叫者所以沒人踩到,現在兩邊都先解析成實體路徑 [出處:2026-10-06 [[Projects/提交時自動更新筆記日期_計劃]] 實作] [根因:relpath 兩端一個解析過一個沒有] [test:t_doctor_updated_stale]
  WHY:decision-add、decision-supersede 成功之後,列出別篇連到這篇、同一子句還寫待定的行與 c6 補括號指令;只印、失敗只在 stderr 講一句,決策已寫入、回傳碼不變(同 cascade 的 fail-open);supersede 的列出排在 cascade 之後,stdout 第一行照舊 [出處:2026-10-05 [[Projects/結案連帶掃描_計劃]]] [因:翻案或補上決策之後,別篇寫「待裁定」的句子沒人提醒] [不選:要求被連的那篇已收尾才列(加決策不改狀態,會永遠列不到)] [test:t_settle_backrefs_listed_after_close_and_decisions]
  WHY:驗收紀錄的開頭欄位 system_refs 進 LIST_KEYS(append/remove 可用、lint 認得);new verification --systems 照舊只對功能加 verified_by、不自動寫 system_refs;sync-verified-by 改用 doctor 3/4 同一支判「驗了誰」(有 system_refs 就只看它,寫壞的項不補、在「無漏寫」之前先印一行指到 3/4) [出處:2026-10-03 [[Projects/驗收紀錄寫明驗了哪些功能_計劃]]] [因:正文的指路連結被當成驗過、推送被擋(rtb 清理循環第 1 輪第 2 項);自動寫會讓作者事後在正文補的功能不再被檢查(設計審 r3)] [test:t_sync_verified_by_system_refs] [test:t_new_verification_no_auto_system_refs] [test:t_system_refs_registered_field]
  WHY:[2026-09-30 [[Projects/存量漂移改法_計劃]] 代碼審 r4]set 整欄改 valid_under/revalidate_when 時,值裡還留著 <整項新內容> 就擋、檔案不動——那是 drift fix --kind c4 證據頁預填指令裡要人填的那一項,原封不動照貼會把佔位字寫進驗收前提 [test:t_drift_fix_c4_evidence_then_replace]
  WHY:[2026-09-30 [[Projects/漂移修法補強_計劃]] 第 2 節]同一道檢查多擋 c4 範本句的兩個佔位字 <卷證>、<sha>:範本不再自動填卷證目錄(設計審 r2 後整類拿掉自動判斷),整句照貼一定留著 <卷證>,擋下逼人換成從清單挑的目錄與真的提交。三個字面放同一份常數,證據頁的範本與預填指令都從那裡取;訊息點名是哪一個,<整項新內容> 那句訊息一字不改;其他檢查與順序不動。跟擋 drift fix --reason 佔位字的那份用途不同、不合併。代價:驗收前提裡本來就合法要寫這兩個字串的會被擋,機率極低,訊息講明是佔位字檢查。代碼審 r1(邊界席)後打錯的變體也擋,只擋兩邊都有角括號、括號裡只有佔位字本身的:全形角括號、括號內多空白、sha 大小寫。少一邊角括號的第一版也擋,代碼審第二輪重現「若卷證>20個就重驗」「輸出 git-sha> 時重驗」被誤擋,拿掉;<卷證 目錄>、<sha 1>、<git-sha>、<SHA-1>、<sha256> 照收 [test:t_set_conditions_blocks_drift_placeholders] [test:t_set_conditions_blocks_placeholder_variants]
  WHY:[2026-09-26 驗收前提欄位可改,另一個對話回報、Enzo 裁「好」]`set` 收 valid_under/revalidate_when,整欄換掉(一個值=單行、多個值=一行一項清單,原本單行/清單/空的/多行區塊都拿乾淨);另列 COND_KEYS、不併進 SCALAR_KEYS(那份白名單的數量有漂移守衛在數,且這兩欄本質可以是清單)。不給 append/remove:這兩欄是散文常提連結,append/remove 用連結目標判「同一項」會把提到同一篇的不同條件當重複。其他欄位給兩個值照擋。★引號改白名單、全寫入指令共用★(代碼審 r1 兩席:原本只列「要加引號的」,本工具自己讀自己永遠對得上,標準 YAML/Obsidian 讀卻會把「空白+#」後面當註解切掉、把雙引號裡的反斜線當跳脫):`_yaml_plain_ok` 只放行確定兩邊讀法一樣的值,其餘由 `_yaml_quote` 加引號——沒反斜線沒雙引號用雙引號、否則單引號、兩種都不行就擋;fmt_scalar、fmt_list_item 與決策文字欄位(`_fmt_decision_value`,r2 架構席抓到的第三套手刻判準)都改走它,所以 set 其他欄位、append、decision-add/supersede 一併修到;白名單另擋標準 YAML 會讀成日期、十六/八/二進位、六十進位、無限大的寫法(r2 通才席)。副作用:signoff 寫的日期現在加引號(本工具讀起來一樣,Obsidian 改讀成字串);DATE_KEYS 照舊刻意不加引號、不經這裡 [test:t_set_condition_fields_standard_yaml_safe] [test:t_decision_add_standard_yaml_safe] [test:t_set_condition_fields_replace_any_shape] [test:t_set_condition_fields_multi_values] [test:t_set_condition_fields_reject_bad_values] [test:t_set_other_keys_single_value_only] [test:t_set_condition_fields_keep_other_lines]
  WHY:[2026-10-07 [[Projects/改重驗事件時列出引用它的句子_計劃]]]`set <節點> revalidate_when …` 寫入成功後,列出全庫連到這篇、同一句(不跨句尾 _SENT_END_RE、24 字內)講到 revalidate_when 的那一句(來源篇與行號)並印出改完之後的事件清單;只印不擋不改,判斷在 _revalidate_backref_lines(連結認法同 doctor S21:行內程式碼裡的不算、先過 link_target),沒有引用句不多印;同一行每句各一筆、最多列 20 句、掃描出錯只在 stderr 說寫入照樣完成(同 _drift_print_backrefs) [出處:rtb 第三次比對回傳第 10 項(交接 B5);Enzo 2026-10-07 裁「改的那一刻列出來」] [因:revalidate_when 是自由文字,別篇寫「某事發生時由 `[[X]]` 的 revalidate_when 觸發重驗」,X 的事件被改掉後那句永遠不會觸發] [不選:doctor 全庫用關鍵詞重疊比對聲稱的事件(兩邊只有 3 句引用、1 句真壞,門檻沒樣本可定)] [test:t_set_revalidate_when_lists_backrefs]
  KEY:[2026-09-25 筆記欄位關卡補齊]寫入指令補兩道:①`set responsibility` 用新開節點那支判斷(`_nodehome_resp_ok`,至少 10 字、要有實字),不過就擋、檔案不動,不看開關——跟 `new --responsibility` 同一種擋法(原本 set 可以寫進一個字);②`append about_code`、`new --code` 共用的 `_about_code_path` 補「不在圖譜資料夾裡」——有一篇 Issue 就是用 append 把筆記路徑寫進 about_code;要連結別篇請寫 related。lint 的 about_code 規則也呼叫同一支,兩邊判法一致 [test:t_set_responsibility_min_length] [test:t_about_code_writer_rejects_vault_path] [test:t_lint_about_code_must_exist]
  KEY:[推送閘回頭擋住自己 2026-09-16]修好 linter 送檔那批之後第一次推,★推送前的新增告警閘當場擋下★,抓到三條這批自己帶進來的新告警:兩個函式超過複雜度上限、一個 import 沒人用。三條都修掉、沒有走放行。★這道閘以前根本不會擋★——它跑的是同一份宣告,而那份宣告在當天之前從來沒真的檢查過任何一行。修複雜度的做法不是硬拆:把「決定鎖放哪」抽成模組層獨立一支(`_vault_lock_where`),順便讓代碼審 r2 抓到的那個坑(位置排在可重入判斷後面)變成★結構上不可能再犯★。連帶一條測試翻紅——它用函式名抓區段來驗「有沒有走共用的信任檢查」,檢查搬家就抓不到,正好證明它真的在盯
  KEY:[代碼審 r2 折入 2026-09-16]★「鎖放哪」必須在「這把鎖是不是自己已經拿著」之前決定★——退路那版把判斷排在可重入檢查後面,巢狀呼叫時拿舊路徑的鍵去查、查不到,內層卡滿 60 秒再拋「別的程序正在寫」這句★假訊息★;而這正是本函式說明裡「第四輪已修過」的舊坑從退路分支重新長出來。★同批還抓到自己的假測試★:原本那條「巢狀允許」寫成前後兩個不重疊的區塊,根本沒測到巢狀,改成真巢狀(用短逾時代替 60 秒)當場翻紅 [test:t_vault_lock_falls_back_instead_of_giving_up]
  KEY:[代碼審 r1 折入 2026-09-16]★鎖的地方不可信要換個地方鎖,不是乾脆不鎖★——第一版寫成「不可信就直接寫」,那是把一個安全問題換成一個正確性問題:原本鎖檔雖然落在不可信的地方、★鎖本身仍然有效★,不鎖之後兩個程序就能同時做讀—改—寫。而且觸發條件不需要攻擊者,把快取目錄搬到別的磁碟這種正常設定就會踩到。退路選筆記庫自己(要寫的就是它、使用者一定擁有它、兩個程序算出來的路徑一樣,互斥照樣成立);位置換過一次只講一次,不每次都唸 [test:t_vault_lock_falls_back_instead_of_giving_up]
  KEY:[寫入鎖的資料夾也要過信任檢查 2026-09-16]筆記庫寫入鎖把鎖檔建在家目錄底下,註解寫著「照派工鏡頭快取的先例」,★但只抄了放哪裡、沒抄那道信任檢查★。實測把中間一層換成指向別處的符號連結,鎖檔真的被寫到那邊去,而同一支檢查對那條路徑判「不可信」;鎖失效的後果是兩個程序互相蓋掉筆記庫的修改。修法=不過關就不在那裡建鎖、直接寫並出聲說鎖沒生效。★沒擋到的殘留★:檢查排在建資料夾之後,連結指到的地方仍會多出一個空資料夾——鄰居那幾處同樣順序,是共用寫法本來就有的缺口,不是這處特有;真正危險的動作(寫檔、改權限、刪目錄)都在檢查之後。要連空資料夾都不建得改成逐層建逐層檢查,會動到鄰居,另案。 [test:t_private_dir_trust_shared_across_four_sites]
  KEY:[2026-09-08 scope 值域宣告制]lint 多一段 scope/ 檢查(plan:[[Projects/工具分類_計劃]]):只在 vault 往上找到的 .lumos/config.json 有 scope 區塊({values:[…],required:bool})時啟動,沒宣告=一個字不說;啟動後 非 MOC 節點 沒掛(required)/掛超過兩個/值不在表內 → ★只 warning 不擋★,不走 created cutoff。設定檔搜尋與 extra_frontmatter_keys 共用同一支 helper(_lumos_config_near_vault) [test:t_lint_scope_policy]
  KEY:[2026-08-05 標籤收編]值域 lint(cutoff 2026-08-06 新節點硬擋,舊帳不回溯)——status 依 type enum(verification 用 pass)/summary FLAG: 三值(敘述移 KEY 行)/priority P0-P3/risk 四值;feature/area 凍結 warning 勸轉 scope/。schema 表單源=lumos-project-notes SKILL〈標籤家族〉 [test:t_lint_tag_value_enums]
  KEY:[2026-08-05]aliases 宣告制——system/issue 新節點(created≥2026-08-05)lint 硬擋「缺 aliases 鍵」;逼★判過★不逼有值(aliases: []=明示無同義詞,合法;湊數別名吃 3.5 檢索權重=主動污染排序)。配套:模板自帶 aliases: []+NEW_HINT 教學(來源限真實出現過的說法)+append 白名單納 aliases;兩庫回填 2026-08-05(toolchain 22 節點 23 條/Landmark 71 節點 152 條,grounded 規則) [test:t_lint_aliases_declared]
  KEY:[2026-08-05]decisions 結構守衛修假陽性——原始條數只認 entry 縮排層(恰 2 空格),alternatives_considered 巢狀清單不計(Landmark 回填實戰:照 ADR 規範寫巢狀清單被誤報「壞損」;真壞型 sibling 吞沒照抓) [test:t_lint_decisions_nested_list_not_false_positive]
  KEY:[2026-08-05]`new verification <名> --plan <計劃> --systems <A,B>` 一鍵雙向——建檔當下填 plan_refs+對每個 Systems append verified_by(寫後自驗沿 cmd_append);指到不存在節點 rc2 且不建檔(不留半套);把「事後 sync-verified-by 撿漏」變「寫入時就對」 [test:t_new_verification_bidirectional]
  FLOW:set/append/self-audit/decision-*→load_raw_for_edit(讀raw,拒BOM/CRLF)→line-based改fm→atomic_write_verify(★(2026-08-21 程式碼實證)實際順序:先在**記憶體**對 new_lines re-parse+expected_check+lint 指紋比對→全過才建 tmp 寫入→os.replace;檢查失敗時 tmp 根本未建立★)→敗則原檔不動
  KEY:[2026-08-11]新增 `remove <note> <key> <value>`=append 逆操作(T1 list 項移除)。缺口來自實戰:死背書(verified_by 指向已 superseded 的驗證)與降格後殘留 core_refs,都只能靠移除 list 項來收,而 set 只收純量、append 只能加,唯一退路 obsidian processFrontMatter 需 Obsidian 執行中→實務無路可走。比對沿用 link_target()(精確 target,不做前綴/basename 匹配);★不命中一律 rc=2★(靜默 no-op 回成功=呼叫端以為清乾淨了,比報錯危險);清空後連 key 行一併移除(裸鍵被 YAML 解成 null 比沒鍵更糟);core_refs 納入 LIST_KEYS(升格加/降格拆兩向都走 T1)。★不支援巢狀 dict 型 list 項★(core-knowledge facet 的 implements 需 T3 手術層,非本次範圍)。實戰驗收:LandmarkMember doctor E1 死背書 14→0、C 指針轉「無」。詳 [[Verification/2026-08-11_T1_remove_list項移除]]
  KEY:[2026-08-23]`remove <note> <key>`★不帶 value=把純量欄位整個拿掉★(design-loop about-code-field r3 抓到:回滾要刪 stamp,但 set 只能覆寫、remove 只動 list——純量沒有刪除原語)。不加新子命令,一個指令學一次。守衛三條:type/status/created 骨架欄硬擋(刪了 lint/doctor/分類全炸)/清單欄不准省 value(一句話誤刪整個 verified_by)/欄位不在 rc2。同批 about_code 進 LIST_KEYS、about_code_stamp 進 SCALAR_KEYS(語意欄位基礎,計劃 [[Projects/固定席扇出降權_計劃]])
  KEY:寫入原語(set/append/remove/new/archive/decision-add/decision-supersede/self-audit,另有改摘要的 summary-add/summary-line)是「專案層」圖譜寫入的唯一安全路徑,取代手改 frontmatter / obsidian property:set
  KEY:T1 寫後自驗 atomic——所有 fm mutation 經 atomic_write_verify:記憶體 re-parse 斷言該 key 寫成目標值 + 無引入新 lint 指紋 → 通過才寫 .lumos-tmp → os.replace 原子換入;任一步失敗原檔零變動(★(2026-08-21 程式碼實證)原文「先寫 tmp 再驗」順序寫反;保證不變★) [test:t_set_minimal_diff,t_append_exact_dedup]
  KEY:set 走 SCALAR_KEYS 白名單(10 鍵 <!--lumos:count=10 re=\"[a-z_]+\"(?=[^}\n]*\}  # pitfall_\* 2026-08-09) in=scripts/lumos-->:status,updated,created,type,self_audit,signed_off,regen,pitfall_ask,pitfall_source,about_code_stamp;scripts/lumos:7035)、append 走 LIST_KEYS(7 鍵 <!--lumos:count=8 re=\"[a-z_]+\"(?=[^}\n]*\}   # aliases 2026-08-05) in=scripts/lumos-->:verified_by,plan_refs,related,tags,aliases,pitfall_when,core_refs;7036)★原文列舉漏 pitfall_*/aliases/pitfall_when,(2026-08-21 程式碼實證);以常數為準勿再列舉★;白名單外 key 直接 rc2(list 用 append、decisions 翻盤/新增走 decision-*) [test:t_append_block_key_rejected]
  KEY:鐵則1(多wikilink必YAML list)由 append 結構性保證——一項一行 + link_target dedup,絕不字串塞多個[[]];鐵則3/4(含「: 」長文引號化、日期 bare)由 fmt_scalar/_fmt_decision_value 包辦
  KEY:decisions[] 是巢狀結構,只能走 decision-add/decision-supersede/decision-reindex 的 surgical line-based 手術(非 ruamel round-trip,避免 reflow 破壞最小 diff);要求 2-space 縮排
  KEY:[M1/P2 2026-07-15]決策穩定 ID——add 指派 id:d<max+1>(翻案永不重用)、supersede 唯一命中(子字串多重命中 rc=2 列候選/#dN 精確定址)+回傳全域 id <rel>#d<N>(dispatcher 解包,CLI 對外仍 int rc)、reindex 冪等回填(混合狀態 max+1 不撞號);寫後自驗升級 ID 精確驗證(有 id 時)
  KEY:[M4/S1 2026-07-15]supersede 觸發主網 surfacing——rc=0 後 dispatcher 獨立 try 包「rel_cascade_create 建帳+cascade_surface 列鄰居」;stdout 首行逐字保留、cascade 面全走 stderr(CASCADE/NEIGHBOR 行式 schema);無 id→CASCADE-SKIP、失敗→CASCADE-ERROR fail-open(rc 仍 0,補網 E2 兜底)
  KEY:[驗證紀錄兩個條件欄 2026-09-16]lint 多一句軟提醒:type=verification 且 status=pass 的節點,valid_under(這結論在什麼前提下才算數)或 revalidate_when(改到什麼時候該回頭重驗)是空的就唸一句。★出身★:某天五篇驗證★全★把回頭條件寫進正文、欄位留空,於是掃描工具全掃不到、lint 全綠放行,鐵則四被靜默架空——是審查席讀出來的,不是工具抓到的。★只提醒不擋★(舊帳很多,光排序那一篇就掛著五份空條件的驗證,擋了每個提交都紅);★只對 pass★(其他型別沒這兩個欄位,stale/fail 本來就還在處理中不必催)。★判空跟掃描端共用同一支 helper★(代碼審訂正):直接轉字串的話,裝著兩個空白字串的清單會變成有括號有引號的非空字串、被判成有寫,而掃描端逐項去空白後拿到零條——兩邊口徑不一樣這道提醒就有洞。出身見 [[Issues/lint不守驗證紀錄空回頭條件]] [test:t_lint_warns_empty_revalidate_when]
  KEY:[連鎖待辦單 2026-09-16]`rel-cascade visited`=空單銷帳。★空不空當場機械驗★:重放帳本、展開待判鄰居(跟 resume 共用 `_rel_cascade_pending` 唯一實作),一個都沒有才准記;有待辦就 rc2 擋下並印還剩幾篇——這個動詞唯一的危險是變成萬用消音鍵,呼叫端說了不算。帳本讀取放行 `visited` 事件(★2026-09-16 代碼審當天訂正★:原本寫「它沒有鄰居與邊型欄位,折疊會自動略過」——那只是寫入端的慣例,讀取端一個字都沒保證,實測手工塞一筆帶齊三個粒度欄位的巡過紀錄就能蓋掉真正的待判狀態、讓空單守衛放行;已改成折疊只認 event=transition,不影響任何既有判定);收它的唯一用途是讓健檢的「零筆=沒看過」對空單閉嘴。上線當天 15 張零判定的單裡 14 張是空的,一次銷完。★另一道守衛:起點筆記解析不到就擋★——起點被刪或改名時展開鄰居會得到零筆,那是問不到、不是真的沒東西可判,當成空單放行會把還沒確認完的待辦悄悄消掉。出身見 [[Issues/空連鎖單巡過無法銷帳]];同機制的未修缺口見 [[Issues/連鎖判定confirm會寫進被翻案的舊決策編號]]
  KEY:[decision_refs 自動養成 P+T1 2026-07-15]decision-reindex --all 批次編號(顯式,前置);rel-cascade confirm 回寫 decision_ref(_append_decision_ref exact-string dedup,非 link_target——它剝 #dN 會誤合同節點不同決策)。不對稱信任雙欄:by ai→decision_refs_ai(E3 firing 讀聯集/E2 抑制碰不到)、by human→decision_refs(可抑制)
  KEY:[2026-07-20]set status 反正規化同步——status 存兩處(欄位+tags 的 status/* 標籤,模板生),set status 同一次原子寫入就地改寫 tags 內既有 status/* 項(無則不添,純同步不發明);寫後自驗同驗兩處;繞過路徑(手改/外部工具)由 lint+doctor Check M 漂移守衛硬擋(見[[Projects/狀態標籤同步守衛_計劃]])
  DEP:scripts/lumos atomic_write_verify｜load_raw_for_edit｜_write_lf(唯一寫入原語,UTF-8/LF/no-BOM)｜parse_frontmatter｜parse_decisions
  TEST:set/append/decision/archive/new 全套 t_-prefixed 回歸(t_set_*,t_append_*,t_decision_*,t_archive_*,t_new_*);狀態標籤同步 t_set_status_syncs_tag+t_status_tag_drift_guard
  WHY:[2026-09-29 Projects/存量漂移改法_計劃]lumos set 把 Issue 改成結案值(done/resolved/wontfix:狀態表 issue 那一格與結案集合的交集,不用跨類型的結案集合)時,列出它★全部★回頭條件、只印不擋,結案時才有人看到留著的 REVISIT;跟 doctor E5 共用一支判定,不塞進計劃收尾的連帶待辦(那支只管計劃)
  WHY:[2026-10-15 [[Projects/筆記指令健檢與規格閘小修_計劃]] d1]新增 summary-add 往摘要加一行,寫入前跑提交時那套筆記形狀與格子檢查(_summary_write_shape_check),summary-line 換出來的新行也跑同一支;格子的舊行鍵照提交時的來源組(HEAD 版本這篇的摘要加被換掉的那一行) [出處:web 示範兩個代理都要加 RULE 行只能手改開頭欄位] [因:多一個寫入入口不能變成繞過提交檢查的路;傳 None 會把改舊行當新寫] [不選:不檢查前綴(沒前綴的孤行讓兩道檢查都空轉)] [test:t_summary_add_runs_note_shape_check] [test:t_summary_line_runs_shape_check]
  WHY:[2026-10-15 [[Projects/筆記指令健檢與規格閘小修_計劃]]]append 的 lands_in 在寫入端就跑讀取端(lint、處置閘)同一支 _lands_in_bad:先用 link_target 拿掉 [[ ]] 與 .md,合格就寫成純字串並講改了什麼,仍不是 Systems/<名> 就擋;set 與 append 的說明列出可改欄位,跟擋下訊息共用 _set_keys_text、_append_keys_text [出處:web 示範後端代理照收連結寫法、到處置閘才被擋] [因:寫入端與讀取端判法不同,錯的值要到最後一關才被發現] [test:t_append_lands_in_normalizes]
  WHY:[2026-10-15 代碼審 code-筆記指令健檢與規格閘小修 r2]寫入前形狀檢查(當時是 _drift_fix_shape_err 共用;r3 起共用判定抽成 _write_shape_verdict,_drift_fix_shape_err 只剩 drift fix 的薄包裝)照 note_shape 總開關:off 不檢查、warn 只提醒;summary-line 只在確定不是 git 專案時跳過,git 跑不起來照擋 [出處:代碼審 r2 架構對齊、資安席] [因:同一支寫前檢查不能一處看開關一處不看;逾時不該被當成非 git 放過] [test:t_drift_fix_shape_follows_gate]
  WHY:[2026-10-15 代碼審 code-筆記指令健檢與規格閘小修 r3]寫入前形狀檢查收成 _write_shape_verdict 回(擋下原因、提醒清單),warn 的提醒跟格子提醒一樣由呼叫端印,設定讀一次傳下去;擋下訊息由呼叫端照自己的形狀加前綴,drift fix 走薄包裝 _drift_fix_shape_err [出處:代碼審 r3 架構對齊席] [因:同一命令裡兩種提醒走兩條通道、前綴靠字串開頭判斷] [test:t_summary_write_warns_via_return_list]
decisions:
  - content: 所有 frontmatter 寫入經 atomic_write_verify「寫 tmp → re-parse 自驗(值正確且無新 lint 指紋)→ os.replace」,任一步敗則原檔零變動
    id: d1
    context: 圖譜檔被 doctor/lint 把關,半寫壞的 frontmatter(YAML 解析爆、引入新指紋)會污染全圖;直接寫檔無法保證寫完仍合法
    why_chosen: 寫後自驗把「寫出來的東西真的 parse 得回目標值、且沒新增 lint 問題」變成寫入成功的前置條件;atomic rename 確保不留半截檔,失敗即無痕回滾
    decided: 2026-06-26
    valid: true
  - content: 純量走 set(SCALAR_KEYS 白名單)、list 走 append(LIST_KEYS)、巢狀 decisions[] 走 decision-add/decision-supersede;白名單外 key 一律 rc2 拒絕
    id: d2
    context: frontmatter 三種結構(純量/list/巢狀)各有不同的安全格式鐵則與最小 diff 策略,混用會破格(如把 list 當純量塞逗號串、reflow 巢狀)
    why_chosen: 按結構分原語各自保證對應鐵則(append 保鐵則1 的 YAML list、decision-* 保 surgical 巢狀不 reflow);白名單擋誤用,把錯誤導向正確指令
    decided: 2026-06-26
    valid: true
  - content: decisions[] 翻盤/新增用 surgical line-based 編輯(只動目標行),不走 ruamel round-trip
    id: d3
    context: ruamel round-trip 重序列化整份 YAML 會 reflow、破壞「構造性最小 diff」(只改該改的行、其餘逐字原樣),也可能誤動子清單
    why_chosen: line-based 手術精確命中目標決策的 valid/superseded_by 行,diff 最小可審;代價是要求 2-space 標準縮排(0-indent/tab 直接報錯不靜默處理)
    decided: 2026-06-26
    valid: true
verified_by:
  - "[[Verification/2026-07-15_主網M1_決策穩定ID]]"
  - "[[Verification/2026-07-15_主網M3_cascade帳本]]"
  - "[[Verification/2026-07-15_主網M4_觸發與連鎖]]"
  - "[[Verification/2026-07-15_主網實驗場_LandmarkMember]]"
  - "[[Verification/2026-07-15_decision_refs養成_P前置_T1回寫]]"
  - "[[Verification/2026-07-15_decision_refs養成_codeloop硬化]]"
  - "[[Verification/2026-07-16_fromscratch守衛M1_CheckJ]]"
  - "[[2026-07-20_狀態標籤同步守衛]]"
  - "[[Verification/2026-08-05_流程優化六件落地]]"
  - "[[Verification/2026-08-05_標籤結構收編落地]]"
  - "[[Verification/2026-08-11_T1_remove_list項移除]]"
  - "[[Verification/2026-08-21_L4交叉審計30節點清帳]]"
  - "[[Verification/2026-10-05_過期鎖安全接手實作驗證]]"
  - "[[Verification/2026-10-05_背景快取命中清鎖驗證]]"
about_code:
  - scripts/lumos
---
# lumos-cli-write

## 2026-10-05 寫入鎖的安全邊界

[[Issues/過期鎖接手可能雙持]] 的跨程序交錯證明「先看 mtime 再按路徑 rename」可把別人剛建的新鎖搬走。[[Projects/過期鎖安全接手_計劃]] 決定停止自動接手，理由是派工鏡頭共用此原語，鎖內的啟動者 PID 不能證明背景工作已停；只加 PID 檢查會把同一類雙持帶回來。正常獨佔建立時要處理短寫與建檔錯誤，否則停止自動接手反而會使半成品鎖永久阻斷。防回歸測試為 `t_excl_lock_stale_takeover_is_single_owner`、`t_excl_lock_creation_failure_cleans_own_file`、`t_vault_stale_lock_fails_with_path`。這是同版程序的保證；混用舊版前須先停舊進程，不能宣稱跨版本安全。

`scripts/lumos` 的**專案層圖譜寫入原語**(下表各列;以 `lumos --help` 為準)—— 對知識圖譜 frontmatter 的唯一安全寫入路徑。直接手改 frontmatter / obsidian `property:set` 會繞過寫後自驗與格式鐵則(實測 `property:set` 塞多 wikilink 會長出亂碼 ghost 節點)。

> 源起:CLI 核心非日報觸發。

## 寫入原語(對應 `cmd_*`;2026-08-24 自足性審計補回漏列的 remove,2026-10-15 補 summary-add/summary-line)
| 指令 | 結構層 | 做什麼 |
|---|---|---|
| `set <node> <key> <value>` | 純量 | 改 `SCALAR_KEYS`(以 scripts/lumos 常數為準,2026-08-24 為 10 鍵含 about_code_stamp);行級手術最小 diff |
| `append <node> <key> "[[x]]"` | list | 追加 `LIST_KEYS`(以常數為準,2026-10-03 為 10 項,含 about_code/core_refs/pitfall_when/aliases/lands_in/system_refs);鐵則1 安全格式 + `link_target` dedup |
| `remove <node> <key> [value]` | list/純量 | 逐值拿掉 list 項(清死背書 verified_by/拔 core_refs);不帶 value=整欄拿掉純量(骨架欄 type/status/created 擋);同受 atomic_write_verify 保護 |
| `summary-add <node> "<一行>" [--after 片段]` | 摘要 | 摘要加一行(要有前綴;去重;寫前跑提交時的筆記形狀與格子檢查,舊行照提交時的舊行規則),[[Projects/筆記指令健檢與規格閘小修_計劃]] d1 |
| `summary-line <node> "<舊片段>" "<新片段>"` | 摘要 | 換或刪摘要裡唯一對上的那一段;換出來的新行同樣跑寫前形狀檢查 |
| `self-audit <node> [--model][--date]` | 純量 | 寫 `self_audit: <model>/<date>` 節點級自足性審計戳記(內部即 `set self_audit`) |
| `decision-add <node> "<content>" --decided DATE [--context][--why]` | 巢狀 | append 一條 ADR 決策(無 `decisions:` 則在 fm 末尾建) |
| `decision-supersede <node> "<content子字串>" --by "..." [--ended DATE]` | 巢狀 | 把該條決策標 `valid:false` + 補 `superseded_by`/`ended` |
| `new <type> <name>` | 建檔 | 依 `TEMPLATES`(system/verification/issue/project)建檔 + 印「寫入當下教學」(符號行/合約鏈) |
| `archive [--days N] [--apply]` | 移檔 | 滾動歸檔老 Verification(days 是選填旗標預設 180,非位置參數;另見 `cmd_archive` 的「活守衛護欄」邏輯) |

`new`/`archive` 嚴格說是建檔/移檔而非 fm mutation;其餘(set/append/remove/self-audit/decision-add/decision-supersede,2026-10-12 加 question-add/question-set,2026-10-15 加 summary-add/summary-line)走 `atomic_write_verify`。寫入鎖 `_vault_write_lock`:2026-10-12 起所有呼叫 `atomic_write_verify` 的入口都拿同一把(set/append/remove、決策四支含 reindex --all 與 amend、決策引用、守衛綁定與審計、question-add/set),`atomic_write_verify` 沒拿鎖就不寫。

## T1 寫後自驗 atomic(核心不變式)

2026-10-13 起，寫入原語自己的拒絕統一丟 `WriteBlocked`，訊息在建立時就清洗(誰接都印不出控制字元)；各分派照既有寫法接成 `擋下:` 與 rc2，沒被接到的由命令列入口 `_cli()` 接(分派函式維持叫 `main`,精簡版產生器靠這個形狀)；非此信號的程式錯誤不吞。`load_raw_for_edit` 只負責讀取/BOM/CRLF/解碼拒絕；符號連結、不是一般檔、硬連結(`nlink>1`)由 `_write_refusal_reason` 以 lstat 一次判,只用在寫入原語、簽核帳與 drift fix 載入(drift fix 連 `--dry-run` 也拒),讓其他唯讀與 no-op 路徑照舊。`signoff` 拿鎖後才讀原稿，筆記先寫、帳以 append-only 開啟並記原長度；帳用 `os.open`(O_NOFOLLOW、不帶緩衝)追加，任一步失敗以 `os.ftruncate` 截回原長度(新建的帳刪掉)，再於鎖內還原筆記，逐邊照實回報；追加途中被 Ctrl-C 這類程序內中斷,帳一樣截回、筆記還原,再把中斷往外丟;帳的那一行把 U+2028、U+2029、U+0085 跳脫,備註切不出第二行。`summary-line` 寫成後才印成功差異。[test:t_qfm_r6_writeblocked_inventory_and_edges,t_qfm_r6_signoff_rolls_back_both_sides,t_qfm_r8_signoff_and_write_refusal,t_summary_line_verify]
所有 frontmatter mutation 都經 `atomic_write_verify(path, new_lines, key, expected_check)`:
0. 先確認這個程序拿著 path 所在筆記庫的寫入鎖(`_vault_lock_held_for`),沒拿就丟 `WriteBlocked`、不寫(2026-10-12 起;入口照「`cmd_*` 拿鎖再叫 `_*_locked`」的寫法)。[test:t_qfm_frontmatter_writers_take_lock]
1. `load_raw_for_edit` 讀 raw bytes,**拒 BOM、拒 CRLF**(vault 慣例 LF/no-BOM,異常不靜默正規化,報錯指路 `.gitattributes`/`dos2unix`)。
2. 改完後 re-parse 新 frontmatter,跑 `expected_check(fields)` 斷言**該 key 真的寫成目標值**(decision 類會 `parse_decisions` 重解確認 valid/superseded_by)。
3. 比對 lint 指紋:`set(new_lint) - orig_lint` 必須為空——**不准引入新的 frontmatter 指紋**。
4. 上述全過才 `_write_lf` 寫 `.lumos-tmp` → `os.replace` 原子換入;任一步丟 `WriteBlocked`,tmp 丟棄、**原檔零變動**。

`_write_lf` 是 vault 唯一寫入原語:`write_bytes` 強制 UTF-8/LF/no-BOM,平台無關(不靠 text mode、不需 Python 3.10 的 `newline=`)。

## 格式鐵則由原語結構性保證(不靠人手)
鐵則完整清單在 `skills/lumos-project-notes/reference.md`(格式鐵則 1-4;CLAUDE.md 的「三條鐵則」是另一套工作紀律,別混——2026-08-24 審計訂正);本節點只處理寫入相關鐵則(1/3/4)。

- **鐵則1(多 wikilink 必 YAML list)**:`append` 天生一項一行寫 list,用 `link_target` 比對 dedup,絕不字串串接多個 `[[]]`。
- **鐵則3(含「: 」長文引號化)**:`_fmt_decision_value` 對含 `: `/特殊起首字元的值自動加引號;summary 走 block scalar。
- **鐵則4(日期 bare 不加引號)**:`fmt_scalar` / decision 子欄位格式化保持日期裸值;`--decided`/`--ended`/`--date` 先過 `DATE_RE`/`fromisoformat` 校驗,非 `YYYY-MM-DD` 直接拒。

## 機器層 vs 專案層分工
這組原語只動**專案層**圖譜檔(`docs/<slug>-knowledge/`);與機器層(`install`/`uninstall` 動 `~/.local/bin`、user-scope skills)、生命週期(`bootstrap`/`update`/`init`/`deinit`)正交。

## 已知限制
- decision-* 要求 **2-space 標準縮排**;0-indent / tab 縮排的 decisions 區塊報錯、不自動處理。
- `decision-supersede` 對**已 superseded**(同層已有 `superseded_by`)的決策拒絕重插,避免重複鍵;要改取代者需手動編輯。
- BOM/CRLF 檔一律拒寫,需先正規化行尾(走 obsidian CLI 或 `dos2unix`)。

## 相關
- 操作表:`lumos-project-notes` skill SKILL.md(寫入原語表 + obsidian fallback 對照)。
- 鐵則總綱:`CLAUDE.md`(純量/list/decisions 一律走 lumos,別手改 frontmatter)。
- 實作落點:`scripts/lumos` `cmd_set`/`cmd_append`/`cmd_self_audit`/`cmd_decision_add`/`cmd_decision_supersede`/`cmd_new`/`cmd_archive` + `atomic_write_verify`/`load_raw_for_edit`/`_write_lf`。
- 回歸測試:`scripts/test_lumos.py` `t_set_*`/`t_append_*`/`t_remove_*`/`t_decision_*`/`t_archive_*`/`t_new_*`。

## 建檔骨架對齊紀律(2026-10-12)

- PITFALL:`lumos new` 產的骨架是舊前綴(機制筆記 FLOW/KEY/DEP/TEST、事故 FLAG/DECISION/KEY,事故沒有四段),跟紀律範本〈寫筆記時〉打架,照骨架寫的人會寫出舊格式 [出處:Projects/世界解重新註解2026-10_節點內容_調研 核對] [根因:紀律改版時只改了範本與 lint 訊息,骨架與釘住骨架的測試沒跟著改] [修法:機制筆記骨架改 WHY/RULE/PITFALL/SEE,事故骨架改 FLAG/PITFALL 並預留症狀、根因、現在怎麼繞、什麼條件算修好四段,建檔提示一併改] [test:t_new_teaches_tags]

## 待決問題的兩支寫入指令(2026-10-12,[[Projects/待決問題改存開頭欄位_計劃]])

- `question-add <計劃> "<問題>" --class --stage [--status][--blocking][--irreversible][--decision][--tests][--source][--reason]` 加一題到開頭欄位 `pending_questions`,`question-set <計劃> Q<n> 鍵=值 …` 改一題的幾個鍵;兩支都走 `atomic_write_verify`,寫前先用嚴格讀法 `pq_parse` 驗整份清單、驗這一題跟要寫的一致、驗寫入規則(必附、阻塞不得延後、不可逆不得自答、決策要存在且有效),沒過不寫、回 2。[test:t_qfm_commands_write_and_verify]
- WHY:兩支指令整段讀—改—寫都包 `_vault_write_lock`(decision-add 當時沒鎖;2026-10-12 起所有讀改寫開頭欄位的入口都先拿同一把寫入鎖,見下一行) [出處:設計審 待決問題改存開頭欄位 r1 四席] [因:decision-add 同時起跑 8 個實測只留下 6 條;題號是「最大號加 1」,沒鎖會重號,重號在嚴格讀法下整份讀不懂、規格閘整份擋] [不選:照抄 decision-add] [test:t_qfm_commands_write_and_verify]
- WHY:讀改寫開頭欄位的入口一律先拿寫入鎖(照鄰居「`cmd_*` 拿鎖再叫 `_*_locked`」的寫法;r2 曾用裝飾器,r3 架構席指出是第二種寫法而改回),`atomic_write_verify` 沒拿這個筆記庫的鎖就不寫 [出處:代碼審 code-待決問題改存開頭欄位 r1、r2 併發、正確性、合約圖譜、通才四席] [因:第一輪只補決策三支,第二輪又漏了 reindex --all、amend、決策引用、守衛綁定,逐支補會一直漏;改成寫入函式本身檢查,漏包的在測試裡就紅] [不選:逐支加鎖、保留後寫蓋先寫] [代價:鎖殘留時這些指令會等 60 秒才回「擋下」rc2(守衛子指令在分派層統一接,讀寫失敗也一併回擋下 rc2,只有解碼錯誤照舊 rc1);decision-amend 只鎖讀改寫那段,git fetch 與遠端比對在鎖外;讀取符號連結照常，直到真正寫入才由共用原語拒絕符號連結與硬連結(原子換名會把連結換成一般檔,一篇悄悄分成兩份;代碼審 r5、r7 G1/C6),判在不在庫裡只解析它所在的資料夾] [test:t_qfm_frontmatter_writers_take_lock,t_qfm_r8_signoff_and_write_refusal]
- WHY:`blocking`/`irreversible` 照字面寫 true/false,不經 `_yaml_plain_ok`/`_yaml_quote` [出處:設計審 r1 正確性與整合兩席] [因:格式化函式會把 true 加成 "true",嚴格讀法只收不加引號的布林,自己寫的會自己擋] [不選:讀法放寬收 "true"(標準 YAML 讀成字串)] [test:t_qfm_commands_write_and_verify]
- WHY:`question-set` 用位置參數 `鍵=值`,不用 `--field/--text` 或一次一鍵 [出處:設計審 r1 架構對齊席] [因:「改成已決要附決策」這類跨鍵規則要一次改完才驗得過;`decision=#d3` 的 # 在字中間,shell 不會當註解] [不選:一次一鍵(中間態必附不齊會被擋)] [test:t_qfm_commands_write_and_verify]
- 兩支指令跟其他寫入原語一樣拒寫 CRLF/BOM 的檔(`load_raw_for_edit`);讀法照樣讀得懂那種檔,所以規格閘看得到、指令寫不進去,訊息會講怎麼轉。
- 在 `pending_questions: []` 上加題會先把那行改成區塊起頭(decision-add 在 `decisions: []` 上會寫壞而被擋,沒照抄);定位項目沿用 `decisions_items`(加了欄位名參數);嚴格讀法是這個欄位專用的 `_pq_scan`(決策清單收多行值與子清單,文法不同,不硬掛在 `parse_decisions` 底下)。

## 建計劃筆記沒有後綴時提醒(2026-10-13)

- WHY:`lumos new project <名>` 的名稱完全沒有底線後綴時照原名建檔,建好後提醒慣例與重建指令,不擋、不改名 [出處:[[Projects/示範回饋小修_計劃]] 代碼審 r1] [因:後端示範時照直覺只打主題,建出不合慣例的檔名;既有計劃筆記另有 _調研、_草案 等後綴] [不選:自動補「_計劃」(會改壞既有寫法,而且接著用原名下指令的人找不到這篇;建檔指令從沒改過使用者給的名字)] [test:t_new_project_warns_missing_plan_suffix]

## 歸檔護欄認得句子名(2026-10-15)

- `cmd_archive` 的「還護著存活合約的驗證紀錄不歸檔」改用 `_test_name_boundary_re`:名稱頭尾是英數底線才加邊界,中文頭尾的句子名也配得到(原本 ASCII 的 \b 對中文頭尾永遠配不到,護著中文名合約的驗證紀錄會被誤歸檔)。單源 [[Projects/測試名收自由字串_計劃]]。 [test:t_archive_and_trace_free_string_names]
