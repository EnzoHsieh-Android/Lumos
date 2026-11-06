severity: minor

三問各自判完。結構面對齊得好：佔位符替換和辨認都還是一處，沒有第二支替換函式或第二套放行機制。不一致的地方在錯誤回傳形狀和一處訊息格式，沒有「第二種做法」，也沒有跨層直呼。ci.yml 下載 detekt 這一步是否算第二種工具安裝法，我判不準，標 ⚠ 交編排者。

## F1 開程序失敗用輸出參數 `fail_info` 回報，鄰居都是回傳值
severity: minor
blocking: 否
引句:「fail_info: 選配的 dict。開程序時系統回「參數太長」(E2BIG)就在這裡寫 too_long=True 再回沒跑」
file: `scripts/lumos:40557`（`_lint_new_run_cmds` 的 `out["undone"].append({"kind": "budget"|"env"|"guard", ...})`）；另見 `scripts/lumos:39572`（`_lint_run_and_parse` 回 `(claims, ok)`）
- 既有怎麼寫：`_lint_run_and_parse` 的失敗一律用回傳值表達，回 `(claims, ok)`。失敗原因的分類由 `_lint_new_run_cmds` 在呼叫端看結果後寫進 `out["undone"]`，用 `kind` 區分 `budget`、`env`、`guard`。`_lint_run_and_parse` 沒有參數是拿來帶回狀態的。
- 這次怎麼寫：多收一個會被函式改寫的 `fail_info` dict（輸出參數）。`_lint_new_run_one` 的回傳也從 `got|None` 改成 `(got, fail)` 二元組，失敗種類用字串 `"env"`、`"too-long"` 回傳，最後才轉成 `undone` 的 `kind`。
- 為什麼算不一致：同一條呼叫鏈上，失敗種類同時有「回傳值」和「寫進傳入的 dict」兩種送法。結構仍在同一層，錯誤分類最後也進了同一份 `undone`，所以只算 minor。

## F2 分隔字元路徑借用 `oversize` 清單，放行指紋就地重算，擋下訊息的放行提示跟大檔不同
severity: minor
blocking: 否
引句:「key = _hl.sha256(("separator-path" + _LINT_NEW_SEP + f).encode("utf-8")).hexdigest()[:16]」
file: `scripts/lumos:40259`（`_lint_new_oversize` 的 `("oversize" + _LINT_NEW_SEP + f)` 與擋下訊息「要讓它一直算過就登記:{key}」）
- 既有怎麼寫：大檔指紋在 `_lint_new_oversize` 裡算。擋下訊息印「要讓它一直算過就登記:key」，尾端另有通用的 `lumos lint-waive <指紋>` 提示（`scripts/lumos:72462`）。
- 這次怎麼寫：
  - 在 `_lint_new_sep_split` 裡內嵌同一組 sha256 公式，只換前綴字串。
  - 條目塞進同一份 `oversize` 清單，靠 `kind == "separator"` 在 `_lint_new_block_bits`、`_cl_say_lint_block`（兩處）、`_cl_say_lint_ok` 共四處分流。
  - 擋下訊息對這類條目改印完整的 `_lint_waive_cmd(_o)`，大檔仍印「登記:key」。
- 為什麼算不一致：
  - 這沒有另立放行機制，同一份清單和同一種指紋形狀，所以不算第二種做法。
  - 指紋公式有兩份複本。
  - 同一個擋下區塊裡，兩類條目的放行提示寫法不同。
  - 條目缺 `lines`、`bytes` 欄位，靠每個消費點記得過濾 kind，漏過濾就是 KeyError。

## F3 ⚠ CI 首次引入「下載發布檔並比對 sha256」，專案裡另有一個沒驗雜湊的下載腳本，這步沒接
severity: minor
blocking: 否
引句:「★CI 第一個非 pip 的工具下載,以後別的工具照這步抄★」
file: `.github/workflows/ci.yml:143`（ast-grep 用 `python -m pip install --quiet ast-grep-cli==0.51.1`）；`scripts/fetch-notesmd.sh:40`（`curl -fsSL "$URL" | tar xz`）
- 既有怎麼寫：CI 裝工具只有 pip 釘版本一種，如 ast-grep。專案裡下載外部二進位的既有做法是 `scripts/fetch-notesmd.sh`，用 `curl | tar` 且不驗雜湊。
- 這次怎麼寫：在 ci.yml 內嵌 curl、`sha256sum -c`、`unzip`、`$GITHUB_PATH`。註解自己聲明這是新慣例。
- 為什麼標 ⚠：detekt 不在 PyPI，pip 路線走不通，比對雜湊比 `fetch-notesmd.sh` 嚴。但這確實是 CI 裡的第二種裝工具法，也沒有重用既有的 fetch 腳本。是否算 major 要由編排者按「第二種做法」錨裁定。我只確認它不是不自知地另起一套，註解、釘版本、升版步驟都寫明了。

## 三問

1. **分層與依賴方向：對齊。**
   - `_lint_cmd_with_files` 仍是唯一替換處，在一次掃描裡換完兩種佔位符（`scripts/lumos:39795-39797`）。
   - 辨認全走 `_lint_gate_covers`，呼叫端都是原本的鄰居：`_lint_run_and_parse` 入口、冒煙 `_lintcheck_smoke_cmd`、規則索引 `cmd_rule_check`。
   - `_lint_spawn` 是從 `_lint_run_and_parse` 抽出的子步驟，由後者呼叫，開程序與殺程序群組仍用 `_kill_proc_group`（`scripts/lumos:26638`），沒有跨層直呼。
   - `_detekt_gradle_task_kind` 由 `_detekt_gradle_codes` 和 T4 的 `_detekt_ci_has_typed_task` 共用，位置在 detekt 判定那一帶。
   - `_lint_new_sep_split` 接在 `_lint_new_tools` 的 `oversize` 處理之後，位置和呼叫方向都跟 `_lint_new_oversize` 一致。

2. **命名與錯誤處理：大致對齊，不一致處見 F1、F2。**
   - 命名都沿用 `_lint_*`、`_detekt_*` 前綴。
   - 新增的 `kind: "too-long"` 放進 `undone` 後，和 `budget` 一起落在 `hard_undone`，擋下訊息的處理沿用既有分支（`scripts/lumos:40290-40302`）。
   - 新增的 lint-waivers 條目欄位和上一筆 C901 一致（`origin: ai`、`acked: false`）。
   - 擋下訊息的三段式（發生什麼、為何在意、指令）沒變。

3. **第二種做法：沒有新的放行指紋機制或替換函式；有一處 CI 安裝法待編排者判（F3）。**
   - 圖譜筆記沿用既有 `WHY:`、`REVISIT:YYYY-MM-DD` 等格式，也依「每支檔有家」寫進各檔的家。
   - 大檔放行機制被沿用，只是指紋公式內嵌了一份（F2）。
   - 開子程序仍是 `shell=True`、`start_new_session=True`，逾時用 `_kill_proc_group`，和 `_kill_run`（`scripts/lumos:26665`）一致。
   - 棧別檢核題：派工單沒附表態記錄，這次不用查 tension 題。

不對齊共 3 條，其中 major 0 條
