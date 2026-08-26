### ext-f1
severity: clean
引句:「T3 回填=對 backlog 快照的一次性單趟」
佐證:file: `governance/review-reports/dref-v4/r2-snapshot.md:116`
說明:已明定 backlog 只取一次快照、每節點只處理一次，抽查與 prune 在單趟末尾，不會回頭重列；AI 判不像而跳過也不會在批次內再查。週期性重跑另列 future，且要求先重設持久記憶並重跑 panel。r1 的兩種振盪源在本批邊界內均已消除。

### ext-f5
severity: clean
引句:「條款(六原語,乾淨雙欄:decision_refs / decision_refs_ai」
佐證:file: `governance/review-reports/dref-v4/r2-snapshot.md:118`
說明:現行 spec 明列 V1 至 V6 共六個原語，先前五／六原語數量不一致已修正。

### ext-f6
severity: major
引句:「count-based expected_check:此 ref 正欄恰一份、不在 _ai」
佐證:file: `governance/review-reports/dref-v4/r2-snapshot.md:125`
說明:V1、V2、V3 都明定用正規化 tuple 判斷簡寫與完整路徑是同一決策，但 V6 promote 的移除、去重及寫後計數仍只寫「此 ref」，未釘成正規化 tuple。若 `_ai` 存完整路徑、呼叫 promote 時傳等價簡寫，實作可能新增簡寫到正欄、未移除 `_ai` 的完整路徑，而 exact-string 計數仍錯誤通過。應明定 locate/remove、兩欄異常態 dedup 與 expected_check 全部按 `(env.resolve(節點), did)` 計數，落盤字串只保留一份。

### ext-f7
severity: minor
引句:「promote 落盤前先掃該節點」
佐證:file: `governance/review-reports/dref-v4/r2-snapshot.md:125`
說明:promote 覆蓋提醒沒有明定以 E2/E3 相同的 resolve＋did 正規化口徑判斷正欄是否命中。若直接逐字比對，簡寫與完整路徑會被誤報成未覆蓋；主要是 advisory 噪音，未直接造成靜默漏警，但應補上共用正規化比較函式的要求。

結論:否決維持(promote 的跨欄搬移與寫後驗證尚未完整套用正規化 tuple，仍可能讓等價 ref 重複留在雙欄並錯誤通過原子寫回驗證)。
