severity: blocker

## F1 — 本機閘可被 AI 直接略過，CI 只能事後報紅

severity: blocker  
blocking: 是——不改，AI 可不用例外核准就把證據不合格的提交送上主線，核心「擋下推送」合約失效。

spec：〈承接對照〉、〈四、閘門〉、〈六、上線順序〉。

引句:「受管出口實際消費本版本結果」

問題：設計沿用本機 pre-push 與 push 後 CI，卻沒有要求伺服器端在更新主線前執行或強制通過安全判定。`--no-verify` 可跳過本機閘；現行 CI 是主線已更新後才跑，紅燈不能收回推送。

具體例：AI 執行 `git push --no-verify origin HEAD:main`，提交含 active 護欄但沒有證據 → 預期遠端拒收 → 照 spec 接線時 GitHub 先接受提交，之後 CI 才紅，壞版本已在 main。除非每個消費專案另有已確認的伺服器保護，d9 無法兌現。

佐證：`scripts/hooks/pre-push:574` 只在可略過的本機 hook 呼叫 check；`.github/workflows/ci.yml:4-7` 僅接收 main push／PR 事件，`.github/workflows/ci.yml:181-195` 的 code-loop 是 checkout 後執行的事後檢查。

## F2 — 閘可能驗到 checkout，而不是實際被推送的提交

severity: major  
blocking: 是——不改，推送非目前 checkout 的 ref 時會對錯版本判定，該擋的提交可得到 no_registration。

spec：〈二、綁版本〉、〈四、輸入〉、S4、S28。

引句:「工作目錄與要推的提交不一致時，不讀工作目錄、照提交內容算。」

問題：現有 `security list` 只從工作目錄的 vault 建快照；spec 只明訂「起點版」用 git 讀，沒有定義如何從 marker_sha 建出目標版完整盤點、Verification、工具清單與證據檔快照。S4 又要求閘輸入等於一般 `security list --json`，兩者來源衝突。

具體例：checkout 停在無資安登記的 main，執行 `git push origin feature:review`，feature 提交有 unsound active 護欄 → 預期擋下 → 若沿用現行組報告函式，讀到 main 工作目錄並回 no_registration。

佐證：`scripts/lumos:7346-7350` 的 `cmd_security_list` 直接對傳入 vault 呼叫 `_secinv_snapshot`；`scripts/hooks/pre-push:461-475` 支援逐 ref 推送並把 local SHA 傳給 check，但工作目錄不會切換到該 SHA。

## F3 — AI 可偽造「非作者獨立審查」讓自己通過

severity: major  
blocking: 是——不改，AI 只要填兩個不同名字，就能自行滿足每條護欄必備的 review 證據。

spec：〈二、機械做不到的判斷〉、d2、S8、S20。

引句:「審查人身分只核欄位、不核真人」

問題：review qualified 只檢查 `reviewer != author`、版本綁定與期限；review record、作者名與審查人名都由同一個 AI 可寫的 Verification 圍欄提供，沒有簽章、外部身分或不可由作者產生的卷證。這不是單純限制說明，而是直接違反 d2「非作者的獨立審查紀錄才放行」。

具體例：AI 寫 `author: agent-a`、`reviewer: human-reviewer`，同時自行產生審查內容 → 預期 unsound，因沒有獨立審查 → 照 spec 欄位核對會 qualified，護欄可成 sound。

佐證：母計劃明定「AI reviewer 不能代簽需要人工權責的結論」，見 `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:260-266`。

## F4 — S18 要求環境變更使舊證據失效，但設計明訂不比對環境

severity: major  
blocking: 是——不改，S18 無法照字面寫成會翻紅的測試，舊環境證據可套到新環境。

spec：〈二、綁版本與環境指紋〉、S18、母計劃 G3/V5。

引句:「執行環境只記描述、不比對」

問題：S18 要求「環境換了之後套用舊證據」時真實推送必須被擋；但 schema 的 environment 只是自由字串，沒有目前目標環境的權威來源、指紋或比較算法。

具體例：證據在 PostgreSQL 16／舊容器映像產生，交付環境改成 PostgreSQL 17／新映像，程式與證據檔未變 → 預期 stale 並擋下 → 照 spec 所有可比較 blob 仍相同，environment 不比較，證據維持 qualified。

佐證：母計劃要求綁「建置產物、部署設定指紋，以及環境」，見 `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:264-268`。

## F5 — 一般 JUnit／SARIF／k6 沒有 spec 所稱的 receipt，S10 無法實作

severity: major  
blocking: 是——不改，原始報告被改寫時缺少獨立對照值，S10 的 invalid 判定不存在。

spec：〈二、證據圍欄鍵名與必填〉、〈每種格式判定〉、S10。

引句:「items 每項不准有未列的鍵」

問題：證據 schema 沒有 `report_sha256`、案例清單、案例計數、退出碼或 receipt 路徑；但 S10 要比較 receipt 與原始報告。只有 `tq_capture` 既有格式內建這些欄位，一般 JUnit、SARIF、k6 路徑沒有對照物，且 exact-key 規則禁止實作者自行補欄位。

具體例：AI 把已提交 JUnit 的 failure 改成 passed，控制 id、target id 與 bindings 不變 → 預期 `invalid:receipt_hash_mismatch` → 照 schema 只能重讀修改後報告，沒有舊雜湊或 receipt 可比較，會判 qualified。

佐證：既有 test-quality receipt 明確保存並重驗 `report_sha256` 與案例清單，見 `scripts/test_quality.py:250-274`、`scripts/test_quality.py:282-305`；新通用 schema 沒有相應欄位。

## F6 — 簽章只綁例外文字行，沒有綁例外所核准的護欄版本與範圍

severity: major  
blocking: 是——不改，AI 能保留已簽例外行、只改外層護欄語意，讓舊核准覆蓋使用者沒核准的新版本。

spec：〈四、例外核准用簽章金鑰〉、S26。

引句:「用 git blame --porcelain 找出最後改到那幾行的每個提交」

問題：`git blame` 驗的是例外／revision 那幾行的最後修改提交；exception schema 沒有被核准的 `control_revision`、來源 claim、威脅類別或必要證據集合。未改例外行時，外層語意可變而簽章仍有效。

具體例：使用者簽署 OD-01 revision 1 的 behavior 例外；AI 另提交把 revision 改成 2、改來源要求或新增缺證狀態，但保留 exception 行不動 → 預期舊例外失效、要求使用者重簽 → `git blame` 仍指向原簽章提交，例外繼續蓋住證據缺口。

佐證：凍結稿的 v2 exception 只新增補償措施、覆蓋種類與核可日，沒有護欄 revision 綁定；S26 也只有未簽、錯金鑰、換公鑰與合格簽章樣本，沒有外層護欄變更控制。

## F7 — binding_incomplete 沒有可計算的完整集合

severity: major  
blocking: 是——不改，測試或 fixture 改弱後，舊證據仍可能被判 fresh。

spec：〈二、綁版本與環境指紋〉、S9。

引句:「作者不能挑」

問題：spec 要求 bindings 涵蓋測試、腳本、鎖檔與 runner 設定，但只給了 Systems `about_code` 作為來源；`targets.tests` 只有測試身份字串，沒有「測試身份 → 原始檔」映射。跨 Gradle、pytest、Jest 等 runner 無法從測試 id 通用推回檔案，因此無法機械判定漏綁。

具體例：證據目標是 `OrderTest::rejects_other_user`，bindings 綁 production code 與 runner，漏掉 `OrderTest.kt`；AI 把測試改成永遠通過 → 預期 `invalid:binding_incomplete` → 照 spec 找不到該測試 id 對應哪支檔，舊報告仍可維持 qualified。

佐證：既有 test-quality 要呼叫端明示 `--test-source`，並把路徑存入 snapshots，見 `scripts/test_quality.py:202-209`、`scripts/test_quality.py:232-239`；這個必要映射沒有出現在新 evidence schema。

## F8 — SARIF 的覆蓋證明缺少第二份輸出路徑

severity: major  
blocking: 是——不改，多個列為支援的掃描器永遠無法 qualified，或實作者會把沒有覆蓋證明的 SARIF 誤放行。

spec：〈二、SARIF 覆蓋證明〉、〈三、工具清單〉、S12。

引句:「能出 SARIF、JUnit 的工具不需要改 lumos」

問題：證據項只有一個 `path` 與一個 `calibration_path`。Semgrep 的 `paths.scanned`、OSV 的套件清單、ZAP 內部統計、Trivy／Checkov 計數通常位於工具自家 JSON或另一份輸出，不在 SARIF；schema 沒有 `coverage_path`，也不允許額外鍵。

具體例：ZAP 產出 `report.sarif` 與 `stats.json` → 預期同時核對 finding 與登入／請求／URL 統計 → 照 schema 若 path 指 SARIF 就找不到 stats；若指 stats 又不是 SARIF，結果只能永遠 invalid 或漏驗覆蓋。

佐證：凍結稿自己承認 ZAP／gitleaks SARIF 沒有 invocation，並要求讀工具自己的 JSON；但證據表只提供單一 `path`。

## F9 — tag 與其他非 branch ref 完全繞過新安全判定

severity: major  
blocking: 是——不改，採 tag 發布的消費專案能交付證據不合格版本。

spec：〈四、位置與擋下條件〉、〈實務隱患〉、S18／S19。

引句:「母計劃 d9 要求所有專案都擋」

問題：新判定只加在 `code-loop check`，現行 pre-push 對非 `refs/heads/*` 根本不呼叫 check，只提醒；CI 也只監聽 main branch push，不監聽 tag。

具體例：active 護欄缺證據，AI 執行 `git push origin HEAD:refs/tags/release-1`，部署流程以 tag 發版 → 預期安全閘擋下 → 現行路徑只印 advisory，且不會啟動此 CI。

佐證：`scripts/hooks/pre-push:565-575` 只有 branch ref 呼叫 code-loop；`scripts/hooks/pre-push:619-630` 明定 tag／其他 namespace 一律 advisory；`.github/workflows/ci.yml:4-7` 只接 main branch push。

## 逐節覆蓋

- 開頭欄位、待決問題、d1–d6：已讀；簽章語意綁定見 F6。
- 接手說明與承接對照：已讀；受管出口與目標版本問題見 F1、F2。
- 一、區隔與整體判定：已讀，無額外 finding。
- 二、證據種類、來源、格式、綁定與機械限制：已讀；見 F3–F5、F7。
- 三、工具接入：已讀；見 F8。
- 四、閘門、原因代碼、例外與簽章：已讀；見 F1、F2、F6、F9。
- 五、S1–S30：已逐條讀；S9、S10、S18、S26 的不可兌現處已列。
- 六、P1 與上線順序：已讀；正式出口缺口見 F1。
- 世界解與採用判斷：已讀，無額外 finding。
- 實務隱患：已讀；漏列 `--no-verify` 與非 branch ref，見 F1、F9。多人／多程序與非中英文問題依派工排除。
- 回退：已讀，無 finding。

最嚴重 severity: blocker；blocking 共 9 條。
198,034
