preflight-4: ran

# 設計審第 1 輪收貨紀錄:殺傷力配方失配提醒

## 前置四項掃描(r1-preflight.md)的處置

前掃 21 條命中(①5、②0、③4、④12),全部改進計劃真檔;動到核心的標「核心」,交本輪席位審。

| 前掃編號 | 修改前 → 修改後 | 核心 |
|---|---|---|
| ①1 | 「專案根」→ 平台根(`load_platforms` 的 root;專案根照 `_repo_root_from_env`) | 核心(④1) |
| ①2 | 「工作目錄」→ 寫明讀工作目錄、guard kill 讀隔離工作樹的檢出版本(〈誠實界線〉) | |
| ①3 | 「合約 KEY 前 40 字」→ 配方 invariant 前 30 字(跟 guard kill 輸出同長度) | |
| ①4 | 「回頭重讀那次抽出的共用路徑守衛」→ 不再用 `_repo_path_unsafe`,改用 guard kill 同一種 realpath 圍欄 | |
| ①5 | 「活節點」→ 逐字照 P 段:跳過 verification 型與 superseded、stale | |
| ③1–③4 | 範圍、回退、S1 與 S4 的矛盾 → guard kill 一律不改;kill-add 改成只提醒不擋(保留「宣告不擋、跑時擋」);刪掉「不提供略過旗標」 | 核心 |
| ④1 | kill-add 驗專案根的檔 → 驗平台根;設定讀不了或平台不在設定只提醒「沒驗」 | 核心 |
| ④2–④4、④11 | 抽共用改 guard kill 會改到它的 drifted 說明、非 UTF-8 行為、符號連結圍欄、空原文 → 不改 guard kill;新判斷函式自己的狀態(malformed/outside/missing/hits/ok) | 核心 |
| ④5 | kill-add 插入點 → 配方組好之後、判重迴圈之前(★r1 正確性席 F2 改成判重之後、驗實際要寫的那一條,見下表 c2★) | |
| ④6 | doctor 軟提醒 → 用 `warn_soft`、`--verbose`/`--ci` 全列;REVISIT 改 `lumos doctor --verbose` | |
| ④7 | 跳過規則 → 逐字照 P 段;用已讀的開頭欄位篩 | |
| ④8 | 配方元素非物件、欄位非字串 → `malformed`;整段例外保護 | |
| ④9 | 既有 8 處 kill-add 宣告失配或逃逸配方 → 不擋所以照舊能寫;〈實務隱患〉寫明清單 | |
| ④10 | 段落代號 → P2,放在 P 之後 | |
| ④12 | (其餘語意對照,已照改) | |

refcheck 只對新測試名提醒懸空(實作時建);沒有壞引用。

## 席位報告收貨(6 席全收齊後才動計劃)

四道機械檢查:6 份都已是正規化格式;quote-check 全數錨定;席位沒回報動過 repo 根的 git,reflog 無異動。

finding 編號:c=正確性-opus、b=邊界-sonnet、h=接手-sonnet、r=回滾-sonnet、k=併發-sonnet、a=架構對齊-sonnet,後接報告的 F 編號。全部折進計劃(做法 1–5、條款 S1–S7、回退、實務隱患、誠實界線)。

| 編號 | 等級 | 折在哪 |
|---|---|---|
| c1 b1 a1 | major | 做法 1 基準改成平台根所在 repo 的最上層(跟 guard kill 開工作樹的根一致);S5 對照測試 |
| c2 | major | 做法 3 驗證挪到判重之後、驗實際要寫的那一條(covers 只更新時用既有那條的平台);S2 |
| c3 b2 k1 r5 | major/minor | 做法 2 自己先解析設定 JSON,壞了就判「讀不了」;S4 |
| h1 | major | 新增 kill-rm(做法 4、S6);提醒結尾附修法 |
| h2 | major | RETIRE-IF 改看 `check-p2` 事件(做法 5 記帳) |
| c4 b5 | minor | 圍欄照 guard kill 的 realpath 前綴判法,絕對路徑符號連結歸 outside;S5 |
| c5 | minor | 提醒字面照狀態分寫(做法 3) |
| c6 b3 | minor | malformed 含 platform/invariant 型別;逐條例外保護(做法 1、5) |
| c7 | minor | 設定只讀一次(做法 2) |
| c8 r4 | minor | S7 改綁對照測試、釘 drifted 與逃逸說明字面 |
| c9 | minor | 量改成 rtb 73 條(實務隱患) |
| b4 | minor | 平台根找不到只列一條(做法 5、S4) |
| k2 | minor | 只讀一般檔,不開具名管線(做法 1) |
| k3 | minor | 同檔只讀一次;讀到半截檔的說明(實務隱患) |
| r1 | minor | 明寫用 `warn_soft`、全對用 `ok()`(做法 5) |
| r2 | minor | 被判重擋下時不印(做法 3、S1) |
| r3 | minor | 回退補 test 懸空與 REVISIT 的處理 |
| h3 | minor | REVISIT 寫明回報方式、落點與三段門檻 |
| h4 | minor | 〈誠實界線〉落點:Systems/guard-kill、skill、路線圖 1a |
| h5 | minor | 〈誠實界線〉先提交再跑 guard kill |
| a2 | minor | 專案根用 doctor 既有 `repo_root`(做法 5) |
| a3 | minor | S5 對照測試防兩份判準分家 |

重現不到而沒折的:無。放行的:無。
