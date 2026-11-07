severity: minor

## F1 新測試每次多留 4 個暫存目錄,其中 2 個各帶約 2.3MB 的規則包複本
severity: minor
blocking: 否
引句:「fake = Path(tempfile.mkdtemp(prefix="gctl-ktsg-")) / "sg"」
佐證:file: `scripts/test_lumos.py` 的 `t_kotlin_rulepack_samples` 新增的 SARIF 自檢迴圈(r1-snapshot.patch 第 944–949 行)
失敗場景:迴圈跑「空結果」「讀不懂」兩輪。每輪先呼叫 `_ktpack(copy=True)`,在 `gctl-ktpack-` 下 `copytree` 整個規則包,約 2.3MB。再 `mkdtemp(gctl-ktsg-)` 放假 sg。這四個目錄之後都沒有 `rmtree`。每跑一次這支測試,就多留約 4.6MB 加 2 個小目錄。這支測試的 `_ktpack` 與 `gctl-ktsg-` 殘留本來就有,所以我認為這是沿用舊慣例,但全域「測試完就刪暫存」規則點名過這類殘留。這一版讓殘留從約 N 組增加到約 N+2 組,而且 diff 沒有新增清理。我沒量測整支測試實際留下多少。要收掉的話,在 finally 裡用字面路徑或 `shutil.rmtree` 刪掉自己造的目錄即可。

## F2 Systems/kotlin規則包 的 about_code 沒列新檔 sgconfig-unwired.yml
severity: minor
blocking: 否
引句:「`configs/ast-grep/kotlin-android/sgconfig-unwired.yml`:不接閘的規則(`rules-unwired/`,任何等級)」
佐證:file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md` 在 diff 中的 frontmatter(r1-snapshot.patch 第 861–868 行)。`about_code` 列了 `sgconfig-hints.yml`、`sgconfig-review.yml`,沒有 `sgconfig-unwired.yml`。正文第 64 行卻用反引號寫了這支檔。
失敗場景:專案規則是「每支程式檔要有家」,而且節點只准用反引號寫自己家的檔。新檔沒被 `about_code` 認領,`lumos doctor` 或提交時的家檢查可能會唸,或這支檔在 impact 查詢裡找不到家。.yml 設定檔是否算「程式檔」,我沒驗證,所以只標 minor。沒有執行期代價。

## 資源鏡頭逐題回答
- **多花的時間:** 我在這個 repo 實跑 `check.py` 的 `check()`,整次 1.37 秒。新增的兩次 SARIF 掃描合計 0.044 秒,`loaded_count` 一次 0.048 秒,unwired 掃 bad 樣本一次 0.029 秒。CI 與推送前各多不到 0.2 秒,可忽略。
- **整支測試時間:** `python3.14 scripts/test_lumos.py -k kotlin_rulepack_samples` 用 LUMOS_AST_GREP 跑,結果 25 passed, 0 failed,t_kotlin_rulepack_samples 為 21.2 秒,離 180 秒上限餘裕 9 倍。
- **`_TIMED_OUT` 共用:** `sarif_rule_ids` 一進來就檢查旗標,逾時時設旗標。`scan`、`loaded_count` 與它共用同一個旗標,`check()` 開頭重設。逾時一次後,後面的掃描都直接回 None,不會各等滿上限。
- **既有兩條「2.5 秒內」測試:**
  - 第一條 `sleep 5` 的假 sg:`loaded_count` 先逾時 1 秒,SARIF 探針被旗標略過。
  - 第二條 `--inspect` 回 0、其餘都 `sleep 5`:新掃描變成第一個逾時的人,等 1 秒設旗標,後面全略過。
  - 兩條總時間都沒有變長,而且這次實跑是綠的。
- **子程序回收:** `subprocess.run` 逾時時會 kill 子程序並 wait,OSError 時沒有子程序可收。`#!/bin/sh` 加 `sleep 5` 的假 sg 在 kill 後,孫程序 `sleep` 會再活約 5 秒,這是測試夾具造成的,真的 ast-grep 是單一程序,不會有這個問題。
- **暫存目錄:** 見 F1。

## pitfalls manifest
- 「共享狀態有沒有鎖保護」命中 `rules-unwired/coroutines.yml` 第 11 行。那是規則文字裡的 Mutex,屬併發類題目,依派工詞判範圍外,**標誤報**。

## 固定席判定
- **Systems/kotlin規則包(無合約):**
  - WHY 與 RULE 的字面改動,跟程式一致。`catalog_problems` 確實只放行 `dir == "rules-unwired"`,`[test:t_kt_rulepack_unwired_dir]` 存在。
  - 我沒有依照這個 repo 的筆記格式規則逐條檢查 `[confirmed:2026-11-08]`。
  - 只有 F2 一件待處理。
- **Systems/測試假綠形態 ★INVARIANT★(還原翻紅釘要配前置斷言):**
  - 新測試 `t_kt_rulepack_unwired_dir` 有 `★前置★`,確認型錄有出處不全的列,不會因為讀表失敗而空過。
  - 項目 ③、④、⑦ 是「不應報」的否定斷言,本身沒有各自的正向對照:
    - ④ 的 `只收` 字樣、③ 與 ⑦ 的 `rules-unwired` 與 `出處不全` 字樣,如果訊息改了字,這三條會空綠。
    - 緩解:① ② ⑤ 與既有 kt-f 的「只收」正向斷言會先紅。
    - 判為**符合**,只是略薄。我沒有逐條拿掉守衛做變異驗證。
  - 這裡沒有改 `catalog_problems` 以外的 bug 修正,所以不適用「修 bug 還原翻紅」那一條。
- **其餘連帶:** 因為改到超大的 `scripts/test_lumos.py`,有一批節點被連帶推出。我沒有逐一查看,也不認為跟這份 diff 的實質邏輯有關。

總結:最高等級為 minor,blocking 共 0 條
