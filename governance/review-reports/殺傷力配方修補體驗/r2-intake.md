preflight-4: ran(第 1 輪已跑;本輪只審第 1 輪折入差異)

# 設計審第 2 輪席位收貨:殺傷力配方修補體驗

2 席全新、只審第 1 輪折入差異(r2-delta.diff)。2 席全收齊後才動計劃。四道機械檢查:2 份都已是正規化格式;quote-check 全錨;refcheck 全數對得上;兩欄一致;repo 根 reflog 無異動。

finding 編號:c=正確性-opus、h=接手-sonnet。

| 編號 | 席 F | 等級 | 重現 | 處置 |
|---|---|---|---|---|
| c1 | 正確性 F1 | major | HIT(席位照 spec 改副本實測:對 lumos 自己範本那行寫配方,原版寫得進且殺得掉,照 spec 回 2);兩席獨立一致(h2) | 折:S4 改整欄等於才擋、含有照寫,補反向子句 |
| c2 | 正確性 F2 | minor | HIT | 折:〈做法〉交代跟「宣告不擋、跑時擋」不衝突的理由;同步清單補 kill-add 說明段與 guard kill 結果行 |
| c3 | 正確性 F3 | minor | HIT(實測人寫 `_why` 被濾掉);兩席一致(h3) | 折:只濾 `_logged`、`_rid`;`_logged` 手寫的既有洞記進 Issue |
| c4 | 正確性 F4 | minor | HIT(實測落單替身字元讓身分計算崩潰) | 折:身分算法改 surrogatepass |
| c5 | 正確性 F5 | minor | HIT | 折:Issue 補三種崩潰與回傳碼重疊 |
| h1 | 接手 F1 | minor | HIT | 折:列出加合約片段 |
| h2 | 接手 F2 | minor | HIT | 折:同 c1 |
| h3 | 接手 F3 | minor | HIT | 折:同 c3,`_rid` 蓋在 `{**r}` 之後 |
| h4 | 接手 F4 | minor | HIT | 折:同步清單補 reference.md、INDEX.md、guard-kill 兩處、kill-rm 擋下訊息、下一步那句 |
| h5 | 接手 F5 | minor | HIT | 折:Python 型別名、null 算缺、空平台算預設、重複取第一條、截斷加 …、sort_keys、結尾 <短身分> 是字面佔位字 |

重現不到而沒折的:無(refuted-set none)。放行的:無。
