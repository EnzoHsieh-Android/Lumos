severity: major

我在 `--shared` 臨時 clone 上,把怪輸入餵給 `_plan_source_cell_ok`、`_plan_sources_problems`、`_plan_first_days` 和 `cmd_spec_gate`,臨時目錄已刪。

### 第一輪 F1–F4 修好了沒

- **F1 路徑只看工作目錄:已修。**
  - `Scripts/lumos`、`.git/HEAD`、`scripts`、`scripts/`、`scripts//lumos`、`:行號` 超界、`:3-1`、絕對路徑、`..`,都回 False。
  - 只 `git add` 還沒提交的檔、只在工作目錄的檔,都回 False。
  - `git rm --cached` 的檔回 True,因為 HEAD 還有,符合「對 HEAD 判」的設計。
  - 子模組回 False。
  - 符號連結指向 repo 外、絕對路徑,都回 False。
  - 新漏洞見 F1。
- **F2 HTML 註解裡的表:已修。**
  - 整節包在註解裡、註解沒閉合、註解在圍欄裡、註解在行內程式碼裡、整行在註解裡、CRLF,結果都對。
  - 小例外:`<!-->` 與 `<!--->` 會被當成沒閉合的註解,整份後面都被蓋掉。這種寫法幾乎沒人用,不標。
- **F3 批次與單篇日期分岔:已修。**
  - 改名跟得過去,從 `Systems/` 搬進 `Projects/` 也一致。
  - 目錄整包改名、純改大小寫的改名、複製不跟、刪了重加,批次與單篇結果都一樣。
  - 檔名含 `"` 時 git 會加引號而對不上,太罕見,不標。
- **F4 開頭欄位壞掉靜默略過:只修一半。** 見 F3。

example.com 的變體也都對:`EXAMPLE.COM`、`sub.example.org`、帶埠號、結尾點、`user@example.com` 都擋;`example.com.evil.net`、`notexample.com`、`example.co`、`example.com@evil.net`、IDN 都放行。今天和閏日放行,明天和 2026-02-29 擋。

### F1 指向 repo 內目錄的符號連結:合法寫法被擋,目錄反被放行
severity: major
blocking: 是
引句:「    if len(meta) != 3 or meta[1] != "blob" or path.endswith("/") or nfc(name) != nfc(_pp.normpath(path)):」

| 輸入 | 實際 | 預期 |
|---|---|---|
| repo 內 `alias -> scripts`(目錄符號連結),出處寫 `` `alias/lumos` `` | False,被擋 | 放行:讀者 clone 後查得到,舊版看工作目錄也放行 |
| 同上,出處寫 `` `alias` `` | True,放行 | 擋,因為指向目錄,設計明寫「目錄不算」 |
| 符號連結指向不存在的檔,或指向 `../.git/config` | True | 擋,讀者查不到 |

- 原因:`git ls-tree` 不會穿過符號連結的目錄,所以路徑中段有符號連結就查不到。
- 原因:`120000` 那一支只檢查目標有沒有跑出 repo,沒檢查目標在 repo 裡是不是檔案、有沒有進版控。
- 會遇到這種寫法的專案:有 `.agents/skills -> ../.claude/skills` 這類做法的消費專案。本 repo 目前沒有符號連結,所以自己的測試碰不到。

### F2 出處是剛 `git add` 或剛建、還沒提交的檔:擋下訊息沒講原因
severity: minor
blocking: 否
引句:「        if _validate_repo_ref(Path(rr), path, line, at_sha="HEAD")[0] != "ok":」

- 輸入:`git add staged.py` 之後,出處寫 `` `staged.py` ``,跑 `lumos spec-gate`。
- 實際:擋,訊息只講「出處欄沒有讀者查得到的出處(…repo 內存在的檔…)」。
- 預期:檔明明在工作目錄,作者會困惑。訊息應提醒「路徑要對 HEAD 判,先提交」。判法本身(對 HEAD)是對的,只有訊息不清楚。

### F3 F4 只修了規格閘;型別寫錯和推送前重查仍然靜默
severity: minor
blocking: 否
引句:「            print("[spec-gate] 依據來源: 開頭欄位讀不到 type(開頭 --- 沒收尾或沒寫 type: project),這次不查")   # 代碼審 r1 邊界席 F4」

- 輸入:`type: Project`、`type: plan`、`type: PROJECT` 的新計劃,出處寫「一般知識」。
- 實際:
  - 規格閘一行都不印,整節不查。
  - 提示只在 type 為空時才印。
  - `_spec_gate_push_sources` 與健檢遇到壞 frontmatter 的計劃仍然靜默略過。
- 預期:type 有值但不是 `project` 時,也該印「不查」。
- 本 repo 目前 345 篇 `_計劃.md` 全是 `type: project`,現況沒人觸發。

### F4 每個反引號路徑多跑 2 到 3 個 git 程序,健檢整批算時會變慢
severity: minor
blocking: 否
引句:「        r = subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "ls-tree", "-z", "--full-tree", "HEAD", "--", path],」

- 實測:本 repo 每個路徑約 52 ms,帶 `:行號` 約 103 ms;舊版只做一次檔案系統檢查。
- 重現場景:健檢 S22 對每個 todo 或 doing 的計劃都先算整張表,新舊判斷在後面。依據來源節以後普及,100 篇計劃各 20 個反引號路徑約 100 秒。
- 預期:推送前與 CI 的健檢維持在秒級(`pre-push` 檔頭註解寫 doctor 約 1.1 秒)。
- 補充:`_plan_sources_uncomment` 對單行極端輸入是二次方。35KB 單行放 5000 個行內程式碼加 `<!--` 要 0.5 秒,實際計劃不會有,只記一筆。

總結:最嚴重是出處路徑遇到 repo 內的目錄符號連結會誤擋合法寫法、又放過指向目錄的符號連結,會擋 1 條(F1);其餘 3 條為 minor。
