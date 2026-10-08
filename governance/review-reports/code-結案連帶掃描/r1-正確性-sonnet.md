severity: major

## F1 子句切點寫成兩個半形分號,全形分號「；」不切
severity: major
blocking: 是
引句:「_DRIFT_CLAUSE_SPLIT_RE = re.compile(r"[。;;]|——")」
file: `scripts/lumos:32018`
正則字元類裡的兩個分號都是 U+003B(已逐字元查過,沒有 U+FF1B),全形分號「；」(中文筆記最常用的子句分隔)不是切點。設計文字寫「以 。;; 與 —— 切」,兩個分號顯然是半形加全形,實作成了重複的半形。測試只用 。與 —— 驗切分,走不到這一格。
最小重現(臨時 repo,用 test_lumos 的 _df_repo 夾具;Done_計劃 已收尾):
1. 未收尾計劃 F_計劃 正文寫三行:
   行6 `[[Projects/Done_計劃]] 已上線；這邊還沒做`(全形分號)
   行7 `[[Projects/Done_計劃]] 已上線;這邊還沒做`(半形分號)
   行8 `等 [[Projects/Done_計劃]] 落地；後面是別的事 還沒做`
2. 跑 drift scan:c6 列出行 6 與行 8,行 7 不列。行 6 的「還沒做」跟連結其實隔了一個分號,行 7 同樣的句子只因分號字元不同就不列,兩者判定不一致。
3. 對行 8 跑 `drift fix --kind c6 --settled "已決定好了" --dry-run`:括號補在整行最尾端(「…後面是別的事 還沒做(已裁定:…見 [[Projects/Done_計劃]])」),不在「落地」之後;補錯位置,正是〈做法〉第 3 點要避免的「離那句太遠」。
後果:全形分號句產生誤報 c6,修法把「已裁定」括號貼到不相干的子句後面,而且整行被括號壓掉後真正的待定子句不再被列。

## F2 doctor 的漂移段沒列 c6
severity: minor
blocking: 否
引句:「做:漂移種類 c6 的偵測(drift scan、doctor 的漂移段、推送前 drift check 的只列出)」
file: `scripts/lumos:36531`
`_drift_doctor_lines` 的迴圈是 `for k in ("c1", "c2", "c3", "c4", "c5"):`,本 diff 沒碰它,c6 不在裡面。重現:臨時 repo 放一篇未收尾計劃,正文寫 `待裁定 [[Projects/Done_計劃]]`;`drift scan` 列出 `[c6]`,`lumos doctor --verbose` 完全沒有 c6 那一行(同夾具加一張連著已收尾計劃的 open Issue,doctor 印出 `[c2] … 1 筆`)。〈範圍〉第一項承諾 doctor 的漂移段要有 c6,八支新測試沒有一支跑 doctor 看 c6,所以沒翻紅。

## F3 已裁定括號按整行壓掉,同一行第二個待定子句也跟著消失
severity: minor
blocking: 否
引句:「if "[[" not in line or _DRIFT_SETTLED_MARK_RE.search(line):」
重現:
1. 未收尾計劃一行寫 `待裁定 [[Projects/Done_計劃]];還沒做 [[Issues/Res]]`(Res 已 resolved),scan 列為一筆 c6,related 兩篇。
2. 執行 `drift fix --kind c6 --settled "已決定好了" --by Projects/Done_計劃`,行變成 `待裁定 [[Projects/Done_計劃]](已裁定:… 見 [[Projects/Done_計劃]]);還沒做 [[Issues/Res]]`。
3. 再跑 scan:c6 為 0 筆。「還沒做 [[Issues/Res]]」仍然是同一子句待定加已收尾連結,但整行因為有括號被判已處理,修了一個、漏掉另一個,而且 handled 判定因此回報成功。

## F4 summary 寫成單行值時第一行被略過
severity: minor
blocking: 否
引句:「in_sum = ln.startswith("summary:")」
重現:開頭欄位寫 `summary: KEY:等 [[Projects/Done_計劃]] 待裁定`(單行值,不是 |-)。`_drift_pending_lines` 在這一行設 in_sum 之後立刻 continue,值本身所在的那一行不進回傳清單;scan 沒列這一行(同夾具 summary 用 |- 的 S2 會被列)。drift fix 對那一行回 2 「不在正文或 summary 裡」。本倉庫目前零篇單行 summary,所以現況掃不到差別,但消費專案(rtb)寫成單行就整類漏掉。

## F5 --decision 的新句不重驗待定詞,擋下的目的可被一句話繞過
severity: minor
blocking: 否
引句:「lines[no - 1] = f"{lead}DECISION:[{datetime.date.today().isoformat()}] {o['decision'].strip()}"」
重現:Issue 摘要 `DECISION:(未裁)要不要修`,跑 `drift fix --kind c2 --close --status done --reason "修好了,提交 abc" --decision "還沒做,另開計劃"`。回傳 0,摘要變成 `DECISION:[今天] 還沒做,另開計劃`,結案後同一支指令接著印「摘要還有 1 行決策行寫著待定……用 lumos drift fix --kind c2 --close 結案時會擋」——而它剛用的就是 --close。換句只驗長度與佔位字,沒用 _DRIFT_PENDING_WORDS 再過一次。

## 已走過沒問題的範圍
引句:「lines, live, err = _drift_close_gates(cx)」
- c2 --close 兩道擋:擋下時 res 為 None、一個檔沒寫(驗過 A 同時有待定決策行與活回頭條件,只給 --decision 回 2 且檔案位元組不變);先換 DECISION 行再算 _revisit_lines,--keep-revisits 記的行號是加橫幅之後的行號(實跑修復帳 lines=[13] 對得上檔案);--dry-run 走同一組擋並印預覽;--keep 搭 --decision/--keep-revisits 回 2。
- c6 修法的插入位置:同一連結出現兩次、行尾帶尾端空白、別名與 # 錨點、待定子句後接 —— 、summary 區塊內的行,都補在正確子句結尾;表格行與無待定子句的行回 2 不寫檔;handled 判定靠行號不位移,可靠。
- 行號:有開頭欄位時正文行號 off+no 與檔案一致;BOM 或沒收尾的開頭欄位時整份當正文,行號仍一致;drift fix 對 BOM、CRLF 本來就拒絕。
- 四個呼叫點回傳碼不變;decision-supersede 的列出排在 cascade 之後、stdout 第一行不動;真實圖譜副本 648 篇上 scan 約 1.9 秒、set 約 1.6 秒,_drift_backrefs 成本不構成問題。
- drift check:c6 不進 must,考試的噪音只算 must,歷史重放不受影響;表態綁 related 的行為由既有比對函式處理,t_drift_check_lists_c6_and_ack_binds_related 有實測。
- 八支新測試在現有程式上全綠(c6 關鍵字三支實跑通過),各支都有走到被測分支;缺口只有 F1 的全形分號、F2 的 doctor、F4 的單行 summary 三格沒有測試。

總結:全形分號被誤寫成半形重複字元是唯一會讓判定與修法位置出錯的缺陷,其餘四條都是漏列或可繞過的小洞,兩道擋與列出的主幹路徑經實跑沒有問題。
