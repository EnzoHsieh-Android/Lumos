preflight-4: ran

# code-android-ui-kind r4 收貨(三輪跑滿後人裁加開的第四輪)

審材:r4-snapshot.patch(839 行,2bdefa2da714976d1bfa9f0c15e9e55066682e71..ab35a0f82faba0020ff6b88101aec1d6b4f3eac1);修補差異 r4-repair.patch(e3ea2c16 → ab35a0f8);來源 r4-repair-binding.json;配對案例 r4-behavior-cases.json;pitfalls 清單 r4-manifest.json。
七席全新:正確性、資源、邊界、整合、通才、架構對齊、資安,全部 sonnet;七席交回後才一起從逐字稿存檔。收貨時工作樹分支與 HEAD 都沒變(ab35a0f8)、git status 只有我的帳本與卷證。
格式:正確性席第 1 條有一行說明以「嚴重度:」開頭,收貨工具判成第二個等級宣告;退回該席自己改成「等級理由:」後重存(只改那兩個字,其餘一字未動)。整合席第 3 條 `severity: minor ⚠` 用 report-normalize --write 純格式拆成兩行。
引句:資源席第 2 條引句跨兩行(finally 與下一行 os.unlink),機械比對錨不到;編排者對照 r4-snapshot.patch 的 try 區塊最後兩行逐字核過原文在;同條的檔案位置與重現另行實跑(見下表 R4R2)。其餘全錨。
圖譜鏡頭:固定席有附,各席都答;「授權與歸屬」的 ★INVARIANT★ 判不受影響。

## 逐條重現與去向

重現目錄在 scratchpad(修前腳本取自 `git show e3ea2c16`,修後是工作樹的範本,假分析工具印 "frame","compose_ns" 與 "甲","5")。

| id | 席 | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|---|
| R4C1 | 正確性 | minor | `PYTHONIOENCODING=ascii TP=tp.sh sh rerun_old.sh` → `OK  Q1 甲:compose_ns=5` rc0;同命令對修後版 → `UnicodeEncodeError: 'ascii' codec can't encode character '甲'` rc1 | HIT | 放行 |
| R4B1 | 邊界 | minor | 同 R4C1 | HIT | 放行 |
| R4G1 | 通才 | minor | 同 R4C1 | HIT | 放行 |
| R4B2 | 邊界 | minor | queries.sql 寫 `expect=甲` → `ValueError: not enough values to unpack (expected 2, got 1)` rc1 | HIT | 放行 |
| R4G2 | 通才 | minor | 同 R4B2 | HIT | 放行 |
| R4G3 | 通才 | minor | 假工具輸出 `"\377","5"`:拿掉 `, errors='replace'` 的副本 → `UnicodeDecodeError` rc1;原版 → `BAD Q1` rc1;測試檔沒有這個案例 | HIT | 放行 |
| R4S1 | 資安 | minor | 在放了 `json.py`(內容 print PWNED)的目錄執行修後版 → 第一行印 PWNED | HIT | 放行 |
| R4I1 | 整合 | minor | 讀 scripts/test_lumos.py 的 t_android_ui_attribution_receipt_rerun:環境同時設 LC_ALL=C、PYTHONUTF8=0、PYTHONCOERCECLOCALE=0;r3-linux-repro.txt 量的也是關掉 UTF-8 模式後的編碼;計劃的 PITFALL 根因只寫 LC_ALL=C(這句在 ab35a0f8 新增) | HIT | 放行 |
| R4I2 | 整合 | minor | 讀四處:skills/lumos-android-evidence/SKILL.md「回 2 是收據本身寫錯」、腳本檔頭、家節點第一段、Android逐層診斷計劃 S10,都沒有「分析工具執行不了回 2」 | HIT | 放行 |
| R4I3 | 整合 | minor | 讀 SQL 範本最後的 SELECT:每幀一列,沒有跨幀總和;SKILL L1 要 AI 加總後寫進 why_escalated | HIT | 放行 |
| R4R1 | 資源 | minor | 讀腳本:subprocess.run 沒帶 timeout(修前修後同一行) | HIT | 放行 |
| R4R2 | 資源 | minor | 讀腳本:清暫存靠 try/finally,SIGTERM 預設處理不會跑 finally(Python 行為,未另實跑殺程序) | HIT | 放行 |
| R4A1 | 架構對齊 | minor | grep PYTHONUTF8:只在這支範本、測試與筆記;scripts/lumos 與 hooks 逐處寫 encoding= | HIT | 放行 |
| R4A2 | 架構對齊 | minor | 讀 reference.md:「需要 python3.7 以上」;專案最低版本是 3.14 | HIT | 放行 |
| R4A3 | 架構對齊 | minor | 讀授權守衛:spdx_for 依副檔名選 -- 或 # | HIT | 放行 |

## 處置與理由

- 十五條都是 minor,七席沒有 major 以上;最壞的後果是該回 0 卻回 1 或回錯碼,沒有一條會假過(比對不符卻回 0)。
- 不折:折任何一條都要再開第五輪審查;第四輪本身已是跑滿後加開。後續一次收掉,集中記在 Issues/Android收據重跑第四輪放行的小缺口(含修好的條件與 REVISIT 2026-11-07)。
- 架構對齊三條:UTF-8 模式是為了蓋到傳給分析工具的命令列參數(逐處加參數管不到),理由在腳本註解與計劃的 PITFALL;3.7 下限與兩套 SPDX 已列進 Issue。

## 修補因果

regression_set:R4C1、R4B1、R4G1(拿掉 stdout 重設後 PYTHONIOENCODING 沒人壓)、R4I1(根因句在 ab35a0f8 寫入)、R4I2(回傳碼 2 新意思在 ab35a0f8 加入,只改了兩處)、R4A1、R4A2(UTF-8 模式與 3.7 下限是 ab35a0f8 引入)。其餘 R4B2、R4G2、R4G3、R4S1、R4I3、R4R1、R4R2、R4A3 修前修後行為相同,屬原有漏查。
