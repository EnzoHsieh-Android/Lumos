severity: major

我是資安審查員(資安-sonnet 席)。鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/f9635c8f…d032f7.json.warming` 不存在,沒有東西要處理,直接審了材料。

我讀了 `scripts/lumos` 的證據判定、核可鏈、`security approvals` 與 `security-approval-add` 全段,也讀了 `pre-push`、`ci.yml`,並掃過測試與文件分包。實驗都在 `/tmp/lumos-seat-work/code-安全證據閘與資安格子/資安-sonnet/` 的 clone 上做,沒有動 repo。

逐類結論:
- ① 提示注入:已看,無。所有進輸出的自由文字都經 `_secinv_show` 清理,證據圍欄與核可鏈欄位沒有未經清理的路徑進派工詞。
- ② 越界與執行:ssh-keygen 的參數都是固定值或暫存檔路徑,principal 不能夾帶選項。CI 用 `SHA: ${{ github.sha }}` 走環境變數,沒有 shell 插值。patch 裡沒有真密鑰、私鑰或信箱。
- ③ 一步繞過:下面兩個 major 與四個 minor。

---

1. 凍結基準與核可鏈基準都讀「被推提交自己的」`.lumos/config.json`,改一個檔就能讓主線比對失效
severity: major
blocking: 是
引句:「if _secinv_is_text(ml) and ml.startswith("refs/") and "\n" not in ml:」
- 誰:照常操作的 AI 或使用者。
- 從哪:編輯 `.lumos/config.json`。`mainline: unknown` 的擋下訊息還明說「在 .lumos/config.json 設 security_evidence.mainline」,所以這是照提示做的一步。
- 送什麼:`{"security_evidence":{"mainline":"refs/heads/<被推的分支或任一舊 ref>"}}`。
- 拿到什麼:`_secev_mainline` 把這個 ref 當主線 tip,資安閘的三道比對都被架空:
  - 護欄被刪、`required_evidence` 變少、工具清單變弱的比對,都變成自己對自己比。
  - 核可鏈「主線版必須是推送版開頭一段」的前綴檢查變成自己對自己,整條鏈可以換成 AI 自己的 `approvers_init` 加例外。
  - CI 的 tag 與分支路徑讀的是同一份設定,所以 CI 也救不了。

最小重現(本機):
```
# 主線 main 上有使用者的鏈;feature 分支把鏈整條換成 AI 金鑰簽的鏈
$ lumos security approvals verify --repo .
  ✗ 跟主線分岔 ... rc=1
# feature 再加一筆 config.json,mainline 指向 refs/heads/feature
$ lumos security approvals verify --repo .
核可鏈 ...(提交 26ad0e783262;主線 26ad0e783262):2 筆
     1 ok  approvers_init x
     2 ok  exception G#behavior       rc=0
```
建議:`mainline` 不准從被審的提交讀,改讀主線 tip 版的設定,或限定只能指向 `refs/remotes/<遠端>/…`。

---

2. 沒有任何一步區分「使用者簽」和「AI 自己簽」,首次釘金鑰可以由 AI 一手包辦
severity: major
blocking: 是
引句:「pool = {p: (t, k, ex) for p, t, k in _secapr_parse_keys(e["keys"])} if i == 0 else {}」
- 誰:照常操作的 AI。
- 從哪:`lumos security approvals payload approvers_init …`,接著工具自己印的下一步 `ssh-keygen -Y sign … -f <私鑰>`,最後 `lumos code-loop security-approval-add`。
- 送什麼:AI 自己用 `ssh-keygen -N ""` 生一把金鑰當 `--key`;或工具提示要「你的私鑰」時,AI 讀得到的未加密 `~/.ssh/id_*`。
- 拿到什麼:主線上還沒有鏈時(新功能剛上線的專案都是這個狀態),AI 能自己釘金鑰,再自己簽 `exception`、`gate_setting warn`、`revision`,閘全部放行。主線已有使用者的鏈時,只剩「釘的是 AI 讀得到的未加密金鑰」這一條路。
- `payload` 和 `security-approval-add` 沒有互動式終端檢查、沒有確認提示、沒有要求金鑰類型(硬體鑰、`sk-`),也沒有核對 principal 是否為已知的使用者。

最小重現:
```
$ lumos security approvals payload approvers_init pin --signer ai --key ai=../k/a2.pub --expires-on 2026-12-01 --repo . --out ../pl
$ ssh-keygen -Y sign -n lumos-security -f ../k/a2 ../pl
$ lumos code-loop security-approval-add ../pl --repo .
✓ 核可鏈第 1 筆已追加(approvers_init pin) ... 有效金鑰:ai SHA256:+EkK…   rc=0
```
計劃已自認「簽的時候有沒有觸碰或輸入密碼,工具驗不到」。但「AI 能不能一路用 lumos 指令寫出被當成使用者核可的紀錄」答案是能。
建議:`approvers_init` 與 `security-approval-add` 要求互動式終端加使用者手打確認碼。加上金鑰類型限制,或要求金鑰指紋由使用者在圖譜決策裡預先登記。

---

3. 過期金鑰可以靠回填 `approved_on` 復活,`approvers_add` 還能用它鑄新金鑰
severity: minor
blocking: 否
引句:「pool = {p: v for p, v in keys.items() if v[2] >= ap}」
- 誰:持有已過期但未撤銷金鑰私鑰的人。
- 從哪:把 payload 的 `approved_on` 手改成金鑰到期日以前。
- 送什麼:該舊金鑰簽的回填日期條目,例如 `exception`(上限 30 天)或 `approvers_add`(上限 730 天)。
- 拿到什麼:`approved_on` 只檢查不在未來、沒有檢查單調遞增,所以金鑰到期只是對「簽的人自填的日期」比較。

重現:
```
init 到期 2026-10-01、今天 2026-10-20
approved_on=2026-10-20 → seq2 approval_signer_unknown
approved_on=2026-09-25 → seq2 ok
```
這要手改帳本欄位且要有私鑰,屬於範圍外的刻意偽造,所以降到 minor。撤銷是永久的、判斷與日期無關,沒問題。

---

4. 主線的鏈全部過期後,推送版可以整條重置
severity: minor
blocking: 否
引句:「res["warnings"].append("主線版的核可鏈從第一筆起就沒有有效金鑰,推送版整條換掉(第一次釘金鑰的信任前提)")」
- 誰:照常操作的 AI。
- 從哪:使用者忘了續簽,`approvers_init` 超過 730 天。
- 送什麼:新鏈,從 AI 自己的 `approvers_init` 開始。
- 拿到什麼:`any(e["status"]=="ok")` 為假,diverged 不成立,等於回到首次釘金鑰的狀態,和第 2 條同路。
- 這個路徑要過兩年,沒法當場重現,是推論。

---

5. `project_id` 取根提交,fork 或範本複製出的專案共用根提交
severity: minor
blocking: 否
引句:「"approval_project_mismatch" if e["project_id"] != project_id else None」
- 誰:照常操作的 AI。
- 從哪:同根的 fork 或範本衍生 repo。
- 送什麼:把兄弟 repo 的 `.lumos/security-approvals.jsonl` 複製過來。
- 拿到什麼:`project_id` 一樣,簽章與鏈都有效。要被收,護欄 id、revision、輸入雜湊與日期還得全部吻合,所以實際危害低。這是推論。

---

6. 舊版 lumos 對 tag 推送靜默略過安全證據那一道
severity: minor
blocking: 否
引句:「if grep -q -- '"--security-only"' "$GRAPHCTL" 2>/dev/null; then」
- 誰:使用者。
- 從哪:機器上的 lumos 沒更新(`GRAPHCTL` 是舊版)。
- 送什麼:`git push <tag>`。
- 拿到什麼:grep 不到旗標就整段不跑也不提醒,tag 路徑的資安閘無聲消失。這是為了相容舊 lumos 的設計,但沒有留下「略過了」的可見訊息。
- CI 的 `security_tag` 工作會補,但 CI 是事後。
- 建議:略過時至少印一行提醒。

---

最嚴重 severity:major,blocking 共 2 條(第 1、2 條)。
