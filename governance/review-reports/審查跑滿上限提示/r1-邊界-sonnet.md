severity: major

## F1 S1「新迴圈一律改問處置閘」沒排除 light 分級,字面實作會讓 light 迴圈永遠卡死
severity: major
blocking: 是(照 spec 字面把 light 迴圈的過否判定也改成呼叫處置閘,light 迴圈會從「本來能正常跑到 cap」變成「每次都被結構性擋下,永遠到不了 cap」,跟這份計劃要修的病灶同形狀——實作者會做出壞系統)
引句:「2026-08-25 之後開的迴圈(帳首日期在舊閘退役日之後),loop next 判「過了沒」改問處置閘,不再委派舊閘。舊迴圈照舊。」
file: `scripts/lumos:9557-9561` `cmd_loop_status` 裡 `--disposal` 與 `--light` 是硬互斥:一起用直接印「擋下:--disposal 是獨立的一套閘,不能跟 --panel/--light/--settle/--need/--min-seats 一起用」並回 rc=2。
file: `scripts/lumos:10402` light 迴圈(`light=True`)必為 `panel_fmt=False`(light 與 round 紀錄互斥,見同函式前段 light 守衛),現行 `cmd_loop_next` 第②步呼叫 `cmd_loop_status(..., panel=(panel_fmt and not light), light=light, ...)`——light 時 `panel=False`,根本碰不到已退役的 `_loop_status_panel`,所以 light 迴圈今天本來就能正常跑到 cap(rc 只在 0/1 之間,不會卡在 2)。
敘述:spec 的 S1 條款字面只用「post-cutoff 且帶 --spec 且處置閘沒過」當條件,沒有排除 `light=True` 的情形。若實作者依字面把第②步整段換成「一律問處置閘」,對 light 迴圈會變成每次呼叫 `cmd_loop_status(disposal=True, light=True, ...)`,命中上面互斥守衛回 2,`cmd_loop_next` 第②步 `if rc == 2: return 2` 直接短路,cap 檢查(第③步)永遠到不了——把「本來能用」的 light 迴圈改壞。

## F2 S1 同一句話也沒排除 seq(code 迴圈 standard 循序單審)——這類迴圈的處置帳結構性被處置閘拒收
severity: major
blocking: 是(照 spec 字面套用會讓 seq 迴圈的處置帳每次都被判「處置帳必須綁輪次」擋下,實作者做出的是另一種「到不了 cap」的壞系統,不是修好原本那個)
引句:「上限由分級決定,處置閘要印的那段也叫同一支函式算,不寫第二份對照表。」
file: `scripts/lumos:10402` `seq = (eff_tier == "standard" and _roster_kind(loop_id) == "code" and not panel_fmt)`——code 迴圈 standard 分級走循序單審時 `panel_fmt=False`,不是新病灶命中的那條路(已退役的是 panel_fmt=True 的多席審)。
file: `scripts/lumos:10444` `rmode = "" if (light or eff_tier == "legacy" or seq) else f" --round r{n_next}"`——seq 迴圈的紀錄本來就不帶 `--round`。
file: `scripts/lumos:10467-10476` 工具自己印給人抄的 `disposal_cmd` 模板對 seq 迴圈套用 `rmode=""`,等於教使用者記一筆不帶 `--round` 的處置帳。
file: `scripts/lumos:18321-18325` `_loop_status_disposal` 對 round-less(`__seq` 開頭)又帶 `findings_set` 的判定輪直接印「擋下:這一輪是無輪次(round-less)帳列卻帶了處置結果——處置帳必須綁輪次」並回 rc=2。
敘述:seq 迴圈今天走的是「非 panel、非 light」的舊式連續合格判定(cmd_loop_status 沒開 disposal/panel/light 三個旗標的那條路),沒被退役影響,本來就能正常到 cap。S1 若照字面把「post-cutoff 且非舊迴圈」全部改問處置閘,seq 迴圈會被上面 18321 行的守衛結構性擋下(rc=2),同樣到不了 cap——而且這個組合(seq+disposal)工具自己印的指令模板就會誘導使用者踩進去。spec 沒有任何一句話把「S1 只適用於 panel_fmt=True 的迴圈」寫清楚。

## F3 S6「沒有彙總帳就印沒記處置」跟既有 disposal 引擎的「0 發現空輪(vacuous)」語意衝突
severity: major
blocking: 是(某一輪其實已經合法走完「處置集合」步驟、只是因為留痕/條款/落點/資安等別的步驟失敗才留在未過關狀態,cap 報告卻會照 S6 字面判斷成「這輪沒記處置、判不了」,跟帳面事實矛盾,是誤導使用者的錯誤輸出)
引句:「若有任何一輪沒有彙總帳,則應印那一輪沒記處置並不給建議」
file: `scripts/lumos:18366-18373` `_loop_status_disposal` 明文:「0 條發現的乾淨輪:record 端明文「沒發現別帶處置選項」,這裡再要求處置帳=兩邊打架、乾淨輪永遠過不了……手冊語意=「每個發現都有去向即過」→ 0 條發現視同全處置(vacuous)」,並印「[disposal] 處置集合: ✓ — 這輪 0 條發現,沒有東西要處置(空輪;留痕仍要重驗)」——這種輪 `carrier is None`,結構上跟「沒記處置」完全一樣,但語意是「已經正確處置(0 條)」,不是「沒記」。
敘述:一輪 0 發現(carrier=None、vacuous=True)仍可能因為 ⑤條款綁定/⑥資安席/⑦落點/③留痕重驗任一步驟失敗而讓那一輪整體 FAIL,若這剛好是連續幾輪裡的其中一輪且最終跑滿上限,S6 字面規則會把它算成「沒有彙總帳」而拒給建議,但實際上那一輪的折入數該算 0(乾乾淨淨),不該跟「真的沒記帳」混為一談。spec 沒有把 vacuous 輪跟「沒記處置」的輪分開處理。

## F4 印報告的位置沒有交代要比照既有 `readonly` 慣例守衛,否則會汙染 freeze/replay 的輸出
severity: minor
blocking: 否(不改變 rc/fails,`loop replay` 的漂移比對只讀 `out["rid"]`/`out["fails"]`/rc,不比對印出的文字,所以不會誤判漂移;只是多印一段跟凍結/回放語境無關的建議文字)
引句:「`loop status --disposal`:輪數已達上限、或觸發熔斷時,在判定之後印同一段。」
file: `scripts/lumos:634,648,796` 三處都以 `readonly=True` 呼叫 `_loop_status_disposal`(分別用於 `loop replay --freeze` 首次凍結、凍結後重算、回放對帳),都是唯讀卷證重算情境。
file: `scripts/lumos:18531-18533` 既有慣例是 `if not readonly: _roster_tail(); _severity_tail()`——advisory 尾巴刻意不在 readonly 模式印。
敘述:spec 只講「在判定之後印同一段」,沒有點名要把新報告放進 `_loop_status_disposal` 內部時,得比照既有 `_roster_tail`/`_severity_tail` 的模式加 `if not readonly` 守衛,否則 `loop replay --freeze`/回放時也會印出這段不相干的建議。不影響過關判定,只是卷證輸出多噪音,實作時容易漏掉(README/計劃都沒提到 readonly 這個既有旗標)。

## F5 spec 反覆寫「2026-08-25 之後」,跟共用退役判定函式實際的 cutoff 常數(2026-08-26,>= 比較)差一天
severity: minor
blocking: 否(只要實作直接呼叫既有 `_panel_retired_for`/`_loop_anchor_tier` 等共用函式,邊界就會自動跟現行一致；問題只在 spec 的敘述用詞不精確,若有人照 spec 文字寫死 2026-08-25 當天的邊界測試,會跟函式實際邊界對不上)
引句:「2026-08-25 之後開的迴圈(帳首日期在舊閘退役日之後),loop next 判「過了沒」改問處置閘」
file: `scripts/lumos:8202` `cutoff = os.environ.get("LUMOS_PANEL_RETIRE_CUTOFF", "2026-08-26")`
file: `scripts/lumos:8205` `return bool(_re.match(r"\d{4}-\d{2}-\d{2}", ts)) and ts[:10] >= cutoff`——首筆記錄 ts 剛好是「2026-08-25」當天的迴圈,`ts[:10] >= "2026-08-26"` 為假,不算退役,仍走舊 panel 閘回放,跟 spec 文字說的「2026-08-25 之後」語意(隱含 25 號當天算新)不一致。
敘述:程式碼本身這個「退役日訊息印 2026-08-25、常數卻是 2026-08-26」的不一致是既有(line 8285 訊息文字寫「panel 閘自 2026-08-25 甲裁後」),不是這份計劃造成的,但這份計劃反覆用「2026-08-25 之後」措辭描述同一件事、又沒有明說「一律呼叫既有函式決定邊界、不寫死日期」,容易讓實作或測試在 S9(舊迴圈路徑不變)這條上按 spec 文字寫錯邊界值。

已看,無:
- S2「輪數已達上限而沒帶 --spec 時直接回跑滿上限,並在帳上有材料路徑時補好指令」:現有 `scripts/lumos:10634-10662` 已經有「帳上有 spec_path 就把指令補完」的成熟邏輯(型別驗證、只信最後一輪、repo 根解析都做了),S2 只是要求把這段邏輯挪到 cap 判斷之後也適用,機制上可行,沒發現額外缺口。
- S4/S5 折入數比較規則(最後一輪 vs 前一輪、severity 取最高):`_loop_status_disposal` 內建的 `groups`(`OrderedDict`)本來就依 append 序保留每一輪所有記錄,不管輪次命名是不是 `rN`、有沒有跳號,用清單順序取「最後一輪」「前一輪」都不受影響,沒發現邊界問題。
- S7 提早熔斷(累計折入 > 20,只印不改判定):「只讀帳本裡這個編號的列」的效能主張與現有 `_loop_status_disposal` 讀法(遍歷同一份已載入的 `rounds`)一致,沒發現額外讀帳路徑。
- 回退段(拔掉兩處呼叫、還原 loop next 判定段兩處改動):兩個呼叫點(loop_next 第②/③步之間、`_loop_status_disposal` 收尾前)都是可獨立刪除的加法,沒有新帳欄位、沒有資料遷移,回退機制成立。
- 誠實界線段與 RETIRE-IF 條件:如實承認了「規則看不出後幾輪是不是修正本身帶來的」「門檻沒回測」,REVISIT 掛在計劃節點 `2026-10-26`,格式合規。

最嚴重 severity: major;blocking 共 3 條(F1、F2、F3)。
