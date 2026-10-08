# r4 固定版本派工與資格

本輪依使用者對 Aspidochelone 第三輪停點的 continue，使用已記帳 extra-round 裁決。正式R3FAIL和cap-retro保持原始結論；沒有把未判定修補因果填成 none。

修前端點 532f5a15、修後端點 05e87b5476cf161a203382a50ef008b374e60a31；r4-snapshot.patch 是這兩版四支產品與測試檔的完整 -U10 delta，1455行，SHA256 15816452e6d94bcc59ccec186ff3ccdaf69c71221c91f23cdbe6efce26cbf53f。圖譜固定鏡頭由同一區間 impact 得到，159行，逐條貼入每席prompt。快照不包含歷史卷證的遞迴副本。

修正前症狀見保留的r3機械HIT紀錄，新增控制的先紅後綠紀錄在probe-attempt-ledger。repair-before只是已提交的修補前基線，不謊稱每項新增測試都在舊版跑過；helper初始控制中的兩項只有修後執行。

fix-check record-template 曾實際執行，工具擋下「審查帳找不到第r3輪的載體席」。歷史R3確實未記處置載體，不能冒稱fix-check通過；修正證據先單獨保留，正式處置帳在本輪收貨後整理。此為記帳程序資格，不拿來冒稱產品紅或跳過推送閘。

七席將分批維持至多三個子審查程序，報告只存 /tmp staging，全部回覆之前不搬進repo、不修改產品碼。四檔全hunk要求及安全席皆用相同快照；未讀範圍、未執行測試與來源歸因均須明示。

## 已保存的修正控制

32項消融unittest、138項probe-boundary斷言均通過；最後一個名額兩程序競爭、雙父派工器查帳race、壞帳、鎖逾時、程序死亡、跨日/封存不退額度、零值無帳、冷啟動小數時間、CLI fatal協定及滿額零sleep都有獨立可重放控制。這些不是本輪乾淨審查員自己的動態證據。

本輪補G14時曾漏re匯入，導致7個unittest errors和17個probe-boundary失敗；此修補造成的回歸已修復，兩份原始失敗log保留在probe-attempt-ledger，沒有消去失敗史。

## 收貨、重現與辯方處置

七席均以同一份 1455 行凍結快照完成。邊界與回退席原報告沒有機械可抽取的引句，已由原席只補格式後重送；原文仍以 `r4-*-original.md` 保存。全席正規化與引用路徑檢查通過；最初兩份 quote-check 失敗紀錄也保留，沒有把失敗史改寫成通過。

| finding | 重現 | 處置 | 修補因果資格 |
|---|---|---|---|
| COR4-001 | MISS | 辯方 evidence：現行 schema 與 S3 沒規定 `initialized_at` 必須非負；若要拒絕負值，須先新增政策。 | before 無帳本入口，不能判修補回歸。 |
| D4-CALLS-NULL | MISS | 辯方 evidence：before/after 都把顯式 null 與缺欄位走同一 legacy 路徑；S16 新增的是非 null calls 內容型別檢查。 | 兩版同例一致。 |
| D4-MARKDOWN-INJECTION | HIT | 降為 minor：Markdown 字面呈現會被解讀，但 repo 內沒有把該 summary 接到 HTML renderer 的鏈；保留 repo 外預覽器未驗資格。 | 兩版同例一致。 |
| R4-RES-01 | MISS | 辯方 evidence：窗口上限是每次命令的設定，設計允許 0 停用，沒有規定同帳永久鎖定首次上限。 | before 無帳本入口，不能判修補回歸。 |
| R4-RES-02 | HIT | minor：`--wait-on-limit 1` 仍會睡 300 秒，超過 CLI 自稱的最多等待秒數。 | before/after 同例皆為 300 秒。 |
| ARCH4-01 | HIT | minor 測試缺口：現有零等待控制只耗盡批次上限，刪掉持久帳的 sleep 前查詢仍可綠。 | 新帳本測試的保留力不足，不是 runtime 回歸。 |
| ARCH4-02 | HIT | minor 測試缺口：舊結果計數案例使用冷帳，不能區分「結果檔硬限」與「持久帳硬限」。 | 新帳本測試的保留力不足，不是 runtime 回歸。 |
| SEC-R4-01 | HIT | major 未折：候選檔仍由 `Path.write_text` 跟隨符號連結；在不受信任者可寫輸出目錄的部署下可覆寫執行者有權寫的其他檔案。既有圖譜要求此部署變更時重驗，但 CLI 未機械限制。獨立辯方被安全閘中止，沒有反證，故維持 major。 | sink 在 before/after 相同；只證相鄰既有缺口，不稱為修補引入。 |
| SEC-R4-02 | HIT | minor：舊 meta 的 ESC/BEL 會原樣印到終端；已證標題控制，未證 shell 執行。 | before/after 同例一致。 |

辯方 A–D 原報告保存在 `r4-defender-original.md`；E 的續查只留下安全閘事件與 stderr，沒有產出結論。由於 SEC-R4-01 仍是未折 major，本輪不得建立假處置載體或宣告通過。現有 finding 均未取得 after-only 行為證據；本輪 `regression-set` 可判為 none，但這不消除既有缺口。

## 測試與停止資格

本輪凍結版的針對性控制仍是消融 32 tests OK、探針邊界 138 passed / 0 failed。另補的完整父死子活案例以真父程序、真 SQLite 帳及假模型子程序重現：父程序 rc=-9，子程序在父死後仍完成候選檔，歸檔 pending/candidate 後同帳剩餘量為 0，下一次父派工 skip，真模型呼叫為 0；命令與輸出保存在 `r4-parent-death-ledger-case.txt` 與 `.log`。

全套 `python3 scripts/test_lumos.py` 執行約 22 分鐘後以 129 結束，沒有完成總結；原因未判定，也沒有編排者手動終止證據。`r4-full-suite-interrupted.log` 與資格 JSON 保留。因此全套不能算通過，32/138 的綠燈也不能替代全套推送閘。
