severity: minor

## Z1 數量標記自己一套正規式抽欄位,不在 _SLOT_KEYS
severity: minor
blocking: 否
引句:「_COUNT_TAG_RE = re.compile(r"\[count:([^\]]*)\]")」
file: `scripts/lumos:3921`
說明:`[count:]` 沒進 `_SLOT_KEYS`,用自己的正規式抽,值再交給 `_count_parse`。⚠ 專案本來就有兩種抽法並存:前綴行(WHY/RULE/PITFALL…)走 `slot_parse` + `_SLOT_KEYS`;散文行裡的回頭條件 `[when-*]` 走 `_probe_lines` → `_probe_parse`(32241、32202),不經 slot_parse。count 標籤寫在散文句子後面,走第二條路,跟 `_probe_lines` 的做法同形(同樣的可見行、行內程式碼、圍欄判定;`_drift_cond_split` 也重用了),所以不算新做法。沒驗證的點:若有人把 `[count:…]` 寫在 WHY/RULE 等前綴摘要行,slot_parse 遇到不在 `_SLOT_KEYS` 的鍵會不會唸未知欄位,我沒有跑;請編排者決定要不要補一條「未知鍵」測試或把 count 列入白名單。

## Z2 兩種「數量標記」並存:`<!--lumos:count=…-->` 與 `[count:…]`
severity: minor
blocking: 否
引句:「PRIOR-ART: 最小解在工具這一層:世界上「文件裡的數字跟程式對不上」的標準解是 doctest」
file: `scripts/lumos:3285`
說明:doctor N 段(3285)已有 `<!--lumos:count=N re=正則 in=glob-->`,由 doctor 評估、會擋。新增 `[count:路徑::名稱=N]` 名字同為 count、語意不同(ast 數具名集合、只在 drift scan 評估、doctor 只數標籤)。計劃的 PRIOR-ART 與〈天花板〉1 明講兩者互補(正規式管程式組出來的集合、ast 管字面值),且分流理由(Z 段不評估)有交代。⚠ 專案裡「數量標記」變成兩種語法、兩個評估路徑、兩套求值器,作者可能搞混該用哪種;沒有一處導引(例如 N 段或 skill 命令表的一句「字面值集合用 [count:],其餘用 lumos:count」)。我不判成 major,因為兩者能力不重疊且有書面理由,交編排者裁。

## Z3 `_drift_fix_load` 對 count 開特例,handled 不看 state findings
severity: minor
blocking: 否
引句:「if kind == "count":     # 要讀程式檔才判得出對不對得上,判定在 _drift_fix_count 裡做(那裡會讀工作目錄)」
file: `scripts/lumos:33918`
說明:鄰居 c1~c5 都由 `_drift_fix_load` 統一呼叫 `_drift_current_finding`(33649)確認「這一行現在真的是這種發現」,compute 函式只管算改法。count 的發現來自 drift scan(讀程式檔),不在 `_drift_state_findings` 裡,所以 loader 提前 return、把「現在還對不上」的判定搬進 `_drift_fix_count` 自己做(讀工作目錄那棵樹)。結構上等價且方向正確(沒有繞過 helper、沒有跨層),但是 loader 內 kind 字串特例,而且 `handled` 用 `_count_lines(txt)` 自己驗,不接 `_drift_state_findings`(c1~c5 用 `_drift_no_kind(...)` 或 `_handled(fs, txt)`),`check` 也是恆真 lambda。新增第二種 kind 的 fix 若同樣不是 state finding 會再加一個 if;鄰居沒有「非 state 發現的 fix」先例,所以不是違反既有做法,只是尚無共用的鉤子。

## Z4 `text_of(*paths)` 一支方法兩種語意
severity: minor
blocking: 否
引句:「if not todo or not self._read(todo) or len(paths) != 1:」
file: `scripts/lumos:32547`
說明:鄰居分工清楚:`prefetch(conds)` 只批次預讀(32547)、`_read(paths)` 回布林(32522)、讀文字走 `_text`/`one`(32670)。新的 `text_of` 多參數=預讀回 None、單參數=回文字,同名兩種回傳語意;呼叫端 `_drift_count_scan` 用 `tree.text_of(*sorted(...))` 純為預讀,丟掉回傳值(傳入剛好一支檔時還會順手回文字,沒人用)。另外 `_count_actual` 從外面呼叫的是公開方法 `text_of`,沒有直呼私有 `_read`,這點與鄰居一致。建議拆成 `prefetch_paths(paths)` 與 `text_of(path)`,跟 `prefetch`/`_read` 分工對齊。

## Z5 標籤解析結果的錯誤鍵 `err`(字串)與鄰居 `errs`(清單)不同
severity: minor
blocking: 否
引句:「return {"path": path, "name": name, "n": None if err else int(num.strip()), "err": err}」
file: `scripts/lumos:32238`
說明:`_probe_parse` 回 `{"conds","by","errs","bad"}`(`errs` 是清單)、結案標記也是 `{"closed","errs"}`(31987);`_count_parse` 回單一字串 `err`。失敗回傳形狀的鄰居慣例是「解析結果內帶 errs 清單,由 `_drift_probe_row_problems` 轉成問題」;`_count_eval`/`_count_members`/`_count_enum`/`_count_actual` 回 `(值, 原因)` 與 `_drift_gone_text`(回 `(文字, 判不了原因)`)一致,這部分對齊。命名面:抽取半邊用 `_count_*`(對應 `_probe_lines`/`_retire_lines`),drift 流程半邊用 `_drift_count_scan`/`_drift_fix_count`(對應 `_drift_probe_scan`/`_drift_fix_c1`),前綴分工與鄰居一致。訊息語氣上「數量標記」+原因直接串接,不像鄰居 `RULE 撤除條件:` 帶冒號,純措辭差異。

---
三問總答
1. 分層與依賴方向:新碼放在 `_drift_probe_scan` 之後、`_DRIFT_BORN_*` 之前的同一個區段,對外只經 `_drift_count_scan`(scan 呼叫)、`_count_lines`(doctor Z、fix、scan 共用)、`_count_actual`(scan 與 fix 共用);讀檔走 `_DriftProbeTree` 的公開方法與 `tree.files`,沒有從外面呼叫類別私有方法;`_drift_cond_split`、`_drift_probe_is_py`、`_notelines_regions`、`_visible_lines`、`_strip_inline_markup` 都是重用而非另寫。依賴方向跟 `_probe_lines`/`_drift_probe_scan` 一樣。唯一不同是 fix 路徑 loader 特例(Z3)。
2. 命名與錯誤處理:前綴分工對齊(`_count_*` 對 `_probe_*`/`_retire_*` 抽取層、`_drift_*` 對流程層);`(值, 原因)` 回傳形狀對齊;`err` 對 `errs` 小差異(Z5);訊息語氣大致一致。
3. 第二種做法:(a) 不算新做法,回頭條件已有同形先例,但前綴行裡出現 `[count:]` 的行為未驗,⚠(Z1);(b) 兩種數量標記並存,有書面理由,⚠ 交編排者(Z2);(c) loader 特例與 handled 自驗,結構上等價、無先例(Z3);(d) `text_of` 雙語意,與 `prefetch`/`_read` 分工不一致(Z4)。

總結:不對齊共 5 條,其中 major 0 條;最高等級 minor
