# code-殺傷力配方當場試跑 r3 收貨紀錄(r2 修正差異,上限輪)

機械:兩份 report-normalize 已正規;refcheck 全 ok;quote-check 通才全錨定,架構對齊 F1 的引句跨兩行、錨不到(不採信引句本身,該條由編排者讀碼重現,見下表)。

編號:go1、go2 = r3-通才-opus.md F1、F2;ao1、ao2 = r3-架構對齊-sonnet.md F1、F2。

| id | 怎麼試 | 結果 |
|---|---|---|
| go1 | t_guard_kill_only_ids ⑥d 四格(`./prod.py` 加 old null / new 數字,帶與不帶 --id),修前先跑 | HIT:修前四格 rc1、Traceback;修後 rc2、--json 恰一行、那條 error「配方欄位格式不對」 |
| go2 | ⑥e:invariant 是數字、帶 --id 與合約片段,修前先跑 | HIT:修前 rc1 當掉;修後被片段濾掉、沒有配方可跑 rc2 |
| ao1 | 讀碼:`_guard_kill_pick` 呼叫 `_kill_recipe_judge` 沒有兜底,`_kill_add_warn` 與 `_kill_p2_one` 都有 | HIT(讀碼重現;引句錨不到不影響事實) |
| ao2 | 讀碼:`--id` 路徑 pick 裡 `_kill_check_ctx` 讀一次設定、主流程 `load_platforms` 再讀一次,repo 根也算兩次 | HIT |

到上限(第 3 輪)有 major,攤人;Enzo 裁「換形狀+另開一輪審」。處置:4 條全折。根因:①同類第三次(go1;go2 同屬 guard kill 碰到怪欄位會當掉)→ 換形狀,在 guard kill 當掉的兩步原地擋、片段過濾只比字串;②跟鄰居不一致(ao1 兜底、ao2 設定讀兩次)→ 判法包兜底、`--id` 先照原方式讀設定再給判法用。go1 是 r2 修補造成的(regression-set)。這段修正另開 `code-殺傷力配方當場試跑-r4` 審。
