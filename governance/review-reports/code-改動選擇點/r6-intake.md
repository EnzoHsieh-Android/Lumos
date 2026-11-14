# code-改動選擇點 r6 收貨紀錄(記帳更正輪)

本輪是記帳更正輪,緣由見 r5-記帳更正.md:第五輪各席 `--reviewed` 填各包致同輪 hash 分裂,且資安席快照排除了其他席材料裡有的 docs/.kill-log.jsonl。程式自第五輪凍結(修後 83ac95c8)沒有改動;r6-snapshot.patch 比 r5-snapshot.patch 只多 kill-log 三行。
新派一席資安看整份 r6-snapshot.patch(14982 行、79 支檔,含 kill-log),報告列出 79 支並逐支結論;三句引句全數錨定。其餘六席沿用第五輪報告原檔重記(正確性、邊界、通才、資源、合約、架構對齊),判讀沿用 r5-intake.md。

## 重現表

| id | 核對 | 結果 |
|---|---|---|
| c1 a1 r1 | 同 r5-intake.md 重現表 | HIT |
| s1 | 讀 `_render_gov_choice`:`waive` 的 label、乾節點 row、`nores` 鍵未過 `_kill_esc`,同函式 decl 有過;資安席臨時 clone 加三筆帶換行的帳行跑 `gov --stats`,偽造行單獨成行(與第五輪資安 s1 同一件) | HIT |
| s2 | 讀 `_choice_push_round`:`LUMOS_CHOICE_SINCE` 晚於今天時印一行後 `return []`,不寫治理帳(與第一輪 s2、第二輪 s1、第四輪 s2 同一件) | HIT |

## 分組與處置

| 組 | 條目 | 處置 |
|---|---|---|
| — | c1 a1 | 放行(minor,附來源):同 r5-intake.md;修前同樣對不上,安全方向失敗 |
| — | r1 | 放行(minor,附來源):同 r5-intake.md;與第三輪 r2、第四輪 r1 同一件且已放行 |
| — | s1 | 放行(minor,附來源):lumos 威脅模型為單人自用、AI 依序操作,外來文字回顯屬已裁放行類;要先有人把惡意帳行寫進 repo |
| — | s2 | 放行(minor,附來源):與第一、二、四輪同一件且已放行;生效時印一行,此值只在測試總檔程序設定 |

## 回歸因果(第 6 輪)
- 沒有新修補;判過且無修補回歸:regression-set none。

## 結論
最高 minor、零 blocking;5 條全數附理由放行,0 條折入。
