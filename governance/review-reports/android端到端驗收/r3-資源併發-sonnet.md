severity: major

審查範圍:只審〈資料怎麼流〉第 4、5 步、〈查證紀錄長怎樣〉、〈推送前怎麼按功能判〉、S8–S14、S17、S29–S33、〈實務隱患〉、〈回退〉。已實作的部分只當背景讀。
我跑過的實驗都在 `/tmp/lumos-seat-work/android端到端驗收/資源併發-sonnet/` 下,收齊後已用字面路徑刪除。

**1. 主線版 `e2e` 段讀不到時,會被當成「沒有這一段」而靜默放行**
severity: major
blocking: 是。實作者照現有函式接,就會做出判不清卻放行的閘,跟 S17、WHY「判不清就擋」直接矛盾。
引句:「判不清就擋(回 1),跟安全證據閘一樣不走 fail-open」
- 哪一段:〈資料怎麼流〉第 4 步「主線版沒有 `e2e` 段→不跑」、第 101 行「判不清就擋」、S17。
- 問題:spec 沒要求閘自己區分「檔真的不存在」和「git 讀不出來」。現有 `_e2e_config_at` 靠 `_lumos_config_at_ref` 判斷,後者在 `git show` 失敗後再跑 `git cat-file -e`,只要它的回傳碼不是 0 就判成 `missing`。
- 失敗例子:
  - 輸入:主線提交裡的 `.lumos/macrobench.json` 那個 blob 讀不到(部分複製、離線、git gc 與別的程序競爭)。
  - 預期:S17 擋下,理由是主線版設定讀不到。
  - 實際:我造了這個狀況(刪掉 blob 物件檔),`_e2e_config_at("…","HEAD")` 回傳 `(None, None)`,也就是「檔不在」。閘就會走「主線版沒有 `e2e` 段→不跑」,整道默默放行,連治理帳都不記。
- 佐證:file: `scripts/lumos:55282-55294`(`cat-file -e` 回傳碼 1 就判 missing);file: `scripts/lumos:40524-40534`(`_e2e_config_at` 的 docstring 只提醒要「再擋一次」BOM,沒提這個洞)。

**2. 寫入鎖被 TERM 或 HUP 殺掉後不會自癒,而 waive 是閘唯一的出口**
severity: major
blocking: 是。出口被殘留鎖卡死,實作者照「照 lint-waive 的鎖」字面做會做出壞系統。
引句:「包在鎖裡(照 lint-waive 的讀改寫鎖),寫入用 `_write_lf`」
- 哪一段:第 108 行「judge 與 waive 的讀改寫包在鎖裡(照 lint-waive 的讀改寫鎖)」、〈實驗室驗收〉「鎖」那條、第 121 行的暫存檔說明。
- 問題:
  - spec 只替裝置鎖寫了「程序已不在就清掉接手」,也只驗了裝置鎖。
  - 紀錄用的 `_vault_write_lock` 明寫「過期也不自動接手」,搶不到就等 60 秒後丟 `WriteBlocked`。
  - 只有走 `finally` 的例外會放鎖。終端被關(HUP)、TERM、kill -9 都不會放,而第 94 行自己就預期會有這幾種訊號。
- 失敗例子:
  1. 在 `with _vault_write_lock(p)` 內對程序送 TERM。
  2. 之後每一次 judge、waive、`waive --ack` 都等滿 60 秒再失敗,訊息要求「人工清鎖」。
  3. 鎖檔在 `~/.cache/lumos/vault-lock/` 下,我實測 `WriteBlocked 60.0`。
  4. 被擋的推送要靠 waive 放行,放行寫不進去;spec 只剩 `LUMOS_SKIP_ANDROID_E2E` 一條路,且沒說怎麼清鎖。
- 佐證:file: `scripts/lumos:28569-28620`(`_vault_write_lock`);file: `scripts/lumos:61522-61555`(`_excl_lock_try` 不接手)。

**3. waive 終端確認的等待行為,spec 的說法與 `_confirm_tty` 不符,也沒定「鎖和確認誰先」**
severity: major
blocking: 是。無人看顧的流程可能永久卡住,或確認期間持鎖把別的寫入逼到逾時。
引句:「有終端但沒人答時等 `LUMOS_TTY_TIMEOUT` 秒,預設 30」
- 哪一段:第 107 行「有終端但沒人答時等 `LUMOS_TTY_TIMEOUT` 秒,預設 30」、第 108 行鎖。
- 問題一:
  - `_confirm_tty` 的逾時只套用在 `/dev/tty` 那條路。
  - 只要 `sys.stdin.isatty()` 為真,它走的是沒有逾時的 `input(prompt)`。
  - 例子:AI 或排程在掛著 pty 的 tmux 或 ssh 裡跑 `waive`,永遠不回,沒有「記成 AI 放行」。
  - 同一條也讓 `--ack` 無法在無人時結束。
- 問題二:
  - spec 沒說 `_confirm_tty` 在鎖外還是鎖內。
  - 放在鎖內:人想了超過 60 秒,另一個 judge 或 waive 就 `WriteBlocked` 失敗。HUP 還會殺在鎖內,連到問題 2。
  - 放在鎖外:確認和寫入之間紀錄可能已被別的程序改過,但「讀改寫」本來就是在鎖內重讀,所以應該鎖外確認。這個順序 spec 要寫明。
- 問題三:Ctrl-C 在提示時,spec 沒寫回傳碼和有沒有寫帳。
- 佐證:file: `scripts/lumos:33561-33605`(`input()` 無逾時;逾時只在 `select`)。

**4. 閘沒有整道時間預算,逾時也不在 S17 的列舉裡**
severity: major
blocking: 是。推送前時間預算的行為是實作者會做錯的決定。
引句:「用同一份設定算分岔點與被推送提交兩端的指紋,不同才要求」
- 哪一段:第 4 步全部、S8、S17、S31–S32。
- 問題:
  - 同一個檔裡,安全證據閘有 `_SECEV_BUDGET_SEC = 60` 的整道截止時間,每次 git 都取「剩餘預算」(`_secev_git_left`),用完丟 `_SecevTimeout`,判成整道 evaluation_timeout 並擋下。
  - 這道新閘沒有這個機制。現有 `_e2e_fingerprint` 對 `git ls-tree` 單次固定 120 秒;設定讀取走 `_lens_git` 預設 10 秒或 20 秒。
  - 一次推送最少是:主線挑選、分岔點與被推送提交各一次整個 repo 的 `ls-tree -r --full-tree`、設定讀取、紀錄讀取、按功能的 `git diff`。
  - pre-push 沒有外層逾時(`scripts/hooks/pre-push` 搜不到 `timeout`),CI 的 `code-loop check` 也不會有總預算。
- 失敗例子:
  - 輸入:`--filter=tree:0` 的部分複製、慢速網路磁碟,或一次推 N 個 ref(每個 ref 都重算)。
  - 實際:每個 ref 最壞 2×120 秒加上 20 秒的小呼叫,推送卡住數分鐘到數十分鐘。逾時回傳 `None`,和 git 回非 0 不分,訊息只會說「列不出檔案樹」。
- 數字佐證:
  - `ls-tree` 是整個 repo 不是 `app_dirs`。
  - 我用合成輸入跑 `_e2e_fingerprint`:500k 檔約 0.9 秒、峰值約 385MB;1M 檔約 2.7 秒、峰值約 733MB。
  - 所以「上萬檔也是一次 git 呼叫」成立,但記憶體和時間是跟全 repo 大小成正比,不是跟 `app_dirs`。
  - CPU 沒有問題,問題是沒預算、沒 pathspec。
- 佐證:file: `scripts/lumos:8510-8530`、`9630-9645`(安全證據閘的預算);file: `scripts/lumos:40543-40550`(固定 120 秒的 `ls-tree`)。

**5. `doctor`、`enforcement`、`waive --list` 掃全部紀錄,舊指紋的 AI 放行永遠「待看」**
severity: minor
blocking: 否。有 `--ack` 這個出口,只是持續吵人。
引句:「`lumos doctor` 把還沒人看過的 AI 放行列成提醒」
- 哪一段:第 110–111 行、S14。
- 問題:
  - 第 123 行說舊紀錄不自動刪,所以每個舊指紋的紀錄永遠留著。
  - 通知掃的是工作目錄裡整個 `.lumos/e2e-records/`,不是「被推送提交的那份」。
  - 一筆很久以前的 AI 放行沒被 ack,`lumos enforcement` 就永遠標「沒生效」,而 `--ack` 又要人到終端回答。
  - 開場提示每次都要把所有紀錄讀進來解析,沒有數量或時間上限;紀錄損壞時也沒說怎麼處理。
- 失敗例子:跑了一年累積數百份紀錄,其中一份舊指紋有未看的 AI 放行 → 每個開場提示都帶這條。

**6. `CI` 環境變數有設成任何非空值,閘就靜默跳過,不留帳**
severity: minor
blocking: 否。單人威脅模型下是個意外跳過,不是被攻擊。
引句:「在 CI 裡(`_in_ci`)不跑這道,印一句」
- 哪一段:第 97 行「在 CI 裡(`_in_ci`)不跑這道」。
- 問題:`_in_ci()` 是 `bool(os.environ.get("CI") or …)`,所以 `CI=false`、`CI=0` 一樣算真。
- 失敗例子:終端或工具 export 了 `CI=0`,本機 `git push` 時閘不跑,只印一句「第一版只在本機推送時判」。這個出口不記治理帳,和「出口是環境變數且有留帳」(WHY、第 36 行 REVISIT 的 skipped 計數)矛盾,資料會漏算。
- 佐證:file: `scripts/lumos:225-229`。

**7. 暫存檔殘留、判定用牆鐘時間比先後**
severity: minor
blocking: 否。兩者都要較少見的前提。
引句:「寫一半被殺留下的 `<指紋>.json.<…>.tmp-wlf` 暫存檔,判定只讀 `<指紋>.json`,不受影響」
- 哪一段:第 121 行、第 119 行與 S30。
- 暫存檔:
  - `_write_bytes_atomic` 只在例外時刪暫存檔,TERM、kill -9 會留下 `<指紋>.json.<pid>-<隨機>.tmp-wlf`。
  - 該目錄屬簿記,`_dirty_non_bookkeeping` 不看它,所以不會被擋。使用者若 `git add -A` 或 `git add .lumos`,半截 JSON 就進版控,而且永遠沒人清。
  - spec 只說「判定不受影響」,沒說清除或避免。
- 牆鐘比較:
  - S30 和「取較新的那個」靠兩個 `ended` 的牆鐘時間比,兩份結果可能出自不同機器或時鐘被調過。
  - 例子:機器 B 時鐘慢 5 分鐘,它的按功能失敗(實際較晚)標成比整套 pass 更早,判定就看不到那筆失敗,放行。
  - 時間精度是秒,同一秒的兩筆沒定義誰贏。

**已讀,無 finding**
- 〈實務隱患〉:已讀。金流、對外送出、不可逆都寫了排除理由,資源類的缺口已在 4、5、7 列出。
- 〈回退〉:已讀。
- S9–S11、S13、S29、S31–S33:已讀。它們的時序問題在上面幾條,本身沒有另外的洞。

**交叉引用核對**:`pp_cl_reason`、`_PPC_KIND_SENTENCES`、`_cl_say_block`、`_codeloop_kg_finish`、`_secev_mainline_pick`、`_KNOWN_GATES`、`LUMOS_TTY_TIMEOUT` 都存在。〈推送前一次列出全部擋下原因_計劃〉、〈Android效能判定統計化_計劃〉、〈截圖基準驗收流程_計劃〉都在。

**固定席:這份設計會不會破壞節點宣稱的行為或合約**
- bound-tests-gate 的合約(★INVARIANT★:綁定測試任一紅、懸空、偽證據就 `blocked=True` rc1;沒綁就不擋但記 gate=bound-tests):不影響。新閘是獨立種類 `android_e2e`,接在 `_cl_say_block` 與 `pp_cl_reason`,沒碰綁定測試的判斷和帳。
- pitfalls-code-loop:不影響合約本身。只有「簿記目錄清單」多一項 `.lumos/e2e-records/`,現有程式已加。
- 補充:新閘排在「所有放行早退之前」會讓 `code-loop check` 每次多付發現 4 說的成本。

最嚴重的 severity 是 major,blocking 共 4 條(發現 1、2、3、4)。
