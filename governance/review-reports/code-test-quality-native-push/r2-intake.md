# 第二輪收貨與處置（2026-10-08）

完整七席最後報告收齊後才写入及修改repo。原資安席兩次被平台拒絕交付，沒有 clean 資格；替代資安席重新独立讀同一凍結版本。Windows 原生仍排除；連結清理只有 POSIX + 模擬API資格。

所有七席 quote-check 與 seat-check rc0；五席refcheck rc0。資源席一個臨時fixture路徑、邊界席一個連結示意字串被refcheck辨為不存在repo檔，原報告與rc1原樣保留；真正原碼引用均存在，編排者以獨立反例重現，不把額外示意路徑冒稱repo證據。原席格式重發請求未能啟動（agent thread limit），沒有自行改報告。

## 重現、判準與去向

| ID | 席觀察 | HIT/MISS 與證據 | 歸因／去向 |
|---|---|---|---|
| D1 | 新CLI配舊sidecars可假綠 | HIT：r2-controls-red.txt 真capture rc0；更新控制以去掉summary驗證的舊配套替身驗拒收、命令不啟動 | 原有部署角落未補，不把 presence 修復算造成；folded，綁內容指紋與同bytes載入 |
| D2 | global --vault漏完整性通道 | HIT：架構報告原始反例；新控制test_global_vault_option_retains_structured_deployment_error | 原有漏查；folded，沿正式argparse，不再自行猜cmd |
| J1 | orphan failure未拒收 | HIT：r2-controls-red.txt孤立failure仍executed | 原有漏查；folded，拒收未掛於testcase的outcome |
| X1 | PHP/Node模組真程式被當附件 | HIT：修前5d8同四副檔名綠，修後598e四項紅，見r2-before-impact-controls.txt/r2-controls-red.txt | 有證據的修補回歸：R1新增results分類，既有程式副檔名漏覆蓋被放大；folded，共用五份分類補齊 |
| C1 | cache解析在外側仍清理 | HIT：真POSIX symlink + 受控is_symlink=False；5d8外側bytes保留，598e刪除 | 有證據的修補回歸，限此受控案例；非Windows原生背書；folded，解析後位置也須成立 |
| C2 | extensionless CLI bytecode漏清 | HIT：真SourceFileLoader先產出快取，598e deinit仍留下 | 原有漏查，R1 bytecode修復未涵蓋主入口；folded，已知CPython檔名及使用者bytes保留 |
| R1 | 改名進結果附件後角色來源漏掉 | HIT：真R100改名；5d8有新側report.txt而沒有舊側補償，598e整份清單空，見paired原始輸出 | 資料丟失由R1分類範圍扩展引起；但「原本已保留舊側路徑」不成立。整體舊側補償資格未判定，回歸欄不偷填此項；folded，新增目錄共用既有改名補償 |
| P1 | Semgrep check_id錯型失去JSON | HIT：原始helper反例AttributeError；新增控制由真CLI+fake backend驗structured not_assessed | 原有漏查，未變成clean；folded，先驗型別 |
| L1 | dry-run仍硬寫5檔 | HIT：原始refs scripts/lumos固定文字；改為白名單實際數 | 原有文案未補；folded |
| N1 | 生命周期現況正文只列舊五檔 | HIT：原始正文確少三sidecars，歷史d3清單保留 | 原有文件未補；folded，現況清單去重回單源，不覆寫歷史 |
| N2 | Semgrep自己的家沒寫回 | HIT：R1程式重構有diff，自己的Systems无diff | R1造成的圖譜遺漏；folded，補取捨與驗證關聯 |
| M1 | repair binding缺必要資料/完整差異 | HIT：77改檔只列18；完整SHA f81467bac0b9f1a328ef1a02ca25a78298de9a82eb51655669f84fab9f4c0823 | R1卷證製作缺陷；folded，r2-repair-binding-corrected.json補完整差異、逐檔59個archive_only；原材料保留，不倒寫成派工時已具備 |
| T1 | handbook程序控制放在CLI | HIT：单跑原15控制漏此項；原修正關卡实际经CLI守住，r2-defender.md核對 | 原報告major保留；處置判準minor所有權問題，未證runtime回歸；folded，移入handbook自有控制並接既有test_lumos入口 |
| U1 | UTF16漏DTD拒收 | HIT：純記憶體無害DTD通過；r2-defender.md未見新增偽造權限或已證外部後果 | 原報告major保留；處置判準minor拒收邊界，原有漏查；folded，標準parser宣告事件守住，正常UTF16保留 |

## 材料與因果資格

R2原始binding沒有完整來源欄位，故整體修補因果不能從原兩個相同base欄倒推出；補正保留完整兩端樹碼、固定原R1快照重生byte-equal、fix-check原始JSON（passed且not_run_items空）及祖先rc0。原始18路徑審材没有漏產品碼，但59個歷史卷證與帳本未逐檔聲明，現在完整保留。補正不改变當時資格。R2部分席讀超1800行，照實列限制；R3按個別scope與上下文總量拆席，完整差異可查。

C1、X1有配對與隔離機制證據；R1只確認區間資料丟失，原側補償修前已不成立，不能採用更強說法。原圖譜迴圈／Windows原生／裝置原生重跑均未冒稱驗過。回歸欄因R1的細分因果與資料資格尚未全判定而保持不填，候選C1/X1另有明確配對證據，不把未知洗成none。

## 修前選例與修後驗證

編排者在/tmp九項反例先紅（其中副檔名含四個subtests）；六項隔離最小修補轉綠，才在報告全收後整合。首批42項CLI控制全綠；補UTF16／--vault並移模型控制後44項全綠，另handbook16、scanner21全綠。共享副檔名一致性26個assertion通過。最終提交／fix-check、受波及合約與新輪報告仍须綁定實際版本，這些結果不是最終code-loop PASS。
