C1. 此節點類型為 known-pitfall(世界已知坑,非本專案事故),與其他 known-pitfall-* 節點共用同一分類慣例 | 預期驗證點: docs/lumos-toolchain-knowledge/ 下其他 known-pitfall-* 節點(比對 frontmatter/正文分類寫法是否一致)

C2. pitfall_source 指向外部出處 https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html | 外部知識,repo 不可驗(僅可驗 URL 是否可解析,非 repo 內容)

C3. pitfall_when 定義 content trigger 正則為 `refresh.?token|refreshToken|token.?rotat`,用於在 spec 文本中命中時觸發 advisory | 預期驗證點: pitfalls spec 模式的實作機制(相關指令/skill,如 lumos pitfalls 或 lumos-design-loop 內的 content-trigger 掃描邏輯)

C4. 此節點的落地驗證記錄在 verified_by: [[Verification/2026-08-09_已知坑策展庫v2落地]] | 預期驗證點: docs/lumos-toolchain-knowledge/Verification/2026-08-09_已知坑策展庫v2落地 節點是否存在,且其中是否回指/涵蓋本節點

C5. 機制宣稱:pitfall_ask 由「pitfalls spec 模式」在 spec 文本命中 content-trigger 時,於 design-time 以 advisory 形式攤出 | 預期驗證點: lumos-design-loop skill 或 pitfalls 相關程式碼/指令(確認是否存在 spec 文本掃描→advisory 攤出的流程)

C6. 命中 advisory 後的處置規範:必須「答或寫『已排除:理由』」,並經 panel 審查、裁定留痕 | 預期驗證點: lumos-design-loop skill 文件或 pitfalls 機制文件中關於處置/留痕流程的規範段落

C7. 坑內容(世界已知坑,非本專案事故):refresh token 若採一次性輪換(rotation),多分頁/多請求並發時,先到請求換新成功會使舊 token 作廢,後到請求持舊 token 被拒,導致誤登出 | 外部知識,repo 不可驗

C8. 解法一:前端採 single-flight——偵測到需 refresh 時僅發出一個 refresh 請求,其餘並發請求等待共用其結果 | 外部知識,repo 不可驗

C9. 解法二:refresh 進行中的其他 API 請求應排隊等待新 token;若 refresh 失敗則整批請求失敗並導向登入頁(明文回滾) | 外部知識,repo 不可驗

C10. 解法三:後端容忍舊 token 在短時間窗內重複兌換(grace period),或改由前端保證不重複兌換,二者擇一實作 | 外部知識,repo 不可驗

C11. 節點 frontmatter 標記 created/updated 皆為 2026-08-09 | 預期驗證點: 節點自身 frontmatter 日期,或與其關聯的 Verification/2026-08-09_已知坑策展庫v2落地 節點日期是否一致

C12. 節點狀態標籤為 status/doing(仍在進行中,未標記完成/收斂) | 預期驗證點: 節點 frontmatter tags 欄位本身,或 `lumos query --tag status/doing` 是否會列出此節點
