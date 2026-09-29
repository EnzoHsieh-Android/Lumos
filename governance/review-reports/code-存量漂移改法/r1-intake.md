# r1 收貨紀錄(code-存量漂移改法)

凍結材料:19162c1e..53b6389c 的 git diff -U10,3210 行,超過 1800 行,拆成三份:
- r1-snapshot-a.patch(scripts/lumos,1776 行)、r1-snapshot-b.patch(scripts/test_lumos.py,847 行)、r1-snapshot-c.patch(圖譜筆記與 skills 文件,587 行);整份 r1-snapshot.patch 留作記帳的審材(各席記帳一律填整份的指紋)。
分級:pitfalls --diff 判 high(命中風險型樣);沒有觸發要表態的效能檢核題。
8 席:正確性 opus、邊界 sonnet 5.5、併發回滾 sonnet 5.5、合約圖譜 sonnet 5.5、spec 對照 sonnet 5.5、架構對齊 sonnet 5.5、資安 sonnet 5.5、外家 finder Codex(gpt-5.6-sol xhigh,唯讀沙盒)。外家否決席留到有低共識 major 時當辯方——本輪五條 major 都有可執行證據或多席一致,不開庭。
偏離:實作在會談外的複製倉庫,派工鏡頭 hook 以會談倉庫算範圍會算錯,改由編排者先跑 `lumos dispatch-lens 19162c1e..HEAD` 存檔、當參考資料交給各席(不是 hook 自動附加)。

## 席位收貨

- 8 席全交,等完成通知、ls 確認後才讀;clone-ns 的 reflog 只有編排者自己的提交,席位沒動 repo(各席實驗都在自己的 git clone --shared 臨時目錄)。
- report-normalize:4 份原樣合格;合約圖譜、架構對齊、邊界、外家 4 份最後一行「max severity: …」被當成沒正規化的宣告,退回原席自己改成「最高等級:…」(Claude 三席用續談、Codex 用 codex exec resume 同一會談重出;Codex 兩版 diff 只差這一行)。編排者沒動任何報告。
- quote-check:7 份對整份凍結 patch 全錨定;spec 對照席引的是設計計劃原文,對 `docs/lumos-toolchain-knowledge/Projects/存量漂移改法_計劃.md` 全錨定。
- refcheck:只有 `governance/drift-fixes.jsonl` 不存在(新帳檔,這個 repo 還沒產生過),其餘全對得上。
- seat-check(每席拆成單席派工單再跑):多數報「派工要查但報告沒提到 r1-snapshot-a.patch」——席位報告寫的是「a patch」簡稱;引句全錨得回凍結 patch,判定有讀。只觀測不擋。
- 發現 32 條:正確性 4、邊界 6、併發回滾 7、合約圖譜 3、spec 對照 2、架構對齊 1、資安 2、外家 7;major 11 條(機器數各報告的獨立 severity 行:正確性 F1、邊界 F1 F2、併發回滾 F1、合約圖譜 F1 F2、spec 對照 F1、資安 F1、外家 F1 F2 F3),其餘 minor。
- 多席獨立報到的同一件:
  - `--keep --dry-run` 照樣寫表態(正確性 F1、邊界 F1、併發回滾 F1、合約圖譜 F1、spec 對照 F1、外家 F2,六席)。
  - 印給人照貼的指令沒加引號(資安 F1、正確性 F4、外家 F5)。
  - c4 `--new` 寫出標準 YAML 讀法不同的開頭欄位(邊界 F2、外家 F1)。
  - 驗證失敗教的 git checkout 會連帶退掉之前沒提交的工具修改(正確性 F3、併發回滾 F2)。
  - 帳檔 splitlines 讀不回 U+2028(邊界 F4、併發回滾 F3)。
- 本輪有 major,accepted 必須是空的,32 條全折。

## 機械重現(在審的那一版 53b6389c 上;方法:折入後的新測試格,把修法還原回去就翻紅——等於在舊行為上重現。改壞清單與結果在 `mut_r1` 那批實驗,每個改壞都在全新 clone、清掉 __pycache__ 後跑)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性 F1 / 邊界 F1 / 併發回滾 F1 / 合約圖譜 F1 / spec 對照 F1 / 外家 F2(--keep --dry-run 寫表態) | 還原成 `dry_run=False`,跑 t_drift_fix_review_r1_edges | HIT:①紅,「✓ 表態記下了(DACK-…)」 |
| 合約圖譜 F2(佔位字照抄進筆記) | 拿掉佔位字檢查 | HIT:②紅,c2 --close 照抄提示回 0、status 改成 done |
| 資安 F1 / 正確性 F4 / 外家 F5(指令沒加引號) | `_drift_sh` 改回原樣 | HIT:③紅,`lumos drift fix Issues/a$(touch pwned) 3 …` 切不回同一個節點 |
| 邊界 F2 / 外家 F1(c4 標準 YAML) | 拿掉 `_drift_c4_yaml_err` | HIT:④紅,`已提交 "abc" ok`、`*alias`、`|`、`true` 都回 0 |
| 外家 F3(驗證與記帳不在同一把鎖) | 記帳前的磁碟比對改成恆為沒變 | HIT:⑨紅,驗證後被改仍記帳成功;另讀碼確認原版 `_drift_fix_record` 不重讀目標 |
| 外家 F4(壞序號當 0 號有效) | 拿掉 `_drift_seq_ok` | HIT:表態測試 ⑪紅 |
| 外家 F6(NFC 鍵當實際路徑) | 讀 load_vault:rel 用 nfc 正規化;本機 macOS 檔案系統不分 NFC/NFD,實跑不出 | 採信(推論,Linux 才成立);⑭格在 Linux CI 上才會對還原翻紅 |
| 外家 F7(一般正文被當橫幅) | 橫幅判定改回「開頭是已結案」 | HIT:⑤紅 |
| 正確性 F2(⑦格假綠) | `_drift_related_ok` 改成恆為真,跑原版測試 | HIT(席位的觀察成立):12 passed;補「清單混數字」格後改壞 → 例外翻紅 |
| 正確性 F3 / 併發回滾 F2(checkout 連帶退掉) | 讀 `_drift_fix_clean_err`:乾淨檢查認修復帳指紋,同一篇可累積未提交的工具修改;git checkout 回 HEAD | HIT:讀碼確認;訊息改寫、⑮格斷言新說法 |
| 邊界 F3(橫幅插進圍欄) | 標題搜尋改回不看圍欄 | HIT:⑤圍欄那格紅 |
| 邊界 F4 / 併發回滾 F3(U+2028) | `_drift_jsonl_parse` 改回 splitlines | HIT:⑥紅 |
| 邊界 F5(帳檔路徑寫完筆記才查) | 拿掉寫入前的 `_drift_ledger_path_err` | HIT:⑦紅,筆記被改 |
| 邊界 F6(筆記是符號連結) | 拿掉筆記連結檢查 | HIT:⑧紅,連結被換成一般檔 |
| 併發回滾 F4(governance 是連結時 ack 被擋) | 讀 `_drift_ledger_path_err` 與 19162c1e 的 cmd_drift_ack | HIT:讀碼確認;這是設計審刻意收緊的,折入方式=把升級相容取捨與回頭條件寫進家節點 |
| 併發回滾 F5(帳寫不進去沒有補帳的路) | 讀 `_drift_fix_record` 的錯誤訊息 | HIT:讀碼確認;訊息改成講「確認沒問題就直接提交、下一項會被擋」 |
| 併發回滾 F6(家節點在判定後被改) | 席位自標未能重現 | 採信(推論);鎖內加比家節點,⑬格用內部函式直接驗,改壞翻紅 |
| 併發回滾 F7(舊版不認修復帳是簿記檔) | 讀 19162c1e 的 `_BOOKKEEPING_FILES` | HIT:讀碼確認;折入方式=把混版行為寫進家節點 |
| 合約圖譜 F3(防線計劃表格的 0) | 在臨時 clone 跑 `drift scan` | 席位實跑 c2 17 筆;表格下補一行說明 |
| spec 對照 F2(S2 沒綁測試那支沒測) | 讀測試 ⑧ 的現場:G6 的合約句不在家節點 | HIT;補 ⑪ 格(有正式行、沒綁測試),`_guard_pass_home` 改成不看綁定 → 翻紅 |
| 架構對齊 F1(兩支讀帳檔) | 讀 `_drift_jsonl_rows` 與 `_drift_load_acks` | HIT;合成一支 `_drift_jsonl_parse` |
| 資安 F2(路徑直接印到終端) | 讀 `_drift_c4_print` 與成功訊息 | HIT:讀碼確認;改過 `_esc_clean`(縱深防禦,沒另寫測試) |
| 正確性 F1 另附:dry-run 測試只跑 c3 | 同上 ①格 | HIT |

另:⑫格(--reason 含 U+2028)第一次改壞沒紅——--keep 那條路後面還有 drift ack 自己的檢查兜著;改成 --close 與 drift ack 各測一次後,兩個改壞都翻紅。

## 推送前檢查順帶抓到的(不是席位發現)

- 實作席自報「ruff 告警修前修後一樣」不成立:新增告警閘實跑擋 8 條(5 條 DTZ011 `date.today()`、1 條 C901、2 條全形破折號)。C901(表態指令太複雜,本輪折入時加的)拆出 `_drift_ack_args_err`;破折號改成「到」;DTZ011 五條用 `lumos lint-waive` 放行並寫理由(要的就是本機日曆日期,同檔既有 24 處同一種用法;另寫一個取日期函式會變成第二種做法)。

## 處置

- 32 條全折(folded),accepted 空、refuted 空。程式與測試在 429b109f(`wip: 代碼審 r1 折入`),家節點 Systems/存量漂移守衛 補兩條 PITFALL、一條 WHY、「照清單修」的用法與〈代碼審放行的邊角〉一節(含 governance 連結與混版兩個相容取捨、各帶回頭條件);防線計劃〈修復結果〉表下補一行。
- 設計計劃(存量漂移改法_計劃)沒動:它是設計審凍結過的審材。
