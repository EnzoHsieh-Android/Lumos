severity: major

## F1 新建的 `_range_base()` 修了三點範圍的 bug,但同一支檔裡功能相同、走同一條 pre-push 流程的 `_sc_diffusion`/`_sc_churn` 還在用會踩同一個 bug 的舊算法,沒有被收斂成一份

severity: major
blocking: yes

觀察到什麼:這批新增 `_range_base(rr, diff_range)`(`scripts/lumos:22303`),把「a..b 用 a、a...b 用 merge-base(a,b)」的算法收斂成一份,並在自己的函式註解裡明白指出理由:

引句:「三點範圍拿左端點當起點,刪掉的檔會從錯的版本讀」

但同一支檔案裡,`_sc_diffusion`/`_sc_churn`(`scripts/lumos:5695`、`scripts/lumos:5713`,被 `_small_change_check` 呼叫、`scripts/lumos:5764` 與 `5776`)算 base 用的還是沒改的舊寫法:

引句:「base = git_range.split("..")[0] if ".." in git_range else None」

這行在 r2-snapshot.patch 裡沒被碰,還是舊碼(patch 只加了 `_range_base` 那份新的,沒有把 5716/5776 改成呼叫它)。`_sc_diffusion`/`_sc_churn` 算出的 `base` 一樣是餵給 `_is_code_file(rr, f, base)`——跟 `_pitfall_tier`/`_test_suite_for_range` 判斷「這支檔算不算程式檔」用的是同一個判準函式,只是走的是「風險低計劃小改動閘(spec-gate --push-check)」這條路,而不是「suite docs/light」那條路。兩條路在同一次 `pre-push` 逐 ref 迴圈裡對同一個 `_range` 分別跑(`scripts/hooks/pre-push:216` 先跑 pitfalls 算 `_suite_this`,再於 `pre-push:238` 跑 `spec-gate --push-check "$_range"` 算 light)。

怎麼重現:`git.split("..")` 對三點範圍其實不是「回 None」而是巧合地回左端點——`"A...B".split("..")` 在 Python 裡是 `["A", ".B"]`,取 `[0]` 得到字面 `"A"`,跟直接拿 `A` 當起點一樣錯(不是 merge-base(A,B))。若有人(或未來的自動化)對 `lumos spec-gate --push-check "main...feature" --repo .` 這種三點範圍呼叫(CLI 對 `--push-check` 的 `RANGE` 沒有限制只能兩點,`scripts/lumos:29416` 的 `metavar="RANGE"` 沒有格式檢查),而 `feature` 分支裡剛好把某支「起點是 #! 程式檔、終點被改成純文字或被刪」的檔納入改動範圍,`_sc_diffusion`/`_sc_churn` 會拿 `main`(而不是 merge-base)去判斷該檔是不是程式檔,得到跟這批自己新加的測試 ⑪b(`scripts/lumos` 對應的 `t_test_suite_docs_only_judgement`)明確要防的同一種錯誤結論——只是這次錯的是 spec-gate 的「light」小改動閘,而不是 suite 選擇。

為什麼是 bug 而不是風格:這正是派工詞點名要查的問題——「`_range_base` 跟既有 21723 行那處 `diff_range.split("..")[0]` 是不是又一份」。21723 行(`cmd_cochange_check` 的歷史挖掘起點)語意不同(挖歷史母體用「到哪個提交為止」,不是判斷檔案版本),不算真正的重複;但 5716/5776 兩處語意、消費者(`_is_code_file`)、呼叫時機(同一次 pre-push 迴圈)都跟 `_range_base` 要解決的問題完全一樣,而且這批的作者自己已經證明「三點範圍拿左端點=错」值得寫測試、寫函式去修——卻沒有把新函式套進兩個本來就有相同缺陷的既有函式,等於同一個 bug 類別在同一支檔案裡「修一半」。這正是審查焦點裡「自己再刻一份已有的工具函式」/沒有把新建算法收斂成單一版本的具體例子,不是風格偏好。

file: `scripts/lumos:5695`(_sc_diffusion)
file: `scripts/lumos:5713`(_sc_churn,base 算法舊寫法在這行)
file: `scripts/lumos:5764`(_small_change_check,呼叫上面兩支)
file: `scripts/lumos:5867`(_spec_gate_push_check,git_range 直接來自 CLI,無兩點/三點限制)
file: `scripts/lumos:22303`(新的 _range_base,本該被上面兩處改叫用)

## F2 新的 `_run_group` 是這支掛鉤裡唯一一個帶底線前綴的函式名,跟同檔既有函式(impact_once / impact_done / bound_tests_advisory)與其他掛鉤(pre-commit / post-commit 的 is_shebang_code / should_exclude)的命名慣例相反

severity: minor
blocking: no

觀察到什麼:這批在 pre-push 裡新增了一個 bash 函式:

引句:「每片一個子行程,回傳 0=全綠、3=每片都選中 0 支、1=有紅」

那一行的完整定義是 `_run_group() { ... }`。用 `grep -n "^[a-zA-Z_][a-zA-Z0-9_]*() *{"` 對 `scripts/hooks/pre-push`、`pre-commit`、`post-commit` 三支掛鉤全部函式定義掃過一輪,既有函式一律不帶底線前綴:`impact_once`、`impact_done`、`bound_tests_advisory`(pre-push 本檔)、`is_shebang_code`、`should_exclude`(pre-commit / post-commit 兩支各自都有)。而這幾支掛鉤裡所有**變數**倒是一律帶底線前綴(`_IMPACT_JSON`、`_PP_TMP`、`_range`……)。`_run_group` 是這三支掛鉤裡唯一一個底線開頭的函式名,把「底線=變數、無底線=函式」這條沒寫下來但全檔一致的區分打破了。

怎麼重現:`grep -n "^_\?[a-zA-Z][a-zA-Z0-9_]*() *{" scripts/hooks/pre-push scripts/hooks/pre-commit scripts/hooks/post-commit`,五個既有函式全無底線,只有 `_run_group` 有。

為什麼不是 blocker:單純命名,不影響行為(bash 對函式名前綴底線沒有特殊語意),派工詞明講「風格不列」——這條算不算數把握不大,所以歸 minor 附上而非直接略過:它符合派工詞明講要查的「命名」比對點,而且是可驗證、非「泛泛而談」的具體不一致,留給收貨判要不要折。

file: `scripts/hooks/pre-push:404`(_run_group 定義)
file: `scripts/hooks/pre-push:43`(impact_once,對照組)
file: `scripts/hooks/pre-commit:132`(is_shebang_code,對照組)

## 其他六個對照點:查過,判定對齊,不成立為發現

- `trap 'impact_done' EXIT INT TERM` 改寫成帶 `rm -rf` 的形狀:同檔其他暫存檔(`_AUTOLOOP_LOG`、`_TESTS_LOG`,`scripts/hooks/pre-push:323-324`)在這批之前就沒被任何 `rm` 清過,這批也沒改動它們——它們是刻意留給人推送後讀的輸出檔(訊息裡直接印出路徑要人去看),不是洩漏的暫存檔;新加的 `_PP_TMP`/`rm -rf "$_PP_TMP"` 只收「本來就該清、之前逐檔 rm 會在 exit 1/訊號路徑漏清」的那幾個(`_sg_out`、shard 分片 log),跟既有「人要讀的留檔不清」慣例一致,沒有矛盾。
- `_run_group` 在本 hook 有沒有先例:除了 F2 講的命名之外,把邏輯包成函式、就地定義在會用到它的 `if` 區塊裡(而非像 `impact_once` 那樣頂層定義)在 bash 裡沒有語意風險(每次進 if 區塊都重新定義一次,單次執行不影響);沒發現功能性問題。
- `PIPESTATUS`/`tee` 在其他掛鉤/CI 沒有先例(`grep -rn "PIPESTATUS\|tee "` 只在這批新增的兩行命中),但本檔只 `set -u`、沒設 `pipefail`,手動取 `PIPESTATUS[0]` 是正確且必要的寫法(不能靠 `set -o pipefail` 因為沒開),shebang 確認是 `#!/usr/bin/env bash`(PIPESTATUS 非 POSIX sh 專屬,這裡沒有殼別不符的風險)。沒有既有寫法可以抄,是合理的新增,不算繞過既有寫入口。
- `_DOCS_ONLY_EXTS` 與 `_PITFALL_DIFF_SKIP_EXT`(`scripts/lumos:18540`)、`_NODEHOME_CODE_EXTS`(`scripts/lumos:20457`)的關係:三份清單回答三個不同問題(要不要當代碼掃 pitfall regex / 要不要有家 / 算不算純文件跳全套),`_NODEHOME_CODE_EXTS`(程式副檔名)與 `_DOCS_ONLY_EXTS`(文件副檔名)逐一比對完全不相交,設計上互斥、沒有衝突;`_PITFALL_DIFF_SKIP_EXT` 與 `_DOCS_ONLY_EXTS` 有部分交集(`.json .jsonl .csv .svg .txt`)但語意不要求相等(前者多 `.log .lock .html .patch .diff .rst`,是「不掃描內容找風險型樣」的清單,連 `.patch`/`.diff` 這種明顯不是文件的格式都在裡面,是刻意分開的兩個判準)。沒有既有的「五份一致」那類漂移守衛(對照 `_NODEHOME_CODE_EXTS` 旁的 `t_code_exts_lists_agree` 五份一致測試),但因為語意本來就不要求一致,不需要;不成立為發現。
- `_helper_sources_in` 用 `globals()` 反查函式:`grep -n "globals()" scripts/test_lumos.py` 顯示本檔既有的 `globals()` 用法全是拿來列舉 `t_*` 測試函式本身(測試發現機制),沒有「regex 抓呼叫字樣 → globals() 反查任意輔助函式原始碼」這種先例,是這批新引入的手法。但看實作:過濾 `callable` 與 `__module__ == __name__`、用 `_HELPER_SRC_CACHE` 快取,只在 `_docs_suite_select` 這個新功能內部使用,沒有跟既有機制打架或繞過既有寫入口,是合理的新增,不算違規。
- fixture 裡 `FAKE_KEYS_RC` 環境變數控制假執行器離開碼:`scripts/test_lumos.py:40562-40563`(`t_prepush_and_ci_wired_for_docs_suite` 前面某支既有測試)已經有 `FAKE_HOME_RC` 這個一模一樣的慣例(假執行器讀 `os.environ.get('FAKE_..._RC')` 決定 `sys.exit`),`FAKE_KEYS_RC` 命名與用法都照抄這個先例,對齊。
- `_docs_suite_select` 在 `--list` 路徑上讀 `_load_lumos_inproc()`:`_load_lumos_inproc()` 本身是已有上百個呼叫點的既有快取單例(`scripts/test_lumos.py:211`),模組載入沒有頂層副作用(逐項查過 `scripts/lumos` 檔首到 `if __name__ == "__main__"` 之間全是常數/正則/函式定義);實測整支 `scripts/lumos`(4萬多行)當模組載入只要約 30ms,對「--list」這種本來就要枚舉全部測試的路徑而言可忽略;沒有發現隔離風險(不改 `sys.path`、不 `os.chdir`、不註冊 atexit)。
