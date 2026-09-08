# code-gov-stats-root-b r1 — 收貨與編排者機械重現

preflight-4: n/a(code 迴圈)

★換編號重記★:前身 `code-gov-stats-root` r1 三席記完帳、問閘被擋「報告零引句(驗不了≠通過)」——三席全乾淨、報告全是「已讀,無 finding」但沒有一句逐字引句。
帳不能撤,依規則換編號:請三席各自補引句(續談只准問它自己審過的段落;Codex 用後續回合補五句,逐字稿 `r1-codex-quotes-raw.txt`),結論一字未動,卷證複製到本目錄重記。
前身目錄與帳保留當歷史。★同時修了派工單形狀★:前身 dispatch.json 頂層有 `auditor` 鍵、seats 是字串陣列,roster 把整份當一席 unknown——這是三個迴圈連續誤報「單家族」的真因(記憶已更新)。

分級 standard(單 reviewer 算人數,＋架構對齊、外家否決 Codex terra/xhigh)。被審的是「`gov --stats` hook 段從 vault 反推 repo 根、不吃 cwd」+ 隔離測試(28 行,134 行 patch)。
出身:推送 條款綁測試算進度 卷證時推送閘翻紅,`t_gov_stats_rc_and_full` 平行分片紅、單跑綠——不是不穩,是 #19 上線的 hook 統計段用 cwd 的 git 根找事件檔,假 vault 讀到真 repo、平行閘期間被追加。

## 收貨三道

| 席 | quote-check | refcheck | seat-check |
|---|---|---|---|
| 單reviewer-sonnet | ✅ 全數錨定(補 5 句後) | ok | 觀測 |
| 架構對齊-sonnet | ✅ 全數錨定(補 3 句後) | ok 25 | 觀測 |
| 外家否決-codex | ✅ 全數錨定(補 5 句後;正規化:去行尾雙空白、去重複印出的第二份) | ok 8 | 觀測 |

三席 severity 皆 clean。外家席誠實標「未能實跑:唯讀沙盒無暫存目錄」;單 reviewer 用暫存副本做兩個 mutant(拿掉 git init → 紅;退回 cwd 版且 cwd 在真 repo → 重現原 bug、印出真檔的 `pretooluse-dispatch-lens-hook: 成功 127`)。

## 編排者自己重現的

- 翻紅釘(折入前):呼叫端改回 `git rev-parse --show-toplevel` → 新測試 2 條斷言紅;還原綠。
- 「非 git 的 vault 從此不印 hook 段是不是退化」:寫入端 `_hookevent.py` 只在拿到 git 根時才記,非 git vault 本來就沒這個檔;三席與我同結論。

## 折入(1 條,架構席 ⚠ 升格為 minor)

- f1(spec):`repo_root=None` 預設在唯一呼叫端永遠不出現,鄰居慣例不給預設——改必填,漏傳直接炸。折入後子集 87 passed。

## 誠實記

- S4 hook 統計上線時沒有直接測試,這次才補(已寫進 enforcement可觀測性_計劃)。
- 乾淨輪也要引句——這條規則我這輪才真的踩到;前身的三筆帳留在帳上當「零引句被擋」的實證。

## 留痕紀律

★這一份在按下記帳之前寫完★。carrier=單reviewer-sonnet。

## 處置

1 條折入,accepted 為空。

(本檔在此之後不再修改。)
