severity: minor

審查範圍:r1-snapshot.patch 全部改動,重點是 `scripts/lumos` 的〈依據來源〉檢查、規格閘、推送前重查、健檢 S22,以及 `scripts/hooks/pre-push`。我在臨時環境驗證了出處格的路徑檢查,攻擊面沒有開口。

**逐類結論**
- ①提示注入:已看,無實質洞。
  - 出處格原文(前 200 字)寫進治理帳的 `cells` 欄位,是 JSON 逸出的單行。
  - 這份 diff 裡沒有任何讀取端把 `cells` 印給 AI。
  - 會印給人或 AI 的 `name`、`probs`、doctor 行都先過 `_esc_clean`,控制字元和雙向字元已被換成空格。
  - `_sh_quote(Path(prel).stem)` 這個 shell 引號只用在提示文字上,沒有拿去執行。
- ②讀寫與執行越界:已看,無。
  - `_plan_source_cell_ok` 對反引號內的 token 呼叫 `_validate_repo_ref(Path(rr), tok, None)`。
  - 那支函式先擋空字串、絕對路徑、含 `..` 的路徑,再用 `exists()` 判斷,沒有讀檔內容。
  - 我實跑了 5000 字元檔名、含 NUL 字元、6000 字元深層路徑三種輸入,`exists()` 和 `is_file()` 都回 False,沒有拋例外。
  - 計劃裡的 `[[連結]]` 只查圖譜索引,不碰檔案。
  - `_plan_first_days_batch` 用 argv 陣列呼叫 `git -C ... log`,沒有 shell 插值,路徑參數放在 `--` 之後。
  - `pre-push` 只改了擋下文案和記帳說明,沒有新增執行外部檔案或下載的路徑。
  - 沒有新增密鑰或信箱。
- ③非刻意、一步就能繞過的守衛:找到 F1(minor)。

**F1:生效日環境變數殘留會讓整道〈依據來源〉守衛無聲失效**

這條歸 ③。`LUMOS_PLAN_SOURCES_SINCE` 是使用者或 AI 先前為了測試或緊急覆寫而 export 的變數。
- 攻擊路徑:
  - 誰:使用者本人或照常操作的 AI。
  - 從哪裡:同一個 shell 先前用過測試開關,例如 `export LUMOS_PLAN_SOURCES_SINCE=9999-12-31`,之後沒有 unset。
  - 送什麼:之後照常 `git push` 一份沒有〈依據來源〉的新計劃;或照常跑 `lumos spec-gate`、`lumos doctor`。
  - 拿到什麼:`_plan_sources_is_new` 把新計劃判成舊計劃。
- 後果:規格閘只印「舊計劃不擋」,推送前閘直接放行,doctor S22 也不列。
- 缺口:全程沒有任何提示說「生效日被環境覆寫了」,也不寫帳。
- 先例:`_expected_since` 的 `LUMOS_HIGH_RISK_EVIDENCE_SINCE` 是同一寫法,所以風格上一致。
- 影響:只讓一道規範性的品質守衛失效,沒有執行任意碼或外洩,所以只到 minor。
- 建議:變數生效時往 stderr 印一行「生效日被環境變數覆寫為 X」,或寫一筆帳。

severity: minor
blocking: 否

引句:「v = os.environ.get("LUMOS_PLAN_SOURCES_SINCE", "").strip()」

file: `/Users/enzo/orca/workspaces/lumos-toolchain/plan-sources-required/scripts/lumos:14521`

**另提一句(標 minor、不擋)**
- 刻意偽造算範圍外:手改計劃的 `created` 為舊日期,或在淺複製裡讓首次加入日讀不到,可以讓新計劃被判成舊計劃。
- 這些都是刻意多步偽造,系統天花板不加機制,只在這裡備註。

總結:最嚴重是 F1(環境變數殘留讓〈依據來源〉守衛無聲失效,縱深防禦類 minor),會擋 0 條。
