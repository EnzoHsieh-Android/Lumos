# B 席增量標註：batch8

本批 17 筆，依題目來源將 S30、SY01、SY02、SY03 全部視為搜尋題。僅以本席閱讀內容判分，未讀取禁止的金標檔或其他評審答案。

## 判 2 的理由

- S30／Issues/簿記白名單漏canary與bypass帳.md：直接記錄「記審查帳與跳過帳本身會使通過留痕失效」的死結與本機／CI 差異，處理治理帳時漏看會踩到關鍵事故。

## 開全文紀錄

- 開全文：Issues/E4confirm餵翻案根造成E3.md，原因：摘要只有空欄，須確認清帳與事故主題的關係。
- 開全文：Issues/ci-wait對當日run判no-run.md，原因：摘要只有空欄，須確認是否實質影響治理帳。
- 開全文：Projects/世界repo掃描2026-09-02_調研.md，原因：摘要未交代 openwiki，須確認正文是實質調研還是僅提名。
- 開全文：Systems/節點還原.md，原因：摘要有還原流程但未說明 openwiki 的關係，須查正文比較。
- 開全文：Projects/OpenSpec_調研.md，原因：摘要主要談 OpenSpec，須確認正文對 openwiki 是否有可用的比較內容。

## 難判與可能分歧

- S30／Projects/條款綁測試算進度_計劃.md 判 1：具體說明 CI 帳與 bound-tests 帳能證明什麼，屬帳的使用背景，但主題仍是條款進度。
- S30／Projects/設計審收斂重定義_計劃.md 判 1：治理帳新增 rewrite 收尾值有實質資訊，但一般查「帳」未必需要整份收斂設計。
- S30／Issues/code-loop-pass不能指定分支.md 判 1：說明留痕如何按分支記錄及讀取，有助理解帳的作用，但必要性取決於是否處於 detached 工作目錄。
- S30／Issues/ci-wait對當日run判no-run.md 判 1：直接造成 CI 結論無法入帳，屬有用事故背景；查詢未限定 CI，未升為必看。
- S30／Issues/簿記白名單漏canary與bypass帳.md 判 2：雖然查詢很寬，這篇直接揭示記帳會破壞守衛的反直覺前提，故保留必看。
- S30／Issues/E4confirm餵翻案根造成E3.md 判 0：清帳只是事故發生場景，實際回答的是翻案決策引用錯誤，未把共同字詞當相關。
- S30／Projects/建了沒人跑批次裁定_計劃.md 判 0：用零使用帳作退場證據，主要回答工具存廢，並未解釋帳的機制。
- SY01、SY02／Projects/檢索核心重建_計劃.md 均判 0：兩個查詢只作檢索評測題例，未回答 Check K 機制或 confused deputy 問題。
- SY03／Projects/世界repo掃描2026-09-02_調研.md 判 0：openwiki 僅用於說明已有調研並指向別篇，本篇未提供該工具的實質答案。
- SY03／Systems/節點還原.md 判 1：正文比較 openwiki 全倉生成與任務驅動還原，提供有用替代方案背景，但不是 openwiki 的主要說明。
- SY03／Projects/Agentflow吸收_調研.md 判 1：對 openwiki 失去目擊者的失效模式有實質討論，且摘要已明載撤回錯誤類比；屬延伸背景。
- SY03／Projects/OpenSpec_調研.md 判 1：正文比較第一手 spec 與事後從 code 逆推的來源、保鮮限制，超過僅提名，但主要對象仍是 OpenSpec。
- SY03／Projects/節點還原SOP_計劃.md 判 1：交代 openwiki 類冷啟動缺乏歷史底料及補償方式，屬相關設計背景，未達查工具名稱就必看。
