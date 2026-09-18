severity: blocker

# 審稿:收工點名改量檔案樹_計劃(整合與知識同步鏡頭)

## 1. 第二份拷貝有沒有漏改

已查證:`check-graph-sync.py` 本身是 Claude/Codex 共用同一支檔(靠 `--harness codex` 與逐字稿格式自動判),不是兩支檔,所以「工具名列舉」邏輯沒有第二份原始碼副本要跟著改——閘門 2 的計算結果最終都會流進 `main()` 同一段收尾邏輯。但收尾邏輯本身內部有兩條輸出路徑,計劃沒看到這個分岔。

severity: blocker
blocking: 是,判準:S3 要求的「輸出應明講可能算進不是這輪的改動」若只加進其中一條輸出路徑,模型實際看不到,S3 名義過但目的沒達到。
引句:「★退回全量時必須明講「這次可能把不是這輪的改動也算進來」★,不要安靜地報一個看起來精確的數字」
引句:「[S3] 當取不到上一輪的基準…輸出應明講「這次的清單可能含不是這輪的改動」」
file: `scripts/hooks/claude/check-graph-sync.py:764` def stop_block_reason(rel, graph_rel, mentions) 自己組一份 reason 字串,跟 main() 裡另一份 `msg` list(:844 起)是兩個獨立變數,沒有共用的「degraded 註記」插入點。
file: `scripts/hooks/claude/check-graph-sync.py:11` 模組頭就寫明「exit 0 的 stderr 模型看不到」——`msg`(stderr,:844)是模型看不到的那條,`stop_block_reason`(:764)組出來的字串才是模型唯一看得到的那條(經 stdout 的 decision:block)。三個月後的人若照 S3 字面把提示加進「正在講的那段 msg」,很可能只改到 stderr 那份,模型永遠看不到降級警告,而這正是本計劃反覆強調要防的「看起來正常運作」。

severity: blocker
blocking: 是,判準:S5 只要求存放位置在工作樹之外,沒有要求跟會談身分綁定,而計劃自己舉的動機案例(共用工作目錄)剛好會撞上這個洞。
引句:「基準檔不能放在 repo 的工作樹裡。…放會談自己的暫存目錄。」
引句:「當天同一個主 clone 上同時有三個會談;任何「工作樹上有什麼就是我改的」的假設在這裡都不成立。」
「會談自己的暫存目錄」沒說怎麼跟「哪個會談」綁定(用 session_id?固定路徑?),而本專案已有現成反例。
file: `scripts/lumos:12593` 明寫「鎖檔放 ~/.cache/lumos/vault-lock/(照 dispatch-lens 快取的先例:不放共用暫存目錄——路徑可預測、會被別的使用者先佔)」——這正是計劃想避免的場景:若基準檔路徑不是逐 session 命名,兩個同時在跑的會談會互相蓋掉對方的基準快照,診斷結果變成隨機錯,比修前的「固定少報」更難查。
file: `scripts/hooks/claude/impact-hook.py:172` 本專案既有的作法是手動把 session_id 織進路徑(`tempfile.gettempdir()/lumos-impact-{session_id}/...`),不是單純丟進「暫存目錄」;計劃沒有引用這個既有先例,也沒有說要不要跟進。

## 2. 落點(`Systems/graph-sync-coverage`)塞不塞得進去

已讀,無 finding。該節點目前 52 行、`about_code` 只列 2 支檔(`check-graph-sync.py`、`scripts/lumos`),掛的計劃不算多,不是大雜燴節點,落點合理。

## 3. 接手的人一定會問但計劃沒交代的事

severity: major
blocking: 是,判準:合併後若沒人手動重跑安裝,真正在跑的 Stop hook 仍是舊版,S1–S6 的測試全綠但線上行為沒變,等於白修。
引句:「退回方式:把那支 hook 還原成改動前的版本(單檔還原,不牽動其他檔),並刪掉基準快照目錄。」
計劃通篇沒提到改完 repo 裡的 `scripts/hooks/claude/check-graph-sync.py` 之後,還需要 `lumos install --force`(或 `lumos update`)才會把新版同步進實際觸發用的 `~/.claude/hooks/`、`~/.codex/hooks/`。
file: `docs/lumos-toolchain-knowledge/Projects/Codex行為精修_計劃.md:116` 改同一支檔的前例明寫驗收要含「`lumos install --force` 後 `~/.codex/hooks/` 與 `~/.claude/hooks/` 的 check-graph-sync 與 repo 同檔(cmp 相同)」,本計劃的「驗收條件」四條裡沒有等價的一條。
file: `scripts/lumos:15484` 全域同步只在 `_vendor_toolchain`(即 `lumos install`/`lumos update`)裡才會跑,沒有 pre-commit/pre-push/CI 會自動檢查已部署副本是否落後——已實測 `~/.claude/hooks/check-graph-sync.py` 目前確實落後於 repo 最新一版(缺 2026-09-16 那次 `_mkdir_under_home` 重構),證明這個落差是真的會發生、不是假設。

severity: minor
blocking: 否,判準:不影響正確性,只影響長期維運整潔度,漏了不會讓測試翻紅。
引句:「做法:每次收工存一份快照(工作樹相對上次提交的檔案清單與雜湊),下一次跟上一次比,差集就是這一輪。」
計劃沒說這份快照誰清、多久清一次——本專案同類狀態檔都有明講的保留期,例如 `~/.cache/lumos/bound-filter/` 保鮮 14 天、Stop 擋停標記保留 7 天,這篇沒有對應的一行。
file: `scripts/lumos:26988` 「結果按 (root, run_cmd, 判定規則版本) 快取在 ~/.cache/lumos/bound-filter/,保鮮 14 天」可當直接可抄的先例。

severity: minor
blocking: 否,判準:格式演進屬未來擴充問題,現在寫不寫版本欄不影響這次驗收條件能否過。
快照格式(檔案清單+雜湊)沒有版本欄或格式標記;若之後改雜湊演算法或欄位,舊快照要嘛讀壞要嘛被誤讀成「跟現在不一樣所以整批算改動」,計劃沒交代哪一種是預期行為。
file: `scripts/lumos:26988` 同一段快取先例已經把「判定規則版本」納入快取鍵,是本專案已有的解法模式,計劃可以借用但沒提。

severity: minor
blocking: 否,判準:不影響本次條款的正確性,只是遺留複雜度沒人管。
計劃完全沒提 Codex 逐字稿解析那一整段(`CODEX_TRANSCRIPT_VERSIONS` 版本白名單、`_CODEX_EXEC_CMD_RE`/`_CODEX_APPLY_PATCH_RE`)——量檔案樹上線後,這段還是不是「算改了哪些檔」唯一剩下的用途只是閘門 1(這輪有沒有做過事)?沒交代要保留、簡化還是繼續兩邊各自維護。
file: `scripts/hooks/claude/check-graph-sync.py:117` `CODEX_TRANSCRIPT_VERSIONS = {"0.144.1", "0.153.2"}` 與 `:137` `collect_codex_turn_actions` 是目前唯二消費 Codex 逐字稿格式的地方,量檔案樹上線後其存在理由需要重新交代一次,否則三個月後的人不知道能不能砍。

## 4. 跟提交前/推送前兩道閘的關係

已讀,無 finding。落點節點本身的「三個時機」表已把 Stop hook / pre-commit / pre-push 三者分工寫清楚(各自的資料來源與時機),回退段也明講「真正擋住壞改動的仍是提交前那道閘」,計劃沒有製造新的三閘重疊點名問題——pre-commit/pre-push 本來就已經是版本控制比對,不受這次改動影響。

## 5. 條款 S1–S6 逐條檢查

- S1:已讀,無 finding。指向具體測試名,可判。
- S2:已讀,無 finding。「印出的數字應等於清單長度」是可機械驗的不變量,具體。
- S3:見「1. 第二份拷貝」裡的 blocker——條款本身沒說清楚要涵蓋哪一條輸出路徑。
- S4:已讀,無 finding。「每輪重取基準」判準清楚,對應測試名具體。
- S5:見「1. 第二份拷貝」裡的 blocker——只要求工作樹外,沒要求跟會談身分綁定。
- S6:已讀,無 finding。「內容雜湊、不只比時間與大小」判準明確,好照著驗。

## 總結

最嚴重等級:blocker。blocking 共 3 條(S3/S5 輸出路徑分岔各一條算作同一組風險已合併敘述、共 2 條 blocker 引述 + 1 條 major 部署缺口),另有 3 條 minor(保留期、格式版本欄、Codex 解析段落去留)不計入 blocking。
