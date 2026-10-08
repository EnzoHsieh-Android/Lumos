severity: major

# 架構對齊-sonnet 席 第 2 輪報告

## 三問

1. 分層與順序:drift check 排在 code-loop check 之後、全套測試之前,順序跟其他閘一致(便宜先跑)。分層上不一致:其他掛鉤閘(每支檔有家、note-shape)用掛鉤的 `_hrange`/`_range`(pp_range_for 的空樹兜底)把範圍交給工具,起點的分岔點判斷收在工具端的 `_lens_push_base`。這次掛鉤自己在 bash 裡算主線與分岔點(pp_mainline、pp_drift_range),同一段掛鉤裡兩種起點算法並存。
2. 命名、錯誤處理、訊息:函式名 pp_* 前綴與既有 pp_range_for、pp_touched_file 一致;訊息「擋下」與逃生段格式沿用 note-shape 那段。錯誤處理新增「128 以上停掛鉤」是掛鉤內其他閘都沒有的分支(note-shape、每支檔有家都只認 rc1),屬新慣例,見 F3。CI 端「其他非零讓 CI 紅、掛鉤放行」有寫理由,與 ci.yml 其他步驟(其他非零照原碼 exit)一致。
3. 第二種做法:有。主線尋找順序(多了 refs/remotes/<遠端>/HEAD、<遠端>/main、<遠端>/master)與「取分岔點或遠端舊值較新者」的判準,在 bash 與工具端 `_mainline_ref`/`_lens_push_base` 各一份,兩邊行為不同(見 F1)。CI 的起點補法也是第二種(見 F2)。

## F1 掛鉤在 bash 裡另寫一份「找主線與算起點」,跟工具端 _lens_push_base / _mainline_ref 成兩份邏輯
severity: major
blocking: 是
引句:「_ml="$(pp_mainline)"」
佐證行:file: `scripts/lumos:33059`(_lens_push_base:起點是全 0 或找不到才算分岔點,主線由 _mainline_ref 只認 main/master 的 upstream)
佐證行:file: `scripts/lumos:25784`(_note_audit_resolve 同樣呼叫 _lens_push_base,工具端所有共用起點的檢查都走這一支)
佐證行:file: `scripts/hooks/pre-push:388`(note-shape 在同一支掛鉤裡仍吃 _hrange,不走新算法)
1. 工具端既有做法:起點判斷集中在 `_lens_push_base`,主線找法集中在 `_mainline_ref`,note-shape、每支檔有家、note-audit 共用。
2. 這份 diff 在掛鉤裡另寫 pp_mainline(多三個候選:遠端 HEAD、遠端 main、遠端 master)與 pp_drift_range(is-ancestor 判準、遠端舊值與分岔點取新者),兩份對「主線是誰」「頂端已在主線時」的答案不同:工具端頂端已在主線回 None(整步跳過),掛鉤端一律算 merge-base 交出範圍;工具端找不到主線落空樹、掛鉤端落回原樣交給工具。同一次推送,drift check 與 note-shape 看到的起點可能不同。
3. 之後任何一邊改(例如主線多認一個候選)都要記得改另一邊;掛鉤 bash 沒有 _lens_push_base 的測試套件,長期會漂。工具端本來就能吃 remote 名,較整齊的做法是把新增候選與「取較新者」進 `_lens_push_base`/`_mainline_ref`(讓三道共用檢查一起受益),掛鉤只原樣交範圍。
4. 未能重現(這是結構性的第二種做法,不是可翻紅的輸出錯誤);按錨點規則本應自降一級,但嚴重度錨明定「引入第二種做法 = major」,故維持 major,標 ⚠ 交人裁。

## F2 CI 與 doctor 範本的起點補法是第三份,跟同檔 note-shape 那步「原樣交給 lumos」的做法不同
severity: minor
blocking: 否
引句:「BEFORE="$(git rev-parse -q --verify "$SHA^1^{commit}" 2>/dev/null || git hash-object -t tree /dev/null)"」
佐證行:file: `.github/workflows/ci.yml:141`(note-shape 步驟只補 [ -n "$BEFORE" ] 後原樣交給 lumos)
1. 同一支 ci.yml 的 note-shape 與 code-loop 步驟都靠工具端 `_lens_push_base` 處理全 0 與找不到;drift 這步改成 shell 內補起點,並把同一段字串再複製進 scripts/lumos 的 `_DRIFT_CI_STEP` 給消費專案(靠 t_doctor_drift_ci_template_start_fallback 比對防漂)。
2. 註解有說明理由(前一步 fetch 後 main 的 upstream 就是頂端、工具會整步跳過),屬有意偏離;但根因是工具端「頂端已在主線就跳過」的規則,補在三處 shell 而不是工具端一處。是 F1 的同源後果,單獨看只是重複,不擋。

## F3 掛鉤新增「rc>=128 整支停下」分支,掛鉤內其他閘沒有同型處理
severity: minor
blocking: 否
引句:「echo "存量漂移檢查被中斷(rc=$dr_rc),推送停下,後面的檢查不跑。" >&2」
佐證行:file: `scripts/hooks/pre-push:388`(note-shape 只認 rc1,其他非零一律放行)
1. 其他閘只有 rc1=擋、其他=放行;這裡多出第三種語意。原因(Ctrl-C 不該被當成放行)成立,但只在這一道加,同一支掛鉤的每支檔有家、note-shape 被 Ctrl-C 殺掉時仍會放行往下跑。⚠ 判不準是否該一併補齊其他閘,標 minor 記錄不一致。

## 圖譜鏡頭
本席只判架構對齊,未逐條展開圖譜鏡頭合約;此 diff 對 `Systems/存量漂移守衛` 已記「掛鉤自己算起點」的理由,不影響該節點宣稱,但該節點若記「起點判法共用 _lens_push_base」則與 F1 不符(未逐句核對)。

不對齊共 3 條,其中 major 1 條
最高等級:major
