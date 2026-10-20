severity: major

# 報告:code-資安護欄唯讀盤點 r3 通才-sonnet

比喻:r2 修補像給水龍頭加了限流閥,但閥是每個水管各一個,水管本身可以無限多。另一處是門檻查了「正規化後的路徑」,實際開的卻是「原始字串」。

**實跑範圍**:after 版跑 `-k seclist`,326 項全過;跑 `-k retro`,357 項全過。再把修後的 `r2` 守護測試套在修前的 `scripts/lumos` 上,24 項過、21 項紅,測試能分辨修前修後。

## Finding 1:錯誤上限是「每個節點」,不是全域,輸出仍隨檔案數無界放大

severity: major
blocking: 是

引句:「_SECINV_ERRORS_PER_NODE = 50     # 錯誤清單每篇最多逐筆記幾筆,超出併成一筆 errors_truncated」

失敗場景:
- 輸入:6000 個節點,每個約 322 B(總共約 1.9 MB),每個節點一個含 60 個 `{}` 控制項的 `lumos-security-v1` 圍欄。
- 預期:R4 要的是「輸出有界」。
- 實際(修後):`security list --json` 輸出 89,524,977 位元組;文字模式 76,619,145 位元組、耗時 28 秒。
- 實際(修前,同一輸入):105,774,987 位元組。修補只少了約 15%。
- 上限是節點數(最多 10000)乘以 51 筆,沒有全域總量上限。

測試缺口:`t_seclist_r2_error_cap` 只造兩個節點(`SlEmpties`、`SlFences`),斷言 `< 500_000`。多節點放大完全沒被量到。這正是本席鏡頭的「修之前先對大型輸入跑效能檢查」。

歸因:有證據的原有漏查(修前 105 MB,修後 90 MB,同一輸入)。作者宣稱 R4 已修,但只修了單節點情形,屬修補深度不足。
- 兩版命令:`python3.14 <版本>/scripts/lumos --vault <many/docs/k-knowledge> security list --json | wc -c`
- 修前 105,774,987,修後 89,524,977。

## Finding 2:`--vault` 路徑中「捷徑加 `..`」可繞過 R2 的檢查,讀到 repo 外

severity: minor
blocking: 否

引句:「p = Path(os.path.abspath(str(p)))」

失敗場景:
- 輸入:`--vault <repo>/docs/link/../k-knowledge`。`link` 是指向 repo 外 `outside/inner` 的捷徑;repo 內另有合法的 `docs/k-knowledge`;`outside/k-knowledge/Systems/Secret.md` 含 `OUTSIDE-SECRET-CLAIM`。
- 預期:R2 說「從 repo 根到圖譜之間任一層是捷徑都拒讀」,應退出 2。
- 實際:檢查用的是 `abspath` 消掉 `..` 後的路徑,看起來沒有捷徑;`_secinv_select_vault` 回傳的卻是原始 `Path(vault_arg)`,作業系統照 `link/..` 開到 repo 外。輸出含 `OUTSIDE-SECRET-CLAIM`(`grep -c` 為 1)。
- 單人加 AI 的威脅模型下,這要靠人手工拼這種路徑,實際風險低,所以列 minor。

測試缺口:`t_seclist_r2_docs_symlink` 只測 `docs` 本身是捷徑,以及 `--vault` 指進去,沒測含 `..` 的繞行。

歸因:有證據的原有漏查。修前同一命令也是 1;`docs` 直接是捷徑的案例,修前 1、修後 0(被擋),所以 R2 的主要路徑確實修好了。

## Finding 3:整合測試 ⑤′ 與 ② 的 fixture 分不出「改過」與「沒改過」,斷言對不上宣稱的差異

severity: minor
blocking: 否

引句:「check("整合⑤ 來源改了但紀錄仍 pass:只到 declared_only,並列「來源修訂與證據適用性未核對」」

失敗場景:
- 輸入:`I-SRCCHANGED` 只把 `revision="r2-改過需求"` 換掉。`來源修訂與證據適用性未核對` 是 `_SECINV_RECORD_LIMITS` 的常數,每條紀錄都帶。
- 預期:測試名宣稱「來源改了」這個條件有被偵測。
- 實際:把 `revision` 還原成 `r1`,斷言照過。`I-ORACLE` 與預設紀錄也只差 id,同理。
- 這兩列等於重複驗了「pass 只到 declared_only」。docstring 已承認盤點層分不出來,所以不算假綠,但這兩列沒有獨立的失敗路徑。
- 母計劃六項整合反例:① 到 ⑥ 都有對應斷言,盤點層的預期(只列缺口、保持 `not_assessed`)大致涵蓋。
- ④ 的「相關證據仍未驗」是空斷言,因為 `unverified_control_ids` 恆為全部非 retired 控制項(`scripts/lumos` 的 `_secinv_surface` 一帶)。

歸因:未判定。這是測試在寫入時就有的設計,沒有修前版可比。

## 三問的回答

1. **原問題的修復行為證據**:`r2` 守護測試套在修前版 `scripts/lumos` 上是 24 過、21 紅,例如:
   - R2 docs 捷徑:修前 grep 為 1,修後被擋。
   - R3 非 Verification 證據:修前不列錯誤,修後 `references_valid=false`。
   - R4 決策快取:修前 45.6 秒,修後在 12 秒內。
   - R4 asset 查重:修前 16.6 秒,修後在 8 秒內。
   - R1 stderr 控制字元:修前有 U+0007、U+001B、U+3164,修後乾淨。
   - R7 changed_during_read:修前兩筆,修後一筆。
   - 修了的部分,修前紅、修後綠,證據成立(case_source:r2 守護測試自帶輸入)。R4 的「輸出有界」只在單節點成立,見 Finding 1。
2. **修補處正常與相鄰路徑**:
   - `_read_fd_capped` 抽出後,`-k retro` 357 項全過,`_vault_safe_read_rel` 的 `t_seclist_g8_read_request_bound` 與 `s10_size_caps` 仍過。
   - `no_duplicate_defs` 守衛:在副本新增重名頂層 def,該測試轉紅,守衛有效(拿掉實作確認會紅)。
   - 沒有捷徑的 repo 照常退出 0(R2 對照組)。
   - 相鄰路徑缺口只有 Finding 2。
3. **新發現同案例的修前修後**:Finding 1 修前 105,774,987 位元組、修後 89,524,977 位元組。Finding 2 修前、修後都讀到外部內容。Finding 3 沒有前後可比。

**未驗範圍**:未跑全套;preserve 案例只做了 retro 子集,沒有逐一造修前基準。文件(R7)的句子沒逐條核對。測試暫存已清掉我自己建的兩個 `gctl-run-*`、`-work` 與 `-mut` 目錄,兩個 worktree 已移除。

最嚴重 severity:major,blocking 共 1 條。
