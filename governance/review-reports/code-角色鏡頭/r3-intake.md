# code-角色鏡頭 r3 收貨紀錄(末輪)

兩席全新:正確性-sonnet、架構對齊-sonnet,只審 r2 之後的修正差異(r3-snapshot.patch,458 行)。正確性席驗收 r2 七條修正全部已修好。

| id | 來源 | 嚴重 | 內容 | 去向 |
|---|---|---|---|---|
| c1 | 正確性 F1 | minor | 讀指定版本時,超過 512KB 的 package.json 被當沒有、往上找父層 | 放行:極少見;寫進計劃〈已知限制〉並附 REVISIT 2026-12-29 |
| c2 | 正確性 F2 | minor | 兩趟批次讀取各拿完整剩餘預算,git 異常慢時最多約兩倍 | 放行:掛鉤外層上限照樣擋;寫進計劃〈已知限制〉並附同一個 REVISIT |
| c3 | 架構對齊 F1 | minor | _nodehome_cat_sizes 沒有鄰居的換行守衛 | 放行:唯一呼叫者 _review_role_wanted 已先排除含換行的路徑;改程式要再開一輪、超過 standard 上限 |
| c4 | 架構對齊 F2 | minor | _node_pkg_text 用空字串當「在但讀不了」 | 放行:刻意(回 None 會被當沒有、往上改判,即 r2 的 b2),有測試 t_node_flavor_unreadable_nearest_package_json_is_none |

末輪紀律:新 minor 照記、附理由放行,不觸發新一輪。refuted-set:none(兩席皆為讀碼推論,未實跑;內容與程式對得上,我讀過對應段落)。
