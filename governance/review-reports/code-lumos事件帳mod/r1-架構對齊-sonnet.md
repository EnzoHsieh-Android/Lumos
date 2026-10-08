severity: major

整體判斷:分層(Q1)大致對得上計劃;但外掛重寫了三條 Python 端已有的規則(圖譜判定、主 checkout 判定、會談編號),其中只有 .gitignore 內容有守衛(S9),另外三條沒有。

## Q1 分層與依賴方向:基本一致
- 外掛只寫塊檔,Python 端 `_events_read` 只讀,方向單向,沒有跨層直呼。核心邏輯 `createLedger` 靠注入的 `Io` 與引擎隔開,引擎掛鉤(`$` 與 `on(...)`)只在 `makeIo` 和 `register`。這跟計劃〈做法〉第 2 節「核心邏輯、讀寫檔與跑指令由外面注入」一致。file: `scripts/lumos:23596`(讀取端 `_events_read`,只讀不寫)。
- 事件欄位 `v/ts/session/agent/worktree/ev` 與計劃〈做法〉第 1 節表一致,`ev` 不用 `kind` 也照計劃。`ts` 用 `toISOString()` 帶 Z,讀取端沒有解析 `ts`(`scripts/lumos:23654` 只原樣取出),不衝突。
- 塊檔名(13 位毫秒加 8 位隨機加 `.jsonl`)和讀取端 `glob("*.jsonl")` 依檔名排序相容。file: `scripts/lumos:23596`。

### F1 圖譜判定在外掛重寫一份,沒有守衛
severity: major
blocking: 是 — 兩種語言各寫一份 `_vault_in` 的規則,判錯會讓整份事件帳整個被略過,而 S9 沒有任何一條比對它
引句:「// 跟 lumos 的 _vault_in 同三種:docs/*-knowledge/、docs/knowledge/、頂層就是獨立 vault」
佐證:file: `scripts/lumos:22379`(`_vault_in` 本體)對 patch 行 509(`hasVault`)。
- 規則目前三種一樣。
- 細節差異:Python 的 `is_dir()` 會跟著連結走,TS 的 `kind === 'dir'` 對連結資料夾 ⚠ 不一定為真(要看引擎 `$.fs.list` 怎麼標連結)。
- 守衛缺口:`t_ledger_plugin_files_valid`(`scripts/test_lumos.py`)只比對 .gitignore 內容、`EVENTS_REL`、寫檔位置,沒有比對 `hasVault`。事件帳模組是否有被 `ledger.test.ts` 蓋到,本審沒有逐項核對 ⚠。
- Python 端若改 `_vault_in`(例如新增 vault 佈局),外掛不會被擋。

### F2 主 checkout 判定在外掛重寫一份,細節已不同,沒有守衛
severity: major
blocking: 是 — 兩邊對「哪裡是主 checkout」的規則已有差異,寫入端與讀取端可能落在不同資料夾(讀不到)
引句:「const main = common.endsWith('/.git') ? common.slice(0, -'/.git'.length) : top」
佐證:file: `scripts/lumos:23552`(`_events_root`)對 patch 行 541。
- Python:`common.name == ".git"` 且 `common.parent.is_dir()` 才取上一層,否則退回傳入的 root。
- TS:只看 `endsWith('/.git')`,沒有 `is_dir` 檢查,退回的是 `top`。
- 兩邊 git 逾時都是 3 秒,一致。
- 沒有測試或筆記規則讓兩邊對得上。
- Python 端 `_events_root` 的 root 引數可能是子目錄解析後的結果,「退回 root」與「退回 top」是否等價,需要跑一次才知道 ⚠。

### F3 會談編號規則只靠註解宣稱「同一條」,沒有守衛
severity: major
blocking: 是 — 照嚴重度錨,「外掛重寫一份 Python 端已有的規則、且沒有守衛讓兩邊同步」就是 major;現在正規式雖逐字等價(JS 的 `$` 不像 Python `re.match` 會放過結尾換行),但沒有任何東西盯著,所以不因「改動小」降級
引句:「const SESSION_RE = /^[A-Za-z0-9][A-Za-z0-9._-]*$/ // 跟讀取端 _EVENTS_SESSION_RE 同一條」
佐證:file: `scripts/lumos:23565`(`_EVENTS_SESSION_RE`)與 `scripts/lumos:23777`(`fullmatch` 使用處)對 patch 行 485。
- `grep` 全 repo 找不到任何測試同時引用兩個正規式。
- 這正是「寫入慣例不等於讀取保證」的類型:讀取端改嚴,外掛仍寫出被讀取端略過的資料夾。

### F4 錯誤吞掉的方式跟既有 hook 不完全一致
severity: minor
blocking: 否 — 結構是 fail-open,跟 hook 事件帳的原則一致,只是失敗不留痕
引句:「} catch { /* 觀察壞掉不能影響本業 */ }」
佐證:file: `scripts/hooks/claude/_hookevent.py:49` 的 `record` 與 `scripts/hooks/claude/_hookevent.py:19` 的規則 2「逾時與例外各記成不同的 kind,不得算成跑過」。
- 外掛的 `record`、`onPrompt`、`onTurnStart`、`onTurnEnd`、`onEnd` 一律靜默 `catch {}`,沒有任何痕跡。
- 只有「寫塊失敗」會在下一塊補 `ledger_error`;判定 `temp` 或 `$.session.id()` 失敗等情況沒有 `ledger_error`。
- Python 既有做法是「失敗也要能被看見」(分 kind)。
- 計劃有 `ledger_error` 欄位,但範圍只寫「上一次寫塊失敗」,所以結構上不算違計劃,只是比既有慣例少一層可觀測性。

### F5 寫入端沒有 Python 端的「上層連結就拒用」檢查
severity: minor
blocking: 否 — 讀取端 `_events_read` 已對連結拒讀,外掛即使寫到連結下也不會被讀出來,影響是資料寫到 repo 外而不是讀錯 ⚠
引句:「await io.write(`${dir}/${b.session}/${name}`, lines.map(l => JSON.stringify(l)).join('\n') + '\n')」
佐證:file: `scripts/lumos:31493`(`_note_audit_safe_dir`,.gitignore 做法借用的對象)與 `scripts/lumos:23596`(讀取端 `is_symlink` 檢查)。
- .gitignore 內容有借 `_note_audit_work_dir`(S9 有守衛),但「資料夾或任一層是連結就整個拒用」那半沒借。
- 外掛端是否能偵測連結取決於引擎 `$.fs` 有沒有提供,審查時沒查到 ⚠。

不對齊共 5 條,其中 major 3 條
總結:最嚴重 major,blocking 3 條
