# r1 收貨紀錄(code-batch3)

- ext(否決席)ext-f3 引句原句「新凍結(從未回放過)必跑+存量輪替抽 5 包」在凍結 patch 內錨不到——那是 docstring 的變體措辭(patch 內原文為「②回放:新凍結(從未回放過)必跑+存量輪替抽 5 包(游標檔記…」含全形括號差異,逐字比對失敗)。
  機械重現:finding 主張=「skipped 的新包仍被記進 seen,下週失去必跑資格」——對 replay_weekly.py 現碼逐行讀:`cur["seen"] = sorted(set(...) | set(new) | set(sample))` 確實無條件併入 new,與 out["replayed"] 無關;主張成立,引句換錨到同段落機械可對的行後採信。
- 帳面 findings_set 的 id 對照:兩個外家席報告內部都用 ext-fN 標號,帳上為免撞名改記 extf-fN(finder 席)與 extv-fN(否決席);內席與 arch 依報告原標號。
- r2 收貨備註:delta 席 d-f13 判明——s3-f5 的本體是「測試覆蓋洞」非「程式邏輯洞」(blob 第二層檢查一直都在,只是沒釘測);r1 折入敘述「兩層都拒凍」易誤讀為改過邏輯,以此條正之。d-f7 指出 replace 的 TOCTOU 為改版前即存在的相鄰殘留,非本輪引入,不入折。
