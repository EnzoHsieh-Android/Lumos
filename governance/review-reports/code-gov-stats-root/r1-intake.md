# code-gov-stats-root r1 — 收貨與編排者機械重現

preflight-4: n/a(code 迴圈)

分級 standard(單 reviewer 算人數,＋架構對齊、外家否決 Codex terra/xhigh)。被審的是「`gov --stats` hook 段從 vault 反推 repo 根、不吃 cwd」+ 隔離測試(28 行)。
★這批的出身★:推送 條款綁測試算進度 卷證時推送閘翻紅,`t_gov_stats_rc_and_full` 在平行分片紅、單跑綠——查出來不是測試不穩,是 #19 上線的 hook 統計段用 cwd 的 git 根找事件檔,假 vault 讀到真 repo、平行閘期間被追加。

## 收貨三道

| 席 | quote-check | refcheck | seat-check |
|---|---|---|---|
| 單reviewer-sonnet | 乾淨輪,無引句 | ok | 觀測 |
| 架構對齊-sonnet | 乾淨輪,無引句 | ok 25 | 2 份未提(觀測) |
| 外家否決-codex | 乾淨輪,無引句(正規化:去行尾雙空白、去重複印出的第二份) | ok 8 | 觀測 |

三席 severity 皆 clean。外家席誠實標「未能實跑:唯讀沙盒無暫存目錄」,五點全靠讀碼;單 reviewer 用暫存副本做了兩個 mutant(拿掉 git init → 紅;退回 cwd 版且 cwd 在真 repo → 重現原 bug、印出真檔的 `pretooluse-dispatch-lens-hook: 成功 127`)。

## 編排者自己重現的

- 翻紅釘(記帳前、折入前):把呼叫端改回 `git rev-parse --show-toplevel` → 新測試 2 條斷言紅(「假 vault 沒事件檔→不印」、「印的是假 vault 那份」);還原綠。
- 「非 git 的 vault 從此不印 hook 段是不是退化」:hook 事件寫入端 `_hookevent.py` 只在拿到 git 根時才記帳,所以非 git vault 本來就不會有這個檔;三席與我各自查到同一結論。

## 折入(1 條,架構席 ⚠ 升格為 minor 折掉)

- f1(架構對齊 ⚠→minor,spec):`repo_root=None` 預設在唯一呼叫端永遠不會出現,鄰居慣例是不給預設、呼叫端必給——改成必填,漏傳直接炸而不是靜默少一段。折入後子集 87 passed。

## 誠實記

- S4 那段 hook 統計上線時沒有直接測試,這次才補——已寫進 enforcement可觀測性_計劃「落地後修正」。
- 席名這次照慣例帶模型尾碼(上一輪 roster 誤報單家族的教訓)。

## 留痕紀律

★這一份在按下記帳之前寫完★。carrier=單reviewer-sonnet。

## 處置

1 條折入,accepted 為空。

(本檔在此之後不再修改。)
