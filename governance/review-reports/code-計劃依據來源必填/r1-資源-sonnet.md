severity: minor

三個鏡頭我都跑過。批次 git log 與出處判定沒有會超過預算的問題。擋下留帳沒有去重,但目前量級下只算小成本。

**F1:健檢 S22 的批次 git log,耗時與記憶體可預期**
引句:「        r = subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "log", "--reverse", "-M", "--diff-filter=AR",」
實測:造了 1500 篇計劃、10000 個提交(含約 10% 改名)的 repo,`_plan_first_days_batch` 跑 1.6 秒。`git log` 峰值記憶體約 245MB,Python 端約 40MB。
- 淺複製:`rev-parse --is-shallow-repository` 不是 false 就回 None,沒有退路問題。
- 沒有 git:`OSError` 被接住,回 None。
- 逾時:60 秒會回 None。有 `created` 的舊計劃照樣判舊、被略過;沒有 `created` 的會被當成今天,健檢可能多列幾條提醒。
- 這段只在有 todo/doing 計劃的〈依據來源〉不合格、而且 `created` 早於生效日時才呼叫,而且每次健檢只呼叫一次。
- 吃的資源隨歷史大小線性成長,有上限,不影響健檢可用性。
- file: `scripts/lumos:4794`
severity: minor
blocking: 否

**F2:出處判定本身不碰 git,但新舊判斷逐份計劃花 git**
引句:「    day = _plan_effective_day(rr, _plan_sources_prel(env, rr, rel), n.fields.get("created") if n is not None else None)」
- 一份 50 列、每列約 3 個出處記號的表,`_plan_sources_problems` 實測約 1.9 毫秒。`_validate_repo_ref` 沒帶 `at_sha`,只做 `exists`,不開檔、不叫 git;節點查詢走記憶體裡的索引。
- 新舊判斷才花 git,而且只在表有問題時才跑。每份計劃至少 3 次 git:`rev-parse`、`log --diff-filter=A`、`diff-tree`,有改名最多再追 20 跳。
- 實測在 10000 個提交的 repo 裡,每份計劃約 0.2 秒。推送範圍碰到幾十份「不合格而且是舊計劃」的計劃時約 4 到 8 秒。
- 舊計劃每次推送都要重判,沒有快取,但也有上限。
- file: `scripts/lumos:14343`
severity: minor
blocking: 否

**F3:擋下留帳沒有去重**
引句:「    _gate_event(rr, "spec-gate", "sources-missing", f"{rel}:" + ";".join(probs)[:300], hard=True, nodes=[rel],」
- 每跑一次規格閘或推送前檢查,對同一份沒改過的計劃都會再 append 一筆約 0.7 到 0.9KB 的事件。
- `hard=True` 讓它進入版控的 `docs/.governance-log.jsonl`,不進本機帳。`_GOV_LOCAL_PAIRS` 沒有列 `("spec-gate","sources-missing")`。
- `_gate_event` 的文件寫明「dedup 留給讀時」,寫入端沒有任何去重。
- 推送時 hook 的 `pp_record_block` 還會另記一筆,所以每次被擋實際寫 2 筆。
- 前例 `expected-unsigned` 也是同樣做法。
- 這個 repo 的版控帳已經 21.7MB、124554 行,超過健檢的 `_LEDGER_MB_CAP = 5`。
- 增長量只跟人或 AI 重跑的次數成正比,例如修 10 輪約 7 到 15KB,不是無限長大。
- 因此我只標 minor。若之後出現自動重試或迴圈反覆呼叫規格閘,才會變成 major。
- file: `scripts/lumos:14642`、`scripts/lumos:16804`
severity: minor
blocking: 否

總結:最嚴重是 minor(F3 擋下留帳不去重、版控帳會被重複寫入;F1、F2 皆為可預期的小成本),會擋 0 條
