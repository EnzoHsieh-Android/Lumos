severity: major

### F1 新函式在判斷層裡直接開 git 子行程讀 commit 內容,繞過既有的快照/讀取抽象,是第二套讀法也是跨層直呼
severity: major
blocking: 是 — 命中「major=引入第二種做法或跨層直呼」的嚴重度錨定,同時符合兩項
1. 分層方向:`_nodehome_evaluate`(scripts/lumos:18119)原本的設計是純判斷——I/O 都由呼叫端先建好再傳入(`B`/`N` 由 `_nodehome_side` 建快照、`groups` 由 `_nodehome_commit_groups` 先讀好才傳進來,函式本體只讀 `side.notes`/`side.files` 這些既有結構,自己不開新的 git 子行程)。這次新增的 `_nodehome_note_changed_in_commit` 卻在 `_nodehome_evaluate` 的判斷迴圈裡被直接呼叫,內部再呼叫 `_nodehome_git` 對任意中繼 commit 現拆兩次 `git show`,把 I/O 拉回了判斷層。
2. 第二種做法:讀「某個 git 版本的 note 內容」原本只有一條路——`_nodehome_reader`(scripts/lumos:17874)包出來的 `read()`,帶 differ 快取＋磁碟 fallback,專門避免逐篇重讀;新函式另開一條路,直接裸呼叫 `_nodehome_git(repo_root, "show", ...)` 兩次組出新舊內容再比 `sig`,沒有走 `_NodehomeSide`/`_nodehome_reader` 那套既有快取。

引句:「new = _nodehome_git(repo_root, "show", f"{sha}:{path}")」

file: `scripts/lumos:17930` — `_nodehome_side` 的既有設計:share/changed 快取就是為了不讓每篇 note 都重新 `git show`。
file: `scripts/lumos:17931` — 同一段文件明講「推送前的起點那一側只讀這段範圍裡有變動的節點——不然每一篇都要 git show 一次,65 篇就要 2 秒以上」,是這條 I/O 紀律的既有理由。
file: `scripts/lumos:17898` — `_nodehome_reader.read()` 內既有的唯一 git-show 讀取路徑(帶 differ 快取＋磁碟 fallback)。
file: `scripts/lumos:18121` — `_nodehome_evaluate` 文件字面寫「B=之前、N=之後」等既有建好的輸入,佐證這層原本不做 I/O。
file: `scripts/lumos:18224` — 新增的跨層呼叫點,在判斷迴圈裡直呼 `_nodehome_note_changed_in_commit`。

重現:指令 `grep -n 'def _nodehome_reader\|_lens_git(repo_root, "show"\|_nodehome_git(repo_root, "show"' scripts/lumos`;預期輸出三行命中——17898 行(既有 `_nodehome_reader` 內走 `_lens_git` 的既有讀法)、18087/18088 行(新函式另開的 `_nodehome_git` 讀法),兩條路徑互不共用,可當場核對這是第二套讀 git 的做法。

總結:最高 severity major,blocking 共 1 條
