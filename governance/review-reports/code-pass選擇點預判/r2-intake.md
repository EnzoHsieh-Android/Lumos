# code-pass選擇點預判 r2 收貨

席位:正確性-sonnet、架構對齊-sonnet(全新代理,沒讀上輪報告)。材料:r2-snapshot.patch、r2-repair.patch、r2-repair-binding.json、r2-behavior-cases.md;派工單 r2-dispatch.json(base_commit 826ce8451)。
收貨三道:兩份報告引句全數錨定、refcheck 全 ok;正確性席首交末行寫成 `max severity:` 被 report-normalize 擋,退回該席只改那一行後重交(其餘一字未改),存檔取報告本體、不含它附在報告外的補充說明。
reflog 無異動;正確性席自述在 /tmp/lumos-seat-work 開的 worktree 已 remove,`git worktree list` 核對不在;兩席臨時目錄收齊後已刪。

發現編號:正確性 c1、c2;架構對齊 a1、a2(共 4 條,全 minor)。

## 重現表

| id | 席 | 等級 | 編排者重現 | 處置 |
|---|---|---|---|---|
| c1 | 正確性 | minor | HIT:`t_codeloop_pass_choice_skips` 原本沒有任何案例走到「沒有遠端」那條(`_cpc_repo` 一律加 origin);補案例後,把那條的放行改成 `return False` → 新案例紅(9 passed, 1 failed),還原後綠 | 折:補「沒有遠端」案例 |
| c2 | 正確性 | minor | HIT:讀 `_lens_default_remote`,多個遠端、沒有 origin、分支沒設上游 → 回 None;新案例(fork、upstream 兩遠端)修前印「沒有遠端」→ 紅,修後綠 | 折:訊息分兩種,判不出時教設上游;照舊留給推送前判 |
| a1 | 架構對齊 | minor | HIT(現象):`_choice_range` 舊值固定全零、pass 預判用本機追蹤 ref,兩份取範圍並存 | 放行:範圍照推送前掛鉤輸入模擬是設計審 r2 定的(起點同一支 `_push_range_start`),計劃〈做法〉已寫理由;席位自己也標專案本有兩套並存、找不到唯一做法 |
| a2 | 架構對齊 | minor | HIT(現象):條列手抄 `_spec_gate_push_bad_tail` 前兩行、輸出 stdout 與 mech 鄰居 stderr 不同 | 放行:結構與鄰居相同(原因照印、補出口、記擋下),只差輸出通道與尾段;pass 的出口教的事跟推送前尾段不同(不用先提交紀錄),不能直接共用 |

架構對齊席另標 ⚠:pass 直接呼叫 `_choice_push_round` 算不算跨層——同 r1 a1 的判法,判不是:選擇點本來就只在推送前那一圈,沒有 code-loop 層入口可走,呼叫關係寫在系統筆記 pitfalls-code-loop。

## 修補因果(regression-set)

- c1:修前 ccca94927 與修後 826ce8451 都沒有守「沒有遠端」的案例(席位兩版改壞都綠)→ 原有漏查,不是上一輪修補造成。
- c2:那段呼叫與訊息修前就有、r1 修補沒動(r2-repair.patch 沒有這幾行)→ 原有漏查。
- a1:兩版範圍組裝除了取分支名三行之外相同 → 原有,不是修補造成。
- a2:修前就有同樣的條列加出口印法,修補只換尾段內容 → 原有。
結論:本輪 4 條全數判過因果,沒有一條是上一輪修補造成 → `--regression-set none`。

## 先查世界

- PRIOR-ART:c2「多個遠端時預設推到哪」——git 官方 git-push 文件:沒指定 <repository> 時先看目前分支的 `branch.<name>.remote`,沒有就預設 origin(https://git-scm.com/docs/git-push 〈DESCRIPTION〉與 `branch.<name>.remote` 設定說明 https://git-scm.com/docs/git-config#Documentation/git-config.txt-branchltnamegtremote )。共用的 `_lens_default_remote` 已照這個順序取(上游→origin→唯一一個),判不出時 git 自己也要使用者指定;所以不另猜,改成照實講判不出並教設 `branch.<分支>.remote`。採用。
- PRIOR-ART:c1「提早返回的放行分支要有測試守」——論文〈Practical Mutation Testing at Scale〉https://arxiv.org/pdf/2102.11378 的 ROR/拿掉陳述類運算子就是這種改壞;做法是補一個走到那條分支的案例,並用改壞驗證它會紅(本輪已做)。採用。
