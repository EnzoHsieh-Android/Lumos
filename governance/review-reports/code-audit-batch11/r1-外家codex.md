severity: major

1. severity: major；blocking:是 — Windows 一鍵安裝仍寫死 `python`。`lumos.cmd` 雖改成偵測 `python3`／`python`，但 `get.ps1` 隨後直接呼叫 `python`；只有 `python3.exe` 的環境會在 bootstrap 前失敗，正是 shim 修改聲稱要支援的環境。引句:「`python "$homeDir\scripts\lumos" bootstrap @pass`」 get.ps1:50

2. severity: major；blocking:是 — 發布通道守衛只數字串，無法驗證 clone 或委派行為。我實際以兩個錯誤版本重跑其精確判準：

   - 把 get.sh 的 release clone 改成永遠不執行，但把 `git clone --branch` 留在註解。
   - 把 get.ps1 改回 `install --force`，僅在註解保留 `bootstrap`。

   兩個錯誤版本的五項 predicate 仍全部為 `True`。因此它抓不到錯誤分支、死碼、註解或實際委派退化。引句:「`check("三個 clone 站都先試對外分支",`」 scripts/test_lumos.py:5322；引句:「`check("get.sh 有退回預設分支的備援", sh.count("git clone") >= 2`」 scripts/test_lumos.py:5326；引句:「`check("get.ps1 也委派 bootstrap(兩支行為一致)", "bootstrap" in ps`」 scripts/test_lumos.py:5337

3. severity: major；blocking:是 — `--version` 對 vendored 副本仍把宿主專案的 Git SHA 稱為「這一份的內容指紋」。程式以 `git -C <宿主專案>` 查 SHA；複製到別的 Git 專案後得到的是該專案 commit，不是 lumos 內容。雖上一行附有警告，這個 SHA 仍不能識別目前執行的 lumos，與 CHANGELOG／RELEASING 宣稱的內容指紋用途不符。現有測試只找「只回答現在跑的這一支」文字，沒有驗證指紋來源。引句:「`這一份的內容指紋: %s 在分支 %s %s`」 scripts/lumos:106

4. severity: minor；blocking:否 — RELEASING 對 detached HEAD 的現行行為描述已過期。現在 `_pull_source_or_abort` 對有 remote 且 `git pull --ff-only` 失敗會 fail-closed，`lumos update` 不會「靜默停住」，而會中止。這會讓維護者依錯誤故障模型判斷 tag 安裝。引句:「`之後 git pull 與 lumos update 會靜默停在裝機那一版`」 RELEASING.md:51

補充查證：

- `t_lens_timeout_keeps_warming_cache` 仍能抓到「逾時後砍背景行程」：背景行程若被殺，60 秒內不會產生 cache，測試會紅；刪掉斷言文字中的「沒被殺掉」沒有削弱 oracle。
- get.sh 除 `set -euo pipefail` 外，具副作用的主體都在 `main()`；沒有確認到包裝遺漏。
- 執行環境禁止建立任何暫存檔／目錄，`mktemp` 直接回 `Operation not permitted`，因此無法實跑 file:// 假 repo 的 clone；未把這部分的靜態疑點列為 finding。
