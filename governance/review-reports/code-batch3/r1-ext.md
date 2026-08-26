### ext-f1
severity: blocker
引句:「--loop/--round/--auditor 齊備,kind 不限——退役 caught/missed 也擋,換 kind 即繞過」
佐證:file: `scripts/lumos:3977`
說明:寫側守衛只在三個欄位同時存在時啟動，省略 `--round` 即可避開報告嚴重度核對；但讀側明確接受無 round 帳列並將每筆合成 `__seqN` 判定輪（`scripts/lumos:10478`），而 severity 尾巴又刻意跳過這種輪（`scripts/lumos:10675`）。攻擊者可讓報告宣告 blocker、帳面只填 minor，再把 finding 放進 accepted；disposal 只看帳面 severity，code-loop 的 major/blocker 必折守衛因此不會觸發，最終可錯誤 PASS。新增測試甚至把「無 --round 照舊 rc0」當成預期，沒有覆蓋它仍是 disposal 可消費形狀這件事。

### ext-f2
severity: major
引句:「完整輸入閉包(全列原文+逐行 sha 集+spec sha+檔案 sha/blob+engine_rev)」
佐證:file: `scripts/lumos:391`
說明:回放直接信任 `verdict.json` 內的 rows、all_row_shas、files、spec_sha 與預期 verdict，沒有核對 golden 自身的 git blob、提交版本或外部簽章。竄改者可同步改寫 rows、雜湊集合、檔案雜湊與 verdict，回放便會拿被竄改的閉包驗證自己並回報一致。現有偵測只抓活帳或卷證檔相對 golden 的變化，抓不到 golden 本體的協調式竄改，破壞「凍結」合約。

### ext-f3
severity: major
引句:「①補漏凍結:帳上已收斂且帶 spec_path、但 governance/replay/ 還沒有 verdict 的」
佐證:file: `governance/autonomous_loop/replay_weekly.py:141`
說明:預算不足時新包會被列入 skipped，但游標仍把全部 new 無條件加入 seen；下週它便不再被視為新包，只能排存量抽樣。若新凍結積壓持續大於每週五包，宣稱必跑的新包可延遲多週。游標應只在實際 replay 成功後標 seen，或保留未跑的新包資格。

結論:否決成立（寫側嚴重度守衛可用省略 round 繞過並導致 disposal 錯誤放行；另有 golden 本體竄改盲區及週跑游標違反必跑合約）。
