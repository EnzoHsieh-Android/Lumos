preflight-4: ran

# r2 收貨紀錄(Codex完全支援)

## 前掃
- r2 為修訂稿驗收輪:refcheck 機械跑(結果見上);首輪四類前掃 r1 已跑,本輪不重派 agent,語意類交席位審。

## 外家否決(Codex)r2 收貨(6 條新 finding 全錨、refcheck 5/5;19 條「已修驗收通過」)
- 正規化:severity/blocking 同行拆兩行;原檔 r2-外家否決.raw。
- #21(信任綁 hook 定義 hash、`/hooks` 畫面、變更即重審)=文件宣稱,與 r1 實驗 C/D「不按不跑」不衝突;折入:install/update 提示改寫成「內容變了要再按」,enforcement 永不出 active。
- #22(seats 讀改寫競態)HIT:折入=改成每席一個 token 檔、原子 rename 認領。
- #23(自訂 agent 點名選中未驗)HIT:折入=S2 進場實驗。
- #24(`--orchestrator` 預設 claude 是 fail-open)HIT:折入=比照 `--tier` 首輪必帶、持久化到帳,後續讀帳,缺=擋。
- #25 S1→S0 誤植、#26 驗收標題「四條」實五條:折入。

## 架構對齊 r2 收貨
- r1 3 minor+1 ⚠ 驗收通過;新 1 minor:Codex hook 層值域少「已註冊但檔案不在」的 degraded 態(file: `scripts/lumos:12113` 的 2026-07-07 事故守衛);折入=值域補 degraded。

## 整合知識同步 r2 收貨(7 條新:F9–F15,全錨、refcheck 18/18;r1 8 條中 6 條驗收通過、F3/F5 部分)
- F11(major)HIT:file: `scripts/lumos:10609-10610` created 分支寫死 `"# CLAUDE.md\n\n"` 檔頭 → 折入:檔頭依目標名。
- F12(major)HIT:本 repo `AGENTS.md:8`「不要改 docs/*-knowledge」與範本鐵則一「當次寫回」並存即矛盾 → 折入:本 repo 指路檔第 4 條改成角色條件句;init 對既有 AGENTS 檔印前 8 行提醒人看(語意衝突機器判不了,誠實界線記)。
- F10(major)HIT:reference.md/templates.md 亦有 Agent tool 呼叫(5 處 file:line 機驗)→ 折入:掃描範圍=skill 目錄全部 .md。
- F9(minor)HIT:roster 對帳 advisory 不進合取(`_roster_tail` 文字+code-loop SKILL 21 行)→ 折入:裁定(d)理由改寫「觀測失準」而非「閘失效」。
- F13/F14/F15(minor):折入(措辭一致、$skill 前提、無標題 fallback)。
## 邊界可執行 r2 收貨(7 條:N1–N7,全錨、refcheck 6/6;r1 9 條中 6 條驗收通過、F2/F5/F6b 部分)
- N1(major)HIT:fallback copy 與外方目錄無法分辨 → 折入:我方複製物落 `.lumos-managed` 標記檔,只對有標記的 rmtree。
- N2(major)HIT:file: `scripts/lumos:10235-10238` False 分支訊息寫死 LUMOS_PROBE → 折入:回三態(ok/probe/merge-failed),訊息分開。
- N3(major)HIT=外家 #22 同題 → 折入:每席一個 token 檔原子 rename 認領。
- N5(major)HIT=整合 F15 同題 → 折入:無標題行→插檔案最前。
- N7(major)HIT:r1「沒 armed 檔或過期→什麼都不回」被本輪重寫拿掉 → 折入:先驗 TTL 再認領 token,任一不成立即不回。
- N4/N6(minor):折入(估總量只算該層生效檔;mark 字典補鍵)。
