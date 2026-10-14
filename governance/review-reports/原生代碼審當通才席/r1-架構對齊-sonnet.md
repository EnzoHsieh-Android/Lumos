severity: major

四問逐問答。對照 repo 裡已經有這份計劃的實作(`scripts/lumos:48595` 的 `cmd_seat_import_code_review`、`templates.md:444` 的 §7.9)。下面以被審計劃為準,實作只拿來佐證。

**問 1 分層與依賴方向:大致一致,有一處跨層。**
- 轉換放在 lumos、跑模型放在編排者手上,跟既有做法同方向。
  - 既有的三個收貨指令都是只吃檔案的小工具:report-normalize 在 file: `scripts/lumos:10221`,quote-check 在 file: `scripts/lumos:27364`,seat-check 在 file: `scripts/lumos:27589`。
  - 外家席也是編排者自己換 `claude -p`,見 file: `skills/lumos-code-loop/SKILL.md:28`。
- 不一致在隔離層。既有審查席走派工詞加 lumos-guard 唯讀隔離(file: `skills/lumos-design-loop/templates.md:20` 的 §0),新席改成編排者自己開 `bypassPermissions` 再列黑名單,見下面第 3 條。

**問 2 命名與錯誤處理:結構對,小處不齊。**
- 子指令 `seat-import` 與 `seat-check` 同一族,命名一致。
- rc2 加「擋下:」前綴,與 report-normalize 的用法一致,見 file: `scripts/lumos:10221`。
- `--list-only` 與既有的 `--json` 開關不同,見第 4 條。
- 認不得時另存 `.unparsed.txt` 沒有先例,見第 6 條。
- 席名 `原生審查-sonnet` 與編制格子 `鏡頭5` 脫鉤,見第 5 條。

**問 3 第二種做法:有三處。**
- 引句改由轉換器代產。
- 等級改由第三個模型依一套新規則補。
- 派席與隔離改成編排者開高權限加黑名單。
- 報告格式沒有另立,仍是檔首 severity、每條 severity/blocking/引句/file 四行,這點一致。

**問 4 落點:不完整。** 見第 8 條。

---

1. 引句由轉換器代產,是第二種引句錨定做法
severity: major
blocking: 是
引句:「照每條的檔案與行號,在複本裡讀那一行;那一行去掉首尾空白後至少 10 字」
- 既有做法是審查席自己逐字寫引句,quote-check 再回頭對凍結 patch,錨不到就不採信,見 file: `scripts/lumos:27364` 與 file: `skills/lumos-code-loop/SKILL.md:43`。
- 新設計是轉換器自己讀複本那一行,在上下 3 行內挑第一個符合的當引句。
  - 引句改成轉換器從 patch 挑出來的,對 patch 的比對天然會過。
  - 過了 quote-check,也不能說明原審查員真的看過這一行。
- 計劃的 PRIOR-ART 說「引句錨定…沿用既有規則,不另立」,但這裡自帶了一套「±3 行、至少 10 字、不含括號」的錨定規則。
- 這等於在既有「席宣告引句、機器驗」之外,另立「機器代產引句」。

2. 等級由第三個模型依一套新規則補,是第二種等級規則
severity: major
blocking: 是
引句:「會做錯行為、破壞合約、資料損壞或可被利用的是 major,會造成無法還原的損害的是 blocker,命名、風格、效率、文件精度是 minor」
- 既有做法是審查員自己標 severity。
  - 審查員標 blocker 或 major 時要附翻紅重現,附不出就自降一級,見 file: `skills/lumos-design-loop/templates.md:189`。
  - 等級規則寫在 file: `skills/lumos-design-loop/templates.md:56` 一帶和 §7.8 的 `templates.md:438`,各自單源。
- 新設計讓另一個沒有編排者脈絡的 haiku 呼叫,按計劃內自寫的三行規則補等級。
  - 規則在計劃、手冊、轉換器來源三處各抄一份,沒有指回 §3 單源。
  - 原生審查給的失敗情境也不經「附重現否則自降」那條。
  - 計劃把這個等級當「審查員層宣告」,與 file: `skills/lumos-design-loop/templates.md:307` 的兩層不互改綁在一起,但來源的信任模型已經變了。

3. 派席方式脫離既有隔離機制
severity: major
blocking: 是
引句:「--permission-mode bypassPermissions --disallowedTools "Bash(git push:*)" "Bash(gh:*)" "Bash(git commit:*)"」
- 既有審查席是子代理,帶 `LUMOS-SEAT` 標記,受 lumos-guard 唯讀隔離,見 file: `skills/lumos-design-loop/templates.md:20`。
  - 派工另有 `rN-dispatch.json`,供 seat-check 對帳,見 file: `skills/lumos-code-loop/SKILL.md:43`。
- 新席是用 `bypassPermissions` 開高權限,只靠黑名單擋三個指令。
  - 計劃自己記錄過一次實驗中出現「推送」狀態事件(第 31 行)。
  - 黑名單擋不到 `git remote`、`curl` 這類其他外送途徑。
- 這與「審查席不能做對外動作」的既有策略是兩種方式。
- 它也沒有 dispatch manifest,「收貨三道全照舊」中的 seat-check 沒有輸入。這一點建議釐清。

4. 旗標名 `--list-only` 與既有輸出旗標慣例不同
severity: minor
blocking: 否
引句:「只解析、印出清單(JSON),再把清單交給另一次無頭呼叫」
- 既有 vault-free 小工具要機器可讀輸出時一律用 `--json`,例如 file: `scripts/lumos:54796` 一帶的 quote-check、seat-check。
- 新設計用 `--list-only` 同時表示「只解析」和「輸出 JSON」,把模式與格式綁在一起。
- 結構是對的,只是命名不齊。

5. 席名與編制格子脫鉤,家族辨識靠席名
severity: minor
blocking: 否
引句:「對帳時家族算同門,比較靠審查員名」
- 編制格子是「鏡頭5」,席名卻是 `原生審查-sonnet`。
- 既有慣例是席名 `<鏡頭>-<模型>`,見 file: `scripts/lumos:13552`。
  - 資安席有專屬別名比對,見 file: `scripts/lumos:26631`。
- 鏡頭5 這格沒有類似的別名比對。
  - 席位對帳是否會把這席當成鏡頭5,計劃沒寫。
  - RETIRE-IF 還要靠席名辨識家族。
- 判不準,⚠。

6. 認不得時另存 `.unparsed.txt`,在席報告路徑旁新增副檔
severity: minor
blocking: 否
引句:「其他抽不出 → rc2,原文另存成」
- rc2 的語意與既有一致。
- 但既有的 rc2 路徑都不寫副檔,例如 file: `scripts/lumos:10221` 的 report-normalize。
- 新增的副檔放在卷證目錄旁,卷證目錄有「不准放腳本」之類的測試守衛,見 file: `skills/lumos-code-loop/SKILL.md:40`。
  - 計劃沒說副檔會不會被這些守衛或收貨流程誤認為席報告。
  - 計劃也沒寫寫入失敗時怎麼辦。
- ⚠。

7. 三段長指令寫在手冊散文裡,沒有固定成腳本
severity: minor
blocking: 否
引句:「新增一節〈原生審查席〉寫上面三段指令;收貨、記帳照既有規則。」
- 外家席的先例是把手打的 curl 固定成 `scripts/external-seat.sh`,理由是呼叫方式不再漂,見 file: `scripts/external-seat.sh:1`。
- 新席有三段含 `rm -rf`、clone、分支設定的指令,只靠編排者照抄,漂移風險正是那個腳本要解的問題。
- 章節寫法本身(§7.8、§7.9 的「為什麼有這一席」加指令區塊)與 file: `skills/lumos-design-loop/templates.md:406` 一致。

8. lands_in 漏了管編制與手冊的家
severity: minor
blocking: 否
引句:「  - Systems/pitfalls-code-loop」
- 被改的檔至少有 `_TIER_ROSTER`(在 `scripts/lumos`)、`templates.md`、`SKILL.md` 和新的轉換指令。
- 圖譜裡 `_TIER_ROSTER` 與 `skills/lumos-design-loop/templates.md` 的家是 Systems/design-loop,report-normalize、quote-check 也在那裡。
- 只列 pitfalls-code-loop 與資安席計劃的先例相同,所以不算違反慣例。
  - 但轉換指令、編制表、templates 新節的說明該寫進 design-loop,計劃沒列。
  - 依 CLAUDE.md 鐵則 5,改到哪支檔就要寫進它的家。

不對齊共 8 條,其中 major 3 條
