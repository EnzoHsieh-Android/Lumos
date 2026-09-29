# r3 收貨紀錄(code-存量漂移改法)

凍結材料:429b109f..e7112c53 的 git diff -U10(第 2 輪的修正本身),770 行,不拆;`r3-snapshot.patch`。
5 席全新:正確性 opus、邊界 sonnet 5.5、外家否決 Codex(gpt-5.6-sol xhigh,唯讀沙盒)、架構對齊 sonnet 5.5、資安 sonnet 5.5。
偏離:派工鏡頭同前兩輪,由編排者用整批範圍 19162c1e..HEAD 先算好存檔交給各席。

## 席位收貨

- 5 席全交,等完成通知、ls 確認後才讀;外家否決席用背景等待確認行程結束後才讀;clone-ns 的 reflog 只有編排者自己的提交。
- report-normalize 5 份合格;refcheck 全對得上。
- quote-check:4 份對 r3-snapshot.patch 全錨定;架構對齊席 F2 的引句「檔案系統側 NFC 找檔收成通用的 _nfc_child/_phys_path」引的是編排者寫的共同規則檔,不在凍結 patch 裡,錨不到——不採信引句,改由編排者機械重現(見下表)。載體席選全錨的正確性席。
- 發現 14 條:正確性 4、邊界 4、外家否決 2、架構對齊 2、資安 2;major 4 條(機器數:正確性 F1、邊界 F1、外家否決 F1 F2)。
- 多席獨立報到的同一件:c4 換完的結果標準 YAML 讀法不同而照樣寫入(正確性 F1 全形空白、邊界 F1 冒號後空白、外家否決 F1 控制字元)——同一類第三次(r1 邊界 F2、外家 F1;r2 正確性 F1、外家否決 F1)。「看:」那行 - 開頭沒補 ./(正確性 F2、邊界 F3)。
- 上限到頂(high 3 輪)仍有 major,編排者停下來問人;Enzo 2026-09-29 裁「換形狀修完再審一小輪」:c4 改成「--old 只用來指是哪一項,那一項整個換成 --new,由既有 _yaml_quote 加引號寫整項」,其餘全折,修完破例派一小輪全新席位只審這段修正。
- 本輪有 major,accepted 必須是空的,14 條全折。

## 機械重現(在審的那一版 e7112c53 上;方法同前兩輪:折入後的新測試格,把修法還原就翻紅;每個改壞都在全新 clone、清掉 __pycache__ 後跑)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性 F1 / 邊界 F1 / 外家否決 F1(c4 第三次被繞過) | 換形狀後:不經 `_yaml_quote` 直接寫 | HIT:c4 測試 ⑤b 與 ⑤紅(`a"b'c`、特殊字元不再包引號);`--new` 不擋控制字元與頭尾空白 → r1 測試 ④紅;冒號後空白那個輸入改成整項重寫成 `valid_under: "…"`(r3 測試 ①) |
| 邊界 F2(帶行尾註解的引號項目訊息指錯) | 拿掉行尾註解判斷 | HIT:r3 測試 ①C1 紅(整項重寫會丟註解,現在改成工具不改、講明原因) |
| 外家否決 F2(git 路徑被截斷) | `_drift_git_cmd` 套回 300 字截斷 | HIT:r3 測試 ②例外「No closing quotation」 |
| 資安 F1(git 萬用字元) | 拿掉 `--literal-pathspecs` | HIT:②紅;另讀席位附的 `git add 'd/*.md'` 多暫存實驗 |
| 資安 F2(兩種 Unicode 拼法並存) | 拿掉 `len(ps) > 1` 檢查 | HIT:③紅(替身 `_drift_git_paths` 回兩筆);真實現場 macOS 造不出,席位標推論 |
| 正確性 F2 / 邊界 F3(「看:」與 context 對 - 開頭) | 「看:」不帶 node=True | HIT:⑤紅;Env.find 不剝 ./ → ④ context 那格紅(第一次改壞沒紅:現場 `./-y` 不剝也找得到,改成 `-d/z` 與 `Issues/z` 撞名的現場後翻紅) |
| 正確性 F3(./-x 被當檔名猜) | `_drift_fix_target` 拿掉 explicit | HIT:④紅,「同名筆記有 2 篇」 |
| 正確性 F4(git 指令接線沒測) | 成功訊息改回用索引鍵 | HIT:②接線那格紅(同程序替換 `_drift_git_paths`、跑 cmd_drift_fix) |
| 邊界 F4(<src/lib> 被當佔位字) | 正則加回「小寫/小寫」 | HIT:⑥紅 |
| 架構對齊 F1(`_sh_quote` 住在代碼審收尾段) | 讀 `_sh_quote` 位置 | HIT:搬到檔頭通用區,跟 `_nfc_child`、`_phys_path` 放一起 |
| 架構對齊 F2(`_plan_for_loop` 內聯 NFC 找檔) | 讀 `_plan_for_loop` | HIT(引句錨不到,讀碼確認現象成立);改用 `_nfc_child`,escape 子集 139 格綠 |

## 推送前檢查

- 新增告警閘對 19162c1e..9c236f23:第一次提交多 1 條(說明文字裡的全形破折號「r1–r3」),改成「r1 到 r3」後 0 條;受波及合約測試 59 支照跑。

## 處置

- 14 條全折(folded),accepted 空、refuted 空。程式、測試、指令文件在 9c236f23(`wip: 代碼審 r3 折入`);家節點 Systems/存量漂移守衛 的 c4 PITFALL 改寫成新形狀並註明跟設計計劃第 5 節不同、以家節點與程式為準;引號那行補上 git 指令三項;TEST 清單加 t_drift_fix_review_r3_edges;lumos-project-notes commands/04 的 c4 用法改成整項。
- 設計計劃(存量漂移改法_計劃)仍沒動:它是設計審凍結過的審材;偏離寫在家節點。
