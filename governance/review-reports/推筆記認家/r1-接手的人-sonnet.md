severity: blocker

### F1 [S2] 讓「家」變成第四條保送入口,直接牴觸現有測試與 docstring 鎖死的「about 不是第四條入口」設計
severity: blocker
blocking: 是 — 不改,實作者會在不知情下推翻一條已用兩輪設計審+機械測試鎖住的決定,等於重蹈舊案 r1/r2/r3 的同一種錯。
引句:「家一定進候選、而且進必推名單,不必正文用反引號寫這支檔」
1. `scripts/lumos:21269-21271`——`_impact_mark_about` 的 docstring 明寫「★不改任何一條路徑的 pinned 邏輯★——about_hit 不是第四條入口,free 候選命中後仍是 free」,這正是固定席扇出降權_計劃 r1 被打穿、r2/r3 收斂後鎖定的行為。
2. `scripts/test_lumos.py:914`——現行測試 `t_impact_about_hit` 斷言「★⑨free 候選 about 命中 → 仍 free(不是第四條入口)★」目前是綠的;[S2] 字面實作會直接讓這條翻紅,spec 全文沒有一處提到這支測試或這句 docstring,也沒有討論要不要／如何改寫它。
3. 舊案「合約候選」第 5 條「about 判定不覆寫 hit 欄、不是第四條入口」是 design-loop 三輪收斂後才敢寫的裁定,本案要推翻它至少要在 spec 裡正面回應,不能是實作時才發現的副作用。

### F2 重提丙的「新證據」用的是別的圖譜,不是本工具鏈自己的評測語料,在自己圖譜上「漏標率壓到零」並不成立
severity: major
blocking: 是 — 不改,實作者會在錯誤的前提(precondition 已滿足)下動手,而評測(S10)本身就跑在這份不成立的語料上。
引句:「三個 POS 專案整理後健檢 S8 幾乎沒有沒家的檔」
1. `docs/lumos-toolchain-knowledge/Verification/2026-09-11_每支檔有家落地.md:26`——每支檔有家自己的落地紀錄寫「在本工具鏈自己的圖譜上跑健檢:沒有家的程式檔 43 支……都是上線前的舊帳,只提醒」;本次在凍結副本上重跑 `lumos doctor --verbose` 的 S8 段仍顯示 44 支還沒有家的舊檔(同一量級,非個案)。
2. 但 `governance/eval/retrieval_eval.py` 的 train/held 評測與 [S10] 的驗收都是跑在 `docs/lumos-toolchain-knowledge` 這份圖譜上,不是 POS 圖譜——「新證據」引用的改善發生在別的語料,精確地說「本案要動的這份圖譜」的漏標率並沒有被證明壓到零。
3. 舊案 d4 的原話是「丙需先把 about 漏標率壓到零,無新證據不重提」,用別的專案的改善去滿足這句話裡「零」的門檻,是把 precondition 的驗證範圍偷換掉了。

### F3 [S11] 新增的 lint 硬擋沒有同步 Check J 另外兩處自己的權威描述(check-j-regen-guard 摘要、reference.md「機械把關的真實範圍」)
severity: major
blocking: 是 — 不改,下一個 session 讀這兩篇會拿到跟實際行為不符的「Check J 只擋什麼」清單,正好是這個鏡頭要抓的知識不同步。
引句:「快查表(commands/09)與完整版(reference.md)兩處一致」
1. `skills/lumos-project-notes/reference.md:1100`——「機械把關的真實範圍(誠實地圖)」這段明列「硬擋=J-a/J-b/J-c;J-d……只計數提醒」,沒有 about_code 缺失這一項;[S11] 上線後這段就跟不上新規則,而 spec 只承諾 commands/09 與 reference.md 步驟 4/6 兩處一致,沒提到這一段。
2. `docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md:24`——check-j-regen-guard 自己的 summary KEY 行同樣只列 J-a/J-b/J-c/J-d,是 Check J 行為的另一份權威描述,[S12] 的「兩處一致」也沒把它算進去。
3. 這正是本鏡頭要查的「乙那一半跟既有 regen 章規則、Check J……是不是講同一件事」——目前是不同一件事,而且沒被點名。

### F4 [S11] 的絕對必要條件跟 [S13]／範圍外承認的「合法不管檔的主題型 regen 節點」互相打架,沒有逃生口
severity: major
blocking: 是 — 不改,照 SOP 合法建出的主題型 regen 節點會被 lint 永久擋死,接手人找不到任何文件寫的出路。
引句:「確定要這樣,就在負責範圍講清楚它不管檔的理由」
1. [S12] 規定「每篇還原節點都要帶 `--code`」是無條件的,但 [S13] 同時允許 `lumos new system` 不帶 `--code`(只印提醒、不擋),範圍外一段也承認「概念型、跨模組的說明篇是合法的」——這兩句預留了合法的「不管任何檔」的 regen 節點。
2. 名詞定義寫「從程式重建的節點:蓋了 `regen: from-scratch/<日期>` 章的 Systems 節點」,沒有排除主題型節點;一旦這種節點被蓋上 regen 章,[S11] 的 lint 硬擋就沒有任何條件能讓它通過(不像檔案層級有 `node_home.ignore` 可以豁免)。
3. Spec 沒有替「節點」層級設計對應 `node_home.ignore` 的豁免機制,這是三個月後接手人第一次還原一篇主題型節點時就會撞到的牆。

### F5 「新證據」的論述跟 spec 自己承認的「家不驗語意」互相矛盾
severity: minor
blocking: 否 — 這是論述內部不一致,不直接讓實作者做錯決定(F2 已經從數字面把同一個問題釘死),但屬於「內部不一致」例外,規則要求一律要報。
引句:「每支檔有家只驗路徑、不驗語意」
1. 「為什麼」段用每支檔有家的落地當作滿足舊案「about 漏標率壓到零」precondition 的新證據;但舊案當年關切的漏標(必看 2/9、3/5 沒被 about 蓋到)是語意層的完整度問題,不是路徑存在與否。
2. 實務隱患段自己承認「每支檔有家只驗路徑、不驗語意」,等於承認新證據沒有觸及舊案真正關切的那個維度——這句話跟「為什麼」段的論述立場是矛盾的。

### F6 [S4] 的「大檔」門檻沒說清楚沿用哪個計數函式,跟 [S1]「同一個函式,不另寫一套」的承諾有落差
severity: major
blocking: 是 — 不寫清楚,實作者很可能圖方便直接重用既有的 `_impact_about_counts()`,結果違反 [S1] 自己訂的「家的定義沿用每支檔有家那一支」。
引句:「家的定義與比對鍵沿用每支檔有家那一支(同一個函式,不另寫一套)」
1. `scripts/lumos:17995-18006`——`_nodehome_homes` 只算 `type=="system"` 且 `status` 在 doing/done/stale 的節點,是每支檔有家用的「家」定義。
2. `scripts/lumos:8822-8833`(即現行 `_impact_about_counts`,巨檔門檻 `LUMOS_IMPACT_ABOUT_MAX` 現在讀的對象)不篩 type/status,算的是全部掛 about_code 的節點——同一支檔在兩個函式下的計數會不一樣。
3. [S4] 只說「大檔:家的篇數 ≥ `LUMOS_IMPACT_ABOUT_MAX`」,沒說這個「家的篇數」要用哪個函式算;兩個函式都在,又共用同一個環境變數名字跟預設值 8,實作時猜錯就是兩套「大檔」判準各算各的。

### F7 [S6] 承諾的測試 `t_impact_diff_keeps_homes` 沒被收進「驗收怎麼跑」的任何一個 `-k` 子集
severity: major
blocking: 是 — 不改,照 spec 自己寫的驗收流程跑完,這支測試永遠不會被執行,壞了也不會被擋下來就能過關。
引句:「[test:t_impact_diff_keeps_homes] [test:t_dispatch_lens_includes_homes]」
1. 「驗收怎麼跑」列的八個 `-k` 關鍵字是:`impact_home`、`impact_pins_order`、`dispatch_lens_includes_homes`、`about_stamp_no_longer`、`regen_node_requires`、`restore_sop_requires`、`new_system_without_code`、`impact_hook_shows_home`。
2. 逐一核對 13 支候選測試名,`t_impact_diff_keeps_homes` 這個字串不含在任何一個關鍵字裡(`impact_home` 匹配不到 `impact_diff`),是唯一漏掉的一支;同一條 [S6] 底下的另一支 `t_dispatch_lens_includes_homes` 有被 `-k dispatch_lens_includes_homes` 收到,不對稱地漏了前半句。
3. 這正是驗收要求第 4 點提醒的那類「寫了測試名不等於測試存在/被跑到」的坑,只是這次是「被跑到」那一半漏了。

---

## 逐節讀完結果(未列入 finding 的部分)

- **frontmatter(lands_in/summary 三行 KEY)**:內容與正文一致,問題已併入 F1/F2/F3 討論,不重複列。
- **名詞**(家/必推名單/可選名單/大檔/從程式重建的節點):逐條對過 `_nodehome_key`/`_nodehome_homes`/`LUMOS_IMPACT_ABOUT_MAX`/`regen` 欄位定義,已讀,無 finding。
- **[S3]**:跟現行 `scripts/lumos:21661` 的 `pins.sort(key=lambda r: (r["kind"] != "incident", not r.get("about_hit", False)))` 逐字對得上,已讀,無 finding。
- **[S5]**:純加法敘述跟現行三軸邏輯不衝突,已讀,無 finding。
- **[S6]** 除 F7 指出的驗收漏項外,「diff 聚合丟排序」「dispatch-lens 完全沒用到 about」兩句都查證屬實(`scripts/lumos:21948-21949`;`scripts/hooks/claude/dispatch-lens-hook.py` 無 about_hit/about_code 字樣),已讀,無 finding。
- **[S7]**:新旋鈕命名與慣例(`_impact_knob`)一致,已讀,無 finding。
- **[S8]**:`scripts/hooks/claude/impact-hook.py:647` 現在讀 `about_hit` 印 `★關於★`,改成 `★家★` 是同一行的字串替換,已讀,無 finding。
- **[S9]**:`lumos about-code restamp/revert/migrate-stamp` 三個子命令、`cmd_new` 的 `--code` 走 `cmd_append` 不寫 stamp,皆已用 `--help` 與程式碼核對存在,已讀,無 finding。
- **[S10]**:`out_top3_must` 鍵確實存在於 `governance/eval/retrieval_eval.py:477/541/581` 且不進 `gates`,跟 S10「只印、進 history、manual 比對」的說法一致,已讀,無 finding。
- **[S12]** 除 F3/F4 指出的落差外,SOP 步驟 4 現況(commands/09、reference.md)確實只寫 `--code` 起手式、沒寫「必要」二字,與前掃結論一致,已讀,無 finding。
- **驗收怎麼跑** 除 F7 外,其餘 7 個 `-k` 關鍵字都能對應到對的候選測試名,已讀,無 finding。
- **回頭條件、合約候選、審計修正紀錄**:格式與既有慣例(REVISIT 帶日期、候選≠已標)一致,已讀,無 finding。

## 固定席逐條判(這份設計會不會破壞該節點宣稱的行為或合約)

- **Systems/retrieval-ranking**:`lumos contracts retrieval-ranking` 顯示合約 0 條,沒有機械合約可破;但本案 S2/S3/S6 改的正是它 KEY 行描述的排序行為,且撞上 F1 指出的既有測試——判「不直接破合約(沒有合約),但會讓它現有行為描述失真,需要在同一次提交同步改寫」。
- **Systems/節點還原**:「這篇沒有登記任何『動了會壞』的合約」(`lumos contracts` 輸出);S12 只改 SOP 文字與新增一道 lint 檢查,不改機制本身——判「不影響」,理由是沒有合約可影響,但如 F3 所述遺漏了要同步的另外兩處文件。
- **Systems/check-j-regen-guard**:合約 0 條、技術債 1 條(宣告制 opt-in);S11 新增一條硬擋規則屬於擴大 Check J 範圍,不是破壞既有規則本身——判「不算破壞既有合約(沒有),但擴大了它管轄的範圍卻沒同步摘要」(即 F3)。
- **Issues/canary-record未落盤事件**:講的是 canary record 寫入未落盤的獨立事故,跟本案的 about_code/家/regen 機制無關,只是因為 pitfall_when 命中 `governance/eval/retrieval-goldset.json`(S10 驗收指令提到同一份檔)——判「不影響」。
- **Issues/code-loop守衛main-direct盲區**:講 pre-push 在 main-direct 工作流下 code-loop 硬擋空轉,跟本案改的 impact ranked/lint/SOP 三塊機制不重疊——判「不影響」。
- **Issues/hook卸載殘留註冊**:講 hook 安裝/卸載生命週期不對稱的舊事故,本案沒有新增或移除任何 hook 註冊——判「不影響」。
- **Issues/init-force-slug誤用basename**:講 `lumos init --force` 的 slug bug,跟本案完全不同的程式路徑——判「不影響」。
- **Issues/vendored測試套件在消費端假紅**:講消費端測試覆蓋守衛的假紅問題,本案新增的測試都走同樣的既有覆蓋機制,沒有引入新的 vendored 落差——判「不影響」。

## 實務隱患鏡頭(逐類答)

- **效能(Edit 前推筆記在熱路徑上)**:spec 說「既有的 about 計數已經有快取,本案沿用,不另掃一次」——這句只對「巨檔門檻計數」成立;[S2] 要新增「家」候選清單本身需要 `_nodehome_homes` 這個回傳 `{檔: [節點]}` 的函式,跟現有只回傳 `{檔: 數量}` 的 `_impact_about_counts` 快取是兩份不同的資料結構(細節見 F6),不是單純沿用同一份快取就夠;規模上兩者都是 O(全部節點) 一次全掃,在 30 秒/20 秒預算內應仍可行,但「不另掃一次」這句話本身不夠精確。
- **噪音與召回的取捨**:這正是 F1/F2 的核心——把家變成第四條入口,等於重新打開舊案三輪設計審否決、且機械測試鎖住的那個口子;[S4] 的大檔門檻沿用了舊案「held 22 誤放全出自改主程式」的教訓,方向正確,但沒解決 F1 指出的「入口本身該不該開」這個更上游的問題。
- **舊專案相容**:家的機制是 additive-only,沒填 about_code 的舊專案這條路徑不會觸發,行為退回既有三軸——這部分沒有 finding;但 F4 指出的 regen-lint 新規則會影響所有之後跑節點還原 SOP 的新舊專案,不是「舊專案不受影響」可以一概而論。
- **回滾(關掉旋鈕能不能完全回到原樣)**:新旋鈕 `LUMOS_IMPACT_HOME=0` 與既有 `LUMOS_IMPACT_ABOUT=0` 是兩個獨立開關,spec 沒有寫兩者疊加時(例如 HOME=1、ABOUT=0)的行為該是什麼樣子;沒能指出具體會壞在哪一行,不升等為正式 finding,但建議實作時補一條測試把這個組合釘死。

總結:最高 severity blocker,blocking 共 6 條
