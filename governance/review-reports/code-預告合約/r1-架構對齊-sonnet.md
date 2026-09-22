severity: blocker

## 總評:作者宣稱「九成是讀節點加比對既有判定結果,不需要新的判定引擎」還成不成立

不成立。至少兩處新寫了跟既有判定引擎平行的第二套邏輯,而不是延伸既有的:
`cmd_context` 裡掃預告合約的迴圈重刻了 `extract_contracts()` 已經在做的事(F2);
`_guard_planned_line` 是一支全新的「找 KEY 行」引擎,卻沒有比照 `cmd_guard_bind`/`cmd_guard_audit`
既有引擎的防呆(命中多條就擋),這個缺口造成 F1 那個會噴資料的 bug。

## F1 `_guard_planned_line` 沒有既有引擎的「命中多條就擋」防呆,settle/abandon 會靜默改錯 KEY 行

severity: blocker
blocking: yes

觀察到什麼:既有兩支做「在功能節點裡找到某條 KEY 行」的指令——`cmd_guard_bind`、`cmd_guard_audit`——
都會在迴圈裡累計命中次數,命中一條以上就擋下並印「同時對到好幾條 KEY 行,分不清是哪條」
(`scripts/lumos:10869`、`scripts/lumos:11396` 一帶,兩處都有 `target_idx is not None` 的擋)。
這批新增的 `_guard_planned_line`(被 `cmd_guard_settle`、`cmd_guard_abandon` 共用)做的是同一件事——
拿一段子字串去比對功能節點裡的 KEY 行——卻整段重寫成一支沒有防呆的新引擎:

引句:「if PLANNED_RE.match(s) and claim_sub in s:」
引句:「return lines, i, e」

呼叫端把比對用的子字串砍到只剩 12 個字:

引句:「lines, idx, _e = _guard_planned_line(env, home_rel, claim[:12])」

而一個功能節點本來就允許掛多條 ★INVARIANT★(這是這個 repo 的常態用法,不是特例),同一個節點
先後預告兩條相關的合約、claim 前 12 個字重疊,是完全合理的使用情境——恰好是這個節點的存在理由
(要能同時追蹤好幾條「以後要做」的合約)。

怎麼重現(唯讀在 /tmp 自建 vault,不動 lumos-toolchain 的 git 狀態):

```
lumos guard plan Systems/Pay "大額退費要人工核可" \
  --plan Projects/退款_計劃 --phase "Phase 4" --due 2099-12-31 --why "下游介面還沒定案" --owner enzo
lumos guard plan Systems/Pay "大額退費要人工核可,而且要留存證據以便稽核" \
  --plan Projects/退款_計劃 --phase "Phase 5" --due 2099-11-30 --why "稽核流程還沒定" --owner alice
```

此時 Pay.md 摘要裡有兩行(新插入的在最上面):

```
KEY:★INVARIANT-PLANNED★ 大額退費要人工核可,而且要留存證據以便稽核 [watch:...-而且要留存證據以便稽核] [due:2099-11-30]
KEY:★INVARIANT-PLANNED★ 大額退費要人工核可 [watch:...大額退費要人工核可] [due:2099-12-31]
```

接著只轉正第一次建的那條(短 claim):

```
lumos guard settle "Verification/2026-09-22_大額退費要人工核可" --test t_pay_large_refund_needs_approval
```

指令回報成功:「✓ 轉正:Systems/Pay.md 的預告行已換成正式合約並綁上 [test:...]」,守衛節點也真的被
`cmd_set` 成 `status: pass`。但實際打開 Pay.md,壞的結果是:

```
KEY:★INVARIANT★ 大額退費要人工核可 [test:t_pay_large_refund_needs_approval]
KEY:★INVARIANT-PLANNED★ 大額退費要人工核可 [watch:...大額退費要人工核可] [due:2099-12-31]
```

兩件事同時錯:①真正該被轉正的那行(第二行,alice 的合約以外那條)**完全沒被動到**,還留在
`★INVARIANT-PLANNED★`,即使它的守衛節點已經被標成 `pass`——查那篇節點的人會看到「已生效」
的驗證紀錄,但功能節點裡對應那行合約其實還沒轉正,兩邊對不上。②alice 那條完全不相干、還在
待完成狀態的合約(`...-而且要留存證據以便稽核.md` 至今仍是 `status: pending`)被整行改寫消失——
它的 KEY 行憑空變成別的合約的正式合約行,alice 的守衛節點從此變成孤兒:`verified_by` 還連著它、
節點本身還在 `pending`,但功能節點裡已經找不到任何一行提到它,`lumos context Systems/Pay` 再也不會
顯示這條合約預告過,也不會顯示它逾期(它明明還沒做)。

為什麼是 bug 不是風格:這不是「少防一種輸入」的邊界案例,是這個功能設計上就要支援的常態
(一個功能節點掛好幾條合約),而且後果是靜默資料損毀——不是報錯、不是擋下,是印出「✓ 成功」
之後,圖譜裡兩條記錄都變成假的(一條假裝轉正、一條的預告行憑空消失)。`cmd_guard_abandon`
共用同一支 `_guard_planned_line`(`scripts/lumos:10796`),棄置時會踩到一模一樣的問題,而且
它自己的寫入自驗更弱:`atomic_write_verify` 的檢查只看 `claim[:12] not in str(f.get("summary")...)`
(`scripts/lumos:10800`)——只要「這 12 個字不見了」就判定成功,連刪錯行都驗不出來,因為刪錯行
一樣會讓這 12 個字從檔案裡消失。

修法方向(不是我的任務,但講清楚為什麼可修):照抄 `cmd_guard_bind`/`cmd_guard_audit` 既有的
「累計命中、>1 就擋,請給更精確的片段」防呆,而且比對子字串不要砍到 12 字或改成比對
`[watch:守衛節點全名]` 這種天生唯一的 token(這個 repo 已經在用 `watch:` 當守衛節點的唯一參照)。

## F2 `cmd_context` 印預告合約那段重刻了 `extract_contracts()` 已經在做的掃描邏輯

severity: major
blocking: yes

觀察到什麼:這個 repo 已經有一支專門「從 summary 逐行掃 KEY 行、用正則抓標記後的文字」的共用函式
`extract_contracts(note)`(`scripts/lumos:3672`,現有 ~18 處呼叫點都靠它,不是只有一處在用),簽名是
「從 summary block 的 KEY 行抽標準格式」。這批在 `cmd_context` 裡印「預告中的合約」那段,沒有延伸
這支函式(例如多回一個 `planned` 清單),而是在 `cmd_context` 內部重新寫一模一樣形狀的迴圈:

引句:「_psum = n.fields.get("summary")」
引句:「_m = PLANNED_RE.match(_l.strip())」
引句:「_pl.append(_m.group(1).strip())」

跟 `extract_contracts` 現有邏輯逐行對照(`scripts/lumos:3675`-`3686`):一樣是「先判斷 summary 是不是
字串、逐行 split、strip、拿正則 match、取 group(1) strip 後收進清單」,連變數用途都一一對得上,唯一
差別是換了一個正則(`PLANNED_RE` 換 `INVARIANT_RE`/`DEBT_RE`)跟只在 `cmd_context` 這一處用。

為什麼是 bug 不是風格:`extract_contracts` 目前有 ~18 個呼叫點(impact 計算、search、audit 相關流程
等等),這批新增的「預告中合約」邏輯只長在 `cmd_context` 一處,其他 17 個原本呼叫 `extract_contracts`
的地方完全不知道預告合約的存在——不是它們刻意排除,是設計上這份資訊被鎖死在 `cmd_context` 內部。
之後任何一個原本靠 `extract_contracts` 判斷「這篇有沒有合約」的地方(例如
`scripts/lumos:12136` 的 `lumos query --contract`),永遠看不到預告中的合約,而且下一個人改
`extract_contracts` 時也不會意識到還有一份平行的複製要一起改——這正是「跨層直呼/自己再刻一份
已有的工具函式」在這個 repo 的既有慣例裡明確要避免的那種寫法。

## F3 新欄位 `due`/`owner`/`phases`/`guards` 沒登記進 `_KNOWN_FRONTMATTER_KEYS`,lint 對每一篇守衛節點都給錯誤提示

severity: major
blocking: yes

觀察到什麼:這個 repo 有一份明確用來做「開頭欄位是不是工具認得」檢查的清單
`_KNOWN_FRONTMATTER_KEYS`(`scripts/lumos:4569`),旁邊的沿革註解記著每次加欄位都要登記進來
(`about_code_stamp`/`responsibility`/`lands_in`/`plan_risk`/`door` 都各自登記過)。這批新增了
四個守衛節點專用的欄位並直接手刻寫進新檔:

引句:「f"due: {due.strip()}\n",」
引句:「f"owner: {owner.strip()}\n",」
引句:「f"{GUARD_MARK_FIELD}:\n", f"  - {rel[:-3] if rel.endswith('.md') else rel}\n",」

但沒有把 `due`、`owner`、`phases`、`guards` 這四個新鍵加進 `_KNOWN_FRONTMATTER_KEYS`(該常數本身
不在這次 diff 的改動範圍內,對照 `scripts/lumos:4569`-`4577` 目前的清單可以確認)。

怎麼重現(唯讀,`/tmp` 自建 vault):

```
lumos guard plan Systems/Pay "大額退費要人工核可" \
  --plan Projects/退款_計劃 --phase "Phase 4" --due 2099-12-31 --why "下游介面還沒定案" --owner enzo
lumos lint "Verification/2026-09-22_大額退費要人工核可"
```

實際輸出(四條一模一樣的假警告,每建一個守衛節點就會重複出現一次):

```
⚠ 開頭欄位有個沒見過的鍵『due』——工具不認得這個欄位,它不會被任何檢查讀到(…)
⚠ 開頭欄位有個沒見過的鍵『owner』——工具不認得這個欄位,它不會被任何檢查讀到(…)
⚠ 開頭欄位有個沒見過的鍵『guards』——工具不認得這個欄位,它不會被任何檢查讀到(…)
⚠ 開頭欄位有個沒見過的鍵『phases』——工具不認得這個欄位,它不會被任何檢查讀到(…)
0 error / 4 warning(warning 不擋,但建議順手補)
```

為什麼是 bug 不是風格:這不只是漏登記的瑣事——警告文字本身講的是假話。它說「工具不認得這個欄位,
它不會被任何檢查讀到」,但這批新增的 `_guard_nodes`/`_guard_home_of`/doctor 的 `S15` 段/
`cmd_guard_required` 全部都在讀這四個欄位,是這個功能的核心資料。凡是這個機制建出來的守衛節點,
只要有人順手 `lumos lint` 一下(既有紀律要求「寫完一篇 lumos lint <節點>」),就會看到四條指向
「加進 `.lumos/config.json` 的 extra_frontmatter_keys」的錯誤建議——這是給不知道這四個欄位
有專門檢查在讀的人一個誤導的修法。跟同一份清單裡其他欄位的既有慣例(每加一個新語意欄位就登記)
明顯相反。

## 驗過但沒發現問題的路徑

- `guard plan` 缺欄位擋下(S3)、日期格式擋下:實測正常,錯誤訊息有講清楚缺什麼。
- `guard plan` 同名節點擋下:實測正常(建立同名守衛節點會被擋,不靜默覆蓋)。
- `guard abandon` 沒簽核先擋、`signoff --ref` 之後才放行:對照 `t_guard_settle_and_abandon`
  單一預告合約的情境實測跟描述一致(見上面 F1 才會在「多條預告合約同節點」時破功)。
- `QUERY_CLOSED_STATUSES` 加入 `abandoned`、`_STATUS_ENUM["verification"]` 加入 `pending`/`abandoned`:
  跟既有「編輯既有集合常數」的慣例一致,沒有另開一份平行清單。
- `guard bind`/`guard audit`/`kill-add` 三支既有指令改摘要行時本來就沒有包 `_vault_write_lock`
  (`scripts/lumos:10870` 一帶、`scripts/lumos:11421` 一帶、`scripts/lumos:11031` 一帶皆是);
  這批的 `guard plan`/`settle`/`abandon` 一樣沒包鎖,是跟既有 guard 家族同層對照檔一致的寫法,
  不算引入新的不一致(雖然 `cmd_set`/`append`/`remove` 那條路徑有上鎖,但那是另一組指令家族的慣例)。
- `PLANNED_MARK`/`PLANNED_RE`/`WATCH_REF_RE`/`DUE_REF_RE` 的正則命名跟既有
  `INVARIANT_RE`/`DEBT_RE`/`TEST_REF_RE`/`AUDIT_REF_RE` 的命名慣例(XXX_RE 抓整行、XXX_REF_RE 抓
  `[tag:值]`)一致。
