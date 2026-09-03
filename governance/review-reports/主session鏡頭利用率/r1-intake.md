preflight-4: ran

# r1 前掃留痕(主session鏡頭利用率)

日期:2026-09-03(晚)。前掃席=haiku,固定四項+10 條機械宣稱逐條開檔驗。編排者對每條回原檔核過再處置。

## 機械排乾

- refcheck:統計: 對得上 ok 1 / 檔案不存在 missing 0 / 行號超出檔案長度 out_of_range 0
- prose-lint 0;pitfalls --check 有節;lint 0;doctor 0(409 篇)

## 前掃結果(haiku,29 次工具呼叫):①3 條術語未當場解釋 ②無 ③無 ④10 條:8 對、2 部分對

## ④ 語意類命中(修改前→後)

### 語意-1 「使用帳 gitignored」→ 錯(前掃判部分對,編排者 `git check-ignore`+`git ls-files` 核:被追蹤)
- 修:現況段加一行「被 git 追蹤、append-only 行級合併」;誠實界線改寫。
### 語意-2 「Read 開過那篇筆記」當行為證據 → 假陰性風險(前掃 C10 只驗到 Read 存在;編排者抽最近逐字稿:Read 工具 0 筆——家規要用 cat/sed)
- 修:定義加第三種證據「Bash 指令裡出現筆記路徑」,沿用既有 `extract_bash_file_paths`。
### 語意-3 「lumos gov --stats 可算」→ 它只讀治理帳
- 修:改「唯讀腳本讀使用帳」。
### 術語 ×3:TTL、固定席/自由席、LENS-ACK 當場一句解釋。

## 席位模型偏離(記錄)

派工當下 sonnet 連續回 500/529(通才 ×2、量測效度 ×2、接手 ×1、架構 ×1 共六次失敗),四席全改 opus 重派,r1-dispatch.json 逐席註明;外家 Codex 正常。

## 收貨三道(五席)

| 席 | 條數 | 最高 | blocking | quote-check | refcheck |
|---|---|---|---|---|---|
| s1 通才(opus) | 21 | blocker | 13 | 全錨 | 見 refcheck 輸出 |
| s2 量測效度(opus) | 13 | blocker | 11 | 全錨 | 13/13 |
| s3 接手的人(opus) | 14 | blocker | 10 | 全錨 | 36/36 |
| arch 架構對齊(opus) | 8 | major | 3 | 全錨 | 38 ok / 1 missing |
| ext Codex | 6 | blocker | 6 | 全錨 | 16/16 |

合計 62 條(21+13+14+8+6)、blocking 43(13+11+10+3+6)、blocker 11(s1-f1/f3/f4、s2-f1..f5、s3-f1/f2、cx-f1)——逐檔 grep `^severity` 數的。

## 佐證通道機械重現(編排者)

- cx-f2 / s1-f4 / s2-f2 / s3-f1「extract_bash_file_paths 只認 rm/mv/cp」:`sed -n 218,232p check-graph-sync.py` docstring 明寫 → HIT。
- s1-f13 / s2「本 session 0 次 Edit」:編排者掃最近 12 份逐字稿 tool_use:本 session Edit 0/Write 1/Bash 372;12 份合計 Edit 161 集中在 2 份 → HIT(推送發生率是第一個要量的)。
- s2-f4「scripts/lumos 無副檔名不入樣」:`hook_decide` 用 suffix 過濾(s2 實跑回 None)→ 開檔核 HIT。
- s3-f6「時區」:usage-log ts 無時區、逐字稿 timestamp 帶 Z → 開檔核 HIT。
- s3-f8「test_lumos.py 是錨點」:ANCHOR_FILES 首項 → HIT。
- arch-f1「hook 直接寫帳無先例」:HOOK_ENTRIES 註解記 verification-rot-check 已撤 → HIT。

## 處置摘要

62 條全折(blocker 輪 accepted 必空):量測核心重寫(見計劃「r1 推翻的三件事」與 d2)。
★密度=43 blocking/約 5000 字,遠超重寫門檻;核心「只量不加義務」未被推翻,同編號折入,重寫與否攤 Enzo。★
