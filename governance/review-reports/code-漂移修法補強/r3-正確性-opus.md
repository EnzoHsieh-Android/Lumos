severity: major

# 代碼審第 3 輪 正確性席(opus)

實驗一律在 `git clone --shared` 出來的臨時目錄跑(`.../82c93a23-.../scratchpad/r3c`、`r3m`),直譯器 /opt/homebrew/bin/python3(3.14)。實驗腳本在 `.../82c93a23-.../scratchpad/r3exp/`(exp.py 各種提交形狀、s2.py、s3real.py、s3t.py、c4.py、mut.py 還原翻紅、slow.py)。

## 提交形狀逐一實測(真 git repo,跑 `lumos delguard --staged --json`)

| 形狀 | 刪除行跳過 / 新增行跳過 | 結果 | 判定 |
|---|---|---|---|
| 純工具更新(清單一起更新) | 跳 / 跳 | 不抽,note 記 vendored-skip=1 | 對 |
| 專案改過工具檔再 update | 不跳 / **跳** | 專案自己的 zzMine 照抽;**還在檔裡的 zzToolB 也被抽**(見 F1) | 錯一半 |
| 專案只改工具檔 | 不跳 / 不跳 | 照抽 | 對 |
| 拆除(刪工具檔與清單) | 跳 / — | 不抽,記一支 | 對 |
| git rm --cached | 跳 / — | 不抽,記一支 | 照設計 |
| 第一個提交 | 空 / 跳 | 沒有刪除行 | 對 |
| 暫存的是專案改的、工作目錄是安裝版 | 不跳 / 不跳 | 照抽 | 對 |
| 同提交改工具檔也改清單 | 跳 / 跳 | 不抽 | 誠實界線已記 |
| 工具檔改名搬走 | 跳(照來源) | 不抽,記來源路徑 | 照設計 |
| 專案檔改名成工具檔名(清單也改) | 不跳(來源是專案檔) | 照抽 zzProjSecret | 對 |
| HEAD 沒清單、這次 update 第一次寫清單 | 不跳 / **跳** | 名稱多抽 47 倍、逾時降級(見 F1) | 錯 |

提早離開那一條(「差異裡沒有工具檔路徑就不算」)是拿整份差異文字做子字串比對。改名來源會出現在 `diff --git a/scripts/lumos b/…` 和 `rename from scripts/lumos` 這兩行裡,工具檔路徑又全是 ASCII,不會被 quotePath 改寫。所以**改名來源不會漏**,比錯只會多算。

## F1 新增行的跳過跟刪除行的跳過不對稱,「專案改過工具檔再 update」和「HEAD 還沒有清單的第一次 update」把同一支檔的回收表整份丟掉
severity: major
blocking: 是
引句:「return frozenset(p for p in before if p in after or p not in after_present), after」
file: `scripts/lumos:29587`
file: `scripts/lumos:29375`
file: `scripts/lumos:29437`

1. 問題出在回傳值。第二個值(新增行要跳的)是「改之後原封不動」的整份清單,沒有跟第一個值(刪除行要跳的)對齊。只要一支檔「改之前不是原封不動、改之後是」,它的刪除行會照抽,新增行卻不進回收表(`_delguard_added_tokens` 用 `cur in vendored_skip` 跳過)。結果是同一支檔裡只改了一半、名稱還在的那一行,也會被當成「刪掉了」。這正是回收表原本要降的誤報(函式說明:「檔內改名/搬行即刻回收,降誤報」)。
2. 小例子(`r3exp/s2.py`):HEAD 的 scripts/lumos 是專案改過的版本(多了 zzMine)。update 把 `def zzToolB(a):` 改成 `def zzToolB(a, b):`,刪掉 zzToolA,清單也一起更新。實跑結果是 `hits` 同時出現 zzToolA、**zzToolB**、zzMine;`_delguard_confidence` 對 zzToolB 回 `low`,因為它還在 scripts/lumos 第 1 行。終端印的是「有 3 個被刪符號還在筆記裡被提到」。對照組是同樣形狀但完全沒有清單(也就是加這個功能之前的行為):只抽 zzToolA 和 zzMine,zzToolB 被回收了。
3. 真實大小(`r3exp/s3real.py`、`s3t.py`):HEAD 放本 repo `HEAD~40` 的 scripts/lumos、沒有清單,暫存區放現在的 scripts/lumos 加一份新寫的清單。這就是舊版安裝的專案升到有清單的版本時,那一次 update 的提交。
   - 本修法:`_delguard_parse_diff` 抽出 **379** 個名稱;預設 15 秒 deadline 下,實際等了 **15.4 秒**後印「超時降級…先放行」,治理帳記 `reason=timeout tokens=40`。
   - 對照組(兩邊都沒清單):抽 8 個、0.9 秒跑完。
   - 把 deadline 放到 120 秒:45.7 秒才跑完,印「339 個符號超 cap 未掃」。
   - 換句話說,這次修正把這個形狀從「r1 版整支跳過」變成「逾時、整次提交沒掃完」。同一個提交裡專案自己的檔也一起沒掃到。
4. 「專案改過 scripts/lumos 再 update」是第二輪正確性 F1 說的、「每次 update 都會碰到」的形狀,現在每次 update 都會丟掉 scripts/lumos 整支的回收表,規模跟第 3 點同一級。
5. 測試沒釘到:`t_delguard_vendored_two_states` ① 斷言「scripts/hooks/pre-push in add_skip」,把這個不對稱當成預期行為。它只檢查專案自己的 zzUserGuardFn 有被抽到,沒有檢查同檔還在的名稱會不會被多抽。
6. 設計上衝突的只有「專案檔改名成工具檔名」那個情形(`t_delguard_vendored_rename_and_count` ④ 要 keepMe 照抽)。那裡來源和目的是兩個不同路徑;沒改名、來源等於目的的檔,刪除行照抽時新增行也該照收。

## F2 列不完時給的指令,碰到 git 會加引號的目錄名時數量對不上「共 N 個」
severity: minor
blocking: 否
引句:「f" | awk -F/ 'NF>=4{{print $3}}' | sort -u"」
file: `scripts/lumos:28040`

1. 重現(`r3exp/c4.py`):同一個提交加了 21 個 bulk-XX,再加 3 個目錄 `q"uote`、`back\slash`、`tab<TAB>name`,然後對 c4 跑 drift fix。證據頁印「另有 4 個沒列出」、「同提交的完整清單(共 24 個…)」;照貼印出來的指令,實際只列出 **21** 個。
2. 原因:工具自己用 `show -z` 讀,拿到的是原始名字。印給人的指令沒有 `-z`;`core.quotePath=off` 只管非 ASCII 字元,名字裡有 `"`、`\`、控制字元時 git 照樣整條加引號、加跳脫(`"governance/review-reports/q\"uote/r1.md"`)。awk 切出來的是 `q\"uote`,`[ -d ]` 判不存在,就被濾掉了。
3. 計劃和 [[Systems/存量漂移守衛]] WHY 都寫「指令跟證據頁同一套定義…數量對得上」,這批名字不成立。⚠ 另一種情形:Linux 上磁碟是 NFD、git 是 NFC 時,`[ -d "<NFC 名>" ]` 也會失敗。這一種在 macOS(APFS 不分正規化)上重現不了,只按程式讀法推斷。

## F3 `t_drift_c4_dirs_capped_at_20` 宣稱的翻紅釘「指令把散檔也列進來 → ③紅」還原後不紅
severity: minor
blocking: 否
引句:「翻紅釘:拿掉上限 → ②紅;上限差一(19 或 21)→ ②④紅;不印指令、指令把散檔或已刪的目錄也列進來 → ③紅;」
file: `scripts/test_lumos.py:53764`

1. 還原實驗(`r3exp/mut.py` M12):把 `awk -F/ 'NF>=4{print $3}'` 換回第二輪之前的 `cut -d/ -f3`,只跑 `-k dirs_capped_at_20`,結果 6 passed、0 failed。
2. 原因:根目錄散檔 `governance/review-reports/README.md` 被 cut 切出 `README.md` 之後,後面的 `[ -d ]` 存在檢查就把它濾掉了。散檔這一條被「已刪的目錄」那條的濾法蓋住,測試分不出「只列四段以上路徑」這條有沒有做。前置斷言只證明 README.md 在提交裡,沒有證明它走到了「四段」這道濾網。這正是 [[Systems/測試假綠形態]] 那條合約說的「現場走不到被測分支」:釘子寫了,卻殺不死對應的還原。
3. 其他新測試的還原都會翻紅(下一節)。

## F4 讀 git 兩態的時間不受守衛的 deadline 限制,註解說「算在 deadline 裡」跟行為不一致
severity: minor
blocking: 否
引句:「讀 git 版本每支工具檔一次 git show(有逾時),時間算在這道守衛的 deadline 裡(下面 _over())。」
file: `scripts/lumos:17822`
file: `scripts/lumos:33249`

1. `_vendored_state(root, "HEAD")` 和 `_vendored_state(root, "")` 每次都逐支跑 `_lens_git(... "show" ...)`。每次呼叫固定 20 秒逾時,一共大約 36 次(17 支工具檔各兩次,加兩份清單),不看剩下的 deadline。`_over()` 要等全部跑完之後才判。
2. 重現(`r3exp/slow.py`):在 PATH 前面放一支 git 包裝,只要是 `show` 就先 sleep 1 秒,設 `LUMOS_DELGUARD_DEADLINE=5`,diff 動到 scripts/lumos。實際跑了 **38.3 秒**才印「5.0s 內沒掃完,先放行」。最壞情況是 36×20 秒。
3. r1 版讀工作目錄,不跑 git,沒有這個問題;這是這次改讀 git 帶進來的。正常的 git show 很快(實測整段約 0.8 秒),所以只標低。註解寫「算在 deadline 裡」,讀的人會以為有上限。

## 還原修法會不會翻紅(`r3exp/mut.py`,每次還原前先清 `__pycache__`、確認錨點只出現一次)

| 還原 | 結果 |
|---|---|
| 刪除行只看改之後 | two_states ①④⑤ 紅 |
| 改之後讀工作目錄 | ②③ 紅 |
| 拿掉「已不在暫存區也跳」 | two_states ④、rename_and_count ② 紅 |
| 改之前讀工作目錄 | ①③⑤ 紅 |
| 拿掉「diff 沒碰工具檔就不算」 | ⑥ 紅 |
| 新增行改成跟刪除行同一份 | ①⑤ 紅(也就是 F1 被當成預期行為釘住) |
| NFC 鍵只取一個現存目錄 | c4_r2 ⑥ 紅 |
| 同提交改回印 git 裡的名字 | c4_r1 ⑤、c4_r2 ②⑤⑥ 紅 |
| 格式字元不換 | c4_r2 ③ 紅 |
| 佔位字加回少一邊括號那一支 | placeholder_variants ③ 紅 |
| 閉括號改成選填 | ③ 紅 |
| 指令改回 `cut -d/ -f3`(不濾散檔) | **不紅**(F3) |
| 指令不濾現存目錄 | dirs_capped ③ 紅 |
| 查不到提交也給指令 | ⑤ 紅 |
| 呼叫端不傳 diff_text(提早離開失效) | 不紅;只影響速度、不影響結果,不另報 |

## 佔位字變體與 c4 目錄對應

- 改成「兩邊都要有括號」之後,整字面 `<卷證>`、`<sha>`、`<整項新內容>` 仍由前一道子字串檢查擋;全形、半全形混搭(`<卷證＞`)、括號內空白(含全形空白)、`<SHA>`、`＜sha＞` 都擋得住。拿掉的只有第二輪判成誤擋的單邊形狀。**沒有漏擋**原本該擋、兩邊都有括號的形狀。
- c4 目錄對應:同一個 NFC 鍵對到多個現存目錄時每個都列;磁碟上沒有、只在 git 有的不列;磁碟 NFD、git NFC 時印的是磁碟上的名字,而且跟計劃名那份合成一行「兩者」。三種都實測符合(另見上表還原結果)。

## 圖譜鏡頭固定席逐條判定

- [[Systems/存量漂移守衛]](家):TEST 行補了 t_drift_c4_code_review_r2,方法存在。WHY 說「指令跟證據頁同一套定義…數量對得上」,碰到 git 會加引號的名字時不成立(F2),其他敘述跟程式一致。
- [[Systems/bound-tests-gate]] ★INVARIANT★:沒動 code-loop check。計劃 [S1] [S5] 新綁的 t_drift_c4_code_review_r2、t_delguard_vendored_two_states 都存在,也都跑過(綠),不會懸空。不影響。
- [[Systems/guard-kill]] ★INVARIANT★(rc 優先序、--json 純度):這份 diff 沒碰 guard kill 的程式。不影響。
- [[Systems/授權與歸屬]] ★INVARIANT★:`_VENDORED_TOOLKIT` 和 `_VENDORED_TREE_FILES` 沒改,沒有把授權檔加進白名單。不影響。
- [[Systems/測試假綠形態]] ★INVARIANT★(還原翻紅釘要有前置斷言證明現場成立):新測試大多有前置斷言,也真的會翻紅。例外是 `t_drift_c4_dirs_capped_at_20` 的散檔那一條(F3):前置斷言成立,但被測的那道濾網被另一道蓋住,屬於這條合約描述的形態。
- [[Systems/lumos-cli-read]] ★INVARIANT★(search 排除 superseded):沒碰。不影響。
- [[Systems/lumos-cli-lifecycle]] ★INVARIANT★(re-inject 只改 sentinel 之間):沒碰。不影響。
- [[Systems/design-loop]] ★INVARIANT★(處置閘第五步):這份 diff 是代碼審的 .patch 審材,設計審的判定沒動;計劃的 [SN] 條款綁的測試都存在。不影響。
- 只列名的節點:
  - [[Systems/lumos-deinit]]:拆除形狀實測會跳過並記帳,跟「拆除刪的是工具自己的行」一致。
  - [[Systems/pitfalls-code-loop]]:推送前分級用的 `_vendored_skip` 沒動。
  - [[Systems/delguard]](不在清單上,但 diff 改了它):界線段說「只跳過改之前與改之後都是安裝原樣的」,跟程式一致;沒寫到 F1 的回收表不對稱,也沒寫到 F4 的時間界線。
  - 其餘(check-r、cochange、refcheck、slim 系列等):這份 diff 沒碰它們宣稱的行為。

最高等級:major
