severity: major

## 1. 分層與依賴方向
對齊。新外掛 lumos-context 與 lumos-ledger 同層(mods/claude/<名>/hooks/ 加 .claude-plugin/plugin.json),Python 端只讀事件帳,沒有跨層直呼。seat-check 讀事件帳走既有讀取端,`--events` 與 `--ledger` 分開也符合現況。
對照:file: `mods/claude/lumos-ledger/hooks/register.ts:1`、file: `scripts/lumos:23685`(`_events_read`)、file: `scripts/lumos:23490`(`cmd_seat_check`)。
有一處要補:計劃要把 handoff 改走統一的取值函式,現況只有 file: `scripts/lumos:46262` 一處直接讀 `os.environ`,改法結構上沒問題。

## 2. 命名與錯誤處理
大致對齊,有一條小差異(F3)。seat-check 恆回 0、輸入壞損回 2 的慣例見 file: `scripts/lumos:23499`。計劃寫「恆回 0」,沒交代輸入壞損(例如會談編號格式不合 `_EVENTS_SESSION_RE`)是否沿用 rc2。外掛安裝清單沿用 `_LUMOS_PLUGINS`,各支獨立失敗不影響下一支,跟 file: `/Users/enzo/harness/lumos-toolchain-seat-guard/scripts/lumos:22004` 一致。

## 3. 第二種做法
有兩處(F1、F2)。

### F1 新增「已退役外掛」清單
severity: major
blocking: 否 — 有鄰居做法(`_RETIRED_CLAUDE_HOOKS` 退役 hook 的模式)可類比,不是同功能重複,但外掛端沒有先例、seat-guard 分支也沒有,屬新做法,建議編排者確認要不要現在引入。
引句:「另加「已退役外掛」清單:在裡面的名字已裝就移除。回退一個外掛 = 把它從清單搬到已退役清單。」
說明:seat-guard 分支只有 `_LUMOS_PLUGINS`(file: `/Users/enzo/harness/lumos-toolchain-seat-guard/scripts/lumos:21887`),沒有外掛退役清單;現有的退役機制是 hook 檔專用的 file: `scripts/lumos:21690`(`_RETIRED_CLAUDE_HOOKS`,seat-guard 分支)。外掛退役屬新增。⚠ 判不準這算不算「鄰居已有同功能」,交編排者。

### F2 兩個環境變數配對決定會談編號
severity: major
blocking: 否 — 鄰居(handoff)只靠單一 `CLAUDE_CODE_SESSION_ID`,沒有「官方變數加外掛變數」的第二來源先例;但計劃已寫明理由與併發隱患並要求實測,不是無根據。
引句:「lumos 取會談編號時,只有兩者都不空、而且自己環境裡的 `CLAUDE_CODE_SESSION_ID` 等於 `LUMOS_SESSION_BASE`,才採用 `LUMOS_SESSION_ID`」
說明:現況取會談編號只有 file: `scripts/lumos:46262` 一種做法。此計劃新增第二個來源與配對比對規則。事件帳外掛本身也用 `$.session.id()` 命名會談資料夾,所以外掛與 Python 會形成兩套會談編號來源,計劃只靠實測第 ⑤ 步對齊。⚠ 交編排者確認可接受。

## 3 補充(minor)
### F3 既有外掛檔守衛測試會與新外掛衝突,計劃沒列要改
severity: minor
blocking: 否 — 結構正確,只是漏列既有測試與市集檔的調整,seat-guard 分支已有現成做法可抄。
引句:「[S10] 當 Python 端掃 `lumos-context` 的原始碼,應只出現 `LUMOS_SESSION_ID` 與 `LUMOS_SESSION_BASE` 兩個 `$.env.set`」
說明:file: `scripts/test_lumos.py:71541`(`t_ledger_plugin_files_valid`)寫死「市集只列 lumos-ledger 一個外掛」,file: `.claude-plugin/marketplace.json:4` 也只列一支。加第二支外掛必須放寬這條斷言並改市集檔;seat-guard 分支已另有 `t_guard_plugin_files_valid`(file: `/Users/enzo/harness/lumos-toolchain-seat-guard/scripts/test_lumos.py:70289`)。計劃的做法要點與條款都沒提這一步,`.claude-plugin/marketplace.json` 也沒進落點。

## 4. 落點合不合理
大致合理,一處缺漏(併入 F3)。
- 新開 `Systems/lumos-context` 管新外掛:合理,既有事件帳節點 about_code 只列 lumos-ledger 的檔(file: `docs/lumos-toolchain-knowledge/Systems/lumos事件帳.md:8-14`),新外掛的檔不該塞進去。
- `lumos-cli-lifecycle` 放外掛清單:合理,外掛安裝移除就寫在那裡(file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:155`)。
- `design-loop` 放 `seat-check --events`:合理,收貨三道在那裡(file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:60`)。
- 缺漏:`.claude-plugin/marketplace.json` 的家是事件帳節點(about_code 已列),新增第二支外掛的條目要寫進哪一篇,計劃沒說;`lumos enforcement` 逐支列外掛那一列落在哪一篇也沒列。⚠ 交編排者補。

總結:最嚴重 major,blocking 0 條
