severity: minor

## 問1 分層與依賴方向
新碼的位置與呼叫方向跟鄰居一致:偵測端的遮罩與子句切分放在 _drift_pending_clause 一帶(scripts/lumos:32206、32232),由 _drift_pending_links 與 _drift_c6 往下呼叫;修法端 _drift_fix_c6 呼叫偵測端的 helper,方向同 c1..c5 與 count 的「修法呼叫偵測端」;參數檢查放在 _drift_fix_c6_args(scripts/lumos:34577),跟 _drift_fix_c3_args(scripts/lumos:34558)同一層。handled 改回行內 lambda,跟 _drift_fix_count 一樣(scripts/lumos:35044)。沒有跨層直呼。
引句:「+def _drift_target_clause_ends(env, line, target):」

## 問2 命名與錯誤處理
命名(_drift_ 前綴、_DRIFT_ 常數、(結果, 錯誤) 二元組回傳、「手動改」收尾、尾註「(代碼審 r2 正確性席)」)都跟鄰居同一套;沒有吞例外,擋下都走回傳錯誤字串,與 _drift_fix_c3_args 一致。小落差:_drift_parens_balanced 沒有 docstring,鄰近的 _drift_ 工具函式幾乎都有一行說明(例 scripts/lumos:34558 附近的註解、scripts/lumos:35749)。
引句:「+        return "--settled 的括號要成對(補進去的已裁定括號靠配對判斷到哪裡為止)"」

## 問3 第二種做法
沒有引入新的錯誤處理或流程做法,但括號相關的小工具在同檔已有兩支,這次又加了第三支獨立的深度計數:_ns_paren_groups_only(scripts/lumos:28143,半形全形混用、可巢狀、算深度)與 _drift_m1_paren_span(scripts/lumos:35748,同樣半形全形混用的括號配對)。新的 _drift_parens_balanced(scripts/lumos:34565)與 _drift_mask_settled(scripts/lumos:32206)用法不完全相同(前者只驗成對、不要求群外無字),所以不算重造同一支;但半形全形括號集合另立常數 _DRIFT_OPEN_PARENS(scripts/lumos:32203),前兩支都是各自寫死字面。⚠ 判不準要不要共用括號深度的底層,故只標 minor。

## F1 括號配對深度計數又多一份
severity: minor
blocking: 否
引句:「+        depth += (c in _DRIFT_OPEN_PARENS) - (c in _DRIFT_CLOSE_PARENS)」
佐證: scripts/lumos:28143(_ns_paren_groups_only)、scripts/lumos:35748(_drift_m1_paren_span)、scripts/lumos:34565(_drift_parens_balanced)
說明:同檔已有兩支處理半形全形混用括號配對的工具,這次又加兩處(_drift_mask_settled 與 _drift_parens_balanced)各自寫一份深度計數,且括號字元集改用新常數而不是沿用鄰居的寫法。語意有差(遮罩要從已裁定開頭算起、成對檢查不要求群外無字),所以結構上不算第二種做法,只是重複度偏高;判不準是否該抽共用函式。

## F2 新工具函式缺 docstring
severity: minor
blocking: 否
引句:「+def _drift_parens_balanced(t):」
佐證: scripts/lumos:34565(對照同層 scripts/lumos:34558 的 _drift_fix_c3_args 有說明註解、scripts/lumos:35748 的 _drift_m1_paren_span 有 docstring)
說明:鄰居的 _drift_ 工具函式多半帶一行說明這支函式回什麼,這支沒有。

不對齊共 2 條,其中重大 0 條
