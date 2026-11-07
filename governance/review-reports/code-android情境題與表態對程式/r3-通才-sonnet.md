severity: major

審了 r3-repair.patch 全文。實跑 `t_kt_situation_over_budget`、`t_kt_situation_r2_minor`、`t_loop_close_kinds_classified`、`t_kt_situation_decl_header`,都綠。`_KT_SIT_ROW_RX` 刪掉後 repo 內已無其他引用。下面的重現都用 python3.14 在行程內載入 `scripts/lumos`,沒改 repo。

**F1**
severity: major
blocking: 是
引句:「+        cache["over_budget"] = True」
`_kt_sit_check` 的 `probs` 是區域變數。核對到一半逾時時,函式丟出 `_KtSitOverBudget`,前面已查出的缺段、缺列整批丟掉。`_kt_sit_verdict_one` 接到後回 `None`,只標 `over_budget`。若別題也沒問題,整道閘放行並記 fail-open。

這違反 `_over` 註解自己寫的「已經查出的違規不能丟」。改前同樣的逾時是判無法驗證、擋下,所以這是修補造成的守衛弱化。

最小重現:兩段情境段,表態只答第二段,在第二次 `_kt_sit_deadline_check` 丟 `_KtSitOverBudget`。`_kt_sit_verdict_one` 回 `None`,`cache["over_budget"]` 為 True,第一段的「缺段」被吞掉。

修法:`_kt_sit_check` 內接住 OverBudget,帶著已查出的 `probs` 回傳並標旗,不要直接往外丟。

**F2**
severity: major
blocking: 是
引句:「+        _gate_event_or_warn(repo_root, "code-loop", "warned", r["text"][:120], hard=False,」
新事件 `("code-loop","warned")` 沒登記在 `LOOP_NOT_CLOSE_EVENTS`。`_GOV_LOCAL_PAIRS` 也沒有它,所以事件寫進版控的 `docs/.governance-log.jsonl`。

`t_loop_close_kinds_classified` 從這本版控帳撈出現過的 (閘, 種類),要求每組都歸類過。帳上第一筆證據樣式提醒進版控後,這個既有守衛就翻紅。目前綠,是因為還沒有這種事件進帳。

重現:載入 lumos 後,`("code-loop","warned")` 不在 `LOOP_CLOSE_EVENTS`、`LOOP_CLOSE_EVENTS_BY_DETAIL`、`LOOP_NOT_CLOSE_EVENTS` 的聯集裡,`_gov_routes_local` 對它回 False。附帶:diff 裡沒有任何測試覆蓋「提醒進帳後守衛仍綠」。

修法:在 `LOOP_NOT_CLOSE_EVENTS` 補 `("code-loop","warned")`,並補一條測試把這種事件寫進帳後跑分類守衛。

**F3**
severity: minor
blocking: 否
引句:「+    _home_cache_evict(d, _DRIFT_M1_DEFS_TTL)」
抽出共用的 `_home_cache_evict` 時,原本「目錄不可信一律不碰」的保證只留在舊呼叫端(`d` 是驗證過才傳進來)。新呼叫端 `_home_cache_evict(_kt_sit_cache_path(key).parent, ...)` 沒驗目錄,而且在 `_home_cache_write` 的 `_trusted_private_dir` 檢查之前就先刪檔。

重現:把 `~/.cache/lumos/kt-situation` 換成指向別處的 symlink,別處有一個超過一天的舊檔,呼叫後該檔被刪(實測 survived False)。依單人威脅模型只列 minor。

**F4**
severity: minor
blocking: 否
引句:「+            raise _KtSitUnverifiable(f"{_kill_esc(big)} 超過 {_KT_SIT_READ_MAX // 1048576}MB,不切段")」
新增的 4MB 單檔上限會判無法驗證、擋下,而且沒有出口:段放行只管證據提醒,也不是環境不可用。

改前沒有上限。一支大於 4MB、增行又碰到觸發字的 .kt(例如大型產生碼)會讓整次推送過不了。只能改檔或加入 vendored 跳過。這是新增的擋下路徑,文件有寫,但沒有逃生口。

**F5**
severity: minor
blocking: 否
引句:「-    kws = re.findall(_KT_SIT_HDR_KW_RE, "".join(flat))」
把 `init` 也從宣告關鍵字裡濾掉後,「class 之後緊接 `init {`」會被當成類別本體。改前最後一個關鍵字是 `init`,所以不是類別本體。

重現:`class VM {\n    data class State(val a: Int)\n    init {\n        coroutineScope { }\n    }\n}\n` 經 `_kt_sit_levels`,結果是 `[True,True,True,True,True,True,True]`。init 裡面的行被當成類別層,段材料會往上抓到 `data class State`。
同族還有 `get`、`set`、次建構子,前面接無本體 class/object 一行時也一樣。

測試只測了 `class X @Inject constructor` 這一類,沒測 init、get、set。影響限於段材料抓錯,對應的是提醒而不是擋,所以列 minor。

**F6**
severity: minor
blocking: 否
引句:「+    check("r2 ②快取鍵不看 lumos 檔的大小與時間", k1 is not None and k1 == k2, f"{k1} {k2}")」
切段快取鍵拿掉 lumos 檔的 size 和 mtime 後,切法是否失效全靠人記得升 `_KT_SIT_CACHE_SCHEMA`。

`_KT_SIT_GAP`、`_KT_SIT_SEG_MAX`、`_KT_SIT_CTX`、`_KT_SIT_MAT_MAX` 這幾個常數也不在鍵裡,沒有守衛測試把「切法改了要升 schema」機械綁住。測試環境因為 HOME 隔離不受影響,但開發機和消費專案改切法忘了升版,最多會讀到一天的舊段。

**F7**
severity: minor
blocking: 否
引句:「+  WHY:段放行/lint-waive」並未出現;實際改動是 `_kt_sit_verdict_one` 保留的「無法驗證(段放行{werr})」」
(這條無法逐字對上 diff 單行,錨點以下面的 diff 行為準。)
引句:「+    return f"{_KT_SIT_QID} 表態對不上程式:" + ";".join(probs[:6]) + more」
放行檔現在只管證據提醒,但 `_kt_sit_verdict_one` 只要有情境段就先讀放行檔,讀不了就整題判無法驗證、擋下(`werr` 路徑沒動)。

改前放行檔承擔整段略過的責任,讀不了擋下合理。現在它只決定提醒印不印,卻能擋整次推送,擋的力道和它的作用不成比例。建議:讀不了就當沒有放行,最多多印幾條提醒。

**F8**
severity: minor
blocking: 否
引句:「+1. 證據樣式只證「長得像照做了」,不證「用對了」,而且對不上只提醒不擋;盲判上線前,寫錯寫法只要缺段缺列都答了就推得出去,靠提醒帳事後數;盲判本身是模型判斷,會錯。」
違反 repo 根 CLAUDE.md 鐵則 4:「寫『沒機械守衛 / 只提醒不擋 / 單次量測 / 還沒有 X』這種會過期的話,把那一句本身搬成獨立一行回頭條件、原行刪掉那一句」。

天花板第 1 條仍保留「只提醒不擋」和「盲判上線前…推得出去」。兩條 REVISIT 行(2026-11-20、2027-01-08)是新增的,但原行沒刪那一句。

另外 2027-01-08 那條要數「經盲判或人工確認的真陽性與誤報」,目前治理帳的提醒事件(欄位只有 scope、seg、row、variant、pending)沒有可記確認結果的欄位,條件到期時機器算不出來。

**F9**
severity: minor
blocking: 否
引句:「+            elif kind == "evidence" and reminders is not None and sg["seg"] not in waived:」
每次 `code-loop check`、pre-push、CI 重算表態都會對同一條提醒各記一筆治理帳,記帳又放在判定函式 `_dispositions_verdict` 內(經 `_kt_sit_reminder_lines`)。

同檔的慣例是「判定函式只回傳,帳由呼叫那一層寫」(`_codeloop_lint_new_step`)。這樣會有兩個後果:
- 同一段同一列重複計數。
- 2027-01-08 的「真陽性至少 20 筆」若不依 seg 與 row 去重,數字會被灌水。

總結:最嚴重是情境題逾時時已查出的缺段缺列被整批丟掉、整道閘放行(F1),以及新事件 `code-loop/warned` 未歸類、一進版控帳就讓 `t_loop_close_kinds_classified` 翻紅(F2),會擋 2 條。
