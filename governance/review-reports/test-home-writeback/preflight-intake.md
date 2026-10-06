preflight-4: ran

# 固定前掃收貨

原報告 preflight-raw.md 唯讀保存，PF-1 是既有符號名稱精度、不是核心裁定。

修改前：同repo既有_nodehome_required/side/route_groups是借用入口，不新建解析器。

修改後：同repo既有_nodehome_required/_nodehome_side/_nodehome_commit_groups與_nodehome_mark_note_content是借用入口，不新建解析器。

重現：rg 函式定義驗證 _nodehome_commit_groups / _nodehome_mark_note_content / _nodehome_side 存在；AST 函式清單無 _route_groups / route_groups，HIT。採信並修正；其餘固定四項無命中。

新測試舊碼16通過8失敗；前掃席暫存目錄受限未重跑，不冒稱新增綠燈。正式CLI未改。
