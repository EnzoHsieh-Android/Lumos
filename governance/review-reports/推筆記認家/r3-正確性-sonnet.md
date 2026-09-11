severity: major

## 逐節掃讀

- frontmatter/summary/白話段:已讀,無 finding。
- 為什麼(這批的來源)、PRIOR-ART:已讀,無 finding——引用的舊案決定 d4、r1 五席「漏標率沒歸零」的重現表核對過(governance/review-reports/推筆記認家/r1-intake.md「新證據不滿足『漏標歸零』」列 HIT),改寫後的兩條依據(只加不降/上線抽查)跟 [S5][S14][S15] 的裁定內容一致,沒有自我矛盾。
- 名詞段(家/家對照表/必推名單/可選名單/大檔/從程式重建的節點/組裝檔):已讀,無 finding——`_NODEHOME_HOME_STATUSES=('doing','done','stale')` 與「狀態 doing/done/stale」的定義對得上(scripts/lumos:18002)。
- [S1]:已讀,無 finding——`_nodehome_homes(repo_root, side)` 現在就只吃 `side.notes`(scripts/lumos:17995-18006),本來就不摸 repo_root,是「純函式」的說法站得住;推筆記端要接進來得自己組一個同形狀的 `side`,spec 沒寫這個轉接但屬正常實作細節。
- [S2]:已讀,無 finding(資料模型敘述本身自洽,「已經是候選」明文含參考道,`_impact_mark_about` 的既有寫法(只在 True 時出鍵、不覆寫 hit 欄)也是這條可以直接沿用的先例)。
- [S3]:已讀,無 finding——「家之間照分數高到低、同分照篇名」需要在既有 `pins.sort` 的兩層 key 上再加一層,屬正常實作延伸,沒有自相矛盾。
- [S4]:見 F1。
- [S5]:已讀,無 finding。
- [S6]:見 F2(合併丟標記)。計劃模式那條(`impact --file --json` 不帶 `--ranked`)機械重現屬實(scripts/lumos:23116),跟 r1 G1 的折入一致,沒有新問題。
- [S7]:已讀,無 finding——旋鈕開/關兩條路徑目前在同一個呼叫點(`_impact_mark_about` 在 scripts/lumos:21657)做分流,語意上可以乾淨地用 `if home_on: … else: 舊的 about 那套`,沒看到回不去原樣的死角。
- [S8]:已讀,無 finding,除了跟 F1 共用的那個顯示缺口。
- [S9]:已讀,無 finding——`about-code restamp/revert/migrate-stamp` 三個子指令都真的存在(scripts/lumos:25532/25535/25538),不是杜撰的指令名。
- [S10]:已讀,無 finding——查過 `_touched_edit`(governance/eval/retrieval_eval.py:174-184),它本來就把「全部 pins」收進計分觸及集,`--ablation` 的 `collect_unjudged`/`ablation_blocked` 因此本來就會擋到新進必推卻沒標過的家,S10 這句宣稱不需要新機制,查證成立。
- [S14]:見 F4。
- [S15]:已讀,無 finding——「這次新加進某篇 about_code 的檔」可以用既有 `ownN.get(rel) - ownB.get(src_rel)` 的差集抓到(scripts/lumos:18224 一帶已有同款「新舊 own 集合比較」的先例),接法上沒有缺口。
- [S16]:見 F3。
- [S11]:已讀,無 finding——`_nodehome_parse_note` 目前確實不讀 regen 欄(scripts/lumos:17905-17927 回傳的 dict 沒有 regen 鍵),spec 自己也講「解析多讀 regen 欄」是要新增的接法,不算未定義;「新蓋章」的判法跟既有 `becomes_home` 那段(scripts/lumos:18232)是同一個模式,可以照抄。
- [S12][S13][S17]:已讀,無 finding(純文件/提醒改動,無機械歧義)。
- [S18]:見 F5。
- 範圍外:見 F6(壞連結)。其餘條目已讀,無 finding。
- 落點:已讀,無 finding——三個落點節點(retrieval-ranking、每支檔有家、節點還原)都存在(見固定席逐條判)。
- 實務隱患(spec 自己寫的段落):已讀,無新 finding,內容併入下面「實務隱患鏡頭」一起答。
- 驗收怎麼跑:已讀,無 finding——子集關鍵字逐一比對過測試名清單(t_impact_home_uses_nodehome_definition/t_impact_home_is_entry_and_pinned/t_impact_home_no_duplicate_node/t_impact_home_moves_out_of_lane/t_impact_about_hit/t_impact_pins_order_incident_home_rest/t_impact_home_cap_for_big_files/t_impact_home_is_additive_only/t_impact_diff_keeps_homes/t_dispatch_lens_diff_includes_homes/t_dispatch_lens_spec_includes_homes/t_impact_home_knob_off_is_old_behavior/t_impact_hook_shows_home_label/t_pinned_wording_mentions_home/t_about_stamp_no_longer_affects_ranking/t_home_audit_sample_is_reproducible/t_home_audit_tally_counts/t_nodehome_new_home_unmentioned_reminds/t_nodehome_new_regen_node_requires_about_code/t_nodehome_regen_theme_node_with_responsibility_passes/t_nodehome_legacy_regen_node_only_listed/t_restore_sop_requires_about_code/t_restore_sop_wiring_and_resource_homes/t_new_system_without_code_reminds),每支都被「驗收怎麼跑」列出的關鍵字覆蓋到,沒有像 r1 那樣漏列的情形。
- 回頭條件、合約候選、審計修正紀錄:已讀,無 finding——審計修正紀錄段對 r1/r2 的條數、去重組數、blocking 數的自述,跟 r1-intake.md/r2-intake.md 兩份原始收貨紀錄的數字對得上。

## Findings

### F1 大檔候選是家時,「家」標記只在必推清單顯示,自由席清單看不到
severity: major
blocking: 是 — 不改,S4 承諾「已經是候選的家只加『家』標記給顯示用」對落在自由席的候選是空話,agent 完全看不到任何家的提示。
引句:「不新增、不升級,跟現在一樣只靠原本三條路」
file: `scripts/hooks/claude/impact-hook.py:637-648` `pins` 迴圈裡才有 `ab = "★關於★" if x.get("about_hit") else ""` 這行標記邏輯
file: `scripts/hooks/claude/impact-hook.py:649-653` `free` 迴圈完全沒有對應的標記變數,大檔情境下一個非固定席的家候選印出來時不會帶任何「家」字樣

### F2 多檔聚合的「高分整項取代」會把家標記一起沖掉
severity: major
blocking: 是 — 不改,同一節點在另一支檔算出更高分時,家身分與家清單會被整項覆寫,[S3] 「家次於事故」的排序規則在 `--diff`/派工鏡頭的合併結果裡對不上。
引句:「記下它是哪幾支檔的家,必推名單照 [S3] 的順序排(事故、家、其餘照分數)」
file: `scripts/lumos:21942` 目前只有 `pinned = cur["pinned"] or x.get("pinned", False)` 這一行做跨檔 OR
file: `scripts/lumos:21945` `x["score"] > cur["score"]` 時整項用 `{**x, "files": cur["files"], "pinned": pinned}` 重建,pinned/files 以外的欄位(含將來的家標記)一律用勝出那一檔的值蓋掉

### F3 版面檔/導覽圖若是 .md 格式,會被既有排除規則整批擋在 --diff 之外
severity: major
blocking: 是 — 不改,S16 舉例的「版面檔、導覽圖」只要剛好用 Markdown 寫,推送前波及計算與派審查員的圖譜參考永遠不會把它的家推出來,而 spec 對排除清單的描述本身就漏算了這一類。
引句:「推送前的波及計算與派審查員的圖譜參考本來就收非程式檔(只排除圖譜、帳檔與治理資料)」
file: `scripts/lumos:21790` `_IMPACT_DIFF_SKIP = ("docs/", "governance/golden/")`
file: `scripts/lumos:21793-21798` `_impact_diff_seed_ok` 另外對「全 repo 任何位置」的 `.md` 檔案做無條件排除(docstring 自己寫的是「文檔(.md)」,不是只排圖譜/帳檔/治理資料四類裡的三類)——比 spec 描述的排除範圍多一類,而且正好打中 [S17] 舉例的「導覽圖」那個檔案格式

### F4 抽查腳本只印「兩家都判否」的比例,沒交代人裁結果怎麼併入「超過一成」門檻
severity: major
blocking: 是 — 不改,實作者很可能把 `tally` 印出的「兩家都判否」比例直接當成上線門檻的分母/分子,由人裁定為錯但兩家意見不一致的配對不會被算進這個比例,會低估真實錯誤率。
引句:「判錯的超過一成就先修家、再上線;逐對結果與錯誤率寫進驗證紀錄」
file: 本節本身(r3-snapshot.md [S14])只定義了兩個輸出——兩家都判「否」的比例、以及交人裁的不一致清單——沒有第三步把人裁完的結果併回同一個「錯誤率」數字,兩者是否同一把尺沒交代

### F5 [S18]「共六篇」跟它自己引的機械指令對不上,漏了一篇
severity: major
blocking: 是 — 不改,S18 自稱的收尾清單本身就跟它引用來核對的同一條指令對不上,受波及合約測試真跑閘落地這篇完全沒被列進「點名三篇」或「掃到三篇」任一邊,上線提交寫新驗證紀錄時會漏這篇的交代。
引句:「上線那次提交處理會失效的既有驗證紀錄,共六篇,逐篇判要不要標 stale」
file: `docs/lumos-toolchain-knowledge/Verification/2026-08-22_受波及合約測試真跑閘落地.md:6` `revalidate_when: 改 _bound_tests_* 三函式、改固定席判定...`——2026-09-12 在乾淨 clone 上實跑 `python3 scripts/lumos stale --candidate --match 固定席` 回傳這篇連同 about_code 讀側四項落地等共 5 筆(非 spec 所述的 3 筆),而這篇不在 S18 點名的三篇、也不在「掃到的三篇」名單裡

### F6 壞連結:[[Issues/各棧測試資料夾被當成要家]] 這個節點不存在
severity: minor
blocking: 否 — 不改,只是讀者點不到那個追蹤節點,不影響本案任何機械判定或合約。
引句:「另一個提交修,見 [[Issues/各棧測試資料夾被當成要家]])」
file: `docs/lumos-toolchain-knowledge/Issues/` 目錄下沒有這個檔名或任何相近名稱的節點(`find` 全庫比對零命中),這是 r1 編排者自提 P3/r2 H1 折入後新產生的連結,兩輪都沒人開這篇

## 固定席逐條判(不影響也寫理由)

- Systems/retrieval-ranking:會被本案直接改(甲段落點),但目前檔內沒有 ★INVARIANT★/★IRREVERSIBLE★ 字面合約行——不影響機械合約,因為本來就沒有機械合約可破壞。
- Systems/每支檔有家:同上,是本案落點且直接改動,檔內同樣沒有 ★INVARIANT★/★IRREVERSIBLE★ 字面合約行,只有既有 `node_home.gate/ignore/max_files` 這些設定介面(已查證真實存在,scripts/lumos:982/2130/17751 等),本案沒有改這些介面的既有語意,不影響。
- Systems/節點還原:同上,是本案落點(乙段),檔內沒有機械合約行,本案只加新規則不改舊步驟語意,不影響。
- 五篇事故(canary-record未落盤事件/code-loop守衛main-direct盲區/hook卸載殘留註冊/init-force-slug誤用basename/vendored測試套件在消費端假紅):都是因為連到 `governance/eval/retrieval-goldset.json` 這個檔名被鏡頭撈進來,本案不改 goldset 的檔案格式或這五篇各自講的事故成因,不影響。
- 其餘「超出上限只列名」的節點(known-pitfall-refresh-token/lumos-cli-read/pitfalls-code-loop/lumos-refcheck/anchor-integrity/測試假綠形態/slim-install-安裝器/slim-uninstall-一行卸載/design-loop/lumos-cli-lifecycle/兩篇舊 Verification):鏡頭本身只把它們列名、不展開全文,依名稱與本案主題(推筆記排序、每支檔有家、節點還原)判斷屬於旁支領域,沒有查到跟本案直接交集的機械合約——不影響。

## 實務隱患鏡頭

- 效能:spec 自己寫「Edit 前推筆記那支 hook 外層 30 秒超時、多檔 patch 總預算 20 秒」,已查證屬實(scripts/hooks/claude/impact-hook.py:61/64/794 一帶);家對照表用行程內快取、不讀 git,跟既有 `_ABOUT_COUNTS_CACHE` 是同一種快取模式(scripts/lumos:21250),無新增熱路徑成本疑慮。
- 噪音與召回的取捨:[S4] 的 8 篇門檻沿用既有 `LUMOS_IMPACT_ABOUT_MAX` 常數與既有 `>=` 判斷式(scripts/lumos:21280),語意一致;但见 F1——大檔情境下家標記在自由席顯示不出來,等於「降噪」這件事在畫面上完全看不到效果,只有 JSON 層有差。
- 舊專案相容:`node_home.gate/ignore` 兩個設定鍵都是既有、已經在跑的介面(見上),沒有新專案需要額外遷移步驟;沒跑 `lumos update` 的專案照舊不受影響,spec 這句宣稱查證成立。
- 回滾:`LUMOS_IMPACT_HOME=0` 這條旋鈕目前還不存在(scripts/lumos 全庫搜尋不到這個字串),是本案要新增的——這點 spec 自己在名詞段已誠實標「新增」,不算未定義;旋鈕關閉後要退回的「舊的關於命中」那條路徑([S9])目前確實還活著、還在跑(`_impact_mark_about` 呼叫點 scripts/lumos:21657),回滾路徑在技術上是存在的,沒有查到死路。

總結:最高 severity major,blocking 共 5 條
