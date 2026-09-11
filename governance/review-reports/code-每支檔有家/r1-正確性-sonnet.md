severity: blocker

### F1 反引號裸檔名比對會被不相干的新增檔「巧合命中」而誤擋合法提交
severity: blocker
blocking: 是 — 硬擋(rc1)一個跟被喚醒節點完全無關的提交,且唯一解法是去改別人節點的舊散文,不是修自己的改動
引句:「新增的檔喚醒了沒改的節點裡原本就寫著的檔名」

1. `_nodehome_refs` 的裸檔名(無 `/`)比對只看「在受版控檔裡是否唯一」,不管那個反引號詞當初是不是真的在指一支檔——舊節點裡任何一個不含路徑的反引號詞,哪怕只是舉例,都可能被日後一支毫不相干的新檔「巧合命中」。
2. 重現:建節點 A(不會再被這次提交改動),正文寫 `` `config.py` `` 純屬舉例、當下 repo 裡沒有任何 config.py;另一提交新增 `feat/config.py` 並替它建好正確的家 `Owner`(`about_code: [feat/config.py]`),對這個提交跑 `lumos home check --staged --repo <repo>`。
3. 實測 rc=1,擋訊息印出「Systems/A 寫了 `feat/config.py`(這篇沒改,是這次新增的檔讓它原本寫的檔名變成別人的檔)」——一個只新增並且正確歸戶的檔,因為完全無關的舊節點被硬擋。

佐證行:file: `scripts/lumos:692` `return full, {s for s in spans if "/" not in s}` ——裸 token 集合來自任何反引號片語,不要求看起來像檔名(無副檔名判斷)。

### F2 symlink↔一般檔的 T 型別變更不算「新增」,讓 S3(新增沒家擋)整條失效
severity: blocker
blocking: 是 — 全新、完全沒有家的程式碼可以只靠一次型別變更就從「擋」降級成「提醒」,兩種模式(--staged/--diff)都中
引句:「if code in ("A", "R", "C"):」

1. `_nodehome_changes` 對 git status 為 `T`(型別變更,如 symlink→一般檔)的路徑產生 `(code, old=p, new=p)`;`_nodehome_evaluate` 判「新增」只認 `code in ("A","R","C")`,`T` 永遠進不了 `added`/`code_added`,S3「新增沒家的檔 → 擋」摸不到它,只會落到 `legacy-homeless`(純提醒)。
2. 重現:base commit 讓 `src/tool.py` 是一個 symlink(不算需要家的檔);下一提交把它原地換成真正的 python 程式碼、不給任何家;`git diff --cached --name-status -M` 印出 `T\tsrc/tool.py`。
3. 對這個變更分別跑 `lumos home check --staged --repo <repo>` 與 `lumos home check --diff <base>..<head> --repo <repo>`,實測皆 rc=0,只印「提醒:這次改到 1 支還沒有家的舊檔」,不是預期的 rc1 硬擋。

佐證行:file: `scripts/lumos:1073` `out.append((code, p if code != "A" else None, p if code != "D" else None))` ——T 落在此 elif 分支,old=new=同一路徑,不進 `deleted`、也不進 `added`。

### F3 `_nodehome_changes` 宣稱處理「複製」,但呼叫沒帶 `-C`,C 分支實際不可達
severity: minor
blocking: 否 — 效果上複製仍會被 git 標成 A、照樣落進新增判定,判定結果沒有錯,純屬文件與實作不一致
引句:「改名與複製的新路徑算新增 [S31]」

1. 兩處 `git diff --name-status` 呼叫只帶 `-z -M`,從未加 `-C`/`--find-copies`,git 在這個呼叫下永遠不會回報 `C` 狀態,`elif code in ("R", "C")` 分支裡的 `C` 半邊是死碼。
2. 複製出的新檔實際會被 git 標成單純 `A`,仍會落進既有的 `added` 集合被要求安家——行為沒錯,只是 docstring 聲稱的「複製由這裡處理」跟實際觸發路徑對不上。⚠ 是否要修正措辭或補 `-C` 交編排者判斷。

總結:最高 severity blocker,blocking 共 2 條
