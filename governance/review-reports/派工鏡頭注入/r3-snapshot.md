---
type: project
status: doing
created: 2026-09-03
updated: 2026-09-03
tags:
  - type/project
  - status/doing
  - scope/governance
related:
  - "[[Verification/2026-09-03_派工攔截點實測]]"
  - "[[Projects/impact鏡頭機械化_計劃]]"
  - "[[Projects/派工時自動補清單_計劃]]"
  - "[[Projects/code席爆炸半徑供糧_計劃]]"
  - "[[Projects/主動影響幅度偵測_計劃]]"
  - "[[Projects/impact-diff橋接_計劃]]"
  - "[[Systems/design-loop]]"
  - "[[Systems/retrieval-ranking]]"
summary: |-
  FLAG:DECISION
  KEY:★鏡頭不是閘★——★只限代碼迴圈★:派工詞含 `LUMOS-IMPACT: <base>..HEAD` 時,PreToolUse(matcher Agent)hook 把 impact --diff --json 的固定席附進派工詞(前 8 篇貼內容、其餘列名;0 篇不注入);不帶就逐位元原樣放行。不擋、不驗、不記帳、不量成效
  KEY:Enzo 裁(2026-09-03):散文審查的清單本質是鏡頭;可執行層(合約綁測試)已存在且只有它該是閘;★不要求鏡頭證明有用★
  KEY:r1(2026-09-03,3 席+架構+外家)38 條/blocking 26/2 條引句錨不到不採信/36 條全折(updatedInput 第二種做法折成 d2 有意識偏離,blocker 輪不放行)——三個 blocker 全折:①hook 進 ANCHOR_FILES(自己早上寫的硬約束,第二次差點撤掉)②待審分支檔名不得逐字注入(只列 base 已追蹤且字元白名單的檔,其餘只報數)③節點內容從 base ref 讀(git show <base>:<path>),分支新增的只列名
  KEY:憑什麼做得到=[[Verification/2026-09-03_派工攔截點實測]]:攔得到 Agent、updatedInput 改得了、子代理照單全收;追測二:additionalContext 只到派工者→updatedInput 是唯一通道(有意識偏離四支鄰居 hook,記 d2)
  KEY:★清單早就算得出來★(impact --diff --json 固定席四欄位);採用機制=代碼審模板 §3 第 3 格由「手貼固定席」改成固定一行標記,hook 補內容;★這仍是假設★不是證據(同格位 08-29 上線後 0 執行);REVISIT:2026-10-03 grep 派工單看標記出現率(查有沒有被用,不是有沒有用)
  KEY:r2(21 條/blocking 16/4 blocker,全折)立下★消毒原則=來自圖譜或 diff 的自由文字零輸出★:只印固定字彙(合約類別/kind)、base 已追蹤路徑(ls-tree 帶 quotePath=false)、base 版合約行;`contract` 後綴/`matched_by`/一句話層全不印;分支新增節點連名字都不列;base 必須主線可達(merge-base --is-ancestor)否則放行;清單本身仍用工作樹算=能藏不能說(界線)
  KEY:三個登記點=_GLOBAL_CLAUDE_HOOKS/HOOK_ENTRIES/enforcement 寫死的四元組+ANCHOR_FILES(加交叉測試、同步 anchor-integrity「5 錨點」);檔名 dispatch-lens-hook.py;repo=CLAUDE_PROJECT_DIR→cwd;標記正規式 ^LUMOS-IMPACT:\s*(\S+)\s*$;外層 60s 內層 45s;快取鍵 sha 必過 ^[0-9a-f]{40}$ TTL 20 分鐘
  KEY:誠實界線=永遠不知道有沒有用/錨點只罩 repo 那份不罩家目錄那份/大 diff 超時就靜默放行(LUMOS_HOOK_DEBUG 才印)/綁 2.1.259/本機所有專案每次派工都 fire
decisions:
  - content: 開案:鏡頭版——標記觸發、固定席、d9 截斷、既有合併器安裝、fail-open;不擋不驗不記不量。動工前唯一實測=additionalContext 到不到得了子代理
    id: d1
    context: 2026-09-03 五份計劃全死於設計審(收斂閘漏項敏感度 v1/v2、派工時自動補清單、審查帳節點映射、折入去重留痕),四份死在想證明清單有用(量覆蓋率/記映射/對照組/指紋)。Enzo 裁:散文級要化成測試不切實際,清單當單純鏡頭讓 subagent 考慮相關節點面向就好
    why_chosen: 存活事實三件(攔得到/清單算得出/沒人貼)剛好拼成鏡頭版;砍掉量測支線後,五份計劃二十幾條 blocker 只剩三條仍適用(措辭中性/用既有合併器/誠實揭露無防篡改)。代價=永遠不知道有沒有用,Enzo 接受
    decided: 2026-09-03
    valid: true
  - content: r1 折入兩條有意識偏離:①本 hook 進 ANCHOR_FILES——scripts/hooks/claude/ 第一支被錨的檔,新類別;②用 updatedInput 改寫派工詞——四支鄰居 hook 只用 additionalContext,本案偏離
    id: d2
    context: r1 四席一致 blocker:自己早上在 2026-09-03_派工攔截點實測 寫的「改寫派工詞的 hook 必須進錨點,硬約束」被首版當鄰居慣例撤掉(同日前案死因⑥重演);架構對齊席判 updatedInput 為專案第二種做法(major)
    why_chosen: 錨點:硬約束成立的原因(改得了派工詞)只在本案成立、對只注入上下文的鄰居不成立,對照組選錯;錨點只罩 repo 份不罩家目錄份,寫成界線不再帶過。updatedInput:追測二實測 additionalContext 只到派工者、子代理收不到,改寫輸入是唯一通道;放行條件=永不 deny+進錨點
    decided: 2026-09-03
    valid: true
---
> 白話:代碼審派審查員的時候,規矩要求把「這批改動碰到哪些帶合約或出過事故的筆記」貼進派工詞——實帳沒人做到。本案在派子代理那一刻,由 hook 把機器算好的那份清單**附**進派工詞。★它是鏡頭,不是閘★:不擋、不驗、不記帳、不量成效。成不成功只看一件事——派工詞裡真的多了那段。★只限代碼迴圈★(設計迴圈審的是計劃筆記,沒有 diff 範圍,d9 也明寫維持原樣)。

PRIOR-ART: ① 最小解層級——攔截點、清單算法、截斷規則、安裝器全是既有的:`PreToolUse` hook(本 repo 已有一支同事件、不同 matcher 的 `impact-hook.py`:它掛 Edit|Write,本案掛 Agent)、`lumos impact --diff --json` 的固定席、[[Systems/design-loop]] d9 的「截錄」規則(cap 值沿 `_print_sync_nudge` 的預設 8)、`scripts/merge-claude-settings.py`、鄰居的 TTL 冷卻窗形態。本案自己寫的只有一支 hook 腳本、一段注入措辭、兩處模板改字。② 世界解過沒——「先把該查的列出來、再讓判官逐條看」是 [arXiv 2608.31016](https://arxiv.org/abs/2608.31016) 量到唯一有效的補救(找漏 25%→37%;數字轉引自 [[Projects/收斂閘漏項敏感度v2_計劃]] 與 2026-09-03 治理日報,本案未重讀論文),其餘(換措辭/多席/提示詞優化)全部無效;而★它只是輔助,清單在眼前判官仍漏六成★——所以本案定位為鏡頭。③ 裁定=borrow-design,零依賴。

## 一句話

★代碼審派工詞帶標記時,hook 把固定席節點附上去;不帶就逐位元原樣放行。★

## 為什麼是鏡頭,不是閘(今天五份計劃的結論)

2026-09-03 五份計劃全死在設計審,四份死在「想證明它有用」——量覆蓋率、記映射、做對照組、定指紋。存活的事實只有三件:
- ★攔得到★:[[Verification/2026-09-03_派工攔截點實測]]——`PreToolUse` 匹配派子代理(`tool_name`=`Agent`)、拿得到派工詞全文、`updatedInput` 改得了、子代理照單全收;追測二:`additionalContext` 只到派工者,子代理收不到。
- ★清單早就算得出來★:`lumos impact --diff --json` 的固定席(`pinned: true`;帶硬合約或出過事故的節點),每篇有 `kind`(直接相依/其他)、`contract`(合約種類)、`files`(被哪個檔牽連)三個結構欄位——hook 讀 JSON,不 parse 文字版。
- ★沒人貼★:規則 2026-08-29 上線後唯一一個迴圈、編排者=規則作者本人、次日,零執行([[Projects/code席爆炸半徑供糧_計劃]])。

Enzo 裁(2026-09-03):散文審查的清單本質是鏡頭;可執行那層(合約綁測試、推送前真跑)已經存在且只有它該是閘;★不要求鏡頭證明自己有用★。

## 範圍:只有代碼迴圈(r1 折入)

- d9(2026-09-01)逐字:「code 迴圈固定席以落成核對 capped 節錄為準……design 迴圈維持原樣(pinned 集小)」。截斷規則只給代碼迴圈;本案套用 d9 就只能在代碼迴圈。
- 設計迴圈審的是計劃筆記工作副本,沒有既定 git diff 範圍;r1 兩席實跑 `HEAD..HEAD` 回空。硬塞標記=標記在、鏡頭永遠不注入。
- 所以:標記只進代碼審模板(§3);設計審模板(§1)★不動★。§7.6 架構對齊席是兩種迴圈★共用一格★(r2 三席抓到「代碼改標記、設計不動」照字面做不到)→那格改成兩支明寫:「代碼迴圈:一行 `LUMOS-IMPACT: <base>..HEAD`;設計迴圈:維持手貼固定席」。

## 對現行裁定的處置(四條,全部不繞過)

1. **`impact --diff` 聚合版「不接 hook」**(`Systems/retrieval-ranking:51`、[[Projects/impact-diff橋接_計劃]]):理由=非固定席那層無機械保證、靠審查員兜。★本案只附固定席★,落在它明說有保證的那層;且本案不是閘,不承擔「兜」的角色——審查員仍在場。
2. **[[Systems/design-loop]] d9**(2026-09-01):「上限內貼內容必答、超出列名不必答」;d9 只訂「截錄」,上限值 8 是 `_print_sync_nudge` 的預設,本案沿用同一個數。★只在代碼迴圈採用★(見〈範圍〉)。
3. **錨點:★本 hook 進 `ANCHOR_FILES`★**(r1 四席一致 blocker)。理由是自己早上寫的:[[Verification/2026-09-03_派工攔截點實測]]——「這個機制與提示注入在技術上是同一件事,差別只在善意……該 hook 本身必須進錨點保護清單,這一條是硬約束,不是提醒」。首版寫「比照鄰居不進 anchor」是選錯對照組:鄰居 `impact-hook.py` 只注入上下文、改不了派工詞,硬約束對它不成立、對本案成立。這是 `scripts/hooks/claude/` 第一支被錨的檔(既有五錨=兩支測試 runner+三支 git hook),屬新類別,記 d2。★錨點只罩 repo 裡那份★:裝進 `~/.claude/hooks/` 的副本在機制外,能改家目錄的人本來就能做任何事——這條不再用「鄰居也沒進」帶過,直接寫成界線。
4. **[[Projects/主動影響幅度偵測_計劃]]:同位置 hook「永不 block」**:★比照★,本案永不回 deny。差別=本案用 `updatedInput` 改寫派工詞,四支現役 hook 只用 `additionalContext`——架構對齊席判「第二種做法」(major),★折成有意識偏離★:追測二實測 `additionalContext` 到不了子代理,改寫輸入是唯一通道;這是有意識偏離,記 d2,不是沒看到。

## 為什麼不是「不寫 hook」(r1 簡化席問的)

- 候選 A「只改模板、由編排者手貼」:就是 d8 現制,08-29 上線、次日 0 執行。死因不是內容算不出,是「跑指令→讀→貼」三步落在編排者(一個 LLM session)身上,任何一步省略清單就沒了。
- 候選 B「`lumos loop next` 直接印好可貼區塊」:少了「跑指令」一步,仍剩「貼」——同一個失敗類。
- 本案:編排者只要模板裡那一行標記還在(照模板派工=標記自然在),內容由機器補。★這仍是假設★:「一行固定文字比三步好留」沒有證據,只有結構差異;所以驗收不驗有用,回頭條件驗「有沒有被用」(見〈誠實界線〉REVISIT)。
- 代價:一支對本機所有專案每次派子代理都 fire 的 hook(不帶標記時只做一次字串比對就放行)、一個新的錨點類別。

## 設計

1. **觸發**:`PreToolUse`,matcher `Agent`(早上實測用 `Agent|Task|Subagent`,2.1.259 實際 `tool_name` 是 `Agent`;另兩個是保險,本案只留實測到的那個)。派工詞含一行 `LUMOS-IMPACT: <base>..HEAD` 才動作;沒有就逐位元原樣放行(`{}` 或不輸出)。★標記文法定死★(r2:文法沒定,差一個空白就靜默不注入):逐行比對正規式 `^LUMOS-IMPACT:\s*(\S+)\s*$`,取第一個命中;範圍不含 `..` 或以 `-` 開頭→放行。REVISIT 那條 grep 用同一個正規式。★範圍由標記明寫,不從散文猜;`--repo` 比照四支鄰居:先 `CLAUDE_PROJECT_DIR` 環境變數、再 hook payload 的 `cwd`★(省略 `--repo` 時 `impact --diff` 只從 hook 行程 cwd 往上找,cwd≠目標專案就查錯 repo)。
2. **清單**:`lumos impact --diff <範圍> --repo <cwd> --json`,取 `pinned: true`;★剔除 `files` 全落在 `governance/review-reports/` 的節點★(d8 記在案的已知污染源:凍結快照 patch 是審計證物,impact 沒排除、會頂到滿分;手貼時靠人眼剔,本案機器剔)。剔完 0 篇→★不注入、prompt 逐位元不變★(比照鄰居「皆空不輸出」)。★base 必須是主線可達的 commit★(r2 外家:標記左側填分支上任一 commit,主線讀取就形同虛設):`git rev-parse --verify <base>^{commit}` rc≠0 或輸出不是 40 位十六進位→放行;再 `git merge-base --is-ancestor <base> <主線 tip>`(主線 tip=`refs/remotes/origin/HEAD` 解析到的分支,沒有就本地 `main`/`master`)不成立→放行。★固定席「清單」本身仍用工作樹圖譜算★(impact 載入工作樹 vault):分支作者能改關係讓某節點不被釘=「藏」,藏的結果等於今天沒 hook 的狀態;能「說」的通道全部封在下面 3–5 條——這是界線,寫進〈誠實界線〉。
3. **內容來源=base ref,不是工作樹**(r1 blocker):前 8 篇貼內容,內容用 `git show <base>:<repo 相對路徑>` 讀★base 那版★(base=標記左側)。★`--json` 的 `node` 是圖譜相對路徑★(r2 三席實跑:直接代入 `git show` 全部失敗、每篇都會被誤判「分支新增」)→repo 相對路徑=`docs/<slug>-knowledge/` + node,圖譜根沿 lumos 既有慣例找 `docs/*-knowledge/`(不只一個→放行)。節點在 base 不存在(本分支新增)→★連名字都不列★,只報「另有 N 篇本分支新增節點未列」(名字本身就是注入管道)。理由:工作樹的圖譜筆記是待審分支的一部分(鐵則 1 逼改 code 必改筆記),分支作者可控;base 是主線,不可控。
4. **消毒原則:★來自圖譜或 diff 的自由文字零輸出★**(r1 blocker 只擋了 `files`;r2 載荷席實跑抓到 `contract` 欄位會把 `risk/<任意文字>` 標籤逐字印成 ★RISK·任意文字★、事故節點的 `matched_by` 是觸發字串原文且永遠排最前)。hook 輸出只允許三種東西:①固定字彙表——`kind` 與 `contract` 只印類別(INVARIANT/IRREVERSIBLE/CHECKPOINT/RISK/事故),類別後的文字一律丟;`matched_by`、摘要、一句話層★完全不印★;②★base 已追蹤的路徑★——`files` 與節點路徑只列出現在 `git -c core.quotePath=false ls-tree -r --name-only <base>` 裡的(r2:沒帶 quotePath 中文檔名全被轉義、白名單永遠不過——impact 自己修過同一坑),長度 ≤200;base 是主線,所以主線有的名字就是可信的,不再另設字元白名單(r2:字元白名單會把含空白的合法檔名靜默剔掉);其餘只報「另有 N 個本分支新增/改名檔未列」;③base 那版節點的合約行(`git show` 出來的正文裡以 ★INVARIANT★/★IRREVERSIBLE★/★CHECKPOINT★ 開頭的行)。★定序★:對每個 pinned 節點先問「repo 相對路徑在 base 樹裡嗎」——在:列名、貼內容(前 8 篇)、列 base 已追蹤的 files;不在:只進「未列」計數,後面的檢查都不跑。
5. **截斷**:前 8 篇貼內容(節點名+`kind`+`contract` 類別+base 已追蹤 `files`+該節點 base 版的合約行),其餘只列名。單篇內容上限 40 行(合約行優先),整段上限 400 行,超出截斷並標「已截」。★code-loop SKILL 第 19 行現制是三層(貼內容/前 10 篇「列名+一句話」/純列名),本案有意砍掉中間的一句話層★——一句話=節點摘要=自由文字=注入管道;同步 SKILL.md 時明寫這是砍層不是漏寫。
6. **措辭**:純文字條列(比照四支鄰居的注入格式,不用 Markdown 標題+方括號代號),固定第一行 `lumos 自動附加:本次改動的固定席節點(來源 impact --diff,只供參考)`。★不用命令式、不用「暗號」型措辭★(實測會被子代理指認為提示注入而拒答)。★這個標頭配 `updatedInput` 的組合尚未實測★(追測二測的是 `additionalContext`)——列入驗收第一條。
7. **時間預算與快取**:外層 `HOOK_ENTRIES` 宣告 60 秒、內層 subprocess 45 秒(必須外>內:本 repo 栽過內 20>外 10,見 [[Projects/enforcement儀表板_計劃]])。實測本 repo 單 commit 12 秒、41 檔 17.7 秒、更大 35 秒;同輪多席會對同一範圍重算——★快取★:鍵=(repo 根, base sha, HEAD sha),兩個 sha 都必須通過 `^[0-9a-f]{40}$` 才能當檔名(r2:rev-parse 失敗時會把輸入原樣吐到 stdout,含斜線點號,直接拿去拼檔名=路徑注入),檔名=三者串起來的 sha256;存 `$TMPDIR/lumos-dispatch-lens/<sha256>.json`,寫暫存再 rename;TTL 20 分鐘(沿鄰居 `_ttl_should_inject` 形態),同輪只有第一席付錢。★大 diff 超時=靜默放行★,這是接受的界線(見〈誠實界線〉)。
8. **失敗一律放行、預設靜默**:算不出、超時、不是 git repo、base 解析不到、lumos 不在——原樣放行;比照鄰居「技術性失敗純靜默」,只有 `LUMOS_HOOK_DEBUG=1` 才在 stderr 印一行(白話三段式)。
9. **安裝三個登記點+錨點**:檔名 dispatch-lens-hook.py、住 scripts/hooks/claude/ 目錄(沿 -hook.py 慣例——四支現役有三支如此,check-graph-sync.py 例外;將建,現在還不存在);①`_GLOBAL_CLAUDE_HOOKS` ②`merge-claude-settings.py` 的 `HOOK_ENTRIES` ③★`lumos enforcement` 寫死的四元組★(`scripts/lumos` 約 12109 行;它不讀 ①,漏了就是「根本沒查」而非「查了沒事」;連帶 `t_enforcement_never_raises_on_missing` 釘死的列數要改)④`ANCHOR_FILES` 加一行並 `lumos anchor approve`;★加一條測試交叉核對 `ANCHOR_FILES` 與 `governance/anchor-baseline.json` 的鍵集合相等★(r2:兩者現在沒有任何測試互證,錨點修復可以落地卻沒真保護);⑤同步 [[Systems/anchor-integrity]](它寫死「5 錨點=runner×2+hooks×3」,本案是第 6 個、新類別)。不自造流程、不引入外部二進位、不用 jq。
10. **不做**:不 deny、不驗證審查員有沒有讀、不記治理帳、不量成效、不碰設計迴圈。

## 跟既有手貼格的關係(r1 兩席問的:取代,不是疊加)

- 代碼審模板 §3 第 3 格「圖譜鏡頭」(d8 手貼固定席、含兩條填寫雷)→★改成只放一行 `LUMOS-IMPACT: <base>..HEAD`★,填寫雷①(審計證物污染)由 hook 機器剔、雷②留字。
- 代碼迴圈的架構對齊席 §7.6「圖譜裡相關功能筆記」那格→同一行標記。
- `lumos-code-loop/SKILL.md` 第 19 行對同機制的摘要句→同步改字(templates 改了摘要沒跟=本 repo 記過的「知識同步散落會漏」形態)。
- 設計迴圈 §1/§7.6★不動★。
- 一份派工詞只會有一份固定席清單:標記在、hook 補;編排者不再手貼。

## 驗收(三條,全機械)

1. **正向**:挑一個★已知有固定席的範圍★(例 `c3b4f3f~1..c3b4f3f`,實測 12 釘),派工詞含標記→子代理收到的 prompt 含固定第一行與 ≥1 篇固定席,且子代理沒有拒答(哨兵實測法,同早上)。這一條同時驗〈設計〉6 的標頭組合。
2. **零篇**:挑一個沒有固定席的範圍→prompt 逐位元不變。
3. **反向**:不含標記的派工→prompt 逐位元不變。
★不驗收「有沒有用」★——那是另一條線,今天已裁不走。

## 誠實界線

- ★本案永遠不會知道自己有沒有用★。Enzo 裁:先給鏡頭,要量等迴圈自然累積資料再說。
- 「模板一行標記會被留著」是假設,不是證據(同格位手貼 0 執行)。
  REVISIT:2026-10-03 對 `governance/review-reports/*/r*-dispatch.json` 與派工詞留痕 grep `LUMOS-IMPACT:`,出現率為 0 就承認標記也留不住,停案;這是查「有沒有被用」,不是查「有沒有用」。
- 注入內容=固定字彙+base 已追蹤路徑+base 版合約行,零自由文字;信任等級=主線可寫的人。
- ★固定席「清單」用工作樹圖譜算★:待審分支能「藏」節點(改關係讓它不被釘),不能「說」;藏=退回今天沒 hook 的狀態。要連藏都擋要用 base 版圖譜算清單,本案不做(要另開 worktree,成本翻倍),寫成界線。
- 錨點只罩 repo 裡的 hook 檔,不罩 `~/.claude/hooks/` 的安裝副本。
- 大 diff 可能超時→靜默放行,最需要鏡頭的那批反而最容易掉;快取只救同輪重算,不救單次太慢。接受,因為替代是阻塞派工。
- 綁 Claude Code 2.1.259;動工前重跑攔截實測。
- 裝上後對本機所有專案的每次派工都 fire(不帶標記只做一次字串比對)。

## 未解(動工前要答,不需審查席)

1. `git show <base>:<path>` 的 base 在 shallow clone / base 不在本地時解析不到→放行;要不要退回工作樹版並標「未消毒」?★預設不退,寧可沒有★。

## 實務隱患(逐類答)

- **self-governance**:改的是治理流程。緩解=不動閘、不記帳、fail-open;新增=一支 hook、兩處模板改字、一個錨點。
- **併發**:同輪多席同時派→多個 hook 行程同時算同一範圍;快取檔用「寫暫存再 rename」原子換,重算只浪費不出錯。
- **效能**:單次 12–35 秒實測;快取後同輪一次;不帶標記時 O(字串比對)。
- **回滾**:無持久狀態(快取在 TMPDIR,可整目錄刪)。拆=從三個登記點移除+`ANCHOR_FILES` 移除並 approve+模板那一行改回手貼;沿既有 hook 退役慣例兩階段:先進 `_RETIRED_STUB_CLAUDE_HOOKS`(留空殼),下一版才進 `_RETIRED_CLAUDE_HOOKS`(刪檔)——是兩個不同常數(r2 架構席:首版寫成一個,照字面會加錯)。
- **安全**:改寫派工詞=與提示注入同構;緩解=錨點(repo 份)、內容從 base 讀、檔名白名單、不用命令式措辭。沒有機械防篡改家目錄副本(界線)。
- ★沒有機械守衛的部分★:編排者自己寫派工詞不照模板,標記就不在——鏡頭的本性,回頭條件見 REVISIT。

## 審計修正紀錄(lumos-design-loop)

- r1(2026-09-03,3 席+架構對齊+外家 Codex):38 條(9+9+10+4+6)/blocking 26(5+7+7+1+6)/三個 blocker(錨點硬約束、檔名逐字注入、筆記內容來自待審分支)全折,引句錨不到的 2 條不採信(s2-f3、s3 一條,內容與他席重複);其餘 36 條全折(架構席「updatedInput 第二種做法」折成 d2 有意識偏離;blocker 輪 accepted 必空,不走放行);範圍縮到代碼迴圈、三個登記點、快取與時間預算、手貼格改標記。★blocking 密度超過 skill「建議整份重寫」門檻,編排者判核心未被推翻、在同編號折入,重寫與否留 Enzo 裁★。
- r2(2026-09-03,3 席+架構對齊+外家 Codex,火力只掃 r1 新段落):21 條(5+4+5+2+5)/blocking 16(2+3+5+1+5)/4 blocker(圖譜路徑要接 docs/<slug>-knowledge 前綴、`contract` 與 `matched_by` 是自由文字注入管道×2、§7.6 共用格改一半);全折,1 條引句錨不到不採信(外家 f4「base 未驗證」,內容照折)。折入=自由文字零輸出原則、base 必須主線可達、標記文法定死、quotePath、錨點交叉測試、砍一句話層。
- 席報告與收貨:`governance/review-reports/派工鏡頭注入/`(r1-*/r2-* 席報告、rN-intake、rN-dispatch.json、rN-snapshot、r2-delta.diff)。
