severity: clean

## 第一輪修法驗收
F2:修到 — 讀 git 的呼叫已收斂進 `cmd_home_check` 呼叫的 `_nodehome_mark_note_content`(讀取層,內部改用既有 `_nodehome_reader`,不再自己裸呼叫兩次 `git show`),`_nodehome_evaluate` 本體(scripts/lumos:18131-18277)現在只讀傳入的 `groups[i]["content_paths"]`,對 `_nodehome_git`/`_lens_git`/`_nodehome_reader` 零呼叫;新增的 AST 機械測試 `t_nodehome_diff_route_counts_content_per_commit` check④(scripts/test_lumos.py)當場跑綠(`python3 scripts/test_lumos.py -k nodehome_diff_route_counts_content_per_commit` → 5 passed, 0 failed),核對判定函式呼叫集合裡沒有任何會讀 git 的函式名。

補充查證(三問逐一過,均無新增不一致):
1. 分層與依賴方向:新函式 `_nodehome_mark_note_content`(scripts/lumos:18088)與既有 `_nodehome_commit_groups`、`_nodehome_side` 一樣,唯一呼叫點都在 `cmd_home_check`(scripts/lumos:18519),讀取層組好 `groups[i]["content_paths"]` 再傳給判定層,跟對照組「`cmd_home_check` 組好輸入再呼叫 `_nodehome_evaluate`」的既有形狀一致。
2. 命名與錯誤處理:`before = _nodehome_reader(repo_root, g["sha"] + "^")` 沿用既有 `sha^` 取父提交的既有寫法(舊 `_nodehome_note_changed_in_commit` 也是這樣取);讀不到一律當內容有變的退路(`new is None or old is None or ... → marked.add(p)`)跟舊函式文件字面「讀不到...一律當有變,照原本那樣查」一致,沒有變嚴或變鬆。
3. 第二種做法:`_nodehome_mark_note_content` 讀節點內容全部經過 `_nodehome_reader`,跟 `_nodehome_side`(scripts/lumos:17939)、`cmd_home_check` 自己讀設定檔(scripts/lumos:18505)共用同一支讀取函式,沒有另開一條路;原本 `_nodehome_evaluate` 裡混用 `route_src`(整段範圍算的改名)與 `g["src"]`(單一提交的改名)兩套改名判斷,這次改成單一的 `name_at` 反向沿改名回推,反而收斂掉了一處潛在的雙軌。

總結:最高 severity clean,blocking 共 0 條
