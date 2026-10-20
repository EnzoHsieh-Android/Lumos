severity: major

## F1 — 刪掉壞證據即可讓同種類轉綠

severity: major  
blocking: 是——不改，AI 可刪除失敗證據而不需簽章核可，直接把 unsound 改成 sound。

spec 段落：〈二、同一護欄同一種類有多筆證據〉、〈四、判定輸入凍結〉、S17。

問題：凍結只保護 `evidence_refs` 的節點引用，沒有保護 Verification 圍欄內的證據項集合；刪除壞項不會被視為判定輸入變弱。

具體例：同一 Verification 內有一份 `zero_cases` 與一份 qualified behavior → 預期刪除壞項仍須簽核或按舊集合判 invalid → 照 spec 刪掉壞項後只剩 qualified，`evidence_refs` 未變，種類轉 qualified。

引句:「作者把壞的那份從圍欄刪掉是一個看得到的動作，會留在 diff 與 Verification 的歷史裡；機械上擋不住刪除」

佐證：母計劃要求必驗集合不能由提出通過宣稱的 AI 任選子集。  
file: `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:306`

## F2 — 有效決策要求審報告偽造，正文卻刻意不驗

severity: major  
blocking: 是——不改，照正文實作會漏掉已決 d2 的必驗項，偽造報告仍能放行。

spec 段落：d2、〈二、機械做不到的判斷〉。

問題：有效 d2 明定「報告是否偽造」須有非作者獨立審查紀錄；正文卻不設 judgment id，只把它寫進 `limitations`。因此完整填入表中五個人工 judgment 的 review_record，仍未審報告來源便可 qualified。

具體例：AI 手工製作計數、雜湊、bindings 全吻合的 JUnit → 預期缺「報告是否真由可信執行產生」審查而擋下 → 照正文此項無 judgment id，其他 review 欄位齊全後護欄可 sound。

引句:「機器驗不了的人工判斷判準是否獨立、合法對照是否合法、門檻有沒有意義、校準樣本代表性、報告是否偽造要有一筆非作者的獨立審查紀錄才放行」

引句:「這一項不設判斷 id，因為人審也判不出來，只能靠可信的執行來源」

佐證：母計劃 V5 要保留可信 CI 來源與執行上下文，單純 hash 不足。  
file: `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:266`

## F3 — 在途分支看不到主線分岔後新增的必驗護欄

severity: major  
blocking: 是——不改，舊分支或其 tag 可完全略過主線後來新增的 active 安全要求。

spec 段落：〈四、起點一律是 merge-base〉、〈必驗集合與判定輸入都以 merge-base 版為底〉、S29–S32。

問題：必驗集合只取目標提交與 merge-base；預設分支在分岔後新增的護欄不在任何一邊。這是「已在途分支」的實際缺口。⚠ 若歷史 tag 被允許按歷史政策驗，須由編排者明確裁定；目前「推得出去的東西都判過」與此做法衝突。

具體例：分支 F 從 M0 分出；主線 M1 新增 active 護欄 C；之後對 F 建 release tag → 預期因缺 C 而擋 → 照 spec merge-base=M0，F 與 M0 都沒有 C，C 不進必驗集合，其他項合格即可放行。

引句:「必驗集合 = 要推的提交裡 active 且關注面含 security 的全部條目，再加上 merge-base 版有、但這次被刪除、被降成 candidate 或 retired」

佐證：母計劃 G1 的凍結集合來自已核可範圍、入口與來源版本，不是只凍結分岔當時已有的子集。  
file: `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:306`

## F4 — 已撤銷的舊金鑰仍可替舊分支簽新例外

severity: major  
blocking: 是——不改，金鑰自預設分支撤除後，持有舊私鑰者仍能在未更新分支上取得有效例外或 warn。

spec 段落：〈四、內容簽章〉的驗章、公鑰清單與 merge-base 規則。

問題：每次都用 merge-base 版 approvers 驗章，沒有核對目前預設分支的撤銷狀態；在途分支因而繼續信任已撤銷金鑰。

具體例：M0 信任 A；主線 M1 因 A 洩漏改成只信任 B；舊分支 F 的 merge-base 仍是 M0，新增一份由 A 簽的例外 → 預期拒絕已撤銷 A → 照 spec 用 M0 清單驗章，A 仍有效。

引句:「閘門用 merge-base 版的 .lumos/security-approvers 寫一份暫時的 allowed_signers，對每個物件重算規範化 JSON」

佐證：同份凍結稿把公鑰清單修改設計成撤換信任根，但目前只保護「分支自己修改清單」，未讓主線撤銷對舊分支生效。

## F5 — 已簽過的 warn 可永久重放，成為整道閘的長效關閉鈕

severity: major  
blocking: 是——不改，AI 無須取得私鑰，只要恢復一份歷史簽章物件就能再次關閉擋推。

spec 段落：〈四、擋或只提醒的設定〉、Q4、S45。

問題：gate payload 只有 `value` 與 `approved_on`，沒有 `expires_on`、被取代版本或單次用途；簽章也不綁當前 block 狀態。已用完的過渡期 warn 可在日後原樣重放。

具體例：使用者為七天遷移簽 warn，完成後改回 block；數月後 AI 從歷史恢復同一份 warn 與簽章 → 預期簽章已過期或被撤銷 → 照 spec 仍驗章成功，所有 unsound、讀取失敗與工具鏈錯誤只提醒不擋。

引句:「改成 warn 時判定照算、照印、照記帳，只是不擋；但這份設定要有 d7 的內容簽章」

佐證：Q4 明問過渡期「多長」，但 S45 沒有到期日案例；母計劃的安全例外則明定最長 30 天。  
file: `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:105`

## F6 — bindings 完整性仍由作者挑選，漏綁 fixture／helper 後舊證據不會 stale

severity: major  
blocking: 是——不改，照 spec 實作無法兌現 G3；AI 可不列受影響檔案並沿用舊報告。

spec 段落：〈二、證據圍欄鍵名〉、〈綁版本與環境指紋〉、S9。

問題：工具只知道 Systems `about_code` 與作者填的 `test_sources`、`environment_ref`；沒有來源可列舉 fixture、共用測試 helper、runner 設定、規則庫與需求來源。`binding_incomplete` 只能驗「已宣告者是否在 bindings」，驗不到應宣告但被省略的檔。

具體例：測試讀 `tests/fixtures/roles.json`，AI 改 fixture 並重用舊 JUnit，但不把 fixture 列進 bindings/test_sources → 預期 G3 判 stale 或 invalid → 照 spec about_code、已宣告 test_sources 與 environment_ref 都未變，舊證據仍 qualified。

引句:「綁定集合至少要涵蓋：護欄所在 Systems 節點 about_code 列的全部程式檔、test_sources 列的測試原始檔、腳本、鎖檔、runner 設定、environment_ref 那支環境描述檔、校準夾具」

佐證：母計劃 V5 還要求 fixture、policy、需求來源、規則庫與建置產物指紋；本篇沒有相應的可列舉來源或必填欄位。  
file: `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:266`

## 逐節覆核

- 開頭決策、接手說明、承接對照：已讀；F2。
- 一、區隔與 schema v2：已讀，無額外 finding。
- 二、證據判準、格式、資源限制、人工判斷：已讀；F1、F2、F6。
- 三、工具接入：已讀，無額外 finding。
- 四、閘門、凍結、簽章、warn、v1/v2：已讀；F3–F5。
- 五、S1–S47：已讀；現有條款未覆蓋 F1–F6 的反例。
- 六、上線順序：已讀，無額外 finding。
- 世界解、實務隱患、回退、審計修正紀錄：已讀，無額外 finding。
- 既有銜接查證：`_codeloop_guard_verdict` 的早退、非分支 ref 現行 advisory、`_PPC_KIND_SENTENCES`、`_secinv_*`、`_pq_*`、backing 與 test-quality 成員均實際存在；這部分與凍結稿宣稱相符。  
  file: `scripts/lumos:57313`  
  file: `scripts/hooks/pre-push:619`  
  file: `scripts/test_lumos.py:75207`

風險類覆核：守衛面有 F1–F5；舊資料相容的 v1/v2 雙讀本身無新增 finding，但舊簽章重放見 F5；已在途分支見 F3、F4；與母計劃交界見 F2、F6。依派工威脅模型，不報多程序同時寫及非中英文文字系統問題。

最嚴重 severity: major；blocking 共 6 條。
192,096
