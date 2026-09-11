severity: major

### F1 「每支檔至少一個家」沒有滿足舊案的漏標歸零條件
severity: major
blocking: 是 — 不改，實作者會用不同母體的證據重啟已被明確凍結的第四入口。
引句:「新證據:[[Projects/每支檔有家_計劃]](2026-09-11 上線)讓新增的程式檔提交當下一定有家、原本有家的檔變沒家會擋」
1. file: `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:35` d4 要求壓低的是 about 漏標率；file: `scripts/lumos:17995` 新證據只保證每支檔至少有一篇特定狀態的 Systems 節點。
2. file: `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:534` 舊調研的 31 組自由席必看全是 Projects／Verification，且同檔第 545 行明載 about_hit 動不到它們，因此新證據沒有量到舊決策要求的母體。

### F2 home-only 候選沒有可執行的 kind、score 與分桶定義
severity: major
blocking: 是 — 不改，實作者必須自行發明分數或冒充既有 candidate kind，直接改壞排序與保底語意。
引句:「大檔不整批進必推:只有帶合約的家進必推,其餘家在可選名單照分數競爭」
1. file: `scripts/lumos:21590` 現有結果只會建出 incident、direct、indirect，分數與 L／G 也只在這三條路徑產生；file: `scripts/lumos:21743` 顯示端同樣只認這三種 kind。
2. file: `scripts/lumos:21689` 若把 home-only 冒充 direct，它會進直連水位保底；若新增 kind，分數、動態門檻、renderer 與 evaluator 都沒有定義，與「不改分數公式」無法同時實作。

### F3 dispatch-lens 的 spec 路徑不會自然取得 ranked homes
severity: major
blocking: 是 — 不改，實作者照 S2 改 ranked impact 後仍會留下設計審鏡頭漏家。
引句:「派審查員時的圖譜參考(dispatch-lens 的 diff 與 spec 兩種)也認家」
1. file: `scripts/lumos:23116` spec 鏡頭刻意呼叫未帶 `--ranked` 的 `impact --file --json`；file: `scripts/lumos:23121` 隨後只解析 direct、incidents、帶合約的一跳 indirect。
2. home-only 節點不在該 JSON 三集合內，spec 未定義改成 ranked schema還是另做 home lookup，現有測試名稱也沒有釘住這項接線決策。

### F4 多檔 diff 聚合沒有保留 home 身分與順序的資料模型
severity: major
blocking: 是 — 不改，同一節點跨檔合併後會丟失「是哪支檔的家」，無法兌現 S6 的順序。
引句:「推送前的波及計算(`impact --diff`)聚合時保留家的入口與順序」
1. file: `scripts/lumos:21935` 聚合只保留最高分整筆資料並對 pinned 做 OR；file: `scripts/lumos:21948` 最後固定席全部改按 `(-score,node)` 排序。
2. 當節點對 A 是家、對 B 是較高分非家時，勝出記錄會抹掉 home provenance；spec 未定義 `home_for_files`、跨檔優先序或 incident／home 衝突規則。

### F5 關閉 HOME 旋鈕不能按目前裁定完整回到舊行為
severity: major
blocking: 是 — 不改，回滾開關關掉新入口後，舊 about 排序與顯示仍回不來。
引句:「新增旋鈕 `LUMOS_IMPACT_HOME`(預設 1;0=完全照原本)」
1. file: `scripts/lumos:21269` 舊行為會驗 stamp 後標 about_hit；file: `scripts/lumos:21659` 舊固定席再按 about_hit 排序；file: `scripts/hooks/claude/impact-hook.py:646` 舊 hook 會顯示該標記。
2. S3、S8、S9 卻全域取代排序、移除標示並讓 stamp 不再影響推筆記，沒有規定這三項也受 `LUMOS_IMPACT_HOME=0` 條件控制。

### F6 現有 about 快取與「家」不是同一個集合
severity: major
blocking: 是 — 不改，大檔門檻會被非家節點誤觸發，或熱路徑被迫再掃一套 git 快照。
引句:「找家要掃全圖的 about_code——既有的 about 計數已經有快取,本案沿用,不另掃一次」
1. file: `scripts/lumos:21250` 現有快取掃全部 `env.notes`，不過濾 type／status，鍵也只走 `_posix_norm`。
2. file: `scripts/lumos:17995` 真正的 home helper 只收 Systems 的 doing／done／stale 並走 `_nodehome_key`，而其輸入是 `_NodehomeSide` git 快照，不是 impact 的 `Env`。
3. 直接沿用快取會把 Issues／Projects／非有效狀態筆記計入「家數 ≥8」；直接沿用 helper 則違反「不另掃一次」，S1 與效能裁定目前互斥。

### F7 驗收沒有對新增 home candidates 做未標候選的 fail-closed
severity: major
blocking: 是 — 不改，實作者會用未標節點污染的 P@8／top3 數字作上線判斷。
引句:「評測:用既有評測器跑練習題與保留題」
1. file: `governance/eval/retrieval_eval.py:438` P@8 只量 free bucket，而 file: `governance/eval/retrieval_eval.py:475` 未標的新固定席被直接當噪音與 top3 非必看。
2. file: `governance/eval/retrieval_eval.py:751` 只有 `--ablation` 會因未標候選 fail-closed，spec 第 95 行的兩條驗收命令都未帶它，也沒有先 refresh／repin labels。
3. home-only 節點加入或既有 free 節點改成 pinned 時，兩把尺的母體同時改變；只比較輸出百分比不能證明不退步。

### F8 三份既有 pass 驗證會被本案直接失效，落點卻未處理
severity: major
blocking: 是 — 不改，圖譜會同時保留互相矛盾的 pass 背書。
引句:「前後數字寫進驗證紀錄」
1. file: `docs/lumos-toolchain-knowledge/Verification/2026-07-10_檢索排序v1.md:7` 固定席定義屬 valid_under；file: `docs/lumos-toolchain-knowledge/Verification/2026-07-11_檢索goldset評測.md:5` 背書現行 edit 評測母體；file: `docs/lumos-toolchain-knowledge/Verification/2026-08-24_about_code讀側四項落地.md:33` 明確驗過即將被移除的 about 排序與標示。
2. spec 只要求新增驗證紀錄，沒有把這三篇標 stale、superseded 或逐篇重驗，尤其 2026-08-24 那篇會在上線後仍以 status pass 宣稱相反行為。

### F9 舊專案相容性只回答「不更新」，沒有回答正常更新後的硬擋
severity: major
blocking: 是 — 不改，更新工具後第一次修改既有 regen 節點的消費專案會遇到未規劃的提交阻斷。
引句:「舊專案沒更新:沒跑 `lumos update` 的專案照舊行為,不會壞」
1. file: `scripts/lumos:4368` 現有 lint 已把任何非空 regen 視為重建節點；file: `scripts/hooks/pre-commit:91` 所有 staged 圖譜節點都會逐篇 lint 並以 rc 非零擋提交。
2. S11 加入後，更新過的舊專案只要修改一篇既有且缺 about_code 的 regen 節點就會被擋，spec 沒有盤點命令、backfill、grandfather cutoff 或更新提示。

### F10 驗收漏掉錨點重新核可
severity: minor
blocking: 否 — 不改，實作者通常會在 pre-push 才被既有守衛攔下，不會直接產出壞系統。
引句:「子集:`python3 scripts/test_lumos.py -k impact_home`、`-k impact_pins_order`、`-k dispatch_lens_includes_homes`」
1. file: `scripts/lumos:14900` `scripts/test_lumos.py`、`dispatch-lens-hook.py`、`impact-hook.py` 都是 anchor files；file: `docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md:19` 修改後須走 `anchor approve --note` 並由 verify 比對。
2. S8 與新增測試至少會改到其中兩支錨點，但驗收清單沒有 anchor approve／verify，交付步驟不完整。

### F11 hook 標頭會把非合約家誤稱為合約或事故
severity: major
blocking: 是 — 不改，agent 會把結構化 ownership 誤讀成不可破壞的合約。
引句:「顯示:Edit 前推筆記的清單上」
1. file: `scripts/hooks/claude/impact-hook.py:630` 現行 renderer 把所有 pinned 項放在同一桶，file: `scripts/hooks/claude/impact-hook.py:641` 標頭宣稱每篇都帶不能破壞的合約或出過事故。
2. S2 允許普通、無合約的小檔家進 pinned，S8 只裁定換行首標籤，沒有要求同步改寫桶標頭與信任語意。

## 逐節覆核

1. frontmatter、summary、白話摘要：已讀，F1。
2. 「為什麼」：已讀，F1；PRIOR-ART 本身無新增 finding。
3. 「名詞」：已讀，F2、F6。
4. 「核心裁定／甲」：已讀，F2–F8、F11。
5. 「核心裁定／乙」：已讀，F9。
6. 「範圍外」：已讀,無 finding。
7. 「落點」：已讀，F8。
8. 「實務隱患」：已讀，F5、F6、F9。
9. 「驗收怎麼跑」：已讀，F7、F10。
10. 「回頭條件」：已讀,無 finding；週清單實作存在於 `governance/autonomous_loop/lens_weekly.py:2` 與 `governance/eval/lens-utilization/recount.py:448`。
11. 「合約候選」：已讀，候選文字本身無新增 finding，但 S2/S4 尚受 F2 阻斷。
12. 「審計修正紀錄」：已讀,無 finding。

## 交叉引用與現況查核

1. 五個 wikilink 目標 `固定席扇出降權_計劃`、`每支檔有家_計劃`、`retrieval-ranking`、`節點還原`、`check-j-regen-guard` 均存在。
2. `_impact_reverse_lookup`、`_impact_mark_about`、`_nodehome_homes`、`_nodehome_key` 均存在；`LUMOS_IMPACT_ABOUT_MAX` 現行預設確為 8。
3. `impact --file/--ranked/--diff`、`dispatch-lens --spec`、`lint`、`new system --code`、`about-code restamp/revert/migrate-stamp` 均存在；`LUMOS_IMPACT_HOME` 是 spec 明載的新項，不列未定義。
4. commands/09 與 reference 的節點還原第 4 步及 `--code` 路徑存在，未發現壞交叉引用。

## 固定席逐條判

1. `Systems/retrieval-ranking`：會影響；固定席來源、排序、輸出母體與 about 行為全被改寫，F2、F4、F5、F7、F11 未折前不能維持其行為敘述。
2. `Systems/節點還原`：不影響其既有七步流程與合約；乙案只加強第 4、6 步出口。
3. `Systems/check-j-regen-guard`：不破壞既有 provenance 守衛；S11 增加正交欄位檢查，宣告制 opt-in 天花板仍由 S88 保留。
4. `Issues/canary-record未落盤事件`：不影響，沒有改 canary 寫入、鎖或治理帳落盤。
5. `Issues/code-loop守衛main-direct盲區`：不影響，沒有改 code-loop 的 main/direct 範圍判定。
6. `Issues/hook卸載殘留註冊`：不影響其卸載殘留機制，S8 只改既有 hook 顯示內容。
7. `Issues/init-force-slug誤用basename`：不影響，沒有改 init、force 或 slug 推導。
8. `Issues/vendored測試套件在消費端假紅`：不影響，沒有改 vendored 偵測或消費端測試選擇。
9. `Systems/known-pitfall-refresh-token`：不影響，沒有改坑單刷新或 token。
10. `Systems/lumos-cli-read`：不影響其 search／superseded 讀取合約，變更限 impact。
11. `Systems/lumos-refcheck`：不影響 refcheck 抽取與驗證語意。
12. `Systems/anchor-integrity`：會影響，F10 漏了三支相關 anchor files 的核可流程。
13. `Systems/pitfalls-code-loop`：不影響，沒有改 pitfalls 分級、code-loop 或處置閘。
14. `Systems/測試假綠形態`：不直接破壞其 bug-fix 前置條件合約，但 F7 會讓評測結論失真。
15. `Systems/slim-install-安裝器`：不影響，沒有改安裝器的檔案範圍與專案不碰合約。
16. `Systems/slim-uninstall-一行卸載`：不影響，沒有改卸載清單或刪除範圍。
17. `Systems/design-loop`：不影響其審查流程；S1–S13 均有 test/manual 綁定，但本輪 findings 尚未處置。
18. `Systems/lumos-cli-lifecycle`：不破壞更新、注入與 sentinel 合約；更新後的消費端 lint 行為缺口另見 F9。
19. `Verification/2026-07-10_檢索排序v1`：會失效，其 valid_under 明載的固定席定義被改，見 F8。
20. `Verification/2026-07-11_檢索goldset評測`：會失效，pin/free 母體改變後既有 edit 評測背書不能原樣沿用，見 F7、F8。
21. `Verification/2026-08-24_about_code讀側四項落地`：會直接失效，其 pass 內容正是 S3、S8、S9 要移除的排序、stamp 與標示，見 F8。

## 實務隱患鏡頭

1. 效能：有，F6；熱路徑目前沒有一個同時符合 home 語意、工作樹視角與單次掃描的資料來源。
2. 噪音與召回：有，F1、F2、F7；S5 避免了舊 r1 的主動降級，但大檔 home 分數與評測母體仍未定義。
3. 平行路徑：有，F3、F4；單檔 ranked、diff 聚合與 dispatch-lens spec 目前使用不同 schema。
4. 舊專案相容：有，F9；未更新不壞不等於正常更新後不壞。
5. 回滾：有，F5；關掉 HOME 尚不能恢復 about 排序、stamp 判定與舊標示。
6. 可觀測性：有，F7、F8；推播漏網週清單已存在，但上線驗收與既有 pass 驗證的生命週期沒有閉合。
7. 分發與錨點：有，F10；功能會動到錨點檔，驗收未納入重新核可。
8. 資安、個資、金流、不可逆與對外寄送：無；本案只改本機讀側輸出、lint 與文件，不新增秘密處理、正式環境寫入或外送。

## 舊案重蹈判定

1. 沒有重蹈舊 r1 的直接傷害：S5 明確禁止因「不是家」降級既有事故、合約與反引號候選。
2. 有重蹈舊 r1 的證據錯置：舊案已裁定 about 是 must-see 的高精確度子集而非等價物，新案又把「每檔至少一個 Systems 家」說成舊母體的漏標歸零。
3. 因此演算法方向不同，但 d4 的重提門檻尚未被滿足，F1 折掉前不能以舊決策授權實作。

總結:最高 severity major,blocking 共 10 條
