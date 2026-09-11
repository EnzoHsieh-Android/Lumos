severity: minor

## r1 分組核對(架構對齊鏡頭相關,供編排者核對,非 finding)
- G5(major,原架構席 F3:「同一份清單」其實是四份副本、主程式裡沒有):修到——[S1] 新增第五份具名常數並接進一致性測試(擴成五份一致),明文不借用 `CODE_EXTS_T`。file: `scripts/lumos:17360-17363` `_NODEHOME_CODE_EXTS` 常數與註解;`scripts/test_lumos.py:7595-7618` `t_code_exts_four_lists_agree` 已擴成比對五份清單。
- G31(minor,原架構席 F4:規則五該落在設計審那篇,不該塞進新開的那篇):修到——落點段新增「更新 `Systems/design-loop`」一項,新開篇 responsibility 明寫「不管設計審出口(那在 design-loop)」。file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:35` 已落對應 KEY 行(落點第六步、四問第四題)。
- 架構席原 clean 的 F1/F2(分層、命名)這輪重查仍成立:提交前/推送前掛鉤只呼叫 `lumos home check`,沒有自己重寫判定;`node_home.max_files`、`_KNOWN_GATES`、`_STATS_NODE_SEMANTICS` 都沿用既有家族寫法(見下方佐證)。

### F1 [S38] 跟名詞段「讀哪個版本」對「要不要批次讀取」自相矛盾,是本輪修訂沒接好的縫
severity: minor
blocking: 否 — 程式與測試都照名詞段(非批次)做,矛盾只留在文字裡,沒有真的變成第二套實作
引句:「提交前只讀提交索引、推送前只讀範圍兩端的提交，一次批次讀取」
file: `scripts/lumos:17512-17527` `_nodehome_reader` 實際邏輯是「跟磁碟一樣的直接讀,不一樣的才用 git show 讀」,不是批次讀取
file: `scripts/lumos:13519` `_vendored_state` 的註解「第四輪架構席:第三輪另寫了一套 cat-file --batch 解析」正是名詞段說「架構審查曾把另寫一套批次讀取判成第二種做法退回」那個前例,佐證這條規矩是真的、[S38] 卻寫反了
file: `scripts/test_lumos.py:36088` `t_nodehome_reads_index_not_worktree` 只測「讀索引不讀工作目錄」,沒有任何批次讀取的斷言,跟 [S38] 掛的這個測試名對不上它現在寫的內容
名詞段「讀哪個版本」與「實作時對計劃的修訂」段都已改成「直接讀＋git show」,但 [S38] 與「提交變慢」隱患段的處置句(同一份 spec)仍留著「一次批次讀取」沒跟著改;若之後有人只讀 [S38] 去改實作,會做出這個 repo 已經否決過一次的批次讀取。

總结:最高 severity minor,blocking 共 0 條
