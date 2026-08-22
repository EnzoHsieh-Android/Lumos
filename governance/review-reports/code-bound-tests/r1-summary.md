# code-bound-tests r1(2026-08-22,一席 sonnet 實作審)
- #1 blocker 設定檔壞直接炸、rc 剛好 1 被當真紅 → 折:_platform_test_index/Env 包 try,fail-open 記 no-config;測試⑦。
- #2 major 新分支首推 EMPTY_TREE..sha 把全庫合約當受波及 → 折:範圍以 empty-tree 起頭視為 diff-unavailable(fail-open);測試⑧。
- #3 major 懸空/偽證據判紅=舊債變硬擋 → **不折,附理由**:doctor --ci 的 Check T 本來就把 dangling/fake 當硬擋(scripts/lumos:784/787 用 warn 非 warn_soft),pre-push 早就擋,這裡沒有新增擋的面;但其中「Class.Method 帶點寫法因集合扁平而誤判懸空」是真的 → 折:方法名含點時退查最後一段。
- #4 minor 函式屬性 stash 殘留 → 折:每次呼叫先清。
存活 0 major。全家族測試 12/0。
