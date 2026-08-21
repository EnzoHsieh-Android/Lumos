C1 [✅] FLOW 屬實:doctor Check Y 掃 type=system 節點正文 inline-code → `_is_symbol_shaped` 篩形狀 → 比對 `build_code_haystack` 產出的 haystack → 查無則 `warn_soft`(軟提醒) | 證據: scripts/lumos:1168(section Y)、1177-1189(_is_symbol_shaped)、1192(_hay=build_code_haystack)、1200(type!=system 跳過)、1220(s not in _hay)、1223-1226(warn_soft)

C2 [✅] delguard 為 diff-based(staged diff,pre-commit hook 觸發);Check Y 為 doctor 全量掃描(隨時可跑) | 證據: scripts/lumos:11588(`git diff --cached`)、scripts/hooks/pre-commit:57(`lumos delguard --staged`)、scripts/lumos:1156-1158(註解明講「delguard 驗…diff-based,只在 commit 時；本檢查驗…全量」)

C3 [✅] 首發實績:圖譜寫 `ActivityService.RegisterAsync`,實際為 `SubmitRegistrationAsync` | 證據: scripts/lumos:1159-1160;回歸測試 scripts/test_lumos.py:5110-5122(`_y_repo` 建置 RegisterAsync 節點+SubmitRegistrationAsync 實作,斷言前者被抓、後者不吵)

C4 [❓] 找不到:滿額贈 `ListAvailableAsync`→`GetActivitiesAsync` 一節,repo 內僅 scripts/lumos:2493 提到 ghost 符號 `ListAvailableAsync`(drift-history 77天/11取樣點持續),但「實際方法名為 GetActivitiesAsync」未見於本 repo 任何檔案(LandmarkMember 原始碼不在此 repo,`GetActivitiesAsync` 唯一出現在 skills/csharp-idioms/SKILL.md:120 的無關範例句)。已搜 scripts/lumos、scripts/test_lumos.py、skills/、governance/、.github/,無對應佐證。

C5 [❓] 找不到:滿額贈 `GetOrdersForRedeemAsync`→`GetOrderSelectionAsync` 一節,repo 內僅 scripts/lumos:2493 提到 ghost 符號 `GetOrdersForRedeemAsync`(同一則 drift-history 紀錄),但「實際方法名為 GetOrderSelectionAsync」全 repo 零命中(已 grep scripts/lumos、scripts/test_lumos.py 確認)。同 C4,LandmarkMember 原始碼不在本 repo,無法核對。

C6 [❓] 找不到完整佐證:程式碼註解只明講「這條」(即 C3 的 RegisterAsync)在同日 10 個 agent 兩階段交叉審計中被漏掉(scripts/lumos:1159-1160,"這條"為單數指代);C4/C5 兩條符號的發現敘事(scripts/lumos:2486-2494)講的是另一套機制——沿 git 歷史取樣重放、橫跨 77 天 11 個取樣點持續存在,通篇未提「10 個 agent 交叉審計」。全 repo(scripts/lumos、scripts/test_lumos.py)搜「10 個 agent」「兩階段交叉審計」僅命中 1 處(1160 行),對應 C3 非全部三條。

C7 [✅] 只掃 Systems 型別節點;Projects/Verification/Issues 不掃,且註解明講是語意決定非調參 | 證據: scripts/lumos:1194-1198(註解:「★只掃 Systems★:語意上只有它宣稱『現在長怎樣』。Projects…Verification/Issues…對那些節點報『repo 查無』是誤報而非發現」)、1200(`if n.fields.get("type") != "system": continue`);測試佐證 scripts/test_lumos.py:5243-5248(t_checky_systems_only,ntype="project" 不吵)

C8 [❌] 數字不符:程式碼註解實測數字為「全型別掃 → 37 命中;限 Systems → 1 命中(且為真陽性)」,並非主張所稱的「降為 4 命中」 | 證據: scripts/lumos:1197-1198(「全型別掃 → 37 命中…；限 Systems → 1 命中且為真陽性。」);全 repo 搜「命中」無任何「4」與此實驗相關的數字出現

C9 [✅] 形狀過濾前(寬鬆抽取任何 PascalCase inline-code)在真實圖譜上 930 候選 / 74 未命中(7%) | 證據: scripts/lumos:1163(「寬鬆抽法(任何 PascalCase inline code)→ 930 候選 / 74 未命中(7%)」)

C10 [✅] 形狀過濾規則字面相符:無底線/無數字/非全大寫/無副檔名,且「以 Async 結尾」或「帶點(含點號)」才算候選 | 證據: scripts/lumos:1166(「收緊成『方法/類別形狀』(無底線/無數字/非全大寫/無副檔名,且 以 Async 結尾 或 帶點)」);實作對應 1177-1189(`_is_symbol_shaped`:排除 digit/isupper/副檔名,靠 `_sym_re` shape_re 排除底線(csharp profile 無底線字元類),`_sufs`(Async)或 `_dot_ok` 二擇一)

C11 [✅] 套用形狀過濾後:279 候選中僅 1 筆未命中(0.4%),且該筆為真陽性 | 證據: scripts/lumos:1167(「→ 279 候選 / 1 未命中(0.4%),★該 1 條是真陽性★。」)

C12 [❌] 否定語境豁免詞清單不完整:主張列 16 詞,實際 zh lexicon 共 26 詞,漏列「已改、棄用、不使用、廢棄、停用、未使用、dead、deprecated、unused、obsolete」等 10 項 | 證據: scripts/lumos:1925-1930(NEG_LEXICONS["zh"] = ("零命中","已移除","不存在","查無","已刪","從未","已退役","移除","無此","原記","舊名","改名","已改","棄用","不使用","廢棄","停用","未使用","dead","removed","deleted","no longer","renamed","deprecated","unused","obsolete"))

C13 [❌] 與現況不符:Check Y 並非「只認 C#/前端命名慣例」——2026-08-12 通用性修正後已 profile 化,內建 csharp/kotlin/python 三種 symbol_profile(python 明確是 snake_case、非 C#/前端慣例,且註解自陳「證明 profile 化是必要的」),可經 `.lumos/config.json` 的 `symbol_profile`/`symbol` 欄位切換或覆寫,非「其他語言棧需擴充形狀規則」才能用 | 證據: scripts/lumos:1899-1920(SYMBOL_PROFILES 含 csharp/kotlin/python 三組 shape_re)、1937-1966(load_symbol_profile 讀 config.json 切換 profile + 欄位級 override);測試佐證 scripts/test_lumos.py:5205-5212(python profile 下 snake_case 生效測試)

C14 [✅] 機制邊界屬實:Check Y 只驗符號是否存在(`s.split(".")[-1] not in _hay` 純字串存在性比對),不驗語意/用法是否正確,無任何上下文語意檢查邏輯 | 證據: scripts/lumos:1220(存在性比對邏輯,haystack 為純符號名稱集合,無呼叫脈絡比對);build_code_haystack 定義於 scripts/lumos:2306 起,僅建立符號名稱集合

C15 [✅] 三個依附/驗證節點檔案確認存在(僅核對檔案存在性,未讀取內容,依規則禁讀 docs/lumos-toolchain-knowledge/ 內文) | 證據: docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md 存在;docs/lumos-toolchain-knowledge/Verification/2026-08-12_CheckY_符號存在性.md 存在;docs/lumos-toolchain-knowledge/Verification/2026-08-12_通用性修正_profile化與歷史重放.md 存在(find 檔案系統列出,未 cat)

C16 [❌] 數字不符:Check Y 相關測試(`t_checky_*`)實際共 9 條,非主張所稱「5 條」;涵蓋範圍(否定語境豁免/Projects不掃/形狀過濾擋環境變數・範例ID・檔名)三項各有對應測試存在但總數不對 | 證據: scripts/test_lumos.py 內 `t_checky_flags_missing_symbol`(5109)、`t_checky_silent_when_symbol_exists`(5118)、`t_checky_negation_context_exempt`(5126)、`t_checky_deprecation_vocab_exempt`(5136)、`t_checky_profile_switches_language`(5200)、`t_checky_neg_extra_is_configurable`(5216)、`t_checky_unknown_profile_falls_back_loudly`(5231)、`t_checky_systems_only`(5243)、`t_checky_shape_filter_excludes_noise`(5251)——共 9 個函式(行號經 grep -n 對應區段核對)

✅8 ❌5 ❓3 ⏭0
