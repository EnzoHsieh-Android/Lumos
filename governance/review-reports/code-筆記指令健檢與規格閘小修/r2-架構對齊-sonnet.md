severity: major

核對的是 `scripts/lumos`。b76b570e 與目前工作樹的 `scripts/lumos` 內容相同,行號都取自這份。

上一輪架構席要求的八項,逐項核對結果:

| 要求 | 結果 |
|---|---|
| 差異清單改用 `_nodehome_changed_vs_disk` | 做到。`scripts/lumos:34369` |
| 捷徑檔守衛 | 做到,寫法與 `_nodehome_reader` 的 `scripts/lumos:33319` 一致。`scripts/lumos:34383` |
| 三指令預設範圍一致 | 只做到一半,見下方第 2 問的 finding 2 |
| `_doctor_` 前綴 | 做到。`scripts/lumos:9189` |
| `_probe_cond_keys` 共用 | 做到。`scripts/lumos:6960`、`42145`、`42149` |
| updated 迴圈收成一支 | 做到,用 `_fm_touch_updated`。`scripts/lumos:22835`、`22964`、`22981` |
| 留痕不裁的理由 | 做到,理由寫在註解裡。`_gate_event_fit` 沒有被套用,不算新做法 |
| doctor S14 合讀 | 做到,但三個呼叫端的失敗處理各不相同,見 finding 4 |

## 1. 分層與依賴方向

新增的 helper 都放在鄰居同一層,沒有跨層直呼。唯一的問題是 `_spec_gate_status_at` 沒有用既有的範圍起點函式。

severity: major
blocking: 是
引句:「base = git_range.split("..", 1)[0] if ".." in git_range else ""」
- 這行自己重寫了「範圍起點」的求法,而專案已有共用的 `_range_base(rr, diff_range)`(`scripts/lumos:47645`)。
- 同一條推送路徑的鄰居 `_pq_push_remind` 就是用它(`scripts/lumos:9063`),並明講三點範圍要取 merge-base。
- 新寫法碰到 `a...b` 會拿左端點當起點,正是 `_range_base` 的 docstring 記載過、已修掉的錯。
- 這是第二種做法,而且帶著已知的舊錯。
- `_spec_gate_status_at` 讀起點版本本身沒問題,它用的是既有的 `_note_text_at_rev`(`scripts/lumos:22758`),再接 `split_frontmatter` 加 `parse_frontmatter`,與 `scripts/lumos:17719` 同寫法。
- 順帶一提,`repo_rel = (env.vault / prel).resolve().relative_to(Path(rr).resolve()).as_posix()` 這四行在 `scripts/lumos:6977`、`22792`、`9970` 已有三份,新增的是第三份。這裡只算提醒,因為專案裡本來就沒有共用 helper。

## 2. 命名與錯誤處理

severity: minor
blocking: 否
引句:「if not staged and not diff_range:     # 跟 home check、note-shape 同一條:沒帶範圍照 --staged(代碼審 r1 架2)」
- 訊息文字與鄰居一致,但落點與語意不一樣。
- `home check` 和 `note-shape` 把預設放在分派層,用 `is None` 判斷,所以 `--diff ""` 會走範圍錯誤的路。這兩處在 `scripts/lumos:59071`、`59113`。
- `cmd_cochange_check` 把預設放在命令函式裡,用 `not diff_range` 判斷,所以 `--diff ""` 會悄悄改成查 staged。
- 同一個函式的 docstring 還寫著「皆缺 --staged/--diff 或 git 失敗=2」(`scripts/lumos:46251-46252`),現在是過期的。
- 所以只有訊息一致,三指令的預設範圍並沒有完全一致。

severity: minor
blocking: 否
引句:「ex = _excluded_line(ln) if len(re.findall(r"[:：]", s)) >= 2 else None」
- 防回溯的補丁只加在 lint 的呼叫端 `scripts/lumos:6929`。
- 真正的消費者 `_door_exclusions` 在 `scripts/lumos:8211`,同樣呼叫 `_excluded_line`(`scripts/lumos:8187`),沒有加這道守衛。
- 我在 `_EXCLUDED_RE` 上用「已排除:」加 2000 個空白再接一個字測試,卡住超過 120 秒。
- 這是逐點補丁,不是改共用的解析器。`_excluded_line` 的 docstring 還自稱「唯一」解析。

severity: minor
blocking: 否
引句:「_sg_latest = _spec_gate_latest_merged(env) or _spec_gate_latest_records(env)」
- 同一個合併函式,三個呼叫端三種失敗處理:
  - 推送閘 `scripts/lumos:10012`:讀不到就擋。
  - `_spec_gate_low_not_red` `scripts/lumos:9215`:退成 `{}`。
  - doctor `scripts/lumos:3245`:退回只看本機帳。
- 結構沒錯,但失敗語意不一致。

severity: minor
blocking: 否
引句:「return "擋下:git 列不出檔案清單,沒辦法先跑提交時的筆記形狀檢查——summary-add 要在 git 專案裡用」
- 非 git 專案的偵測在 `scripts/lumos:22774` 做了一次,而 `_drift_fix_shape_err` 內部也會做一次,見 `scripts/lumos:43927`,兩處措辭不同(「筆記形狀檢查」對「筆記形狀擋」)。
- `_summary_write_shape_check` 現在會尊重 `gate_mode` 的 off/warn(`scripts/lumos:22779`)。
- 同樣呼叫 `_drift_fix_shape_err` 的 drift fix 寫入端不看 `gate_mode`(`scripts/lumos:44072`)。
- 兩個「寫入前形狀檢查」的行為不一樣。這是為了對齊提交時的行為而改的,但專案裡又多了一個分歧。

severity: minor
blocking: 否
引句:「planned = {x.rstrip("/") for x in _planned_ref_tokens(text)}     # 集合只算一次(代碼審 r1 資2)」
- `_planned_ref_tokens` 的 docstring 寫著 refcheck 與 doctor P 段共用。
- 兩個呼叫端現在各自做一次相同的 `rstrip("/")` 正規化,在 `scripts/lumos:3516` 與 `30367`。
- 正規化放進共用的 helper 才一致。

## 3. 第二種做法

- 找到一個:finding 1 的 `_spec_gate_status_at` 自寫範圍起點。
- 另外 `scripts/lumos:9224` 的「工作目錄有未提交改動」檢查,用的是 `_lens_git(... "status","--porcelain","--untracked-files=no")`。專案裡這類檢查原本就有近十種寫法(例如 `scripts/lumos:15434`、`57387`),所以不算新增第二種。
- `_NS_NEG_COND_OPEN` 與 `_NS_NEG_CLAUSE_PUNCT` 已與 `governance/eval/negation-revisit/neg_revisit_measure.py:241-242` 同步,並被 `scripts/test_lumos.py:89061` 的對照表守住,與專案既有做法一致。
- `_spec_gate_pick` 的同時間改取後列、`float("-inf")` 的寫法,與 `scripts/lumos:13098` 慣用法一致。

不對齊共 6 條,其中 major 1 條。
