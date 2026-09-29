# code-角色鏡頭 r2 收貨紀錄

兩席全新:正確性-sonnet、架構對齊-sonnet,只審 r1 折入的修正差異(r2-snapshot.patch,572 行)。引句全錨。外家本輪未派(standard 的外家席為 note-if-absent;r1 已派過)。

| id | 來源 | 嚴重 | 內容 | 去向 |
|---|---|---|---|---|
| b1 | 正確性 F1 | major | 改用 _json_at_ref 後起點設定帶 BOM 被當讀不懂,宣告整份丟 | 折:_json_at_ref 容許 BOM(共用函式,所有用它的地方受惠);測試 t_review_role_config_bom_and_deep_json_at_base |
| b2 | 正確性 F2 | major | _node_flavor 工作樹改走 reader 後,最近那份 package.json 讀不了會往上找父層改判 | 折:讀不了回空字串=在但解析不了→判不出;非 UTF-8 照 git 版換字元;測試 t_node_flavor_unreadable_nearest_package_json_is_none;PITFALL 寫進 Systems/棧別提問表態閘 |
| b3 | 正確性 F3 | minor | 起點設定超深巢狀時 RecursionError 逸出、角色被靜默丟掉;r1 那支測試的對應斷言是空測 | 折:_json_at_ref 多接 RecursionError;空測那行拿掉,改由上面的新測試走真路徑 |
| b4 | 架構對齊 F1 | major | 用 ls-tree -l 另查大小是第二種做法,且上限兩處各守一次 | 折:拿掉 ls-tree 那支;在批次讀取那一層旁加 _nodehome_cat_sizes(--batch-check)與 _nodehome_cat_blobs_capped,原本的 _nodehome_cat_blobs 不動;讀取端不再二次截斷;測試 t_cat_blobs_max_bytes_skips_big_objects |
| b5 | 架構對齊 F2 ⚠ | minor | 掛鉤重叫沒有除錯紀錄 | 折:重叫前 _debug 一行 |
| b6 | 架構對齊 F3 | minor | 兩處寬接不留任何紀錄 | 折:兩處都在錯誤輸出印「提醒:…(例外類別名)」;派工那處抽成 _dispatch_lens_role_text |
| b7 | 架構對齊 F4 ⚠ | minor | 註解寫「照棧別題組設定警告」但內容刻意不回填值 | 折:註解改寫成「印法照它、內容刻意不回填值」 |

另:兩處拆小函式是為了不帶進新的複雜度告警(_nodehome_cat_blobs 維持原樣、cmd_dispatch_lens 抽出角色那段)。

refuted-set:none(b1/b2/b3 照席位附的重現在測試裡先紅後綠;b4 以單元測試驗大小上限)。

## 引句錨不到的撈回

- 架構對齊 F3(對應 b6)的引句跨兩行,diff 每行帶「+」前綴,quote-check 錨不到。機械重現:`grep -n -A1 "^+        except Exception:$" r2-snapshot.patch` → HIT(推送前分級那處 `except Exception:` 下一行即 `_rr = None`),現象成立,照撈回、已折入。
