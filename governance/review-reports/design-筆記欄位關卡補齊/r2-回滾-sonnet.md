severity: blocker

## F1 開關只關得掉推送前那一段,提交前 lint 與 `lumos set` 長度擋沒有任何開關能關

severity: blocker
blocking: yes

「回退」節聲稱靠設定檔就能不改程式收手:
引句:「在自己的 `.lumos/config.json` 把 `note_lint.gate` 設成 `warn` 或 `off`,不必改程式、不必等更新。」

但這個開關只接在「一、推送前健檢加『筆記格式』段」(doctor 推送前/CI),`note_lint.gate` 這個判斷只出現在做法一裡:
引句:「擋不擋看專案開關 `.lumos/config.json` 的 `note_lint.gate`」

做法二新增的五條 lint 錯誤等級規則(S6–S10)完全沒提到要看任何開關,例如:
引句:「若 system、project、verification、issue 筆記沒有填 status,則 lint 應報錯誤並講允許的值」

而這五條規則是加進 `cmd_lint` 的錯誤清單(`errs = list(n.lint)`),`scripts/lumos:4790` 起的 `cmd_lint` 目前完全不讀 `.lumos/config.json`、沒有任何 gate 判斷分支;`scripts/hooks/pre-commit:103` 對每個 staged 的圖譜 `.md` 檔直接呼叫 `lumos lint`,rc≠0 就 `lint_fail=1` 硬擋(`scripts/hooks/pre-commit:108`),中間沒有讀 `note_lint.gate` 或任何開關的邏輯。也就是說:一旦這批規則上線,任何消費專案只要提交一篇缺 `status`、日期格式錯、`decisions.valid` 不是布林、`about_code` 沒進索引、或「_計劃」筆記沒填 `lands_in` 的筆記,提交就會被擋——把 `note_lint.gate` 設成 `off` 或 `warn` 對這一層完全無效,因為這一層根本沒讀這個開關。

做法三的 `lumos set responsibility` 長度擋同樣沒有開關:
引句:「去掉空白後不到 10 個字就擋、檔案不動(現在只有新開節點時要求)。」
這條也沒有 gate 判斷,設 `note_lint.gate=off` 一樣關不掉。

「回退」節自己其實也承認光改設定檔不夠,要真正整個撤掉得還原提交:
引句:「要整個拿掉就還原這批提交(健檢新段、lint 新規則、set 的長度檢查各自獨立)。」

但這句話跟同一節開頭「不必改程式、不必等更新」放在一起,沒有講清楚「不必改程式」只涵蓋做法一(推送前段),做法二、三這兩個實際上會擋住每一次提交的新規則,唯一的關法是 revert 或 `git commit --no-verify`(而 --no-verify 只是繞過 hook,commit 內容仍不合規、CI 那邊還是可能再擋一次,因為 CI 讀的是 `doctor --ci`,而 doctor 的「筆記格式」段本身確實有掛 `note_lint.gate`——但那是 doctor 重跑同一批 lint 錯誤等級規則,gate 只決定「有錯要不要讓 doctor/CI 退出碼變非 0」,不影響 pre-commit 那一層本來就已經擋下的事實)。上線隔天要撤的人如果只照「回退」節第一句做(把 gate 設成 warn/off),會誤以為所有新規則都關掉了,實際上提交路徑上的五條 lint 規則與 `lumos set responsibility` 檢查完全沒受影響,仍在正常擋人。

## 已讀、無 finding

- 修掉的現存 10 篇違規不需要回退的判斷(「已修的 10 篇筆記不用退」)——這批只是補欄位,即使規則全撤也不影響筆記內容正確性,沒有找到反例。
- 治理帳寫入條件(「開關是 warn 時不算問題、不寫」)與現有 `_gate_event_or_warn` 機制(`scripts/lumos:933` 起)同構,沒看到會讓既有治理帳讀取端(`governance/replay`、`governance/eval`)因為新 gate 名稱而炸掉的證據,不標。
- `lands_in` 指到的兩個節點 `Systems/lumos-cli-write`、`Systems/lumos-cli-read` 確實存在(`docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md`、`docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md`),回滾這份 spec 本身不會留下壞連結。

---
最嚴重 severity: blocker;blocking 共 1 條。
