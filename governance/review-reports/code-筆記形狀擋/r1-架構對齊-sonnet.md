severity: major

## F1 became_code 用 git grep 重做「新程式檔喚醒舊引用」,鄰居已有同功能的記憶體算法

severity: major
blocking: 是 —— 引入第二種做法:home-check 的「foreign-awakened」偵測(新增的程式檔喚醒沒改動節點裡已寫的檔名)已經用記憶體裡的 vault 索引(`N.notes`、`refs_now`、`ownN`)算好,一次迴圈比對集合;note-shape 對同一個概念(`_ns_became_code` 找到的新程式檔要不要去喚醒舊筆記)另外開一支子行程 `git grep -F` 去掃全庫文字、再手拆冒號欄位解析輸出。兩套「找誰引用了這個檔名」的判定邏輯分岔,以後其中一套改了規則(例如 token 抽取規則、排除路徑)另一套不會跟著變。
引句:「args = ["grep", "-n", "-I", "--full-name", "-F"]」
file: `scripts/lumos:23704`
對照(鄰居既有算法): `scripts/lumos:23029-23036`(`_nodehome_evaluate` 內 `foreign-awakened` 段,純記憶體比對 `refs_now(rel) & code_added`)

## F2 _ns_regions 自己重寫 frontmatter 邊界與頂層鍵判定,沒有借用既有的 split_frontmatter/TOP_KEY_RE

severity: major
blocking: 是 —— 全庫只有一套「frontmatter 從哪到哪、頂層鍵怎麼認」的權威實作(`split_frontmatter` 切邊界、`TOP_KEY_RE`/`parse_frontmatter` 認頂層鍵),lint、索引、寫回全走這一套。`_ns_regions` 為了判斷一行落在 summary/decisions/body 哪一塊,自己重新掃「第一行是不是 `---`」「掃到下一個 `---` 收尾」,並另開一條長得幾乎一樣的正則 `_NS_TOPKEY_RE` 認頂層鍵,而不是先呼叫 `split_frontmatter` 定位邊界、共用 `TOP_KEY_RE` 認鍵。日後 frontmatter 語法有調整(例如允許 BOM、允許非 `---` 分隔),两套會各自漂移。
引句:「_NS_TOPKEY_RE = re.compile(r"^([A-Za-z_][\w-]*)\s*:")」
file: `scripts/lumos:23438`
對照(既有共用實作): `scripts/lumos:179`(`TOP_KEY_RE`)、`scripts/lumos:229`(`split_frontmatter`)、`scripts/lumos:240`(`parse_frontmatter`)

## F3 治理帳寫入覆蓋範圍跟鄰居不一致(home 每次都寫,note-shape 只寫擋下/跳過)

severity: minor
blocking: 否 —— 結構沒問題(仍走同一支 `_gate_event_or_warn`),只是寫入時機跟最近的鄰居 `cmd_home_check` 不同:home-check 不分 passed/warned/blocked 每次都落一筆帳(`scripts/lumos:23424` 的 `kind` 可以是 "passed"),note-shape 只在 `mode=="block"` 且有違規,或 env 跳過/淺層 clone 時才寫,warn 模式即使有違規也完全不寫帳。此差異在程式碼與圖譜筆記裡都有特別交代是刻意決定(避免 rtb 抱怨的帳本雜訊),但既然題目問「跟鄰居一樣嗎」,兩道最近的閘在「同一件事要不要每次留痕」上就是不同做法,交由編排者判斷这個分岔要不要可接受。
引句:「只有擋下與跳過寫治理帳,放行不寫——刻意跟每支檔有家每次都寫 passed 不同」
file: `scripts/lumos:23792`(cmd_note_shape docstring)
對照: `scripts/lumos:23424`(home-check 每輪必寫 `_gate_event_or_warn`)

## F4 CI 新步驟少了鄰居 code-loop gate 步驟的 rc 攔截與 ::error:: 標注

severity: minor
blocking: 否 —— 同一個 job 裡緊鄰的「code-loop gate」步驟(`.github/workflows/ci.yml:98`)把 `lumos code-loop check` 包在 `|| { rc=$?; ... echo "::error::..."; exit "$rc"; }` 裡,失敗時印出 GitHub Actions 看得懂的錯誤標注、並保留原始 rc;新的「note-shape gate」步驟(`.github/workflows/ci.yml:121`)直接跑 `python scripts/lumos note-shape --diff ...`,沒有任何包裝,失敗只靠 `run:` 步驟預設的非零結束碼變紅,沒有 `::error::` 訊息、沒有把 stderr 內容轉成 PR 看板可讀的標注。結果雖然一樣會讓 CI 紅,但跟緊鄰步驟的錯誤呈現慣例不一致。
引句:「python scripts/lumos note-shape --diff "$BEFORE..$SHA" --repo .」
file: `.github/workflows/ci.yml:143`
對照: `.github/workflows/ci.yml:106-114`(code-loop gate 的 `rc=$?`/`::error::` 包裝)

## F5 doctor 提醒段讀設定檔只擋「檔案本身是捷徑」,沒有覆蓋鄰居已修過的「資料夾是捷徑」

severity: minor
blocking: 否 —— `_nodehome_config` 的直讀路徑(`from_snapshot=False`)在 r2 資安席之後特別註明「整條路徑都要看:只看 config.json 本身,.lumos 資料夾是捷徑時照樣讀到外面」,並用 `p.is_symlink() or (p.exists() and p.resolve() != ...)` 同時擋檔案與資料夾兩層捷徑。note-shape 的 doctor 提醒段(`_note_shape_doctor_lines`)直讀同一支 `.lumos/config.json` 時只檢查 `cp.is_symlink()`,沒有檢查 `.lumos` 資料夾本身是不是捷徑,等於把鄰居已經修過一次的洞在新的直讀路徑上重開一次。此段只影響 doctor 的提醒文字(不擋提交/推送,因為真正的擋是走 `_nodehome_reader` 讀快照那條路),風險小,列 minor。
引句:「if cp.is_file() and not cp.is_symlink():」
file: `scripts/lumos:23738`
對照: `scripts/lumos:22260`(`_nodehome_config` 對「.lumos 資料夾是捷徑」的註記與判斷)

## 逐問小結

第1問 對齊:新碼跟 cmd_home_check 一樣直接寫進 `scripts/lumos`、沒有另開模組或層級,呼叫方向也一致——兩支 hook 都是「bash 掛鉤 subprocess 呼叫 lumos 子指令」,CI 也是同一個 job 裡加一個等重的 step,沒有出現繞過 CLI 直接 import 內部函式之類的跨層直呼。
file: `scripts/lumos:23327`(cmd_home_check)對照 `scripts/lumos:23790`(cmd_note_shape);`scripts/hooks/pre-commit:124`對照`:133`;`scripts/hooks/pre-push:236`對照`:247`;`.github/workflows/ci.yml:98`對照`:121`

第2問 部分對齊(細節見 F3/F4/F5):子指令命名、argparse 註冊、rc 語意(0 通過/1 擋/2 用法錯)、`--staged`/`--diff`/`--repo` 三旗標命名、`_KNOWN_GATES`/`HELP_WHEN` 條目寫法、`LUMOS_SKIP_NOTE_SHAPE` 跟已有的 `LUMOS_SKIP_LINT_NEW` 同一種命名慣例、doctor 段落包 try/except 不讓一段壞掉拖垮整份健檢(這條完全對齊 doctor 既有慣例),這些都跟鄰居一致。治理帳寫入覆蓋範圍、CI 步驟的錯誤標注、設定檔捷徑防護三處跟最近的鄰居有落差,見 F3–F5。
file: `scripts/lumos:32309`(note-shape 的 argparse 註冊)對照`:32302`(home 的);`scripts/lumos:23807`(LUMOS_SKIP_NOTE_SHAPE)對照`:21540`(LUMOS_SKIP_LINT_NEW);doctor try/except 段 `scripts/lumos:998-1003`對照文件裡同款寫法(如 `scripts/lumos` 內多處「健檢一段壞了不能拖垮整份」的 except Exception)

第3問 部分對齊:`_node_code_ref_tokens` 加 `bare_text`/`anchors`/`keep_fences`/`pins`/`singles` 關鍵字參數且預設值維持原行為、`_nodehome_golive`/`_nodehome_clamp_base` 加 `mark=None` 參數、`_nodehome_merge_wrote_new_lines` 拆出 `_merge_new_lines` 三處,做法都是「延伸既有共用函式、預設不變」,完全對齊本次 diff 自己在別處立下的擴充慣例;但 F1(新程式檔喚醒舊引用改用 git grep)與 F2(frontmatter 判區塊不借用 split_frontmatter/TOP_KEY_RE)是實質的第二種做法,已經個別列為 major。
file: `scripts/lumos:19869`(`_node_code_ref_tokens` 簽名加參數)對照`scripts/lumos:22913`(`_nodehome_golive` 加 `mark` 參數)

不對齊共 5 條,其中 major 2 條
