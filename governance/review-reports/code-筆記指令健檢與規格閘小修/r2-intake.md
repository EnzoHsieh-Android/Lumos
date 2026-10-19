# code-筆記指令健檢與規格閘小修 r2 收貨與修正

七席(正確性、邊界、資源、整合、通才、架構對齊、資安)全部交回後一次存檔;report-normalize 只做格式搬移(資源 1 處、正確性 3 處)。major 12 條(正確性 2、邊界 2、整合 3、架構對齊 2、通才 3),最大一族是 refcheck 把「路徑+子命令、無旗標」整串當路徑誤報 missing(正、邊、整、通四席獨立一致)。資安席 minor、blocking 0。

## 錨不到的三句引句:機械重現

| 編號 | 指令 | 輸出 | 判 |
|---|---|---|---|
| 邊界 引句#2 | `grep -n "_NS_NEG_CLAUSE_PUNCT = " scripts/lumos` | `35391:_NS_NEG_CLAUSE_PUNCT = set(",，、。;；:：!?！？…—")` | HIT(席位把全形標點打成半形;內容相同) |
| 通才 引句#9 | 同上 | 同上 | HIT(同上) |
| 整合 引句#3 | `grep -rn -F 'lumos cochange check [--staged' . \| grep -v review-reports` | `docs/lumos-toolchain-knowledge/Systems/cochange-guard.md:42:- \`lumos cochange check [--staged\|--diff <A..B>] [--repo] [--json]\` …` | HIT(diff 外既有筆記) |

## 編排者裁定(交作者照做)

- G1 refcheck 指令判法(正1、邊1、整2、通1):統一規則改成「第一個詞是真檔、後面的詞不像路徑(不含 `/`、沒有副檔名)就當指令,只核對第一個詞」;帶空白的資料夾路徑(後面的詞含 `/` 或副檔名)照整串核對。S18 與 refcheck 家節點的 WHY 一起改。
- G2 文件跟上(整1、整其餘):d3 用 decision-amend 補「起點已 done 才寬待、不做清單照查、這次才改 done 的照 doing 嚴」;〈做法〉10 B2、〈實務隱患〉(c) 同步。
- G3 測試缺口(通2 與通其餘):補「done、留痕過期、條款測試紅 → 擋」的行為測試;gone 測試的 docstring 要嘛補斷言、要嘛改字。
- G4 範圍起點(架1):`_spec_gate_status_at` 的起點改用既有 `_range_base`,三點範圍取 merge-base。
- G5 子句標點(邊2):回到「Unicode 類別 P 都算子句記號」的統一規則,只扣掉斜線、連字號類、底線(並列詞),不再明列。
- G6 未提交警告雜訊(正3、邊3):判斷時排除簿記檔(先找 scripts/lumos 既有的簿記檔判定,不要自寫清單)。
- G7 同秒取舊(正2):先依 token 去重再比時間;同秒時取本機帳那一筆;補 (B,A,B) 回 B 的測試。
- G8 已排除行回溯(資1):把冒號前置檢查搬進 `_excluded_line` 本身,所有呼叫端一起受保護;補 `_door_exclusions` 路徑的耗時測試。
- 其餘 minor 全修;駁回 0 條。
