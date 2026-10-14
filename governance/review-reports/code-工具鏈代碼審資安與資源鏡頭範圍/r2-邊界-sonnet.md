severity: minor

兩支新測試的夾具與斷言大致守得住。範本逐句斷言有一個缺口:句子被搬出派工詞圍欄時,測試不會紅。我在臨時副本(已刪)上做了變異;repo 本體只讀,沒有改動。

**實驗結果**
- 把 `_is_toolchain_repo` 的 `is_file()` 換成 `exists()`,`t_loop_next_lens_scope_marker_odd_kinds` 的「SKILL.md 是目錄」那條翻紅(`toolchain rc 1/1`)。壞符號連結與 `--repo` 不存在兩條仍綠,因為這兩種情況 `exists()` 也回 False。這兩條的價值是防例外和防誤判,不是區分 `is_file` 與 `exists`。
- 把 `loop next` 的編號判斷收緊成 `^code-[A-Za-z0-9_-]+$`,`t_loop_next_lens_scope_loose_code_ids` 三條全紅。改成「長度大於 5 且不含半形空白」,只有 `code-　x`(全形空白)那條綠,其餘兩條紅。三個夾具分得開。
- 把 templates.md 改成 CRLF 後,`t_templates_toolchain_lens_scope` 47 條仍全綠。`read_text` 會做換行轉換,CRLF 不是風險。
- 把「工具鏈三類」的標題降成 `####` 會被 ⑧ 抓到。
- 把 DoS 那句整句刪掉,⑥b 會紅。
- 把 `_SEC_FILL_OUT` 寫回原本的「消費專案留空」,逐字比對會紅。

**上一輪邊界席列的情況**
- `code-`、`code- x`、全形空白編號,現在有測試釘住。
- 判別只看根目錄那一支檔的邊界,現在寫進範本與 RULE。我讀 `_vault_repo_root` 核對:沒有 `.git` 時退到 `vault.parent`,也就是 `docs/`,所以「沒有 .git 的副本判成消費專案」成立。
- 這輪修補沒有讓這些情況變壞。

severity: minor
blocking: 否 — 只是測試守衛有缺口,不是現行行為錯誤
引句:「DoS / 資源耗盡 / 限流在這個 repo 歸資源席,不報。」
問題:⑥b 的逐句斷言用 `sent in three`。`three` 是整個 `### 工具鏈三類` 小節,包含圍欄前的說明段(給編排者看,不貼進派工詞)和圍欄內(貼給子代理的段落)。這句 DoS 與「卷證…不報」、「接受不看」都必須在圍欄內才會到子代理手上,測試沒有限定位置。
具體失敗情境:把 DoS 那句從圍欄末行搬到圍欄前的說明段(「…原樣貼進逐類清單填空。DoS / 資源耗盡 / 限流在這個 repo 歸資源席,不報。判別只看根目錄…」)。
- 輸入:`python3.14 scripts/test_lumos.py -k templates_toolchain_lens_scope`
- 輸出:`47 passed, 0 failed`。
- 實際結果:資安席從此收不到這句,「工具鏈本 repo 的 DoS 歸資源席」就失效。
- 對照:整句刪掉,輸出是 `✗ ⑥b〈工具鏈三類〉逐句含「DoS / 資源耗盡 / 限流在這個 repo 歸資源席,不…」`,`46 passed, 1 failed`。
- 建議:會貼進派工詞的句子,改成在「三類」小節第一個圍欄內比對,說明段的句子才在整節比對。
file: `scripts/test_lumos.py`(patch 的 `⑥b〈工具鏈三類〉逐句含` 迴圈)

severity: minor
blocking: 否 — 只是提示文字不準,不影響行為
引句:「鏡頭範圍: 帳本所在 repo 是工具鏈本 repo——被審分支也在這個 repo 時」
問題:判別根是 `Path(repo).resolve() if repo else _vault_repo_root(env)`。帶 `--repo` 時,判的是 `--repo` 指到的目錄,不是帳本所在 repo。但那一行無條件寫「帳本所在 repo 是工具鏈本 repo」。
具體失敗情境:帳本在消費專案、`--repo` 指到工具鏈目錄,輸出仍印這句。夾具 `_mk_lens_dirs` 加獨立 `mkvault()` 的現有測試就是這個組合(帳本在臨時 vault,`--repo` 指 tc),印出的就是這句。編排者讀到的前提與事實不符。條件語氣的後半句讓照貼的人不至於少審,所以只算 minor。
file: `scripts/lumos:16154`、`scripts/lumos:16432`

severity: minor
blocking: 否 — 屬記帳綁定的缺漏,不是行為錯誤
引句:「另加兩支測試釘住現況:`code-`、`code- x`、`code-　x` 都當代碼審;SKILL.md 是目錄、壞符號連結、`--repo` 不存在都落 default。」
問題:新增的 `t_loop_next_lens_scope_loose_code_ids` 與 `t_loop_next_lens_scope_marker_odd_kinds` 沒有任何計劃條款的 `[test:]` 綁定。patch 裡只有 S1 綁 `t_loop_next_lens_scope_toolchain_vs_consumer`,新條款也沒加。
具體失敗情境:兩支測試被改成空殼或刪掉,條款綁定閘看不出來。只剩原始碼提到函式名的 `--suite keys` 子集可能碰到它們。
file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md`(patch 新增的「代碼審第一輪的修正」段)

已讀,無 finding:
- `_tpl_dispatch_fences` 新增 §3.1、§9 分支。標籤用 `sub`,`seen` 與 `sec` 不衝突;`labels == 10` 的計數寫死,新增圍欄會紅,屬刻意的嚴格。
- ⑥ 變異對 `### §3.1 ` 與 `## 9. ` 各自只點名那一份。
- `_SEC_NB_DOS_ORIG` 整行比對加 ③b「不報」段不含「工具鏈」。
- 筆記指標測試(sitecustomize 的 WHY、兩條 KEY 指 d8、`about_code`)。
- `Issues/工具鏈範圍外手法紀錄` 的改寫。

最高等級 minor,blocking 0 條。
