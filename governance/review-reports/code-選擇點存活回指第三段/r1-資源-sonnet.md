severity: minor

我讀完整份 diff,沒找到會讓正常操作逾時或把機器資源用光的問題。子程序、Ctrl-C 收尾的路徑都沒有新漏洞:`_kill_run` 的逾時與 `KeyboardInterrupt` 照舊收程序群組,探針輪替有上限,`choice-layer/` 另有 14 天清理。只找到三處可以更省,都沒有靜默判錯。以下都是讀碼推算,我沒有實際跑過。

severity: minor
blocking: 否
`scripts/lumos:82415`(`_choice_push_segs`):推送閘對範圍內全部有壞法的行算判讀狀態,不只被抽中的存活行。已被殺掉或已放行、但帳上留著舊 layer 事件的行,也會各花一次 `_residual_blob_at` 的 `git show`。
`_choice_layer_deps` 對每個判讀行各自把涉及計劃的全文序列化再雜湊,沒有跨行快取。第 1、4 層判讀未歸計劃時,涉及的是全部進行中計劃,每行雜湊的量是這些計劃全文加總。
規模推算:300 個判讀行,每行 git show 約 0.1 秒、雜湊約 300KB,合計接近 `_CHOICE_GOV_BUDGET` 的 30 秒。
超時後 `ctx.doc` 回 None,讀不到判讀的行都被歸成「存活·未判讀」,處置句也跟著錯。這不影響擋不擋,只是子原因標錯。
改法:只對 `_choice_disposition` 為 survived 且被抽中的行算 seg,並對 `(layer, plans)` 的 deps 結果做快取。
引句:「xs = [x for x in res["lines"] if x["status"] == "mutant" and (x.get("mutant") or {}).get("identity")]」

severity: minor
blocking: 否
`scripts/lumos:29516`(`_KillCompile` 的嫌疑篩選):改成「錯誤所在檔的壞法全列嫌疑」後,每個嫌疑各做一次單獨 Gradle 編譯。
場景:一支檔有 10 個壞法、只有 1 個編不過,就要單獨編 10 次。一次 `choice-kill` 最多 30 個壞法,每次單獨編以 20 到 40 秒估,10 次約 200 到 400 秒。
編譯預算是 1800 × 0.25 = 450 秒,很容易被同一支檔吃光。之後 `cap()` 回 None,程式設 `cstate="budget"` 並 `return []`,其他檔的嫌疑確認和換候選批次都被放棄。
結果是照現在的規則交給測試階段,不判錯,只是合批編譯的效益被吃掉。
改法:同檔嫌疑先二分(一半一半套上再編),或限制每批單獨確認的個數。
引句:「sus = [g for g in ranges if rel[g] in bad_files]」

severity: minor
blocking: 否
`scripts/lumos:81375`(`_choice_layer_split`):分份只靠把存活數減半。涉及計劃本身(條款加預期值表)就超過 200KB 時,減半到 1 個也不會變小。
未歸計劃的存活涉及全部進行中計劃,所以每個存活各成一份。每份先做 5 次減半的重新渲染,再各寫一份計劃全文的 `-body.md` 旁檔。
推算:30 個未歸計劃存活、涉及計劃加總約 400KB,會得到 30 份、30 個各約 400KB 的旁檔,約 12MB。
`--template` 每呼叫一次就換新清單編號並重新產生,旁檔留 14 天,重複呼叫會線性累積。同一批計劃正文在份與份之間完全重複,編排者也得派 30 個代理。
`governance/choice-layers/` 沒有清理,這是紀錄性質,增長速度跟人工判讀同級,我沒有另外列為問題。
改法:未歸計劃的存活要有份數上限,或旁檔共用一份。
引句:「while n > 1 and len(text.encode("utf-8")) > _CHOICE_LAYER_PART_BYTES:」

總結:最高等級是 minor。
