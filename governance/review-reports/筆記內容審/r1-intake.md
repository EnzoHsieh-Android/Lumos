# r1 收貨紀錄(筆記內容審)

preflight-4: ran

前置掃描(便宜席 sonnet,固定清單①未定義詞②壞引用③範圍矛盾④機械宣稱驗語意)結果見 r1-preflight.md:四類皆無命中,計劃未因前掃修改。

## 席位收貨

- 6 席全交(正確性 opus;邊界、接手、併發、架構對齊 sonnet;外家否決 Codex,從 clone 目錄啟動);收齊前沒動被審材料。
- report-normalize:接手席缺檔首等級行,用 `report-normalize --write` 補(純格式搬移,值=報告內最高的 blocker);其餘已正規化。
- quote-check:5 份全錨定;外家席 #10 引句把 `[[Issues/治理帳多個寫入者都沒上鎖]]` 寫成沒有連結括號而錨不到——同一句的內容併發席 F4 以錨定引句報了,下表以併發席那條重現。
- refcheck:missing 皆為席位舉例用的假設檔名(governance/note-verdicts/x.json 這類),不是引用錯。

## 編排者重現

| 發現 | 重現 | 結果 |
|---|---|---|
| r1g-F11 / r1c-F6 閘名沒登記 | 讀碼:`_KNOWN_GATES` 最後一項是 note-shape,全檔沒有 note-audit;`_gate_event` 對名單外的閘名拒寫 | HIT(讀碼確認) |
| r1h-F1 / r1a-F6 判定檔提交讓代碼審留痕失效 | 讀碼:`_BOOKKEEPING_DIRS` 只有 code-loop、review-reports、replay 三個資料夾 | HIT(讀碼確認) |
| r1g-F6 / r1a-F14 file 證據跟著捷徑讀到 repo 外 | 讀碼:`_validate_repo_ref` 不帶 at_sha 時 `target.exists()`、`read_text()`,只擋絕對路徑與 `..` | HIT(讀碼確認) |
| r1g-F8 / r1a-F15 / r1c-F1 / r1h-F2 / r1f-F1 連鎖帳本那支不是整檔一次寫 | 讀碼:`rel_cascade_create` 以 O_EXCL 建檔寫一行開頭,之後 `_ledger_append` 逐行追加、單筆上限 4KB | HIT(讀碼確認) |
| r1g-F9 doctor 用字串比對判 CI 接線 | 讀碼:第一層 doctor 那段 `if "note-shape --diff" not in body` | HIT(讀碼確認) |
| r1c-F4 / r1g-F10 治理帳頻率會變高 | 讀 Issues/治理帳多個寫入者都沒上鎖 的 REVISIT 段:已點名第二層是最需要鎖的使用者 | HIT |
| 其餘條目 | 設計層論證,各席附 file:line 且引句全錨定;逐條去向見計劃〈審計修正紀錄〉r1 與鏡像核對 r1-mirror.md | 採信,折入 |

## 處置

39 條全折(輪內有 blocker,不得放行);refuted 無。Enzo 2026-09-27 裁「照現在設計繼續補」(未選「工具自己跑判定者」與「先停第二層」)。

鏡像核對(便宜席 sonnet,材料含本輪席報告目錄):39 條未處理 0、部分 5(皆為寫進誠實界線的殘餘風險)、相反 0;新矛盾 2 處(〈前身 r3〉段的章節編號位移與「三處都加參數」舊說法),已改。見 r1-mirror.md。
