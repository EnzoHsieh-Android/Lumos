severity: major

# 治理帳例行紀錄分流 r2 整合審(外部投稿,第 2 版修訂稿)

審查對象:/tmp/gov-ledger-split-r2.md。立場:三個月後接手的人,預設文件與現實已對不上。
r1 折入的部分(繞道留版控、hard 規則、沿用 .ci-log、兩本各自吞錯、lint-new 計數不改)方向對,但折入時用「種類名稱精確比對」落實「繞道一律留」,對不上程式現況的實際種類(findings 1)。補進來的「消費專案本來就忽略」是未查證宣稱,查證為假(findings 2、3)。

## 〈盤點〉

1. 使用紀錄帳讀者的宣稱不實
severity: minor
blocking: 否(不影響 spec 的判定正確性,但同步範圍漏改多篇會說錯話,屬 minor)
引句:「只有本機的使用統計在讀,沒有任何判定讀它。」
佐證:
- `scripts/lumos:16186` 是 `.usage-log.jsonl` 唯一的程式碼出現處(寫);全 repo 沒有任何讀它的程式。`scripts/usage_scan.py` 讀的是 `~/.claude/projects` 的逐字稿,不碰這本帳(`scripts/usage_scan.py:1-12`)。
- `docs/lumos-toolchain-knowledge/Verification/2026-08-21_工具鏈體檢修復批.md:41-43` 明寫 write-only,並掛 `REVISIT:2026-11-19 這本帳還是零程式讀者就退場`。分流上線後這本帳停止追蹤,frecency 語料變成每台機器各一份,那條 REVISIT 的前提(「有宣告的未來讀者」)被動了,spec 完全沒提。
- 還在說「usage-log 寫進版控帳 / 事件帳」的筆記:`Systems/lumos-cli-read.md:34,37,58,140`、`Systems/retrieval-ranking.md:67`、`Systems/pitfalls-code-loop.md:33`(簿記白名單)、`Issues/code-loop-pass自失效追尾.md:17`。〈做法〉6 只點名 `Systems/reversibility-governance-ledger`,這幾篇不在同步範圍。
修法方向:〈盤點〉改寫成「目前沒有任何程式讀它」,同步範圍補上列筆記,並把 2026-11-19 的 REVISIT 與本案對齊。

## 〈範圍〉

已讀,無 finding(「不拆版控帳」「不動五本」與 〈全repo審視〉#18 一致)。

## 〈做法〉1 分流規則

2. 「留痕種類」用名稱精確比對,漏掉程式裡實際存在的略過類種類,跟本案自己的「略過、繞道一律留版控」保證互相矛盾
severity: major
blocking: 是(守衛面主風險;依 spec 字面實作,人給理由的略過紀錄會進本機帳,CI 與別台機器看不到)
引句:「skipped、skipped-env、fail-open、relaxed、degraded(略過、繞道、放寬設定、工具出錯自動放行的痕跡)」
佐證:
- `scripts/lumos:42844`:bound-tests 的人工略過旗標記成 `skipped-flag`(要求非空理由;`--skip-bound-tests --note` 的提示明說「會進治理帳被統計」,`scripts/lumos:44266`)。`bound-tests` 在觀察型名單上、`hard=False`、`skipped-flag` 不在名單 → 依三條規則會寫進本機帳。這正是 spec 〈實務隱患〉說要留版控的「略過」。
- `scripts/lumos:5787`:`check-j` 的 `shallow-skip`(hard 假、略過檢查的痕跡),同樣不在名單,而 `check-*` 在觀察型名單上 → 進本機帳。
- 既有讀者的慣例是前綴比對:`scripts/lumos:7988`(`gov --stats` 的「被跳過」用 `startswith("skipped")`)。spec 改成精確比對 5 個字,與現有慣例分岔。
- 其他降級類種類同樣沒被名單涵蓋:`bound-tests` 的 `unfilterable`、`whole-suite-deferred`、`range-unavailable`(`scripts/lumos:42851,42881,42945`)。是否算「繞道」spec 沒定義,名單只列名字不列判準。
- 既有測試 `scripts/test_lumos.py:8991` 斷言 `skipped-flag` 出現在治理帳;`Systems/bound-tests-gate.md:82` 的類別表也列了它。
- spec 自己的護欄「分錯只會偏吵,不會偏丟」(〈做法〉1 末段)在這裡不成立:`skipped-flag` 被分錯是「丟」(對 CI 隱形),不是「吵」。
修法方向:改成「kind 以 `skipped` 開頭或含 `skip`」加列舉 `shallow-skip`、`fail-open`、`degraded`、`relaxed`,或反過來把本機帳白名單縮到「已逐一列舉的 (閘, 種類) 配對」(只有 doctor-run、check-* 的 warned、ledger-growth、daily-wrapper、各閘 passed/hinted/none/covered/reminded 這類),其餘預設留版控。並加一條測試掃全檔所有 `kind` 字面值,逼每個種類都被明確歸類。

3. 觀察型名單的 `check-*` 是萬用字元,與「名單是唯一定義、沒放進名單就留版控」衝突
severity: minor
blocking: 否(表述歧義,實作者二選一都可通過 S1~S5 的測試)
引句:「兩份名單是唯一定義,各放一個常數,寫入器查它們決定路徑。」
佐證:
- 〈做法〉1 第一條寫「doctor 各段 check-*」,但 `_KNOWN_GATES`(`scripts/lumos:7771-7803`)是逐一列舉(check-s…s16、check-e1…e3、check-p2、check-p2s、check-lint-decl、check-j、check-r、check-k…),沒有萬用字元;`check-r`、`check-j` 另有 `hard=True` 事件(`scripts/lumos:1908,3394`)。
- 用前綴比對,未來新增的 `check-*` 閘會自動進本機帳,違反 spec 自己的「新增的閘…就照舊進版控帳」;用逐一列舉,spec 該列出來,否則「唯一定義」不是唯一。

## 〈做法〉2 本機帳

已讀,無 finding(`CI_LOG_NAME` / `_ci_log_path` 在 `scripts/lumos:38432,38525`,模式屬實;`_gate_event` 的 `docs = root / "docs"` 在 `scripts/lumos:1331-1333`,與「docs/ 不存在時不寫」一致)。

## 〈做法〉3 寫入器

已讀,無 finding(四支直接寫者屬實:`scripts/lumos:1358,1426,42423,43253`;`_bound_tests_log`、`_delguard_log_result`、`_loop_gov_mark` 確實轉呼叫 `_append_governance_log`)。

## 〈做法〉4 忽略規則與升級路徑

4. 「消費專案本來就忽略使用紀錄帳」為假;升級路徑對最需要的專案不補忽略規則
severity: major
blocking: 是(〈相容〉整段建立在這個前提上;不修會讓一批消費專案的目標完全達不到,而且本機帳有被 `git add -A` 帶進版控的路)
引句:「消費專案的 `docs/.gitignore` 從建 vault 起就忽略它」
佐證:
- `scripts/lumos:20868-20873` 與 `Verification/2026-08-21_doctor-run事件落地.md:30`:2026-06-26 到 2026-08-21 之間建的 vault,忽略清單寫在 `docs/<slug>-knowledge/.gitignore`(從來沒生效),不是 `docs/.gitignore`;`.usage-log`、`.ci-log` 是 2026-08-21 才補進清單(`scripts/lumos:20881`)。spec 把本 repo 的處境說成特例,實際是同期所有消費專案的共同處境。
- 〈做法〉4:`_init_additive_setup` 補規則時「`docs/.gitignore` 不存在就不建」。上述專案正是沒有 `docs/.gitignore` 的那批 → 本機帳在它們那裡是未追蹤檔,工作目錄照樣髒(目標失敗),且 `git add -A` 會把本機帳提交進版控,等於把例行紀錄塞回版控帳,與〈相容〉「偏吵,不偏丟」的說法不符(多出來的是髒,沒丟,但「例行操作之後工作目錄保持乾淨」這個目標對這批專案不成立)。
- 〈相容〉說「消費專案的使用紀錄帳本來就被忽略,不受影響」,對上述專案也為假(它們的使用紀錄帳仍被追蹤,本案只對本 repo 做 `git rm --cached`)。
- 追加細節未定義:`docs/.gitignore` 最後一行沒有換行字元(使用者手改過、或 Windows CRLF)時,直接「在尾端追加」會把新規則黏在上一行尾端(`.ci-log.jsonl.governance-local.jsonl`),兩條規則同時失效;「已有就不重複」用整行比對還是子字串比對也沒說(`_write_lf` 的行尾慣例見 `scripts/lumos:20879`)。
修法方向:(a) 缺 `docs/.gitignore` 時就建(只含帳檔忽略的內容,這是 `_scaffold_project` 已有的內容,不覆寫任何東西);(b) 追加前補換行、整行比對;(c) 〈相容〉改成誠實描述,並說明舊專案的使用紀錄帳要不要一起 untrack。

5. 回滾段自相矛盾,且「還原提交」對已停止追蹤的檔的行為未驗證
severity: minor
blocking: 否(回滾路徑的敘述問題,不影響上線判定)
引句:「還原本案提交即可。舊版不讀本機帳,上線期間的例行觀察在統計裡看不到(判定不受影響);使用紀錄帳要恢復追蹤得手動 `git add -f`。」
佐證:
- 同一句先說「還原提交即可」,又說「要手動 `git add -f`」。`git revert` 會把 `docs/.usage-log.jsonl` 的刪除還原成追蹤狀態,同時還原 `.gitignore` 的新增行;此時磁碟上已累積的 ignored 檔會被舊內容覆蓋(git 對 ignored 檔視為可覆寫) — 本機累積的使用語料靜默丟掉。⚠ 未實跑 revert 驗證;〈實務隱患〉最後一條「不可逆:…還原提交即回到原行為」至少該補「磁碟檔會被覆寫」或改成先備份。

## 〈做法〉5 讀者

6. S18 度量與 spec-gate 比例段共用小函式的「最舊一筆」語意沒定義
severity: minor
blocking: 否(〈天花板〉2 已承認跨機器誤判,這裡缺的是同機器上線初期的行為)
引句:「doctor 的 spec-gate 比例段與 S18 度量改成讀兩本(抽一支模組層級的小函式給它們共用,`cmd_gov` 的 `load` 不搬)」
佐證:
- S18 的暖機判斷依賴 `_gov_metric_events` 回傳的「最舊一筆」:`oldest > cutoff` 就整條度量不判(`scripts/lumos:3871-3875`,`_gov_metric_events` 在 `scripts/lumos:3820` 附近、檔尾讀取在 `scripts/lumos:3695-3705`)。兩本帳各自做「只讀檔尾」,各自有 `_from`/最舊值;合併後取 min 還是 max、版控帳被截尾而本機帳沒被截時怎麼算,spec 沒寫。取 max 會讓上線後 N 週內所有牽涉本機帳種類的度量靜默不判;取 min 則視窗宣稱涵蓋實際不連續的範圍。
- 度量只收 `blocked warned skipped-env hinted acked` 五種(`scripts/lumos:3973`):`warned`/`hinted` 的觀察型閘事件進本機帳,`blocked`/`skipped-env`/`acked` 留版控,同一條規則要跨兩本算,卻只有「跨機器」被列為天花板。
- 另有「doctor 帳本成長段」(`scripts/lumos:2238-2300`)寫 `ledger-growth` 事件,而該事件本身在觀察型名單上 → 走進它所監看的那本本機帳;spec 只說「加一行同門檻的軟提醒」,沒說新提醒是否也落帳、落哪一本。

7. 判定類讀者清單漏列一個直接開檔的讀取點,但該讀取點只讀 design-loop,結論不變
severity: minor
blocking: 否
引句:「判定類讀者一行不改」
佐證:
- 清單之外還有直接開 `.governance-log.jsonl` 的讀取點:`scripts/lumos:1250`(rewrite 血緣,spec 已列)、`scripts/lumos:11146`(`_escape_released_loops`,spec 已列)、`scripts/lumos:25543`(lint-new 計數,spec 已列)、`governance/autonomous_loop/replay_weekly.py:38`(spec 已列)。逐一核對,四者讀的閘都不在觀察型名單;**結論成立**,但 spec 沒要求任何機械釘子防止「日後有人讓判定類讀者去讀觀察型閘」。S3 只斷言現況。這是 minor:補一條掃描釘(判定類讀者的閘集合與觀察型名單不相交)即可。

## 〈做法〉6 既有測試與文件同步範圍

8. 同步範圍只點名一篇筆記、用泛稱「手冊…scaffold 註解」,漏掉會說錯話的具體位置
severity: major
blocking: 是(使用者問題的核心:同步範圍夠不夠;下列位置分流後會變成錯誤指示,且其中兩條 REVISIT 就在本案上線後一~兩週內到期)
引句:「手冊提到治理帳寫在哪裡的段落、scaffold 的註解,一起改。」
佐證(逐項):
- 到期 REVISIT 會讀到空的:`Projects/合約測試閘什麼時候跑_計劃.md:282`(REVISIT:2026-10-07「查治理帳 `red-advisory` 的筆數」;`red-advisory` 是 bound-tests、hard 假 → 進本機帳)與 `Projects/守檔筆記對照改動_計劃.md:32`(REVISIT:2026-10-15 量治理帳 `note-reread` 的各事件;`reminded`/`covered`/`none` 進本機帳)。在別台機器或 CI 查版控帳會得到 0,結論是「只提醒就夠了」,這是會影響升級成擋的人裁判準。〈天花板〉沒列。
- 數字標記:`Systems/reversibility-governance-ledger.md:31` 的 `<!--lumos:count=6 re=(?m)^\s+load\((?:\"\.|CI_LOG_NAME) in=scripts/lumos-->` 只認 `load(".…` 與 `load(CI_LOG_NAME`;spec〈做法〉2/5 要照 `CI_LOG_NAME` 的樣子用常數 `GOV_LOCAL_LOG_NAME`,`load(GOV_LOCAL_LOG_NAME,` 不會被這條正則數到 → 實際讀 7 本、標記仍 6、Check N 不報(靜默漂),或寫成字面值則變 7 與敘述「ci 條件載入」對不上。
- 該篇筆記裡實際措辭:`reversibility-governance-ledger.md:54`(「doctor 是唯一新寫者」)、`:103`(「帳檔已入 git 追蹤,非 gitignore」)才是 spec 想改的;spec 用的「來源幾本」「帳檔都進版控」不是原文,接手的人要自己猜是哪句。
- 手冊:`skills/lumos-project-notes/reference.md:61`(「彙整 bypass/rot/governance-log」,少一本;還提到已拆除的 rot)。
- 程式內說明:`scripts/lumos:20877-20881`(scaffold 忽略清單的說明文字「治理帳刻意不在這裡」仍成立,但清單要加一行,同一段說明要更新);`scripts/lumos:2236-2238`(帳本成長段註解「這本帳有四個整檔讀者」);`scripts/lumos:3867`(S18 註解「同 doctor 其他讀治理帳的段落」)。
- 既有測試:`scripts/test_lumos.py:416-424`(斷言治理帳不被忽略,正確,但同組要加本機帳被忽略)、`:42493`(`t_init_gitignore_matches_design` 要擴)、`:5954-5955,6038-6058,8907-8991,10509,15394,23716,25031`、`scripts/test_autonomous_loop.py:1736`(斷言例行事件落在 `.governance-log.jsonl`)。spec 交給「實作時 grep」,沒有數量;這批裡 8907-8991 一組(bound-tests)直接與 findings 2 相撞。
修法方向:〈做法〉6 改成逐檔清單(含上列 file:line),把「到期 REVISIT 的查法」列為同步項,並在天花板補一條「手冊與 REVISIT 裡寫『查治理帳』的指示,分流後要改成 `lumos gov`(兩本合併)」。

9. 工具鏈來源 clone 的升級路徑(`_pull_source_or_abort`)沒被提到
severity: minor
blocking: 否(走完程式碼推演可以通過,但沒有測試,屬應補)
引句:「⑤改到的既有測試、圖譜筆記與手冊同步。」
佐證:
- `scripts/lumos:20529-20640`:消費專案的 `lumos update` 先在來源 clone 拉新版;來源 clone 因 `lumos show/context` 而常態弄髒 `docs/.usage-log.jsonl`(`scripts/lumos:20553` 註解寫的正是這個症狀)。本案那個提交把 `docs/.usage-log.jsonl` 從追蹤移除後,舊版 `_pull_source_or_abort` 走「聯集合併」:`git checkout --` → `pull --ff-only`(檔案被刪)→ 以 `f.exists()` 分支補回本機行(`scripts/lumos:20620-20632`),我逐行推演可以重建檔案,不會擋人。但這條路徑目前唯一的測試(`scripts/test_lumos.py:38684-38728`)用的是「檔案仍被追蹤」的情境,「上游把追蹤中的簿記檔移除」沒有任何測試覆蓋;而且這是本案唯一會影響所有消費專案升級的步驟。⚠ 未實跑。
- `_BOOKKEEPING_FILES`(`scripts/lumos:24193`)與 cochange 排除清單(`scripts/lumos:36525`)應保留 `docs/.usage-log.jsonl`(舊版來源 clone 與消費專案仍需要),spec 沒說保留還是移除;移除會讓聯集合併分支對尚未升級的舊 clone 失效。

## 〈驗收條款〉

10. S1 的「所有進版控的檔一個位元組都不變」缺基準與例外
severity: minor
blocking: 否
引句:「所有進版控的檔 應 一個位元組都不變,例行紀錄 應 出現在本機帳 [test:t_gov_split_routine_goes_local]」
佐證:
- 測試內的假 repo 會跑 pre-commit/pre-push 的哪幾道,spec 沒枚舉;`bound-tests` 的 `green` 與 `nodehome-check`/`drift-check` 的 `passed`、`delguard` 的 `ok` 才算「例行」,但 findings 2 所指的 `skipped-flag` 路徑不會被這條測試觸到,所以 S1 + S2 兩條組合起來仍測不出名單漏洞。S2 的矩陣(「擋人、略過或繞道痕跡、自動放行或主動決定」)應逐種類枚舉成表,而不是列舉代表。
- S4/S5 與寫入細節一致,已讀,無 finding。

## 〈天花板〉與〈實務隱患〉其餘

已讀,無 finding(〈實務隱患〉「金流/對外送出/不可逆」三條已排除屬實:兩本帳皆 append,停止追蹤不刪磁碟檔)。

## 總結

最嚴重 severity: major(3 條 blocking:留痕種類名單漏 `skipped-flag`/`shallow-skip` 與保證矛盾;「消費專案本來就忽略」為假、升級路徑不補忽略規則;同步範圍漏掉兩條近期到期的 REVISIT、數字標記與多篇筆記);其餘 7 條 minor。
