# r4 收貨紀錄(code-存量漂移改法)

這一輪是上限(high 3 輪)到頂後,Enzo 2026-09-29 裁「換形狀修完再審一小輪」的破例加審。
凍結材料:e7112c53..9c236f23 的 git diff -U10(第 3 輪的修正本身),965 行,不拆;`r4-snapshot.patch`。
5 席全新:正確性 opus、邊界 sonnet 5.5、外家否決 Codex(gpt-5.6-sol xhigh,唯讀沙盒)、架構對齊 sonnet 5.5、資安 sonnet 5.5。
偏離:派工鏡頭同前三輪,由編排者用整批範圍 19162c1e..HEAD 先算好存檔交給各席;共同規則這輪寫明「引句只准引凍結 patch」。

## 席位收貨

- 5 席全交,等完成通知、ls 確認後才讀(外家否決席等背景行程結束);clone-ns 的 reflog 只有編排者自己的提交。
- report-normalize 5 份合格;refcheck 只有資安席一條 `docs/...` 省略寫法對不到(那席 0 條發現,不影響)。
- quote-check:4 份全錨定;邊界席 F1 的引句把兩行程式接成一句,錨不到——不採信引句,改由編排者讀碼重現(見下表)。載體席選全錨的正確性席。
- 發現 13 條:正確性 5、邊界 2、外家否決 3、架構對齊 3、資安 0;major 7 條(機器數:正確性 F1 F2、邊界 F1、外家否決 F1 F2 F3、架構對齊 F1)。
- 多席獨立報到的同一件:c4「哪種項目能整項改寫」的判斷還是漏(正確性 F2、邊界 F1、外家否決 F1);./ 開頭退回用檔名猜(正確性 F3、外家否決 F2、架構對齊 F3);乾淨檢查的 git diff 還把檔名當萬用字元(正確性 F5、邊界 F2、外家否決 F3)。
- 破例這輪仍有 major,編排者停下來問人;Enzo 2026-09-30 裁「改走 lumos set、修完直接推」:c4 不再自己寫開頭欄位,改列證據與一條預填好的 lumos set 整欄指令(要改的那項放佔位字,set 擋原封不動的佔位字);其餘全折;修完不再派審查席,靠測試與改壞驗證把關就推。
- 本輪有 major,accepted 必須是空的,13 條全折。

## 機械重現(在審的那一版 9c236f23 上;方法同前幾輪:折入後的新測試格,把修法還原就翻紅,或讀碼確認;每個改壞都在全新 clone、清掉 __pycache__ 後跑)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性 F1(提示教人給片段,照做會刪掉其餘前提) | 讀 9c236f23 的 `_drift_fix_hint` c4 那條與 `_drift_c4_print` | HIT:讀碼確認,提示仍寫 `--new "<新片段>"`、證據頁把範本句當 --new;席位另用 rtb 那 3 筆真實 c4 實跑 rc 0 刪掉內容。c4 改走 lumos set 後整類消失;新 c4 測試 ②(各項與預填指令)在證據頁不標要改的那項、或指令各項不對時翻紅 |
| 正確性 F2 / 邊界 F1 / 外家否決 F1(整項改寫的判斷漏網) | 讀 9c236f23 的 `_drift_c4_item`:只看緊鄰下一行、raw[0] 白名單漏 - # ? | HIT:讀碼確認,三席各附標準 YAML(PyYAML、Ruby)讀壞的重現;c4 不再寫檔,這段程式整個拿掉 |
| 正確性 F3 / 外家否決 F2 / 架構對齊 F3(./ 退回用檔名猜) | Env.find 的 explicit 找不到改回退用檔名猜 | HIT:r4 測試 ①紅,`lumos set ./z status done` 改到 A/z |
| 正確性 F5 / 邊界 F2 / 外家否決 F3(乾淨檢查的萬用字元) | 乾淨檢查拿掉 --literal-pathspecs | HIT:r4 測試 ②紅,`q*.md` 沒改卻因 `qz.md` 有改動被擋 |
| 正確性 F4(合併衝突時報成三種拼法) | `_git_paths_nfc` 不去重 | HIT:r4 測試 ③紅 |
| 架構對齊 F1(列 git 原樣路徑第二份實作) | `_guard_raw_git_path` 改回自己掃 | HIT:r4 測試 ④紅;現在 guard 與 drift 共用 `_git_paths_nfc` |
| 架構對齊 F2(c4 一律加引號、沒走 fmt_list_item) | 讀碼 | HIT;c4 不再寫檔,整欄重寫交給既有的 set,這條隨之消失 |
| c4 改走 lumos set 的新保護 | c4 也做乾淨檢查 / set 拿掉佔位字檢查(移到 `_set_conditions_locked` 後再驗一次) | HIT:c4 測試 ③、④各自翻紅 |

## 推送前檢查

- 新增告警閘對 19162c1e..ca7a0314:第一次提交多 1 條(`_cmd_set_locked` 複雜度 11 > 10,佔位字檢查加在這裡),把檢查移進 `_set_conditions_locked` 後 0 條;受波及合約測試 59 支照跑。
- 相關子集(drift 403、guard 481、set_ 107、cond 101、escape 139、context 41、find 46、nodehome 240、valid_under 7)全綠。

## 處置

- 13 條全折(folded),accepted 空、refuted 空。程式、測試、筆記、指令文件在 ca7a0314(`wip: 代碼審 r4 折入`):家節點 Systems/存量漂移守衛 的 c4 PITFALL 改寫成「c4 不寫檔、改走 lumos set」並註明跟設計計劃第 5 節與 [S5] 不同、以家節點與程式為準;Systems/lumos-cli-write 補 set 擋佔位字;Systems/lumos-cli-read 補 find 對 ./ 的規則;commands/04 的 c4 用法改寫。
- ★這一段修正沒有再派審查席★(Enzo 裁「修完直接推」),只由新測試與改壞驗證把關;留痕 note 寫明。
