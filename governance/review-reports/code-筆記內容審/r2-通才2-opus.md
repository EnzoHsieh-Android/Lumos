severity: minor

# r2 代碼審(修正差異)— 通才2-opus

範圍:逐 hunk 讀完 r2-delta.patch,對照 r1-intake.md 的修法清單,在自己 `git clone --shared` 的臨時複本(scratchpad/g2/repo)做探針與翻紅實驗;repo 本體沒動。相關子集 `-k note_audit`(130)、`-k decision_amend`(10)、`-k note_shape`(107)全綠。

逐條修正走過一遍、確認成立的(不另列 finding):同編號多處在 prepare 全列、batches 把同編號當成一個單位不拆份、record 用排序後的指紋清單比對(自己構造「清單只有一處、事後又加一處」,輕判定正確被拒);已收尾計劃只改名時對起點做改名偵測(拿掉那段 ② 翻紅);清單照位元組讀(CRLF 報告的表頭正則 `\s*$` 與表格行 `strip()` 都吃得掉 CR,改成位元組讀報告沒有引入新回歸);終點全 0 跳過、終點找不到 rc2;兩層略過開關只認 1(文件、掛鉤提示、CI 訊息原本就都寫 `=1`,沒有別處用「有值就略過」);decision-amend 的空行多行值、區塊清單拒絕、`git mv` 未提交的改名(把 `--cached` 改回 HEAD,⑥c 翻紅);證據行號範圍與 search 路徑不存在;doctor 刪除次數改讀遠端(改回 HEAD,⑩b 翻紅);沒有主線時 `ml` 為 None,刪除次數與事後掃描都安靜跳過,不會炸。

## F1 decision-amend 只認暫存區的改名:搬檔後只 add 新檔,已推的決策照樣被改
severity: minor
blocking: 否 — 要「一般 mv(或在 Obsidian 改名)再只 add 新檔」這種部分暫存才會漏;git mv、git add -A 都擋得住,屬修正不完整的殘餘縫
引句:「ns = _ns_git(root, "diff", "--cached", "--name-status", "-z", "-M", ref, "--", vrel)」
file: `scripts/lumos:24895`
失敗場景:決策 d1 已推到 origin/main 的 `Systems/D.md`。作者在 Obsidian 把它改名成 `New.md`(磁碟上搬檔,不是 git mv),接著 `git add docs/.../New.md`。這時暫存區裡舊路徑 `D.md` 還在,只是工作目錄刪掉了;`diff --cached ref` 看到的是「新增 New.md」,不是改名,所以 `old` 還是新路徑,遠端上找不到這個路徑,就放行改掉了已推的決策。
重現(臨時複本,借 test_lumos 的 `_na_repo`/`_nh_node` 建專案):
```
status: D docs/kg-knowledge/Systems/D.md
A  docs/kg-knowledge/Systems/New.md
cached vs ref: A	docs/kg-knowledge/Systems/New.md
worktree vs ref: R100	docs/kg-knowledge/Systems/D.md	docs/kg-knowledge/Systems/New.md
amend rc 0 ✓ decision-amend Systems/New.md d1.why_chosen 改好了(這條決策還沒推上去)
```
改法建議:比對改拿 ref 跟工作目錄比(`git diff --name-status -z -M <ref> -- <圖譜夾>`,不加 `--cached`)。上面輸出顯示這樣認得出 R100,而且 git mv 未提交的情況一樣涵蓋;或者圖譜夾裡有「工作目錄已刪、還沒暫存」的檔時直接拒絕。

## F2 新加的「還沒加進 git 就拒絕」在沒有遠端時也擋,跟 S12「沒有任何遠端應准改」相反,也沒有測試
severity: minor
blocking: 否 — 擋的方向安全,訊息也教人 git add;不過跟條款字面衝突,新筆記的正常流程會被多擋一次
引句:「raise ValueError("這篇筆記還沒加進 git(改名請用 git mv,或先 git add),確認不了它在遠端的舊路徑,不改")」
file: `scripts/lumos:24881`;`docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md:126`(S12:「沒有任何遠端應准改」)
失敗場景:專案沒設遠端,作者 `lumos new system Fresh` 後接著 `decision-add` 再 `decision-amend`,還沒 git add。這道檢查放在 `if remotes:` 之前,所以照樣拒絕。探針輸出:`P3 rc 2  擋下:這篇筆記還沒加進 git(…)不改`,當時 `git remote` 是空的。有遠端時,全新、從沒推過的筆記也一樣被擋,雖然它根本不可能已經推上去。另外把這三行整段改成 `if False:`,回歸測試照樣 19 條全綠,等於這條新拒絕沒有測試守。
改法建議:把這道檢查挪進 `if remotes:` 裡面;或者只在「圖譜夾裡有工作目錄已刪的追蹤檔」時才拒絕(跟 F1 一起處理)。加一條「沒遠端、未追蹤 → 准改」的測試。

## F3 清單寫在跟欄名同一層縮排時認不出來,decision-amend 靜默把 frontmatter 改成不合法的 YAML
severity: minor
blocking: 否 — lumos 自己的解析器本來就把這種寫法讀成空清單,lint 也不報;受害的是其他 YAML 讀者(Obsidian 屬性面板等),而且要作者手寫或用別的工具寫出這種縮排才會碰到
引句:「if k1 > k0 and not head_val:」
file: `scripts/lumos:24937`
失敗場景:YAML 允許序列跟上層鍵同一層縮排(PyYAML `default_flow_style=False` 寫出來就是這個樣子):
```
    alternatives:
    - 甲
    - 乙
```
續行迴圈遇到 `_ind == sub` 就停在 k1 == k0,所以不算「值寫在下一行起」,拒絕條件不成立。結果只換掉欄名那一行,兩個 `- ` 項目留在原地。
重現(臨時複本):
```
before | lumos: [{... 'alternatives': [], ...}] | pyyaml ok [{... 'alternatives': ['甲', '乙'], ...}]
   lint rc 0 []
amend rc 0 ✓ decision-amend Systems/D.md d1.alternatives 改好了(這條決策還沒推上去)
after | lumos: [{... 'alternatives': '只剩一個', ...}] | pyyaml ERR while parsing a block mapping
   lint rc 0 []
```
改好之前是合法的 YAML,改好之後變成解析錯誤,而 `_check` 跟 lint 都放過。這跟 r1 外家席說的「清單欄被壓成一句」是同一族缺陷,這次只修到縮排比欄名深的那一種。改法建議:欄名那一行的值是空的、而且下一個非空行是跟欄名同一層的 `- ` 開頭時,也當清單拒絕。

## F4 回歸測試有三處修正沒守到,S16 綁的測試也沒涵蓋新加的「沒抓完整歷史」
severity: minor
blocking: 否 — 修正本身我逐一走過是對的,缺的是翻紅守衛;以後有人改壞不會紅
引句:「# ① 同一小標題下一字不差的兩行:清單列每一處;判定者只看過一處時,另一處上下文不同照樣要求(輕的判定要每一處上下文都對)」
file: `scripts/test_lumos.py:49734`、`scripts/test_lumos.py:49640`
失敗場景(在臨時複本逐一改壞,跑 `-k note_audit_code_review_r1`):
- M1:record 的上下文比對改回「每個編號只取第一處」(`cur_ctx.setdefault(id, [fp])` 加上 `_note_audit_parse_list` 的 `rows.setdefault(rid, [fp])`)→ `19 passed, 0 failed`。① 的註解寫「判定者只看過一處時,另一處上下文不同照樣要求」,但 ① 只測了「兩處都在清單裡時照收」,「清單只有一處、現在多一處」這個方向沒有斷言。
- M3:`_note_audit_batches` 的判斷改回 `len(cur) >= _NOTE_AUDIT_BATCH`(同編號的幾處又可能被切到兩份)→ `19 passed, 0 failed`。沒有任何測試構造超過 150 行、切點又落在同編號兩處之間的情況;這種情況下兩份清單的指紋清單都跟現況對不上,那個編號的脈絡判定就永遠收不下。
- M7:decision-amend 的「還沒加進 git」拒絕整段拿掉 → `19 passed, 0 failed`(見 F2)。
- 另外,S16 條款這次加了「CI 呼叫了卻沒抓完整歷史時也印一行」,但它綁的 `t_doctor_note_audit_ci_and_bypass_scan` 五條斷言都沒碰 fetch-depth,只有 r1 回歸測試的 ⑩ 在守。條款跟它綁的測試對不上。
對照:同樣手法改壞 `--cached`、刪除次數讀 HEAD、起點改名偵測,⑥c、⑩b、② 各自翻紅,所以這三處是有守到的。

## F5 範圍終點找不到:第二層改成 rc2,第一層 note-shape 與每支檔有家還是放行,同族沒掃
severity: minor
blocking: 否 — 推送前與 CI 的終點實務上都找得到,要範圍寫錯才會碰到;影響是三道閘對同一個輸入給出不一樣的結果
引句:「# 放行等於整道檢查沒跑(代碼審 r1 外家席),所以當參數錯」
file: `scripts/lumos:24112`(note-shape `--diff` 終點找不到 → 跳過 rc0)、`scripts/lumos:23391`(home check 同樣)
失敗場景:同一個專案、同一個寫錯的範圍 `HEAD..definitely-missing-tip`:
```
note-shape --diff rc 0 筆記形狀擋:範圍 HEAD..definitely-missing-tip 的終點在本機找不到,跳過(fail-open)
note-audit check rc 2 擋下:範圍 HEAD..definitely-missing-tip 的終點在本機找不到——範圍寫錯了?
home check rc 0 每支檔有家:範圍 HEAD..definitely-missing-tip 的終點在本機找不到,跳過(fail-open)
```
r1 修這條的理由(找不到就是範圍寫錯,放行等於沒查)對另外兩道一樣成立。略過開關那一族這次有順手改第一層,這一族卻沒提,收尾報告也沒記。改法建議:一起改,或者在計劃的實作紀錄裡寫明第一層維持放行的理由。

## F6 清單解析函式的說明還寫著每個編號對一個指紋
severity: minor
blocking: 否 — 只是說明文字過期,不影響行為
引句:「"""清單檔 → {orchestrator, model, version, fp, fp_ok, tip, rows:{id: ctx_fp}} 或 None。"""」
file: `scripts/lumos:24534`
失敗場景:這次把 `rows` 改成 `{id: [排序後的指紋…]}`(同一個 hunk 裡的 `rows = {k: sorted(v) for k, v in rows.items()}`),docstring 還寫 `{id: ctx_fp}`。之後有人照說明拿 `lst["rows"][rid]` 當字串跟單一指紋比,就會永遠不相等,輕的判定全部收不下。

最嚴重 severity:minor;blocking 共 0 條。
