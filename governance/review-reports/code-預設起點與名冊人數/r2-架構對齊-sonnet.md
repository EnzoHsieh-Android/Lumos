severity: minor

1. 說明文字還寫「兩套並存」,新入口沒補進去
severity: minor
blocking: 否
引句:「主線候選沿用推送閘的 _push_mainlines(遠端 HEAD、main/master 的 upstream、遠端 main/master),只多加本機 main/master——」
file: `scripts/lumos:47177`(`_lens_push_base`)、`scripts/lumos:47264`(`_push_range_start`)、`scripts/lumos:47235`(`_push_mainlines`)、`scripts/lumos:47394`(`_mainline_ref`)
- 這不算第三套主線判法,不構成 major。`_codeloop_default_base` 的候選清單用 `_push_mainlines`(`scripts/lumos:47229`),挑法用 `_push_pick_base`(`scripts/lumos:47346`),算法跟 `_push_range_start`(`scripts/lumos:47258`)同一條路。
- 它多出來的只有本機 main/master 這一步。這步跟 `_mainline_ref` 非 remote_only 分支(`scripts/lumos:47400`)的 `"main","master"` 退路是同一個想法。
- 但上面四處 docstring 都把主線判法寫成「`_lens_push_base`/`_mainline_ref` 一套、`_push_mainlines`/`_push_range_start` 一套,兩套並存」,收斂路指向 Issues/推送前其他閘的範圍在合過主線時會多算。
- 現在有第三個呼叫入口,而且是第一個「推送前、尚無推送遠端資訊」就用 `_push_mainlines` 的地方。下一個改這四支的人讀了這些說明,會看不到這個入口。
- 建議在 `_push_mainlines` 和 `_mainline_ref` 的 docstring 補一句「手動 `code-loop check` 預設起點(`_codeloop_default_base`)也走 `_push_mainlines`,只多加本機 main/master」。
- 至於新加的手冊段落說「不另立第三套」,以重用候選清單與挑法來說成立。

2. 找上游遠端的寫法是就地再寫一份(⚠ 判不準)
severity: minor
blocking: 否
引句:「up = _lens_git(repo_root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")」
file: `scripts/lumos:50953`;對照 `scripts/lumos:34000`、`scripts/lumos:42396`
- repo 裡沒有「取目前分支的上游遠端」的共用小函式。`scripts/lumos:34000` 是同一條 rev-parse,但取整個 ref 而不是遠端名,fallback 用 `for-each-ref`。`scripts/lumos:42396` 另用 `git remote` 取全部遠端。
- 新寫法是 rev-parse 取上游、`split("/",1)[0]` 取遠端名、再 fallback 到 origin。這跟既有各處同一種形狀(`_lens_git` 加 rev-parse),所以不算引入新做法。
- 但推送閘的遠端是由掛鉤的 `--push-remote` 明確傳入(`scripts/lumos:47233`),這裡改成自己推斷。這是預期差異,因為手動檢查沒有推送參數。
- 若之後第三處也要「取上游遠端」,值得抽成共用函式。現在先記一筆即可。

3. 同一個判定函式內,預設起點與表態範圍用兩種主線判法(⚠ 判不準)
severity: minor
blocking: 否
引句:「mb = _codeloop_default_base(repo_root)」
file: `scripts/lumos:51006`(新)對照 `scripts/lumos:51082`(`_mainline_ref(repo_root)`)
- `_codeloop_guard_verdict` 的 tier 範圍現在用 `_codeloop_default_base`。同一函式後面算表態適用範圍(3.5 步)仍用 `_mainline_ref(repo_root)`。
- 兩者在常態下結果相同,因為都優先看 `main@{upstream}`。本機 main 落後、或有多個遠端時,可能算出不同的起點,於是 tier 範圍與表態範圍不一致。
- 這是原本就存在的並存,新改動沒有讓它變糟。但因為 `_codeloop_default_base` 的出發點就是「固定順序取第一個會算錯」,而 `_mainline_ref` 仍是固定順序取第一個,同一個病根在 3.5 步還留著。
- 判不準它會不會實際出錯,所以標 ⚠。建議在手冊段落的 WHY 或 Issue 記一句這個殘留。

手冊段落位置:
- 「手動 code-loop check 的預設起點」放在 `Systems/pitfalls-code-loop.md` 末尾,新開 H2。這個節點是 `_codeloop_guard_verdict` 的家,位置合理。
- loop-convergence-recording.md 的「loop next 人數」段放在文末新 H2,跟該檔既有格式一致。
- SKILL.md 步驟 1 新增的「首輪派審前先自己變異」跟本次兩個功能無關,屬於範圍外夾帶,不是寫法問題。

總結:最高等級 minor,blocking 共 0 條
