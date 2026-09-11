severity: minor

已逐類檢視:1(注入類)/2(登入權限)/3(密鑰與個資)/4(加密與傳輸)/6(行動端執行期)已看,無新發現;5(執行邊界)為本輪主要發現,見 F1、F2(對應派工詞特別點名的「靠資料夾命名讓程式檔逃過要有家的要求」);新增依賴:無。

### F1 新加的「同名資料夾」錨只驗頂層字面是否存在,不驗它是不是真的程式目標,repo 既有頂層資料夾即可免費滿足
severity: minor
blocking: 否 — 只影響知識圖譜文件化/治理留痕義務的涵蓋範圍,不觸發程式執行、不外洩資料、不繞過登入權限,屬縱深防禦類治理控制放寬,不到 major 門檻
攻擊路徑:誰——有提交權限的內部人或被合併進來的外部 PR;從哪裡——本 repo 既有的任一頂層資料夾(`scripts/`、`docs/`、`governance/`、`configs/` 都已存在,見 `git ls-files | cut -d/ -f1 | sort -u`);送什麼——新增 `scriptsTests/inject.cs`、`configsTests/x.swift` 這種「既有頂層名 + Tests 字尾」的資料夾;拿到什麼——`base in top_dirs` 只驗頂層是否存在同名資料夾字面、不驗它是不是真的 App/測試目標對應的程式目錄,檔案照樣判為測試檔,永久跳過「每支檔有家」的提交前/推送前強制擋。這個 repo 自己的頂層資料夾就能免費滿足新錨,多數真實 repo 幾乎不會被「同名資料夾」這道新門檻擋下,新錨的實質提高有限。
引句:「if base and ext in exts and base in top_dirs:」
佐證 file: `scripts/lumos:17819`(companion-dir 檢查只比對字面存在);`scripts/lumos:18009`(`top_dirs` 直接取 repo 現有全部頂層資料夾名,不篩選)

### F2 src/androidTest 測試資料夾分支完全沒補新錨,任何語言的程式檔照舊能靠資料夾名稱跳過要有家
severity: minor
blocking: 否 — 同 F1,屬治理文件化義務的縱深防禦類放寬,不觸發執行/外洩/繞過登入
攻擊路徑:誰——同 F1;從哪裡——repo 任何位置的 `.../src/.../androidTest/` 或 `.../src/.../test/`(Gradle 保留名,不看副檔名);送什麼——放進任何語言的程式檔,例如 `tools/src/androidTest/backdoor.py`、`x/src/test/evil.sh`;拿到什麼——`under_src` 這條判準完全沒被這輪 delta 動到,沒有比照頂層那條加上副檔名/棧別驗證,一樣跳過「每支檔有家」。r1 資安 F1 原句「兩條判定都不驗副檔名或語言」點名的是兩個分支,這輪只修了頂層字尾那條,r1-intake.md 把 C1 判「折」的說法對這條分支不成立——是修正沒補完整,不是新發現舊帳。
引句:「return any(seg in under_src and "src" in parts[:i] for i, seg in enumerate(parts[:-1]))」
佐證 file: `scripts/lumos:17821`(`under_src` 分支邏輯與 r1 版本逐字相同,delta 未觸碰)

總結:最高 severity minor,blocking 共 0 條
