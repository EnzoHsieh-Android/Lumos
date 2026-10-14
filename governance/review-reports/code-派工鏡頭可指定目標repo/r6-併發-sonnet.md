severity: major

## 範圍與做法

我讀完修補差異,並用 lens-repo 的 `scripts/lumos dispatch-lens --spec` 在暫存 repo 實測。實驗目錄是 scratchpad 下的 `cr-lr6-資源/`,跑完已刪。作者這輪補的上限(20 篇、12000 字)都有效。漏掉的是目標架構段,它沒有任何上限。

## Finding

severity: major
blocking: 是 — 目標架構段(`arch_text`)沒有總量上限,實測單次輸出 4.6MB 到 9MB,會把整段塞進審查席派工詞,席位起不來或被塞爆
引句:「return _frame_injected(_arch_target_text(root, "HEAD", vault_rel, _arch_target_split(cands, rules), warns, show=show))」
問題:這輪的字數上限 `_LENS_SPEC_TEXT_MAX` 只套在 `cmd_dispatch_lens_spec` 的 `lines`。目標架構段是另一個欄位 `arch_text`,在 `_dispatch_lens_spec_arch_text` 另外算,上限管不到。
`_arch_target_text` 裡有三處輸出量是設定檔或筆記決定的,都沒有上限:
- 超過 `_ARCH_TARGET_LENS_NODES`(3)個節點時,每個節點仍各印一行「節點太多」的列名行,行數隨 config 的 `arch_targets` 條數成長。節點名走 `show` 的 300 字上限,但跳脫會把 1 個反引號變成 6 個字元,每行最多約 1800 字元。config 沒有條數上限。
- 前 3 個節點各貼最多 30 條規則,規則原文只過 `_kill_esc`,沒有長度截斷。這在 `_arch_target_text` 的 `lines += [f"  - {cl(text)}" ...` 那行。
- `warnings` 逐條不限數量(上面兩項才是主因)。

這段是被審 repo 的 HEAD(`.lumos/config.json` 與 Systems 節點)產生的,投稿者可控。

具體失敗情境(實測):
- 輸入 1:config 有 3000 條 `arch_targets`,節點名是 `Systems/` 加 250 個反引號,config 約 915KB。計劃提到 3000 支對應的檔案。
  結果:`arch_text` 為 4,637,251 字元,耗時 8.4 秒。
- 輸入 2:3 個目標節點,每個有 40 條 `RULE:`,每條 100KB(共約 12MB 筆記)。計劃提到對應的 3 支檔案。
  結果:`arch_text` 為 9,008,764 字元,stdout 為 18MB(`text` 與 `arch_text` 各印一份),耗時 4.5 秒。
- 作者自量的 5000 連結(1593 字)只涵蓋 `text` 段,沒量 `arch_text`。
- 修法方向:對 `_arch_target_text` 的結果套同一支 `_lens_spec_cap_lines`,或在函式內給規則原文每條字數上限、列名行數上限。

佐證:`scripts/lumos:51156`,`scripts/lumos:44128`(`_ARCH_TARGET_LENS_NODES` 只限貼規則的節點數,不限列名行數)。

## Finding

severity: minor
blocking: 否 — 要 5000 條規則的 config 加 2 萬個候選路徑才會撞,一般專案用不到;撞到時只是這次沒有鏡頭(放行),不會擋住派工
引句:「cands = [sps[0] for _k, sps in _lens_spec_nfc_groups(m.rstrip(".,;:)」』】") for m in found)」
問題:目標架構段的比對是「候選路徑數 × 規則數」,而且不吃 `_LENS_SPEC_BUDGET` 的 30 秒預算。它在 `cmd_dispatch_lens_spec` 跑完之後才開始算,時間另計。`_arch_target_split` 對每個候選逐條掃規則,候選數由 1MB 計劃上限決定,規則數由 config 決定,兩邊都沒有條數上限。
具體失敗情境(實測,候選全部不命中任何規則,走完全部規則):
- 2000 條規則 × 1 萬候選:16.2 秒。
- 5000 條規則 × 2 萬候選:63.7 秒,超過掛鉤約 47 秒的外層逾時。
- 2 萬條規則 × 4 萬候選:超過 100 秒我就中止了。

結果:掛鉤逾時後只附一行逾時說明,整份固定席與落點都沒附。這個乘積成本不是這輪修補新增的,但這輪重寫了候選整理(`_lens_spec_nfc_groups`),仍沒補上這個計算的時間預算或條數上限。建議候選數或規則數設上限,或讓 `_arch_target_split` 也看 `deadline`。

佐證:`scripts/lumos:51156`,`scripts/lumos:44265`。

## 已讀,無 finding

- **只在提交裡的節點與落點上限(20 篇)**:兩處的上限都有效。落點的迴圈在列滿 20 篇後記為「另有 M 篇沒列」,不再往下讀。
- **字數上限的行界截斷**(`_lens_spec_cap_lines`):單行超長與一般情況都正確。`_lens_visible` 在上限之後才跳脫控制字元,最壞約放大 6 倍,不超過約 72KB,可接受。
- **固定席段落其他輸出**:行數與字數都有界,再受 12000 字的總上限保護。
  - 渲染固定席時,每個節點的合約行最多 40 行、每行 200 字。
  - 牽連檔最多 5 個。
  - 太泛不列、超預算沒算都最多 5 個。
  - 只在提交裡的程式檔最多 5 個。
- **兩種寫法都試是否翻倍 git 查詢**:不會。`_lens_spec_commit_cands` 把所有寫法交給 `_spec_commit_cands_norm` 先做 NFC 去重,`cat-file --batch-check` 仍是一次呼叫,`ls-tree` 分批 200 個。
- **同一個名字的 NFC/NFD 寫法數量**:
  - 構造 2^14 到 2^15 種寫法的同一個名字,工作樹寫法 16384 個連結 3.5 秒、1.26MB 的程式檔候選 7.4 秒。
  - 提交寫法 14 位元的連結 3.5 秒、程式檔 4.1 秒。
  - `if n not in sp` 的串列比對在這個量級沒有二次方爆炸,都在 30 秒預算內。
- **名字跳脫的耗時**:`_lens_author_name_show` 先切 `s[:limit]` 再跳脫,單名最多約 1800 字元。掛鉤抄本同理,範圍值與計劃值各最多 300 字。沒發現超長或大量名字造成的耗時問題。
- **逾時收子行程**:這輪沒動 `subprocess.run(timeout)` 與 `impact` 子行程的剩餘秒數。`impact` 吃的是 30 秒預算的剩餘時間,掛鉤殺 lumos 前它已結束,沒看到新增的孤兒行程。目標架構段不開子行程,只是同步計算(見上一條 minor)。
- **掛鉤說明行**(`_range_what`、`_spec_what`、`_frame_injected`):長度都有界(最多約 1800 字元),加框只是拆掉含框線的行,沒有新增大小問題。

最高等級 major,blocking 1 條。
