severity: minor

第 4 輪通才回歸驗收完成。八個包裝函式與 decision-amend 在我跑的所有路徑上,stdout、stderr、rc 都跟修前一致。有一處行為退步(符號連結筆記),另有一處文字殘留,兩者都不擋合併。

做法:把兩版 `scripts/lumos`(修前 646dc3a8、修後 d6bb423f)各放進臨時副本,對同樣的新建筆記庫逐支實跑,比對輸出與 rc。

**八個包裝函式與 decision-amend**
- 八個包裝函式的參數名、預設值、回傳值都跟修前一致,是手寫的包裝,不是自動產生。呼叫端的傳參方式也都還對:`cmd_decision_reindex` 的 `--all` 巢狀呼叫、`_append_decision_ref`、`_dref_remove_ref`、`cmd_dref_promote`、main 內各入口。
- 我實跑了 decision-add、decision-supersede、decision-reindex(單篇與 `--all`)、guard bind(成功、方法名不合法、找不到節點)、guard audit(預設與 `--model`/`--date`)、decision-refs promote 與 prune。兩版輸出、rc、`git diff --stat` 都相同。
- decision-amend 實跑了成功、已推上去被擋、撞號、欄位不存在、清單欄位、不在 git 裡、沒遠端、含換行的文字、結構欄、節點不存在、編號形狀不對。除一處例外,兩版輸出與 rc 都相同。
- 例外是拿鎖逾時和 OSError:修前會噴追蹤(traceback),修後走「擋下」rc2。這是改好,不是退步。
- 我沒有實測鎖逾時(要等 60 秒)。
- 這四個包裝入口的 `.md` 呼叫 `atomic_write_verify` 前都是 `env.vault / rel`,路徑都落在筆記庫底下。
- 核心圖譜自己當筆記庫跑時,它就是 `env.vault`,不受影響。

severity: minor
blocking: 否
- 輸入:筆記庫內的某篇筆記是指向庫外的符號連結檔(例如 `Systems/baz.md -> /外部/baz.md`),執行 `lumos set baz status draft` 或 `lumos decision-add baz ...`。
- 走到哪一行:`atomic_write_verify` 開頭的 `_vault_lock_held_for(path)` 對 path 取 `os.path.realpath`。連結解析到庫外,與庫的 realpath 不符,就丟 RuntimeError。
- 修前:放行,寫成功,rc 0。連結本身被換成一般檔。修後:印「寫開頭欄位前沒拿這個筆記庫的寫入鎖…這是工具本身的漏洞,請回報」,不寫入。
- 這個訊息誤導:鎖其實拿著了。
- 實跑時庫目錄本身是符號連結沒問題(兩版都寫成功)。
- 這個 repo 的 docs 底下沒有符號連結。專案其他守衛也把符號連結當攻擊面,所以我判成只影響少見佈局。
- 歸因:有證據的修復回歸。
- 兩版查證命令:在 `mk.sh` 造的筆記庫裡 `ln -s <庫外>/baz.md docs/p-knowledge/Systems/baz.md`,再跑 `python3.14 <版本>/scripts/lumos set baz status draft`。
- 查證結果:修前 `✓ set Systems/baz.md`,修後 `擋下:…沒拿這個筆記庫的寫入鎖…`。
- 引句:「    if not _vault_lock_held_for(path):」
- 佐證:file: `scripts/lumos:19937`、`scripts/lumos:19965`(修後版)

severity: minor
blocking: 否
- 圖譜筆記的 WHY 行還寫著「所有讀改寫開頭欄位的入口都經 `_vault_locked` 拿鎖」,但修後程式裡 `_vault_locked` 已經不存在(`grep -c` 得 0)。補丁只改了同檔後面那條 WHY,這一行沒動。
- 依專案規則,這屬於筆記對不上程式的線索,不影響行為。
- 歸因:有證據的修復回歸(修前這句話是真的,修後變錯)。
- 查證命令:`git show d6bb423f:docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md | grep -n _vault_locked` 得第 150 行;`git show d6bb423f:scripts/lumos | grep -c _vault_locked` 得 0。
- 引句:「2026-10-12 起所有讀改寫開頭欄位的入口都經 `_vault_locked` 拿鎖」
- 佐證:file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:150`

**推送前檢查入口**
- `--push-check` 開頭是 `-` 的範圍(`--push-check=--output=<檔>`)現在被擋下並放行,rc 0。修前真的會用該路徑寫出檔案(`PWNED-before` 出現,`PWNED-after` 沒出現),修後沒有。
- 我試過 `main..feat`、`main...feat`、`HEAD~1..HEAD`、`..HEAD`、`HEAD~1..`、`refs/heads/…..refs/heads/…`、`HEAD~1..HEAD~0`,輸出與修前一致。
- 找不到起點的範圍(例如單一版本 `feat`)只差一處:範圍文字多了引號(`'feat'`)。
- 合法範圍不會以 `-` 開頭,所以沒有誤擋。
- 新增的「兩端要是 git 認得的提交」檢查,在我試的範圍都沒誤擋。
- 一個小差異:`_pq_renames` 的 git 逾時從 60 秒變成 `_lens_git` 預設的 20 秒,算不出時退回空表(當沒改名)。對很大的庫理論上比修前更容易跳過改名比對,我沒量到實例。

**三問**
- ①原問題(鎖逾時與跨筆記庫拿鎖、`-` 開頭範圍)的行為證據:`-` 開頭範圍有上面的 PWNED 兩版對照。拿 A 庫的鎖寫 B 庫會被擋,靠 `_vault_lock_held_for` 的路徑比對,我只確認了筆記庫在符號連結下仍可用,沒另外造 A、B 兩庫的案例。
- ②修補處的正常、錯誤與相鄰路徑:上述八支加 amend 的所有路徑都一致。唯一退步是符號連結筆記。`-k amend` 10 通過、`-k qfm` 195 通過、`-k decision_add` 7 通過。`-k lock` 有 4 支紅,是我只複製 `scripts/` 造成缺 `governance/eval` 與 `install.sh`,不是程式問題。
- ③新發現的同一案例在修前、修後:符號連結筆記,修前寫成功,修後擋下並印誤導訊息。`_vault_locked` 的筆記殘留,修前是真話,修後是錯話。

總結:修補沒有打壞既有功能,沒有擋合併的問題,只有符號連結筆記的行為退步與一行過期筆記兩個 minor。

臨時副本都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r4-通才回歸-sonnet/`。我跑測試留下的兩個 `gctl-run-*` 現場已刪。
