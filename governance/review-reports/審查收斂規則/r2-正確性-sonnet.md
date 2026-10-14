severity: major

## 已讀範圍
- 計劃全文和這輪改動 diff 都讀了。
- 對照的程式在 `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos`:`INV_TAG_RE`、`AUDIT_REF_RE`、`_guard_formal_line`、`_kill_find_contract`、`cmd_guard_audit`、`_pitfall_tier`、`_lens_contract_lines`、`cmd_loop_escape`。
- 證據分兩種。第 1 點用正規式實測(見 finding 1)。其餘幾點是讀程式推出來的,沒有實際跑。
- 實驗沒在 scratchpad 建目錄,只用了行內的 python 一次性片段,沒有留下任何檔案要刪。

severity: major
blocking: 是 — `[residual:]` 不在 `INV_TAG_RE` 裡,「正文相同只差標記」的比對會被它弄壞,而計劃沒有安排修這點。
引句:「`guard audit` 重審不碰 `[residual:]`,所以重審不會抹掉殘留。」
問題:計劃說 `[residual:]` 是「跟 `[audit:]` 同家族、一個方括號一個欄位」,但 `INV_TAG_RE` 只剝 test/audit/kill/src/git/manual/keeps。計劃的七項「要一起改」清單和 S1 到 S7 都沒有提到把 `residual` 加進去。結果是「乾淨宣稱文字」會帶著 `[residual:…]`。下面幾處都是拿剝完標記的文字比相等或比子字串,會受影響。
- `_guard_formal_line` 比的是 `INV_TAG_RE.sub("",claim)` 對 `INV_TAG_RE.sub("",該行)`。
- 呼叫它的三處是 `_guard_home_of_fields` 的家筆記對回(約 16489)、漂移檢查 c5(約 37542)、約 40418 那處。
- `_kill_find_contract`(kill-add、guard audit、doctor 共用)和約 17515 的顯示用 `[:30]` 也用這個剝法。

具體失敗情境:
- 殘留標記寫在家筆記的正式合約行上,而計劃筆記裡預告的原句沒有它。實測結果是比對不相等:剝完的 A 行是 `X 不可重複   [residual:Projects/p#d12]`,剝完的 B 行是 `X 不可重複`,比較得 `False`。
- 於是 `guard settle`、c5 漂移檢查和 `guard bind` 的對回都會認為「家筆記沒有這條正式行」。
- 使用者會看到「已轉正」被誤報成未轉正,或一直被要求重跑 settle,而且只有帶殘留的合約會這樣。
- 反方向也成立:若 `INV_TAG_RE` 剝掉 residual,`_guard_formal_line` 會恢復正常,但這是額外的程式改動,計劃沒列。S2、S4 只測了 audit 保留和徽章,抓不到這個問題。

佐證:file: `scripts/lumos:5495`(`INV_TAG_RE` 定義)、file: `scripts/lumos:16287`(`_guard_formal_line` 剝後比相等)、file: `scripts/lumos:17397`(`_kill_find_contract`)。

severity: major
blocking: 是 — 新判準有一個類別沒有出口,第 3 問還是會永遠收不了斂。
引句:「透過系統對外的入口(端點、公開函式、資料庫結構)就測得到的**,一律是局部退化」
問題:判準只定義了「測得到就是局部退化」。「繞過設計」被寫成「要改架構或部署形態、而且對外入口測不出來」,是兩個條件同時成立。局部改動(例如鎖太早釋放、條件寫反)只在特定交錯時序才出事,這種對外入口測不到,也不是改架構,所以兩類都放不進去。
- 「等價或殺不掉」的出口只收「行為等價」或「配方多檔多處、`kill-add` 表達不了」,沒有收「非確定性、跑不穩」。
- 反過來,照字面讀的話,「測得到」的門檻沒有任何成本或確定性的限定。多節點這種「繞過設計」,理論上只要有多節點測試環境,也算「對外測得到」。

具體失敗情境:
- 審計員提出「鎖在回傳前被提早釋放」,只在兩個請求交錯時才出錯。
- 照字面這是局部退化,必須有 `kill-add` 配方且被 `killed`。但這種配方要嘛 `survived`,要嘛 `timed_out_weak`,按計劃都算沒殺掉。
- 三輪後只能「攤給人裁」,跟原本一樣沒有終點。
- 另一邊,第二個代理被問「能不能從對外入口測到」時,幾乎一定能想出辦法說能(例如併發壓測),整個殘留機制可能因此永遠用不上。
- 計劃沒定義「測得到」是理論上能還是在現有測試基礎設施下能。

severity: major
blocking: 是 — 「編排者只能往嚴改、殘留要第二個獨立代理同意」只是流程文字,沒有任何東西能強制,所以繞得過去。
引句:「兩邊都說測不到,才准記殘留。」
問題:`guard residual` 的寫入驗證只查節點存在、決策存在、`valid` 不是 false、內容非空,不查第二個代理的判斷。計劃也沒有任何地方留下第二個代理的結論,沒有帳欄位、沒有戳記、沒有決策內容必填項。繞過的路徑有:
- 編排者自己決定把哪條反例、用什麼措辭交給第二個代理,而「只給那條反例與合約」就是由編排者挑選的。
- 同意與否沒有次數限制。第二個代理說「測得到」,編排者可以換措辭或換代理重問,直到得到「測不到」。
- 編排者可以跳過第二個代理,直接呼叫 `guard residual`,工具照寫。
- 「編排者不准把局部退化改成繞過設計」只有文字,沒有機制:殘留決策一旦記下,工具看不出它當初是怎麼分類的。
- 這正是計劃自己引的 maker≠checker 規矩,但它自己的 checker 沒有留痕,事後也無從審計。
- 殘留決策的「四欄」是從 `decision-add` 來的,沒有欄位承載第二個代理的 id 或結論。

具體失敗情境:
- 編排者想收斂,直接 `guard residual … Projects/p#d9`,工具驗證通過。
- 戳記、徽章、高風險分級全都照常運作,看起來一切合規。
- 事後無法分辨這筆殘留有沒有經過第二個代理。
- 建議:至少讓 `guard residual` 要求一個 `--checker <模型/日期>` 之類的留痕參數,並讓 doctor 檢查殘留決策內文有沒有第二個代理的紀錄,讓繞過在帳上看得到。

severity: major
blocking: 是 — 升高風險的判法會漏,也有一個實作上卡在「熱路徑不載圖譜」的矛盾。
引句:「`pitfalls --diff` 算風險分級時,改動碰到的檔若在某篇帶 `[residual:]` 合約的節點 about_code 裡,分級升為 high」
問題:
- `_pitfall_tier` 的註解明寫「★vault-free★,pitfalls 在 pre-push 熱路徑上不載圖譜」。要判斷某檔在不在某節點的 about_code 裡,一定要讀圖譜。計劃沒說怎麼處理:是改 `_pitfall_tier` 破壞 vault-free,還是另外加一道。
- 如果圖譜讀取失敗,例如找不到 vault,會默默退回原本的分級,殘留機制就悄悄失效。
- 漏判一:只看 about_code 裡的檔。綁定測試檔、被審的合約行本身所在的筆記檔都不在 about_code。有人把綁定測試刪掉或削弱,或者把合約行的 `[residual:]` 連同程式一起拿掉,都不會被升高。應該以 base 版圖譜判斷,而不是以改動後的版本判斷。
- 漏判二:殘留決策記在 Projects 計劃節點,但合約在 Systems 節點時,有 about_code 的是 Systems 節點,所以這部分沒問題。但如果合約本身寫在 Projects 筆記(沒有 about_code),就完全不會升高。
- 漏判三:合約守的程式分散在別的節點家的檔(例如共用工具函式),不在這個節點的 about_code 裡。about_code 是目錄或萬用字元時,「碰到」要不要算也沒定義。
- 過度判:同一個節點 about_code 裡任何一支檔(不管跟那條合約有沒有關)被改,都會升到 high。節點管很多檔時,一條殘留會讓整個節點的所有小改動都走完整代碼審。

具體失敗情境:
- 有人在同一個提交裡刪掉 `[residual:…]` 標記,再改程式。用改動後的圖譜判,就不再是帶殘留合約,分級回到 standard。
- 另一個情境是,只動綁定測試,不動 about_code 裡的檔,也不升高。

severity: minor
blocking: 否 — 徽章對新增合約和新增標記的 diff 看不到,但主要風險已由前面幾條涵蓋,這條可以同輪順手處理。
引句:「所以「帶殘留」改放進接在後面的徽章(跟現在的綁定測試狀態徽章並排,例「⚠帶殘留 2 筆」),不靠行內文字。」
問題:`_lens_contract_lines` 的註解寫明是「base 版節點全文裡的合約行」。同一個 diff 裡新加的 `[residual:]` 標記,在 base 版裡還不存在,所以那一輪的鏡頭看不到徽章,只有下一輪或下一次改動才看得到。這個漏洞對「本次審查正好是記殘留的那個提交」特別明顯:代碼審席恰好是需要被提醒的人,卻什麼都看不到。計劃沒說徽章是從 base 還是 head 算、也沒說殘留的筆數怎麼數(單行多個標記、重複同一個決策)。

severity: minor
blocking: 否 — 新欄位的參數互斥沒有交代,實作時容易漏,但不影響整體設計。
引句:「`lumos loop escape` 加選填 `--residual-ref <節點>#<決策 id>`,記進逃逸帳的 `residual_ref` 欄」
問題:
- `cmd_loop_escape` 對 `--list` 有一串「不能跟記帳參數混用」的檢查,對 `--withdraw` 有 `others` 元組,對 `--auto` 也有自己的參數分支。新參數若沒加進這三處,會出現 `--list --residual-ref x` 被靜默接受,或 `--withdraw` 配 `--residual-ref` 被忽略。
- 計劃沒說 `--residual-ref` 寫入時要不要驗證指向的節點和決策存在。逃逸帳註解只說歸因守衛防「編號打錯」,如果這個欄位不驗證,RETIRE-IF 量到的 `residual_ref` 可能全是打錯的字串,量測失真。
- `--auto` 模式從提交範圍推迴圈編號,沒有殘留歸因的來源,所以應該明說「`--auto` 不支援」。

## 其他節
- `[residual:]` 與 `AUDIT_REF_RE`:`\[audit:\s*([^\]]+)\]` 只比對自己的標記,放在行尾加 `[residual:…]` 不會互相干擾。`cmd_guard_audit` 的 `line[:m.start()] + … + line[m.end():]` 也只換掉 audit 那段。已讀,無 finding。
- `guard bind` 的行定位:它用 `TEST_REF_RE.sub("", line)` 剝測試標記後做子字串比對,residual 留在文字裡不會令子字串找不到。已讀,無 finding。
- 已排除的反例:「重審會抹掉殘留」。這一點在計劃裡是正確的,殘留是獨立標記,`cmd_guard_audit` 只覆蓋 `[audit:]`。

最高等級 major,4 條 blocking(`INV_TAG_RE` 漏 residual 一條、判準沒有出口一條、第二代理無留痕可繞一條、升高風險的判法一條),另有 2 條 minor 非 blocking。
