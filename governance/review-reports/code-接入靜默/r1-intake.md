# code-接入靜默 r1 收貨與機械重現

被審 commit 69d5fdd,凍結快照 `r1-snapshot.patch`(sha256 5dbeb677c8b4248c…)。
兩席:單reviewer-sonnet(9 條)、架構對齊-sonnet(5 條)。合計 14 條,去重後 14 個獨立問題。

## 收貨三道(全機械)

| 席 | quote-check | refcheck | seat-check |
|---|---|---|---|
| 單reviewer | ✅ 9/9 全錨到凍結快照 | ok 14 / missing 0 / out_of_range 0 | unreported 1(只觀測不擋) |
| 架構對齊 | ✅ 5/5 全錨到凍結快照 | ok 17 / missing 0 / out_of_range 0 | unreported 2(只觀測不擋) |

seat-check 的 unreported 是命名造成的:兩席都用 `scripts/lumos:行號` 當證據而沒有寫出 patch 檔名,
檢查器因此判「沒碰材料」。逐條看引句都錨得回凍結快照,判非真缺口。

## 佐證通道機械重現(編排者自己跑,不採信席位的數字)

★這批席位報的很多是「某個測試工具會不會回 0」——那是可以直接跑出來的,所以全部重跑一次。★

| 現象 | 指令 | 結果 | HIT/MISS |
|---|---|---|---|
| C# 對不到測試回 0(f1) | `dotnet test --filter FullyQualifiedName~lumosProbeNoSuchTest9f3c`(dotnet 9.0.117,現建 xunit 專案) | rc=0,印「No test matches the given testcase filter」 | HIT |
| 同上加旗標會回非零 | 同上 `-- RunConfiguration.TreatNoTestsAsError=true` | rc=1;對到真測試時 rc=0 | HIT(這是解法,席位沒提) |
| jest 對不到測試回 0(f1) | `jest -t lumosProbeNoSuchTest9f3c`(jest 29,現建專案) | rc=0,印「Tests: 1 skipped, 1 total」 | HIT |
| jest 有沒有旗標可修 | `--passWithNoTests=false` | 仍 rc=0 → jest 沒有對應旗標 | HIT(席位沒查這層) |
| pytest 對不到測試回非零 | `pytest -k lumosProbeNoSuchTest9f3c`(pytest 8) | rc=5;對到真測試 rc=0 | HIT(所以不是全部工具都分不出來) |
| ★xcodebuild 三段寫對、方法名打錯仍回 0★ | 在 calc-ios 真跑 `-only-testing:CalculatorTests/CalculatorEngineTests/lumosProbeNoSuchTest9f3c` | rc=0,`Executed 0 tests` | HIT(★兩席都沒報這條,是重現時自己撞到的★) |
| ★-quiet 會把唯一的證據藏掉★ | 同上,帶 / 不帶 `-quiet` 各跑「1 支」與「0 支」四次,逐行比對 | 帶 -quiet:兩份輸出完全一樣(只差時間戳);不帶:`Executed 1 test` vs `Executed 0 tests` | HIT(同上,席位沒報) |
| unfilterable 沒有讓推送擋下來(f2) | 讀 `_codeloop_guard_verdict`:兩處判定都只比對 `status == "red"` | 屬實 | HIT |
| S3 的 symbol 那組被截斷吃掉(f3) | 讀 `_profile_stack_mismatch`:兩組串接後 `out[:8]`,測試那組永遠在前 | 屬實 | HIT |
| 兩支掃描的略過名單不同步(f4) | 逐字比對兩處字面 set:健檢那份多 `scripts` | 屬實 | HIT |
| rglob 對略過名單沒有剪枝(f5) | 讀 code:`root.rglob("*")` 後才過濾 | 屬實(未另跑效能量測,結論不依賴數字) | HIT |
| 新快取繞過共用信任檢查(f6/架構 f5) | 讀 code:只有 `mkdir` + `_write_lf`,沒有 `_trusted_private_dir` | 屬實 | HIT |
| 冒煙測試證不了精準度(f7) | pytest `-k` 是子字串比對 | 屬實(概念層,已寫成誠實邊界) | HIT |
| 快取沒有版本與保鮮期(f8) | 讀 code:key 只有 realpath + run_cmd | 屬實 | HIT |
| 猜不到的語言骨架留空、S3 也抓不到(f9) | 讀 code:`load_test_profile` 對空字串靜默退回 csharp;`_profile_stack_mismatch` 只認得表內副檔名 | 屬實 | HIT |
| `.vue` 產出壞設定(架構 f4) | 用 `.vue` 檔跑一次骨架產生 → `symbol_profile: "vue"`,而正典表沒有這個鍵 | 屬實 | HIT |
| 新產出被關在保護鎖後面(架構 f2) | 讀 code:`_scaffold_project` 開頭 `kg.exists(): return`,外層 `cmd_init` 又更早 return | 屬實 | HIT |

★MISS 0 條。★ 每一條都自己重現過才折。

## 編排者判讀:兩條「觀察對、判準要自己想」

- **f1 的觀察對,但它開的藥不對。** 席位判「骨架指令必被判不可信 → 骨架有問題」。
  重現之後看到的是更深一層:**判準本身建立在一個沒驗過的前提上**——「測試工具找不到測試會回非零」。
  八種棧裡只有 Python 成立。照席位的藥去改骨架,只會讓 C#/Node 的骨架好看一點,
  xcodebuild 那條(本案的起因)還是抓不到。所以整條判準換掉,不是改骨架。
- **f2 說「跟派工詞背景欄的宣稱不符」,但真正的問題不是宣稱。**
  假綠的殺傷力跟紅一樣(你以為合約被守著,其實沒有),所以要走跟紅同一條路:
  高風險擋、低風險比照 2026-09-07 人裁只提醒。不是「把宣稱改軟」。

preflight-4: ran
本輪沒有另派前掃便宜 agent:code 迴圈的前掃對象是 patch 不是散文 spec,
上面「佐證通道機械重現」那一整張表就是編排者自己逐條跑的等價步驟。
