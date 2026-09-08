<!-- 外家否決席(Codex gpt-5.6-terra, xhigh, --sandbox read-only);原始逐字稿 r1-codex-raw.txt;正規化:去行尾雙空白、去重複印出的第二份;五行引句由該席在後續回合補(逐字稿 r1-codex-quotes-raw.txt),結論未動 -->
severity: clean

① 非 Git vault：已讀,無 finding。非 Git 時沒有可歸屬的 hook 根；hook 寫入器只在 `git rev-parse` 得到根目錄後記帳，因此不再讀 cwd 的事件是隔離修正，repo 內未見相反消費契約。
引句:「repo_root=hook 事件檔所在的 repo 根,由呼叫端從 vault 反推(_vault_repo_root);★不准用 cwd 的 git 根★——」

file: `scripts/lumos:4732` `_vault_repo_root` 先向上找 `.git`，才退回 `vault.parent`。
file: `scripts/hooks/claude/_hookevent.py:138` `guard()` 只有取得 Git 根時才呼叫 `record()`。

② 測試與突變：已讀,無 finding。拿掉 `git init` 後，根會退到 `root/docs`，讀不到刻意寫在 `root/governance` 的 fixture，`out1` 的「hook 段出現」斷言必紅；退回 cwd 版同樣讀不到 fixture 根，該斷言必紅。
引句:「_sp.run(["git", "-C", str(root), "init", "-q"], capture_output=True)」

file: `scripts/test_lumos.py:71` `run()` 未改變 cwd。
file: `scripts/test_lumos.py:4455` Git 初始化是 fixture 根解析的前提。
未能實跑：唯讀沙盒無可用暫存目錄，測試在選取 `gov_stats` 前即失敗。

③ `repo_root=None`：已讀,無 finding。現有唯一呼叫端明確傳入 `_vault_repo_root(env)`；`None` 僅讓未來直接內部呼叫略過 hook 段，沒有現行呼叫端回歸。
引句:「_render_gov_stats(_raw, ded, loaded, since_days, cutoff, node, repo_root=_vault_repo_root(env))」

file: `scripts/lumos:4549` 唯一 `_render_gov_stats` 呼叫提供 `repo_root`。

④ 刪除 helper 殘留：已讀,無 finding。對目前 hooks、知識圖譜與 skills 的精確掃描未發現 `_gov_repo_root_for_hooks` 活引用；歷史 review snapshot 不屬執行路徑。
引句:「def _render_gov_stats(rows, ded, loaded, since_days, cutoff, node, repo_root=None):」

file: `scripts/lumos:4164` 現行渲染函式改由參數取得根目錄。

⑤ Python 3.9 時戳：已讀,無 finding。測試與寫入端都產生 `isoformat(timespec="seconds")` 的帶冒號 UTC offset（如 `+08:00`），可由 Python 3.9 `fromisoformat` 解析，且讀側比較的是兩個 aware datetime。
引句:「now = _dt.datetime.now().astimezone().isoformat(timespec="seconds")」

file: `scripts/test_lumos.py:4460` fixture 使用同一種 ISO 時戳。
file: `scripts/lumos:4294` 讀側以 `datetime.fromisoformat` 解析。

總結: 最嚴重 severity clean；blocking 0 條。
