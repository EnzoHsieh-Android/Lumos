# 設計前掃留痕
preflight-4: ran

來源 preflight-raw.md 兩條 major/blocking 原樣保留，不是正式帳、不能當成已接受裁定。

| ID | 觀察與重現 | 處置 |
| PF1 | HIT：原測試漏 --loop，cmd_canary 的報告／全錨分支只在 loop 與 auditor 都有時執行。 | 測試加每案例唯一 code- 迴圈，seed 加既有必需 snapshot，再加 reported 前置斷言；核心裁定未變。修正前來源 preflight-test-source-before.patch，修正後來源 preflight-test-source-after.patch。漏 loop 的舊反向結果及漏 snapshot 的 seed 失敗完整保留，不能用它們宣稱本案分支覆蓋。正確前提反向控制看 repair-counter-old.json/log。 |
| PF2 | HIT：有效引句報告＋binary ff fe 快照，原 CLI rc1/UnicodeDecodeError，canary 無成功帳；見 preflight-encoding-probe.json。 | 觀察成立；「本案應修該既有編碼錯誤」的判準尚待正式席判讀。核心裁定不變，交輸入／回退鏡頭獨立核對。不把靜態未驗當已實測。 |

無核心裁定被前掃自行改寫。repair-counter-old 僅為舊程式反向控制，並非正式程式驗證通過。
