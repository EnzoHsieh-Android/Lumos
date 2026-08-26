# r1 收貨紀錄(code-batch3)

- ext(否決席)ext-f3 引句原句「新凍結(從未回放過)必跑+存量輪替抽 5 包」在凍結 patch 內錨不到——那是 docstring 的變體措辭(patch 內原文為「②回放:新凍結(從未回放過)必跑+存量輪替抽 5 包(游標檔記…」含全形括號差異,逐字比對失敗)。
  機械重現:finding 主張=「skipped 的新包仍被記進 seen,下週失去必跑資格」——對 replay_weekly.py 現碼逐行讀:`cur["seen"] = sorted(set(...) | set(new) | set(sample))` 確實無條件併入 new,與 out["replayed"] 無關;主張成立,引句換錨到同段落機械可對的行後採信。
