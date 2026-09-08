# 審查有沒有用記帳 r3 — 收貨與編排者機械重現(上限輪)

preflight-4: ran

五席驗收 r2 的 13 條折入。這輪的特殊處:實作已在工作樹上進行,通才席直接載入工作樹的 WIP 碼、拿七份真實席報告跑——比讀散文更狠,抓到三條泛偵測的漏洞。

## 收貨三道

| 席 | quote-check | refcheck | seat-check |
|---|---|---|---|
| 通才-sonnet | ⚠ 17 句 1 句錨不到(不當載體) | ok | 觀測 |
| 接手的人-sonnet | ✅ 全數錨定 | ok | 觀測 |
| 簡化守護者-sonnet | ✅ 全數錨定 | ok | 觀測 |
| 架構對齊-sonnet | ✅ 全數錨定 | ok | 觀測 |
| 外家否決-codex(terra/medium) | ⚠ 7 句 1 句錨不到(「不加」寫成「不設」,前輪修好段,不掛 finding) | ok | 觀測 |

## 編排者自己重現的

| # | 席 | 我怎麼驗 | 結果 |
|---|---|---|---|
| c1 殘留寫法列舉會漏(Severity:/sev:/嚴重度:高/## F1 — BLOCKER) | Codex #1 blocker、通才 F1 blocker | 拿 code-batch20 真報告跑 WIP 偵測 → 0 處 | **HIT** → 偵測改泛的(severity/嚴重度字樣、方括號、標題嵌等級、破折號接大寫),例外列舉(引句/圍欄/總結句) |
| c2 同席同輪兩筆 N 重複 | Codex #2 blocker | 今天 code-clause-bindings r2 外家席兩筆 | **HIT** → (auditor, report_sha256) 去重,寫進 S3 文字 |
| c3 檔首跳 HTML 註解=重新引入專案殺掉的註解偵測 | 架構 major | 三處明令 | **HIT** → 不跳;來源註記放檔級行後 |
| c4 rc2 不落帳,看不到撞牆後沒記 | 接手 blocker | 查帳:被擋的嘗試零痕跡 | **HIT** → 擋下時寫 canary/rejected 閘事件;gov --stats 印次數 |
| c5 架構席 `- severity: X` 格式被拒沒過渡 | 通才 | — | HIT → 收貨正規化多一步(去列表符號);擋下訊息講怎麼改 |
| c6 總結句「最嚴重 severity: X」會被當殘留 | 通才 | 330 份報告有 | **HIT** → 總結句列舉例外 |
| c7 intake 字彙不只 HIT/MISS | 通才 | 舊 intake 用 採信/不採信 | HIT → 加 重現/採信 |
| c8 K/30 天門檻仍是拍腦袋 | 簡化(minor)、通才 | — | 保留、標暫用值、REVISIT 看(r2 已列) |

## 折入(8 條)

c1–c8 全折,accepted 為空(輪內有 blocker)。碼側同步:`_report_normalize_issues`(泛偵測+例外)、`_review_yield_round`(去重)、`_gate_event_or_warn(canary, rejected)`。

## 我判錯、被席位糾正的

- 我把「跳過檔首 HTML 註解」當理所當然——那正是這個 repo 今天下午才用兩條 blocker 殺掉的東西,我自己殺的。
- 我列舉殘留寫法,以為列得夠——通才席拿早上真報告證明「列舉會漏、例外才該列舉」。

## 留痕紀律

★這一份在按下記帳之前寫完★。carrier=接手的人-sonnet(全錨、算人數、blocker;通才席一句錨不到不當載體)。

## 處置

8 條全折,accepted 為空。上限輪:不再開新編號,實作碼的殘餘風險交代碼審(code-review-yield)。

(本檔在此之後不再修改。)
