# about-code-impl-std r1 架構對齊審查

被審:`/tmp/about-code-impl-std-r1.md` ★剩四項的實作規格★(#4/#6/#9/#10)+「本案新增/修改工具清單」表。
只判「跟本專案既有做法一不一致」,不找 bug、不評風格。

---

## 問一:分層與依賴方向——新邏輯放的位置、呼叫誰、誰呼叫它,跟鄰居一樣嗎

**#4(cmd_impact 讀 about_code)★對齊★。**
新邏輯就地寫在 `cmd_impact` 的 ranked 融合區塊裡(四處 `results.append` 在 `scripts/lumos:14178/14203/14214/14223`,`pins = [...]` 在 `:14226`),排序旋鈕走既有 `_impact_knob`(`:13883`),過期比對呼叫既有共用函式 `git_last_change_dates`(`:13549`,此函式刻意沒掛 `_impact_` 前綴、也不是 module-private,本來就是設計給 impact 之外的呼叫者用)。這跟鄰居(direct/indirect/incident 三段各自 append、各自呼叫 `_impact_knob`)分層方向一致。

唯一存疑(⚠ 交編排者,非硬判):規格「cmd_impact 開頭全掃 env.notes 的 about_code 建 {檔: 節點數}」這句沒寫清楚是要切成獨立頂層函式,還是直接寫進 `cmd_impact` 函式體。既有慣例是「重活切給 `_impact_*` 小函式,`cmd_impact`(`:13982`)本身只派工」——`_impact_reverse_lookup`(`:13590`)、`_impact_contract`(`:13666`)、`_impact_bfs`(`:13704`)、`_impact_load_config`(`:13955`)全部是獨立掛在頂層的函式。字面照做(inline 寫進 `cmd_impact` 開頭)就會破壞這個分工;如果只是口語簡寫、落地時仍會切成 `_impact_about_counts()` 這樣的函式,則對齊。規格文字本身判不出是哪一種,標 ⚠。
引句:「`cmd_impact` 開頭全掃 `env.notes` 的 `about_code` 建 `{檔: 節點數}`」

**#6(過期檢查另開迴圈)★不對齊,major★。**
規格:「在新迴圈裡自己從 vault 往上找 .git(對齊 cmd_impact `:14024` 的後備寫法)……找不到 → 整段跳過並 `ok(...)`」。
引句:「往上找 `.git`(對齊 `cmd_impact :14024` 的後備寫法)」

但 `run_doctor` 這整個函式裡,`repo_root` 早在 Check C 就解過一次(`scripts/lumos:681-685`):

```python
repo_root = None
for p in env.vault.parents:
    if p.name == "docs":
        repo_root = p.parent
        break
```

而且這是 `run_doctor` 函式體裡的**普通區域變數**,不是某個 check 私有的東西——後面 Check D(`:1066`)、Check P(`:1124`)、Check Y(`:1196`)、Check N(`:1259`)全部原封不動複用同一個 `repo_root`,一次都沒有重算,只做 `if repo_root is None:` 判斷。這是 `run_doctor` 這一層目前唯一、且已經被四個既有 check 沿用的「repo_root 哪來」答案。

規格的新迴圈完全沒提這個既有變數,反而叫它「自己找」——這既是分層問題(同一函式裡已解過的東西,新段落不重用、另外重解一次),也是「引入沒人用過的第三種演算法」:
- Check C 的既有寫法:vault 往上找**名叫 `docs` 的資料夾**,取其上一層。
- `cmd_impact` 主解析路徑(`:13997-14001`):從 **`Path.cwd()`** 往上找 **`.git`**。
- `cmd_impact` 後備(規格引用的 `:14024`):`vault.parent.parent`——固定跳兩層,不是走訪,也不找 `.git`。
- 規格提的新寫法:從 **vault** 往上找 **`.git`**。

四種各不相同,規格自稱「對齊 `:14024`」但 `:14024` 實際是 `vault.parent.parent` 定值算法,跟「vault 往上找 .git」不是同一支——引用本身對不上自己要做的事。真正該對齊的對象近在同一函式裡(Check C 的 `repo_root`),規格捨近求遠,另立第四套。

---

## 問二:命名與錯誤處理

**旗標命名★對齊★。**
`LUMOS_IMPACT_ABOUT`/`LUMOS_IMPACT_ABOUT_MAX` 跟 `LUMOS_IMPACT_BASENAME_MATCH`(`:13609`/`:13624`,預設 1、0=逃生)、`LUMOS_IMPACT_RESCUE_N`(`:14254`)、`LUMOS_IMPACT_LMIN_HOP2`(`:14219`)同一套 `LUMOS_IMPACT_<語意>[_MAX/_N/...]` 命名與「knob=0 留逃生」語意,規格自己也點名對齊 `:13609` 那組——屬實。

**新欄位命名 `about_hit`★對齊★。**
不覆寫既有 `hit`(存 body-inline-code/basename-match 來源標記,`impact-hook.py:358`、`scripts/lumos:14310` 在讀)。這條在 impl-r1 上一輪(f2)已經抓過並定案,本輪沒有新問題;跟既有 `pinned`/`rescued`/`combo` 這類散在 results dict 裡的布林欄位風格相容,只是多一個字根避開歧義。

**fail-open 寫法★對齊★。**
規格「git 缺席 → 用 updated 欄;兩者都沒有 → 視同沒過期」跟 Check S 現有的「缺 updated → 不做過期判定(避免誤報)」(`scripts/lumos:838-841`)是同一種「缺資料就不罰」哲學,也跟 `_GIT_DATES_CACHE` 的 `except (OSError, subprocess.SubprocessError): out = {}`(`:13580-13582`)同一種「失敗回空、上層自己接住」寫法。

**warn_soft 訊息格式★對齊★。**
規格 `f"{rel} (about_code_stamp {stamp_date} < git 最後改動 {git_date})"` 跟 Check S 實際的 `f"{rel} (self_audit {sa_date} < updated {upd})"`(`scripts/lumos:842`)是同一種「`{rel} ({欄位1} {值1} < {欄位2} {值2})`」格式。規格引用的行號 `:868` 其實是 `warn_soft(...)` 呼叫那一行,真正的格式化字串在 `:842`——行號小誤,但格式本身核對得上,不算不對齊。

**「找不到就跳過」訊息習慣——半對齊,細節是問一那條 major 的下游症狀。**
Check D/P/Y/N 在 `repo_root is None` 時一律印 `ok("(這個專案沒有 docs/ 資料夾,……跳過)")`(`:1124`/`:1196`/`:1259`)——用 `ok()` 而非 `warn()`,規格「找不到 → 整段跳過並 `ok(...)`」在**用哪個函式**這件事上是對的。但訊息文字規格寫的是「about_code 過期檢查:找不到 git,略過」——框架換成了「git」而不是鄰居統一講的「沒有 docs/ 資料夾」。這是問一 major 的直接下游:規格打算自己重找 `.git`,連帶訊息措辭也跟著換了;若改成複用 Check C 的 `repo_root`,訊息理應跟 D/P/Y/N 一樣講「沒有 docs/」。不重複計入不對齊條數,併入問一那條 major 一起看。

---

## 問三:第二種做法——有沒有引入專案裡原本沒有的做法

**巨檔計數的快取鍵★不對齊,major★。**
規格:「以 `id(env)` 為鍵掛行程內快取(impl-r1 s1f7;同 `_BASENAME_COUNTS_CACHE :13587` 慣例,`--diff` 多檔共用 env 免重掃)」。
引句:「以 `id(env)` 為鍵掛行程內快取」

但實際去看這兩個既有行程內快取:

- `_BASENAME_COUNTS_CACHE = {}`(`:13587`)——鍵是 `str(repo_root)`(`:13624-13639` 附近 `key = str(repo_root)`)。
- `_GIT_DATES_CACHE = {}`(`:13546`)——鍵是 `(str(repo_root), str(vault))` 這種路徑 tuple(`:13561-13563`)。

全庫沒有一個行程內快取用 `id(...)` 當鍵——兩個既有先例都是「路徑字串」,`id(env)` 是物件記憶體位址,語意完全不同類。而 `cmd_impact` 在同一函式開頭本來就已經解出 `repo_root`/`repo_root_for_lookup`(`:14024`),規格若真要「同 `_BASENAME_COUNTS_CACHE` 慣例」,直接拿 `str(repo_root_for_lookup)` 當鍵就是,沒有理由改用一個全庫沒有先例、語意也不同的鍵法。

功能上不會馬上壞:`cmd_impact_diff` 的 `--diff` 迴圈確實「建一次 env、逐檔復用」(`:14025` `_env_shared = Env(_vault) if _vault is not None else None`),同一輪迴圈裡 `id(env)` 是穩定的,不會誤命中。但這不構成必須用 `id(env)` 的理由——`repo_root_for_lookup` 在同一輪迴圈裡同樣穩定,兩者效果一致,規格選了沒有先例的那個。這正是「引入第二種做法」:往後接手的人在同一支檔案裡會看到三種行程內快取,兩個用路徑字串、一個用物件身分,得自己猜哪個才是規矩、猜錯了(例如照抄 `id(env)` 手法去做別的快取)會踩上「物件被回收、id 被下一個物件複用」這種路徑字串鍵完全不會有的陷阱。

**#9 / #10 ★對齊★,沒有另立新路。**
- #9 hook 顯示只是讀新欄位、印一個標記,套進 `build_ranked_context` 既有的 for 迴圈(`impact-hook.py:344-348`),沒有新機制。
- #10 新指標套進既有的「`verdict[...]` 手動摘一份到 `gates = {...}` 才算門檻,其餘全部透過 `"verdicts": {r["split"]: r["verdict"] for r in reports}`(`governance/eval/retrieval_eval.py:499`)整包流進 history」機制——`must_pinned_count`(`:410`)就是同款「只進 verdict/history、不進 `gates` 手動清單(`:569-575`)」的觀測型指標,`pin_top3_must` 照樣放進 `verdict` dict、不手動加進 `gates` 即可達到規格要的效果,沒有引入新機制。分母為 0 回 `None`、彙總時排除,也跟既有 `_macro()`(`:266-268`,自動濾掉 `None` 再平均)與 `row[f"{name}_p"] = ... if labels else None`(`:333`)這條既有的「per-row 可回 None、彙總層自動濾掉」路徑相容。

**#4 的 stable-sort 排序手法——不算新技巧,對齊。**
`pins` 列表本身的相對順序,在 `all_direct.sort(...)`(`:14101`,按 `contract_priority`)、`all_indirect.sort(...)`(`:14102`,按 hop/`contract_priority`)那兩行就已經決定過一次;新排序只是在既有排序結果上疊一層「about_hit 優先」,不是另立一套獨立判準,沒有跟既有 `.sort(key=(...))` 系列打架。

---

## 結論

不對齊共 **2** 條,其中 major **2** 條:
1. 問一/#6:doctor 新迴圈自行重找 repo_root(從 vault 找 `.git`),沒有複用 `run_doctor` 本身已經算過、且被 Check D/P/Y/N 共用的 `repo_root` 變數(`scripts/lumos:681-685`),且該演算法與既有三種 repo_root 解法(cwd 找 `.git`、`vault.parent.parent`、vault 找 `docs` 目錄)都不同,規格引用的對齊行號本身也對不上。
2. 問三/#4:巨檔計數快取鍵用 `id(env)`,偏離全庫僅有的兩個行程內快取一致採用的「路徑字串為鍵」慣例(`_BASENAME_COUNTS_CACHE`/`_GIT_DATES_CACHE`),且已有現成的 `repo_root_for_lookup` 字串可用、沒有換來額外能力。

另有 **1** 條 ⚠ 交編排者判準:問一/#4 的巨檔計數究竟要不要切成獨立 `_impact_*` 頂層函式(比照 `_impact_reverse_lookup` 等鄰居),規格文字「cmd_impact 開頭全掃」沒寫清楚是 inline 還是另切函式,兩種讀法一種對齊一種不對齊,判不準。
