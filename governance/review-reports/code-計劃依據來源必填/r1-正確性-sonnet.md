severity: minor

審完整份 patch,並在臨時 repo 實跑。五種出處的判法與推送前挑計劃都沒找到會誤擋或漏擋的 major,找到 4 條 minor。實跑過的情境如下:
- 改名、刪除、改名加刪除的推送挑選,行為正確。
- 非 UTF-8 的舊計劃不會被這一圈誤擋。
- 2 萬列的表約 1 秒,超長引號輸入沒有崩潰也沒有爆時間。
- 全形冒號、無冒號、空引號、`..`、絕對路徑、目錄、不存在的節點、不存在的路徑,都擋得對。

F1 批次首次加入日跟單篇 `_plan_effective_day` 在「從 Projects 以外搬進來」時不一致
引句:「first.setdefault(parts[2], first.get(parts[1], day))」
severity: minor
blocking: 否
- 輸入:臨時 repo 裡 `Systems/a_計劃.md` 在 2026-01-01 加入,2026-09-01 `git mv` 到 `Projects/a_計劃.md`。生效日設 2026-06-01。
- 實際:`_plan_first_days_batch` 回 `2026-09-01`,`_plan_effective_day` 回 `2026-01-01`。
- 原因:批次 `git log` 的路徑限定在 `<圖譜>/Projects`,改名來源在路徑限定之外,git 會把它印成 A 而不是 R,舊日期接不上。
- 預期:兩邊都是 `2026-01-01`,判舊。
- 後果:整個圖譜目錄改名(例如 `docs/a-knowledge` 改 `docs/b-knowledge`)發生在生效日之後時,健檢 S22 會把所有 todo/doing 的舊計劃判成新計劃全列出來。推送前那圈用單篇判法,不受影響。
- 計劃筆記只講「改名在同一個目錄裡」,這個缺口沒寫進天花板。

F2 `_plan_source_cell_ok` 放過的假出處:範例列本身、未來日期
引句:「_PLAN_SOURCES_EXAMPLE = "| 擋下要留帳 | 誤報率要持續量才知道該不該撤 | https://example.com/paper.pdf |"」
severity: minor
blocking: 否
- 輸入:把擋下訊息每次都印出的範例列,原封不動貼回計劃。
- 實際:`_plan_source_cell_ok` 回 True,閘放行。另外「使用者 2099-12-31:「這樣做比較穩」」也回 True,因為日期只用下面這行驗是否為真實日期:
  引句:「_dt.date.fromisoformat(s)」
- 預期:至少擋掉自己印的範例。`example.com` 是保留網域,可以寫死拒絕。未來日期也不該算有效日期。
- 後果:作者(尤其是 AI)照訊息抄範例就能過閘,正好是這道閘要擋的「亂貼一個格式對的出處」。
- 測試用 `https://example.com/a` 當放行案例,這個缺口抓不到。

F3 反引號路徑與節點連結的存在判斷偏鬆,跟函式註解的說法不符
引句:「if _validate_repo_ref(Path(rr), tok, None)[0] == "ok" and (Path(rr) / tok).is_file():」
severity: minor
blocking: 否
- 實跑結果(輸入→實際):
  - 反引號路徑是指向 repo 外的符號連結 `scripts/link.txt`(指向 `/etc/hosts`):放行。
  - `` `.git/HEAD` ``:放行。
  - 被 gitignore 或未追蹤的檔:放行(判斷讀工作目錄,不是 git 樹)。
  - 在 macOS 上 `` `SCRIPTS/A.PY` ``:放行,在 Linux 上會是不存在。
  - 行號被先剝掉再傳 `None` 給 `_validate_repo_ref`,所以 `` `scripts/a.py:999` ``、`` `README.md:5-2` `` 都放行。註解卻寫「去掉尾端 :行號,交給 _validate_repo_ref 判」,實際行號完全沒被判。
  - `[[Foo/規格閘]]`:放行,因為 `env.resolve` 在帶斜線的完整路徑找不到時,會退回只比檔名。
- 預期:出處是讀者查得到的版控內檔案,行號超出範圍要擋,目錄錯的連結要擋。
- file: `scripts/lumos:37635`(`_validate_repo_ref`)
- file: `scripts/lumos:944`(`resolve` 的退回邏輯)

F4 推送前每份被改到的計劃各跑一次 git,寬範圍會慢
引句:「if not probs or not _plan_sources_is_new(env, rr, prel):」
severity: minor
blocking: 否
- 輸入:實跑 `_spec_gate_push_sources`,範圍是本 repo 全部 408 份 Projects 檔(模擬新分支首推從空樹掃),生效日設預設 2026-11-08。
- 實際:耗時 33.9 秒,無擋下。
- 原因:生效日之後,舊計劃幾乎都缺〈依據來源〉節,所以每份都會走 `_plan_effective_day` 的逐篇 `git log` 加 `diff-tree`。
- 預期:跟健檢一樣用批次。健檢那邊已用 `_plan_first_days_batch`,計劃筆記也說逐篇呼叫要多 20 到 60 秒。
- 影響範圍:只有範圍很寬的推送會碰到。

總結:最嚴重是 minor(出處判定偏鬆、批次與單篇日期在搬目錄時分岔、寬範圍推送變慢),會擋 0 條。

臨時目錄 `/tmp/lumos-seat-work/code-計劃依據來源必填/正確性-sonnet` 已刪除,沒有改動 repo。
