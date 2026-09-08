severity: blocker

## F1　PostToolUse 仍是代理物：它證明工具成功返回，不證明檔案位元組改變

引句:「事件就是動作本身(工具剛剛改了這個檔)」  
severity: blocker  
blocking: 是  
帳只存 `{ts, session_id, tool, path, event}`，沒有前後雜湊或 diff；Write 把原內容原樣寫回、Edit 的替換結果等於原文，都會留下「動過」事件但工作樹零變化，接手者得到假活動。file: `governance/review-reports/進度從提交推導-v3/r1-snapshot.md:171`

## F2　三態缺少「記錄器當時是否活著」，無法解讀沒紀錄

引句:「三種狀態:有紀錄 / 沒紀錄 / 讀不動」  
severity: blocker  
blocking: 是  
目前設定正常只能證明查詢當下，不能證明被查時段的 hook 曾安裝且持續有效；「沒工作」與「hook 被拆／未裝／壞掉但 fail-open」仍落在同一個沒紀錄。現有 enforcement 也明載 SessionStart 自己沒裝時無法發現整套缺席。file: `docs/lumos-toolchain-knowledge/Projects/enforcement儀表板_計劃.md:83`

## F3　檔案級最後活動不能回答 session 在做哪個任務

引句:「最後誰動、何時、距今多久、有沒有別的 session 也在動」  
severity: blocker  
blocking: 是  
同一支 `scripts/lumos` 同時服務大量計劃條款，S 先做計劃 A、再為計劃 B 動同檔後，A 的查詢只看見 B 的最後事件；帳又明定不記內容、訊息或任務，因此接手者無法由 `{session,path,time}` 還原 S 的目的與做到哪。這與 v2 把多種事實壓成三態同型，只是改成把多個任務壓成一個檔案時間戳。

## F4　讀側沒有觸發點，重演既有唯讀工具無人使用的病

引句:「讀側要不要也做成 SessionStart 進場時自動印」  
severity: blocker  
blocking: 是  
自動入口仍列為待裁，三個消費者沒有任何一個被流程強制或自動呼叫 S3；前例實測 158 篇中 126 篇從未使用 spec-trace，證明「已有唯讀查詢」不會自然形成消費。file: `governance/review-reports/進度從提交推導/r1-接手.md:58`

## F5　帳是 gitignore 的本機副產物，跨機接手沒有可重播的共同歷史

引句:「位置在 `.lumos/` 底下,第一天就 gitignore」  
severity: major  
blocking: 是  
另一台機器或另一個 clone 即使正確安裝 hook，也只會寫自己的 `.lumos/`；新接手 session 查不到原機事件，而 spec 的驗收沒有把「接手」限縮成同一 checkout。Codex 與 Claude 的 hook 又都只能裝在使用者層，不能由 repo 自帶。file: `docs/lumos-toolchain-knowledge/Projects/Codex工作流整合_調研.md:54`

## F6　立案症狀成立，但 v3 產品立案不成立

引句:「症狀:任何一個 session 都答不出這件實作做到哪一步了」  
severity: blocker  
blocking: 是  
本地數字證明手寫框會漂，卻沒有證明「最後碰過哪些檔」能回答原問題；F1–F5 顯示它既不可靠代表實際變更，也不攜帶任務意圖，還沒有確定消費入口。裁定：不要照 v3 實作；最小第六條路是先做無帳本的唯讀接手視圖，重用 dispatch-lens 取計劃檔案，再直接顯示 `git status`、實際 diff 摘要與相關提交，輸出可驗證的「現在有哪些內容變了」，不宣稱 session、任務進度或完成。
hook: Stop
hook: Stop Completed
tokens used
93,705
severity: blocker

## F1　PostToolUse 仍是代理物：它證明工具成功返回，不證明檔案位元組改變

引句:「事件就是動作本身(工具剛剛改了這個檔)」  
severity: blocker  
blocking: 是  
帳只存 `{ts, session_id, tool, path, event}`，沒有前後雜湊或 diff；Write 把原內容原樣寫回、Edit 的替換結果等於原文，都會留下「動過」事件但工作樹零變化，接手者得到假活動。file: `governance/review-reports/進度從提交推導-v3/r1-snapshot.md:171`

## F2　三態缺少「記錄器當時是否活著」，無法解讀沒紀錄

引句:「三種狀態:有紀錄 / 沒紀錄 / 讀不動」  
severity: blocker  
blocking: 是  
目前設定正常只能證明查詢當下，不能證明被查時段的 hook 曾安裝且持續有效；「沒工作」與「hook 被拆／未裝／壞掉但 fail-open」仍落在同一個沒紀錄。現有 enforcement 也明載 SessionStart 自己沒裝時無法發現整套缺席。file: `docs/lumos-toolchain-knowledge/Projects/enforcement儀表板_計劃.md:83`

## F3　檔案級最後活動不能回答 session 在做哪個任務

引句:「最後誰動、何時、距今多久、有沒有別的 session 也在動」  
severity: blocker  
blocking: 是  
同一支 `scripts/lumos` 同時服務大量計劃條款，S 先做計劃 A、再為計劃 B 動同檔後，A 的查詢只看見 B 的最後事件；帳又明定不記內容、訊息或任務，因此接手者無法由 `{session,path,time}` 還原 S 的目的與做到哪。這與 v2 把多種事實壓成三態同型，只是改成把多個任務壓成一個檔案時間戳。

## F4　讀側沒有觸發點，重演既有唯讀工具無人使用的病

引句:「讀側要不要也做成 SessionStart 進場時自動印」  
severity: blocker  
blocking: 是  
自動入口仍列為待裁，三個消費者沒有任何一個被流程強制或自動呼叫 S3；前例實測 158 篇中 126 篇從未使用 spec-trace，證明「已有唯讀查詢」不會自然形成消費。file: `governance/review-reports/進度從提交推導/r1-接手.md:58`

## F5　帳是 gitignore 的本機副產物，跨機接手沒有可重播的共同歷史

引句:「位置在 `.lumos/` 底下,第一天就 gitignore」  
severity: major  
blocking: 是  
另一台機器或另一個 clone 即使正確安裝 hook，也只會寫自己的 `.lumos/`；新接手 session 查不到原機事件，而 spec 的驗收沒有把「接手」限縮成同一 checkout。Codex 與 Claude 的 hook 又都只能裝在使用者層，不能由 repo 自帶。file: `docs/lumos-toolchain-knowledge/Projects/Codex工作流整合_調研.md:54`

## F6　立案症狀成立，但 v3 產品立案不成立

引句:「症狀:任何一個 session 都答不出這件實作做到哪一步了」  
severity: blocker  
blocking: 是  
本地數字證明手寫框會漂，卻沒有證明「最後碰過哪些檔」能回答原問題；F1–F5 顯示它既不可靠代表實際變更，也不攜帶任務意圖，還沒有確定消費入口。裁定：不要照 v3 實作；最小第六條路是先做無帳本的唯讀接手視圖，重用 dispatch-lens 取計劃檔案，再直接顯示 `git status`、實際 diff 摘要與相關提交，輸出可驗證的「現在有哪些內容變了」，不宣稱 session、任務進度或完成。
