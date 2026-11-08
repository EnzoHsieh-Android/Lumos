severity: clean

**1. 分層與依賴方向:對齊**
- ci.yml 的改動只動 prep 與 shards 兩個工作裡既有的兩個下載步驟,沒有新增步驟、沒有搬動順序。這跟 `.github/workflows/ci.yml` 原本「每個工作各自抄、除了 if 逐字相同」的做法一致(diff 第 6 行註解與 `scripts/test_lumos.py:88713` 的 `t_ci_yml_test_tools_in_sync` 說明)。
- 新測試讀 ci.yml 的方式是 `_ci_job_steps(ci)`,跟 `t_ci_yml_test_tools_in_sync` 同一支切法和同一個 `_need_src(".github/workflows/ci.yml")` 前置。file: `scripts/test_lumos.py:88695`
- 問題清單的 helper `_ci_release_download_problems` 放在測試前面,回傳問題清單、空表示全過。這跟 `_ci_test_tools_problems_check` 的「測試呼叫 helper」結構一致。
- 筆記改在 `Systems/bound-tests-gate`,該節點的 `about_code` 本來就列了 `.github/workflows/ci.yml`。file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:141`
- 沒有跨層直呼。

**2. 命名與錯誤處理:對齊**
- 命名:新 helper `_ci_release_download_problems` 與測試 `t_ci_yml_release_downloads_authenticated` 都沿用 `_ci_*` 與 `t_ci_yml_*` 前綴。
- 測試輸出:`check("★前置★ …")`、`check("★改壞★ …")` 的寫法和翻紅釘說明,跟同檔 `t_ci_yml_test_tools_in_sync` 的文件字串結構一致。
- Shell 失敗處理:兩個步驟都保留 `set -eu`,sha256 校驗照舊。重試迴圈用 `&amp;&amp; break`、末次 `exit 1`,沒有吞掉最終失敗。
- 日誌:沿用步驟前一行中文註解寫事故來源與日期的慣例,跟 ci.yml 其他註解一致(例如分片那步的註解 file: `.github/workflows/ci.yml:157`)。
- 筆記 PITFALL 行有 `[出處:][根因:][修法:][test:]`,跟同檔第 134 行(file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:134`)的寫法一致。

**3. 第二種做法:未發現**
- ci.yml 與其他 workflow 原本沒有重試迴圈,也沒有用 token 的步驟,只有舊的 `curl --retry 3`。這次是原地取代,沒有並存兩套。
- `scripts/fetch-notesmd.sh:40` 用 `curl -fsSL` 抓發布檔,跟新寫法不同。它是使用者機器上的安裝腳本,不在 CI、手上沒有 `github.token`,屬不同情境,所以我不判為第二種做法。
- ⚠ 交編排者:若團隊想要「全專案抓發布檔一律帶身分」,這支腳本日後可能被點名。目前不構成本 diff 的不一致。

不對齊共 0 條,其中 major 0 條

建過的路徑:無(沒有在 /tmp/lumos-seat-work/code-ci帶身分下載發布檔/架構對齊-sonnet/ 下建任何東西)。
