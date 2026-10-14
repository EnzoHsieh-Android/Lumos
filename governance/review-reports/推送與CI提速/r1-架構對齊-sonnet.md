severity: major

整體說法:分層與依賴方向大致對得上,有一處在 CI 範圍判定上另立第二套做法。以下分四問回答。

## 問 1 分層與依賴方向
- 分片:既有切法是執行器內一行 `k % _n`(`scripts/test_lumos.py:39278`)。推送前掛鉤和 CI 都只靠 `--shard i/n` 旗標呼叫執行器(`scripts/hooks/pre-push:682`、`.github/workflows/ci.yml:109`、`.github/workflows/ci.yml:128`)。設計把分法換成讀耗時表,依賴方向不變,對得上。
- CI 範圍判定:既有做法是 yaml 只把 `lumos pitfalls --json` 算出的 `suite` 轉交,判斷邏輯在 lumos,yaml 只收 full/docs 兩值(`.github/workflows/ci.yml:52`、`.github/workflows/ci.yml:70`)。同一個 `suite` 輸出又被 shards(`.github/workflows/ci.yml:86`)和 gates 拿去用。設計把 `skip` 判定直接寫在 prep 的 shell 裡查 GitHub API,不走 lumos。判定邏輯從 lumos 搬到 yaml,這就是下面的 finding 1。

## 問 2 命名與錯誤處理
- 旗標名 `--refresh-durations` 是 kebab-case,跟 `--json-summary`、`--keep-tmp` 同風格(`scripts/test_lumos.py:39210`、`scripts/test_lumos.py:39220`)。命名本身沒問題。
- 執行器既有旗標都只改「這次怎麼跑」(`-x`、`--ff`、`--seed`、`--shard`、`--suite`,見 `scripts/test_lumos.py:39212` 到 `scripts/test_lumos.py:39222`)。`--refresh-durations` 卻會改寫進版控的檔案。
- 本機落地檔 `.lumos/test-durations*.json` 沿用 `test-cache*` 的命名、`_is_src` 條件(`scripts/test_lumos.py:39298`)和先寫暫存再 rename 的原子寫法(`scripts/test_lumos.py:39400` 附近),三項都一致。但 `.gitignore:35` 只列了 `.lumos/test-cache*.json`,設計沒說要補忽略規則。
- 讀表失敗的處理跟既有快取不同:既有快取讀壞時 `except (OSError, ValueError): pass`,靜默略過(`scripts/test_lumos.py:39308`)。設計改成「退回輪流分並印一行說明」。這個差異有道理,但見 finding 3。

## 問 3 第二種做法
- CI 查「同一個提交有沒有成功的 CI」:`scripts/lumos:46279` 的 `cmd_ci_wait` 已經在查 CI 執行紀錄(含 sha、結論、fail-open)。設計在 ci.yml 內另寫一套查詢。
- 測試狀態檔:耗時表的落地沿用 `.lumos/*.json`,沒有另立一套寫法,對得上。
- 合併方式:`skills/lumos-project-notes/commands/06-代碼審與推送.md:7` 現在描述的是「合併請求合進主線、合併提交」的情境。設計要改成快轉,是明講的取代,不算第二種做法。要改的不只第 8 步(`skills/lumos-code-loop/SKILL.md:54`),06 的第 7 行也要同步。

## 問 4 落點
- `Systems/bound-tests-gate` 的 `about_code` 列了 ci.yml 和 pre-push,已有 CI 拆工作與分片的 WHY/KEY(行 17、行 41)。concurrency、skip、分片改法該寫在這篇,合理。
- `Systems/測試假綠形態` 是 `scripts/test_lumos.py` 的家(`about_code`),但主題是假綠形態,跟耗時分片不同題。「改到哪支檔就寫進它的家」的規則照樣要求在這篇留一句,主文不適合放這裡。
- 新檔 `scripts/test-durations.json` 沒有家,`lands_in` 也沒列。
- 要被翻案的舊決策是 `Projects/CI加速_計劃` 的「不做檔案樹相同就不重跑」那條 WHY,設計沒把這篇放進 `lands_in`。

## Findings

1. 範圍判定另立第二套做法(⚠ 偏重,判不準是 major 還是 minor)
severity: major
blocking: 是
引句:「推到 main 時,prep 用 GitHub API 查同一個提交」
說明:既有 prep 的 `suite` 判定在 lumos 內(`.github/workflows/ci.yml:52`),CI 查詢也已有 `scripts/lumos:46279`。設計把 skip 判定和 API 查詢直接寫進 yaml 的 shell,等於 `suite` 一個輸出有兩套來源。建議把「同一提交已有成功 PR CI」做成 lumos 子指令,yaml 只轉交,並復用 ci-wait 的查詢。

2. 耗時表放 `scripts/`,偏離既有資料檔位置
severity: minor
blocking: 否
引句:「測試耗時表放新檔 `scripts/test-durations.json`」
說明:`scripts/` 底下版控的非程式檔只有 hooks、templates、vendor。進版控的資料檔既有位置是 `.lumos/`(config.json、lint.json)和 `governance/`(anchor-baseline.json)。另外 `.gitignore:35` 沒涵蓋 `.lumos/test-durations*.json`。

3. 讀表退回的處理,跟既有「各片聯集必須等於全部」的處理方式不一致
severity: minor
blocking: 否
引句:「表讀不到或壞掉就退回現行的照名字輪流分,並印一行說明。」
說明:`scripts/test_lumos.py:39317` 到 `scripts/test_lumos.py:39325` 的註解記過:各片是獨立行程,讀到的狀態可能不同,聯集就會錯。設計是每片各自決定要不要退回,只要有一片讀失敗、其他片沒失敗,就會混用兩種分法。建議讓分法判定只吃一個所有片都會得到同樣結果的輸入(例如只在表格式驗證通過才用,並在 CI 先驗一次)。

4. `--refresh-durations` 的性質跟其他旗標不同
severity: minor
blocking: 否
引句:「新增旗標 `--refresh-durations` 把這些合併進 `scripts/test-durations.json`」
說明:這個旗標改寫版控內的檔案,其餘執行器旗標都只影響這次怎麼跑。⚠ 若要沿用「改版控基準要有簽名動作」的做法,更新耗時表宜走 lumos 子指令。這點只是提示,判不準。

5. 落點不全
severity: minor
blocking: 否
引句:「Systems/測試假綠形態」
說明:耗時分片的主文放這篇會離題。建議主文寫進 `Systems/bound-tests-gate`(改它的行 17、行 41),`測試假綠形態` 只留指標。新檔 `scripts/test-durations.json` 要有家(新開一篇很小的 Systems 節點,或掛進 bound-tests-gate 的 `about_code`)。`lands_in` 要補上 `Projects/CI加速_計劃`,並用 `lumos decision-add` 記翻案。

不對齊共 5 條,其中 major 1 條
