severity: minor

三類都看過。「推 main 被誤判成功能分支」這條路我沒找到,所以沒有會擋的問題。下面只有一條縱深防禦類的 minor。

**主線判斷靠遠端 ref,不靠本機分支名。** `pre-push` 把 stdin 解出來的遠端 ref(`_rref`)直接傳給 `--pushed-ref`,所以下面這些推法都不會被降成 light:
- `git push Lumos feat:main`:遠端 ref 是 `refs/heads/main`,在集合裡,判主線,照全套。
- `HEAD:main`:同上。
- 遠端名不是 origin:不影響,因為 `_note_reread_mainline_names` 不看遠端名。
- 標籤、空字串、`refs/for/…` 這類不在 `refs/heads/` 底下的 ref:一律回 true,照全套。
- 推 main 的同時混推功能分支:main 那個 ref 是 full,整次推送照全套。

預設分支不是 main/master 的情形也不構成洞。這份 diff 沒改 CI,而 `.github/workflows/ci.yml` 的 `push` 只認 main 和標籤。主線名是 `trunk`、`develop` 這類時,它本來就沒有 push 事件的 CI,降成 light 沒有讓任何 CI 被繞過。

其他幾個入口也都往保守的方向走:
- `pitfalls` 逾時或出錯、`pf_json` 為空、舊版 lumos 沒有 `suite_computed` 欄位:全部照全套。
- 舊版 lumos 不認 `--pushed-ref`:`_PF_PR` 探測沒對到字樣,就不帶旗標,所以 `pf_json` 不會變空。
- `_rref` 一定以 `refs/` 開頭,當 argv 傳不會被 argparse 當成旗標。
- 沒有 shell 插值:`${_pf_extra+…}` 是陣列展開,`_rref` 不經 `eval`。
- 秘密與信箱:新增的 `.lumos/lint-waivers.json` 放行條目和 `governance/anchor-baseline.json` 的 hash 都沒有密鑰或信箱。
- 提示注入:新增的 echo 都是固定字串,沒有帶入筆記、檔名或分支名。

**Finding**

severity: minor
blocking: 否
標題:新分支名一律當「功能分支」降成 light,同一台遠端若有 main 以外的受保護或直接發佈分支就沒有本機全套
引句:「分支短名在 _note_reread_mainline_names 的集合裡(永遠含 main、master,再加主線候選指到的分支名,不看遠端名)→ true;其他 → false。」
file: `scripts/lumos:53731`(`_NOTE_REREAD_MAINLINE_NAMES = ("main", "master")`)、`.github/workflows/ci.yml:5`
說明:這是推論,寫不出四件齊全的攻擊路徑。
- 場景:使用者或 AI 照常推 `feat:release` 或 `feat:develop`,而 `release`、`develop` 沒被遠端 HEAD 或 main/master 的 upstream 指到。
- 結果:判成功能分支,本機只跑文件與關鍵字子集;這類分支又沒有 push 事件的 CI,要開 PR 才有。
- 這是計劃本意放寬範圍的邊緣,所以標 minor、不擋。
- 縱深防禦的做法是把降級的分支限定成「遠端上本來不存在、或 `refs/heads/` 底下已有人推過的功能分支」。

**看過的檔(凍結 patch 全部 13 個)**
- `.lumos/lint-waivers.json`
- `CLAUDE.md`
- `docs/.canary-log.jsonl`
- `docs/lumos-toolchain-knowledge/Projects/依實測覆蓋挑測試_計劃.md`
- `docs/lumos-toolchain-knowledge/Projects/推送只跑受影響測試_計劃.md`
- `docs/lumos-toolchain-knowledge/Projects/推送與CI提速_計劃.md`
- `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md`
- `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`
- `governance/anchor-baseline.json`
- `scripts/hooks/pre-push`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `skills/lumos-project-notes/commands/08-自動跑的.md`

前五支文件、筆記與 `skills/` 我只用 grep 掃了有沒有密鑰、信箱、`curl`、`eval` 這類字樣,沒逐行讀。`test_lumos.py` 新增段落一樣只用 grep 掃了 `shell=True`、`os.system`、`token`、`secret`、`password`、`rm -rf` 和信箱格式,沒有命中。

另外在 repo 讀了 `scripts/lumos` 的 `_note_reread_mainline_names` 和 `ci.yml` 的 `on:` 區塊;沒改任何檔,也沒建臨時目錄。
