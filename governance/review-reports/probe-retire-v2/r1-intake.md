# probe-retire-v2 r1 收貨紀錄(2026-08-25)

## 引句機械收貨
quote-check:s2/s3/arch/ext 全數錨定;s1 一句「消除兩閘並存混淆面」錨不到——機械重現:norm 比對 v2 快照 d1 行含「消除兩閘並存混淆面」→ HIT(s1 引句取自 why_chosen 欄位換行處)。

## 佐證抽驗(命令+輸出+HIT/MISS)
- s2「三案各兩輪」:`grep -o 'code-...兩輪' docs/.governance-log.jsonl` 三筆 pass note 皆含「兩輪」→ HIT(v2「單輪」證偽,d1→d3 更正)。
- s1/ext「code-loop reference §4 教 panel/probe」:sed 328/371/399 實讀 → HIT。
- s3「先裁後動成立」:git log 今日相關檔零搶跑 → 採信(其自跑驗證)。
- s3「stale 只掃 Verification/」:scripts/lumos 讀碼(rel.startswith("Verification/"))→ HIT。
- ext「disposal 允許 major accepted」:scripts/lumos:10113-10116 實讀(blocker 才強制清空)→ HIT(d2 裁定由此而生)。

## 輪結論
18 審項/blocking 11,去重五修位全折零放行(blocker 席在輪,accepted 必空);d2/d3 兩筆裁定入 decisions。
