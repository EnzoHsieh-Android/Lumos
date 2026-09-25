severity: blocker

## F1 S3 重用 --touched-from 會把 CI 既有的預告合約全擋守衛悄悄軟化成只提醒
- 情境:實作照 S3 字面做,在 CI 算出「起點到本次提交」的碰到清單,交給 `doctor --touched-from`。這個旗標是既有單一參數,不是這次新開的——`_read_touched_list` 的說明寫死「沒給=None(代表不收窄、照舊全擋)」,CLI `--touched-from` 的 help 也寫「給了它,預告合約逾期那一段就只擋這次碰到的;不給=擋全部(CI 走這條)」。現在 CI 呼叫 `doctor --ci` 完全沒帶這個旗標,所以預告合約逾期那段在 CI 目前是「全部擋」。S3 一旦把這個旗標接上 CI,`touched` 不再是 None,既有那段預告合約逾期檢查會自動從「全部擋」變成「只擋碰到的、其餘只提醒」——這是對一個已經上線的守衛的行為改變,不是這次要做的新功能,但沒有任何條款、回退節或誠實界線提到這個副作用,回退節寫的「拔掉那段呼叫與 CI 的清單參數」也沒說要連帶處理這個。
- 引句:「CI 應以起點到本次提交的改動算出碰到的筆記清單並交給健檢 [test:t_ci_passes_touched_notes_to_doctor]」
- file: `scripts/lumos:974-976`(`_read_touched_list` 說明「沒給=None(代表不收窄、照舊全擋)」)
- file: `scripts/lumos:30353-30356`(`--touched-from` help:「不給=擋全部(CI 走這條)」)
- file: `.github/workflows/ci.yml:97`(現況 `python scripts/lumos doctor --ci`,不帶 `--touched-from`)
- file: `scripts/lumos:2331`(`_guard_touches(_gn, env, touched)`,同一個 `touched` 變數同時餵給預告合約段與這次要新增的 lint 錯誤段)
severity: blocker
blocking: yes

## F2 「跟每支檔有家的讀法一致」誇大了可重用程度,Note 組裝要另寫
- 情境:做法二說提交前 lint 改讀提交索引,「跟『每支檔有家』的讀法一致(它的讀取層已經有現成函式)」。但 cmd_lint 吃的是 `Note`(`.fields`/`.lint`/`.fm_lines`/`.block_keys`),這些全部由 `load_vault` 從磁碟讀進來、跑 `parse_frontmatter` 產生;每支檔有家用的 `_nodehome_reader` 只回傳 bytes,配套的 `_nodehome_parse_note` 把那些 bytes 轉成完全不同形狀的輕量 dict(`type/status/about/resp/regen/sig/text`),不含 `.lint`(格式指紋)、`.fm_lines`(decisions 結構檢查要用)、`.block_keys`。cmd_lint 裡的決策結構檢查、Check J/Check R/Check U、aliases 判斷全部要讀這幾個欄位——照字面重用 `_nodehome_reader` 只解決「讀到 bytes」這一步,把 bytes 組回一個 cmd_lint 能吃的 Note 是全新程式碼,不是「現成函式」就能接上。
- 引句:「提交前掛鉤跑 lint 時,讀的是這次要提交的內容(提交索引),不是磁碟上的檔——跟『每支檔有家』的讀法一致。」
- file: `scripts/lumos:315-317`(`class Note` 的 `__slots__` 含 `fields/block_keys/fm_lines/targets/lint/mtime`)
- file: `scripts/lumos:320-357`(`load_vault` 唯一組出 `Note` 的地方,全部走 `p.read_text(...)` 讀磁碟)
- file: `scripts/lumos:21678-21730`(`_nodehome_reader`/`_nodehome_parse_note`,回傳的 dict 沒有 `.lint`/`.fm_lines`)
- file: `scripts/lumos:4790-4798`(`cmd_lint` 開頭就是 `n = env.notes[rel]`,直接假設 `n` 是磁碟建出來的 `Note`)
severity: major
blocking: yes

## F3 手動 lint 讀磁碟 vs 提交前 lint 讀索引,spec 沒定義用什麼介面區分
- 情境:鐵則二明講「手動跑 `lumos lint <節點>` 維持讀磁碟」,但提交前掛鉤(Gate L)現況就是直接呼叫同一支 `lumos lint "$rel"`,沒有任何旗標。spec 全篇沒有一句提到要加 `--staged`/`--from-index` 這類旗標來分流兩種模式——如果照字面把 `cmd_lint` 改成「有 git 提交進行中就讀索引」,手動跑 `lumos lint <節點>` 在提交過程中(例如 git rebase/commit 期間手動核對)行為會被悄悄改掉,違反鐵則二;如果不改,Gate L 就沒辦法讀到索引內容,S4 就沒有實作路徑。這個介面缺口三個月後照做的人自己得決定,不同人會決定出不同旗標名字,跟 `home check --staged` 這個現成先例(`scripts/hooks/pre-commit:124`)對不上也不會被任何機制抓到。
- 引句:「手動跑 `lumos lint <節點>` 維持讀磁碟(那是在看自己正在寫的東西)。」
- file: `scripts/hooks/pre-commit:103`(Gate L 現況呼叫:`"$CC_PY" "$REPO_ROOT/scripts/lumos" lint "$rel"`,無旗標)
- file: `scripts/lumos:31293`(`cmd_lint` 唯一呼叫點,`args.note` 直接傳,CLI 沒有第二個模式參數)
- file: `scripts/lumos:31240`(`home check --staged` 已有的旗標命名先例,S4 沒有引用它)
severity: major
blocking: yes

## 實務隱患逐類答
- 金流:無——這批規則只碰知識庫筆記格式,不碰任何交易路徑。
- 對外送出:無——lint/doctor/CI 都是內部檢查,不觸發對外請求。
- 不可逆:無——擋的是 push/commit,回退節已寫清楚三處都是可獨立拔掉的新增段落/旗標,沒有刪資料或不可逆寫入。
- 守衛面:有,即 F1——這次改動會讓 CI 既有的「預告合約逾期」守衛從全擋變成只擋碰到的,而這正是守衛面風險最該關注的那種「悄悄變鬆」,且沒有被 spec 自己列進實務隱患或誠實界線。

## 其餘段落已讀、無 finding
「一句話」「順手修」「不在本案範圍」「S1/S2/S5–S11/S10 條款文字本身」「誠實界線」都逐句讀過,S5(status 必填)、S6(日期格式)、S7(decisions valid)、S8(about_code 版控)、S10(set responsibility 長度)對程式現況的描述都用 Grep/Read 核對屬實(見前掃 r1-intake.md 的 HIT-4 與本次額外核對的 `_ENUM_CUTOFF`/`QUOTED_DATE_RE`/`cmd_set` 無長度檢查等),沒有再發現新的現況錯誤。派工詞提到「附上的節點逐條判」,但 `Projects/筆記欄位關卡補齊_計劃.md` 本檔內容與凍結快照逐字一致,尾端沒有附加任何合約/事故節點,無可供逐條判的清單。

最嚴重 severity: blocker;blocking 共 3 條(F1 blocker、F2 major、F3 major)。
