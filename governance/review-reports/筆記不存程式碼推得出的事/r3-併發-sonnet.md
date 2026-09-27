severity: major

# 審查範圍與方法
逐節讀完 r3-work.md(130 行)、對照 r3-delta.patch(相對 r2 的差異)、並在 clone-ns 這份程式碼裡逐一開檔驗證 spec 提到的每個函式/常數/掛鉤/CI 步驟/圖譜節點是否存在、語意是否相符。對「資源併發」鏡頭額外做了一次可重現的本機實驗(見 F4 前的併發鏡頭段落),用來驗證 spec 自己宣稱的「治理帳兩筆同時寫黏成壞行時只會多擋、不會放過」這句話。

# 逐節記錄

## 開頭白話 / 依據 / 拆分紀錄 / PRIOR-ART / RETIRE-IF / REVISIT
已讀。三則交叉引用檔案都存在:`docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md`、`docs/lumos-toolchain-knowledge/Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md`、`docs/lumos-toolchain-knowledge/Systems/外部對照-code衍生wiki.md`。PRIOR-ART 提到的「代碼審留痕綁提交祖先鏈,壓提交或 rebase 後失效」在 `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md` 裡有 2026-09-22 那類事故紀錄佐證(rtb 回饋一節有多筆同形狀 PITFALL)。PRIOR-ART③「兩支的家都是 [[Systems/筆記內容閘]]」有事實錯誤,見 F1。

## 判定者能不能用:小實驗
已讀,無 finding。68 句、opus/sonnet 對照表與上一版(r2)一致,只多了「claude 用 opus、Codex 用同一家審查席模型」一句(呼應〈做法〉第二層第 2 點,已核對一致,見下)。

## 做法 / 哪些行要審(借第一層,不另寫)
- 「①」段(用推送前掛鉤字樣判上線)與程式碼吻合:`_nodehome_golive`(`scripts/lumos:22943`)目前寫死只查 `scripts/hooks/pre-commit`(`scripts/lumos:22947`:`"--", "scripts/hooks/pre-commit"`),但已經有 `mark` 參數可換標記字串;spec 說「加一個看哪支掛鉤的參數」,精確對上這支函式現在缺的正是「檔案路徑」這一半,不是無中生有——已讀,無 finding。
- 「②」done 計劃整篇正文與 d2/d4 呼應,已讀,無 finding。
- 「直接借第一層」這句本身有兩個問題:一是家的歸屬錯誤(F1),二是「不另寫」在 S6 的「列出每一處」上不成立(F2)。

## 通過紀錄怎麼綁:逐行,不綁整批
已讀。跟 `lumos lint-waive` 的內容指紋放行(`scripts/lumos:20572` `cmd_lint_waive`、`scripts/lumos:21446` `_lint_waivers_add`)語意一致:那邊放行「綁指紋不綁版本」是真的,但那支函式的讀-改-寫需要呼叫端上鎖(`_vault_write_lock`,`scripts/lumos:21452`)。note-audit 用的是純 append(`_gate_event`),沒有讀-改-寫的遺失更新風險,兩種機制的鎖需求本來就不同——spec 沒有把這個原因寫出來,但沒有寫錯,不算 finding。

## 第二層:推送前的筆記內容審(`lumos note-audit`)
逐條核對:
- prepare 的 `--orchestrator claude|codex` 必填、猜錯家族即事故的說法,在既有 `--orchestrator` 校驗(`scripts/lumos:7699` `cmd_canary` 對 `orchestrator` 的擋法、`scripts/lumos:7821-7837`)裡有直接對應先例(定錨後不能中途換家)。已讀,無 finding。
- `_write_lf` 是真的暫存檔換名寫入(`scripts/lumos:14146` 定義,`scripts/lumos:14190` 等多處使用)。已讀,無 finding。
- `.lumos/note-audit/` 的 gitignore 與初始化忽略設定:F3。
- 派審查員段的四句與 `judge_prompt.md` 存在性:`governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md` 確實存在。已讀,無 finding。
- `_gate_event`(`scripts/lumos:856`)是真的通用寫入器,`_KNOWN_GATES`(`scripts/lumos:6599`)裡還沒有 `note-audit`,但 spec 自己在做法第 5 點寫了「登記進既有閘名單」,這件事有被涵蓋,不算遺漏。
- check「跟 `home check` 同形狀」:`scripts/hooks/pre-push:237-238` 確實有 `"$PY" "$GRAPHCTL" home check --diff "$_hrange"...`,note-shape 緊接著在下面(`scripts/hooks/pre-push:247`)用同一段範圍再查一次——形狀吻合。已讀,無 finding。
- 出口(skip / gate 開關 / 環境變數)與 doctor 提醒:跟 `_note_shape_doctor_lines`(`scripts/lumos:23862`)、`_note_shape_config`(`scripts/lumos:23480` 附近)的 block/warn/off 叫法與「不是 block 就印一行」的先例吻合。r2 的鏡像核對已經抓到「check 每次放行也要寫 skipped 事件」跟 note-shape 本身「off 不寫、warn 沒違規不寫」不是同一套,但 spec 給了獨立理由(不讓關掉的專案從 RETIRE-IF 消失),屬於刻意背離、非矛盾。已讀,無 finding。
- 消費專案 CI:`_VENDORED_TOOLKIT` / `_VENDORED_TREE_FILES`(`scripts/lumos:16903-16922`)裡確實沒有 `.github/workflows/ci.yml`,但有 `scripts/hooks/pre-push`——跟 spec 說「ci.yml 要手改、pre-push 靠 lumos update 拉」的不對稱完全吻合。已讀,無 finding。

## 上線前校準 / 規範文字跟著改
已讀,無 finding。

## 條款 S5–S17
- S6「重複文字應列出每一處」:F2。
- S17「行集合應等於第一層算出的新增行」在概念上與 F1 無衝突(equality 是就 (path,text) 這個粒度而言,`_ns_range_added` 回傳的 set 本身足以拿來做集合相等比對;F2 只影響「列出每一處行號」這個顯示需求,不影響 S17 的集合相等測試)。已讀,無 finding。
- 其餘 S5、S7–S9、S11、S12、S14–S16 逐條核對過用到的既有機制(`_gate_event`、`_note_shape_config`、`--orchestrator` 家族鎖定)都存在且語意相符。已讀,無 finding。

## 回退
「note-audit 指令改成只印『已撤除』並回 0、永久保留」有精確先例:`docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:82` 寫的就是同一句話(note-shape 版),而且程式裡也有同款「已撤除 hook 的相容期空殼」慣例(`scripts/lumos:17728` 附近)。已讀,無 finding。

## 實務隱患 / 誠實界線
見下方鏡頭段落與 F1–F3。

## 審計修正紀錄
只做鏡像核對用途讀過,未展開查核 r1/r2 卷證內容(依指示只讀 r3-work.md 與 r3-delta.patch,不讀 governance/review-reports 底下其他檔)。

---

# 資源併發鏡頭(逐情境作答)

1. **兩個會談同時 prepare**:清單檔以「待審集合指紋」命名 + `_write_lf` 原子換名(`scripts/lumos:14146`),兩個會談算出同一個待審集合時寫同一個檔名、內容相同,不會互蓋出壞內容;算出不同集合時檔名不同,互不干擾。已讀,無 finding。

2. **兩個會談同時 record,治理帳兩筆同時寫黏成壞行**——這是本鏡頭要求特別驗證的一句話(「只會多擋、不會放過」在「壞行吃掉的是 skip 或通過紀錄」以外的情形是否仍成立)。實測:
   - 用 `_gate_event` 的寫法原樣重建(`open(path,"a",encoding="utf-8"); f.write(json.dumps(ev)+"\n")`),起 6~8 個平行行程、每行程寫 30~40 次、每筆事件放大到 400~2000 個內容編號(≈2.6KB~26KB/行,對應 spec 自己說的「一次推送幾十到幾百個」乃至「計劃轉 done 時可能上千行」的量級),總計數百次併發 append,對輸出檔逐行 `json.loads`。結果:240 行全部是合法 JSON,零壞行(macOS/APFS)。
   - 結合既有讀取端的慣例(`_codeloop_read_from_ledger`,`scripts/lumos:29358-29394`:逐行 `json.loads`、`except Exception: continue`)——這是本 repo 讀治理帳的既有寫法,`_gate_event` 沒有另開一套。壞行(不論是位元組交錯還是行程被砍半途留下沒有換行的殘段)幾乎必然讓 `json.loads` 拋例外而被整行跳過;要讓交錯後的位元組串「碰巧」還能解析成合法 JSON、而且欄位語意剛好對得上,機率上接近不可能(需要兩段獨立寫入在字元邊界上重組成另一個合法物件)。跳過=那筆通過紀錄視同沒寫=check 對那些內容編號判「沒被涵蓋」=擋。也就是說,壞行只可能讓「本來該通過的」變成「暫時被擋」,不會反過來讓本來沒審過的內容被誤判成「已涵蓋」——**這句話成立,而且成立的範圍不只「吃掉一筆 skip 或通過紀錄」,也涵蓋「同時波及同檔案裡其他閘(code-loop、pitfalls…)事件」的情形**,因為所有讀取端都是同一套「解析失敗即跳過」的防線,不分閘名。
   - 但這個結論建立在「單次 `f.write()` 呼叫在作業系統層級對同一個 append 檔案是原子的」這個沒有被 POSIX 正式保證、只是本機/多數本地檔案系統慣例支持的前提上(本實驗只驗證了 macOS/APFS;CI 常見的 Linux/ext4、以及大到超過單一 write() 呼叫緩衝上限的紀錄,理論上仍有極小機率被拆成兩次系統呼叫而露出交錯窗口)。spec 的〈誠實界線〉與〈實務隱患〉都沒有把這個前提寫下來當成需要 REVISIT 的假設——這是可以補強但不構成阻擋的觀察,不單獨列 finding(拿不出具體會失敗的輸入,只是指出前提沒寫明)。

3. **審查中途作者又改筆記**:done。改過的行文字不同 ⇒ 內容編號不同 ⇒ 舊編號永遠不會被涵蓋(自然消失),新編號要重審——`prepare` 重跑會抓到。已讀,無 finding。

4. **CI 讀到的治理帳版本跟本機推送前讀到的不同**:spec 明訂 check 一律讀「被推送的那個頂端提交」裡的治理帳,不讀工作樹。本機 pre-push 在 push 之前,提交物件已經存在本機 git object store,可以用 `git show <本地將推送的 sha>:docs/.governance-log.jsonl` 讀到跟 CI(乾淨 checkout 同一個 sha)完全一致的位元組——這條路徑在既有程式碼裡有直接先例:`_codeloop_read_from_ledger` 讀的就是 tracked 的 `docs/.governance-log.jsonl`,而 `docs/.gitignore`(`scripts/lumos:17347-17351`)特別註記「治理帳刻意不在忽略清單裡,因為 CI 靠它讀留痕」。已讀,無 finding。

5. **record 寫完治理帳、提交之前,別人先推了也改了治理帳(合併衝突、rebase 後通過紀錄還在不在)**:`docs/.governance-log.jsonl` 是純 append-only 的 JSONL,兩條分支各自在檔尾之後接著寫,git 的三方合併/rebase 對「雙方都只在同一個共同基底之後新增內容、沒有互相刪改」這種形狀,標準行為是兩邊都保留、不需要人工解衝突(差異只在最終檔案裡兩批新行的相對順序,不影響以內容編號查表的語意)。這條路本身沒有現成程式碼可以核對(note-audit 尚未實作),屬於設計推演;沒有找到會导致真的衝突或憑證消失的具體情境,不硬湊 finding。

6. **代碼審通過紀錄與這份通過紀錄都要提交時的先後順序**:兩者都是對 `docs/.governance-log.jsonl` 的獨立 append,閘名不同(`code-loop` vs `note-audit`),讀取端各自用「gate 欄位 + kind ∈ passed/skipped」過濾(`scripts/lumos:29377-29387`),互不干擾;唯一的實務順序限制來自 CLAUDE.md 自己的提交紀律(代碼審通過只能單獨開一個「chore(lumos): 記錄代碼審通過」提交,note-audit 通過紀錄要跟功能改動同一個提交),spec 的〈鐵則〉小節有覆蓋到「凍結判定併進功能提交」但沒有明文重複這條——這在 CLAUDE.md 既有規則裡已經講過,不算 spec 自己的洞。

---

# 其他風險類(逐類簡答)

- **對外送出/供應鏈**:限定判定者跟編排會談同一家、不派外家席,已有明文;唯一沒被點名的子風險是「筆記內容本身可能含 prompt injection,企圖讓判定者把推得出的行判成脈絡」——這個風險的爆炸半徑已經被 RETIRE-IF②(月抽樣仍有一成以上程式碼推得出來就重想)與申訴機制間接框住,沒有找到會讓它完全失控的具體路徑,不單獨列 finding。
- **權限/存取控制**:decision-amend 只准改「所有遠端追蹤參照都沒有」的決策編號,拒絕已推上遠端的——這條路目前沒有程式碼可比對(新指令),邏輯本身自洽,不再重複列 S12 的合理性。
- **不可逆性 / 金流**:spec 自己已排除且理由成立(擋在推送前、提交仍在本機),已讀,無 finding。

---

# F1 家歸屬錯誤:PRIOR-ART 與〈做法〉把範圍/上線點/合併演算法的家寫成 Systems/筆記內容閘

severity: major
blocking: 是 —— 這是可核對出錯的節點歸屬事實(不是判斷分歧),而且違反本專案自己的鐵則五(每支檔有家:改到的檔要寫回正確的家),會誤導實作與未來寫回落點。

spec 位置:依據段的 PRIOR-ART(「③第一層筆記形狀擋([[Systems/筆記內容閘]])的「範圍裡哪些筆記行是新寫的」整套算法」)與〈做法〉「哪些行要審(借第一層,不另寫)」第一句。

引句:「兩支的家都是 [[Systems/筆記內容閘]]」

問題:spec 把「範圍裡每個提交各自新增的筆記行」這支函式(即 `_ns_range_added`)算成 `Systems/筆記內容閘` 的家產,但 `筆記內容閘` 這篇筆記自己明文寫著範圍演算法不是它的家:

file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:40`
該行原文:「這篇管 `scripts/lumos` 裡的 note-shape 子指令...範圍、上線點、合併的算法本身的家是 [[Systems/每支檔有家]]」

而 `Systems/每支檔有家` 自己也明文認領這件事:

file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:53`
該行原文:「它借了這道的新分支起點算法、上線點截斷與合併處理——上線點與合併的兩支函式加了參數、拆出一支,這道自己的行為不變...它管的是筆記內容的形狀,不是檔案歸屬,細節見 [[Systems/筆記內容閘]]。改這道的範圍、上線點或合併判法時,記得那邊共用同一套。」

程式面也對得上:`_nodehome_golive`/`_nodehome_clamp_base`(`scripts/lumos:22943`、`scripts/lumos:22954`)寫在「每支檔有家」那一段程式碼裡,`_ns_range_added`(`scripts/lumos:23579`)本身雖然物理上寫在筆記形狀擋那段,但其邏輯血緣(新分支起點、上線點截斷、合併偵測)是從「每支檔有家」借來加參數而成,兩篇筆記都同意這件事——只有 spec 這份文件把兩支函式一律歸給 `筆記內容閘`。只有「判『這行落在正文/summary/decisions 文字子欄還是結構欄』的那支」(即 `_ns_regions`)才真的是 `筆記內容閘` 自己的家產。

實務影響:CLAUDE.md 鐵則五要求「改到程式要寫說明就寫進改到那支檔的家」——如果第二層實作時真的去動 `_ns_range_added`/`_nodehome_golive`/`_nodehome_clamp_base`(例如加「掛鉤路徑參數」,spec 自己在下一段就提到要加),寫回說明應該落在 `Systems/每支檔有家`,而不是這份 spec 暗示的 `Systems/筆記內容閘`;照 spec 字面做會把維護紀錄寫錯地方,之後排查會在錯的節點裡找不到。

# F2 直接重用 _ns_range_added 無法滿足 S6「重複文字應列出每一處」

severity: major
blocking: 是 —— S6 是有具體測試名的可執行條款(`t_note_audit_prepare_content_ids_stable`),若照〈做法〉字面「直接用...不另寫」實作,會拿不到達成這條測試所需的資料。

spec 位置:〈做法〉「哪些行要審」第一句與條款 S6。

引句:「同一段文字在同一篇出現好幾次,列出每一處的行號與次數」
引句:「重複文字應列出每一處」

問題:被指名重用的函式 `_ns_range_added`(`scripts/lumos:23579`)回傳的 `by_path` 是 `{NFC 路徑: set(去頭尾空白的行文字)}`——注意型別是 **set**,不是帶行號的清單。往下看它的填值方式:

file: `scripts/lumos:23633`
```
dest.setdefault(p, set()).update(t_.strip() for _n, t_ in rows if t_.strip())
```
這裡把 `_ns_parse_added` 回傳的 `(行號, 文字)` 元組直接丟掉行號(變數名故意寫成 `_n` 表示未使用),只把文字塞進 `set()`。合併提交那條路徑(`scripts/lumos:23660`)也是同樣的丟法:
```
dest.setdefault(nfc(p), set()).update(x.decode("utf-8", errors="surrogateescape") for x in new)
```

結果是:同一段文字在同一篇出現兩次或十次,`by_path` 裡永遠只留一份(set 天生去重),完全沒有「出現幾次、在第幾行」這個資訊可以直接拿來用。要滿足 spec 自己要求的「列出每一處的行號與次數」,prepare 勢必要另外重新掃一次 tip 版本的檔案內容(逐行核對是否落在 `_ns_regions` 判出的正確區塊、且文字屬於這個 set),這件事 `_note_shape_eval`(`scripts/lumos:23799-23819`)自己就是這樣做的——但 spec 把這個「另外重新掃一遍」的必要工作,描述成「直接借第一層已上線的那一套...不另寫」,容易讓實作者誤以為兩支函式的回傳值就已經夠用,漏掉這段自己要補的邏輯。

# F3 「.lumos/note-audit/ 加進 .gitignore 與初始化時的忽略設定」引用了不存在的機制

severity: major
blocking: 是 —— 這是消費專案(非本 repo)層級的可執行性缺口:沒有對應機制可以「加進」,會讓待審清單檔以未追蹤檔的形式出現在每個消費專案的 `git status` 裡,增加被誤 `git add -A` 提交(judge 派工詞、原始筆記片段外洩到版控)的風險。

spec 位置:〈做法〉步驟 1。

引句:「與初始化時的忽略設定;prepare 順手清掉 14 天前的舊清單」

問題:目前程式碼裡「初始化時寫 gitignore」只有兩條路,而且都不覆蓋 `.lumos/`:

file: `scripts/lumos:17347`(`_scaffold_project`)只寫 `docs/.gitignore`(給 vault 底下的本機流水帳用)。
file: `scripts/lumos:17367-17372`(`_init_additive_setup`)只寫 `governance/.gitignore`(給 `governance/` 底下的本機執行期狀態用)。

兩者都不觸碰倉庫根目錄的 `.gitignore`,也沒有任何寫 `.lumos/.gitignore` 的程式碼路徑。本 repo 根目錄 `.gitignore` 裡確實已經有 `.lumos/testmap.json`(`.gitignore:9`)、`.lumos/test-cache*.json`(`.gitignore:30`)、`.lumos/lintbase-*/`(`.gitignore:36`)這類條目,但這些是這個工具鏈自己 repo 手動維護的既有檔案內容,不是 `lumos init`/`lumos update` 會寫給「消費專案」的東西——`_VENDORED_TOOLKIT`/`_VENDORED_TREE_FILES`(`scripts/lumos:16903-16922`)清單裡也沒有根 `.gitignore`。也就是說,對任何一個「消費專案」(不是這個工具鏈自身)而言,今天並沒有一條路可以讓 `lumos init`/`lumos update` 自動把 `.lumos/note-audit/` 寫進它自己的 `.gitignore`——spec 這句話預設了一個目前不存在的「初始化時的忽略設定」機制,而且沒有把「要新增這條機制」列成待辦。

---

# 總結

最嚴重 severity: major
blocking 條數: 3(F1、F2、F3,皆 major)
