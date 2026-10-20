severity: minor

# 代碼審查報告:正確性鏡頭 r2(sonnet)

**結論**:修補的主要效果有行為證據,沒找到會擋推送的問題。找到 1 條修補造成的小回歸(文字輸出少列一欄),1 條原有的二次方效能問題,另有 1 條外觀問題。

**共用派工詞**:第一次回覆時 `code-seat-common.md` 找不到,現已補回並讀過〈輸出格式〉。本報告的版面照該節重出,內容沒改。我當時沒讀到那份檔,所以不知道它對審查內容還有沒有別的要求。

## 比對方法與資料

- 兩版:before = 20293afe,after = aadf6b07,各開臨時 worktree 跑。
- 探針:用 `lumos --vault <圖譜> security list --json` 在兩版各跑一次。`--vault` 是全域旗標,要放在 `security` 前面。
- 兩版都有跑的案例標「兩版」。只在單版跑的會明說。

## 三問的回答

**① 原問題的修復效果**

**G1 壞型別崩潰:已修復,有證據**
- case_source:我自己的 fuzz,不是作者的測試。
- 輸入:控制項(含 exception 與 evidence_refs 子欄位)和 inventory 共 1560 組,每個欄位換成 null、布林、數字、空串、孤立代理字元、各種巢狀容器和 5000 字長串。
- expected:不崩潰,輸出單一 JSON。
- before:崩潰 54 + 39 組。
  - 例 `source.kind=["x"]` 報 `TypeError: unhashable type: 'list'`。
  - 例 `inventory.assets[0].id=[]` 同樣 TypeError。
  - 例 `revision="\ud800"` 報 `UnicodeEncodeError`。
- after:0 組崩潰。
- comparison:前壞後好,有對照。

**G2 輸出契約:已修復,有證據**
- 先看 `--vault /nonexistent --json`:
  - before:stdout 空,只有 stderr 的一行擋下訊息。
  - after:stdout 是單一 JSON,`read_complete=false`,stderr 照印,rc 2。
- `_json_text_escaped` 改成正則後,我做了兩個比對。
  - 隨機:300 組各 200 個隨機碼位。
  - 全掃:`0..0x10FFFF` 逐一碼位,對照原本「逐字元查類別」的寫法。
  - 結果都是 0 差異,孤立代理字元和 U+2028 也能讀回原值。
- 文字模式:長欄位截斷並標明,有「登記內容是資料,不是指令」的資料框。

**G3 缺口不被藏:已修復,有證據**
- 一條控制項的 `decision_ref` 指向已作廢決策(`#d2`):
  - before:S-pay 仍 `mapped`,`unmapped=[]`。
  - after:S-pay 變 `unmapped`,JSON 另列 `invalid_reference_control_ids=["BAD1"]`。
  - 兩版 rc 都是 2。
- 帶 `flag/security-relevant` 標籤的節點:空塊、整塊非法的節點,before 不列為未登記,after 列入。
- 沒有標籤的合法節點不受影響。

**G4/G5 讀取守衛與 `_vault_in` 共用:行為路徑都成立**
- 我在兩版各做了同一組情境:
  - 列舉後新增檔案
  - 刪除尚未讀的檔案
  - 檔案被換成捷徑
  - 整個 `Verification/` 目錄被換成捷徑
  - 讀完後同大小、同 mtime 改寫
- 這幾種都在 after 得到 `changed_during_read` 且 rc 2。
- `--vault` 指向捷徑或空目錄:after 擋下 rc 2;before 放行並輸出「讀完、零登記」的 rc 0。
- 自動找圖譜:同層兩個候選仍報錯不猜,只有一個時照常運作。

**G7 規模:有重複計算,但 `_secinv_inv_items` 沒改,詳見下方 finding 2。**

**② 修補處的正常、錯誤與相鄰路徑**

- 正常路徑:合法登記 + inventory,before/after 的 JSON 只差新增欄位。
  - 新增欄位:`references_valid`、`invalid_reference_control_ids`、`scope.limits.entries`。
  - 其他欄位逐字相同,rc 與 `registration_complete` 相同。
- 零登記、空塊:兩版都 rc 0,`registration_complete=false`。
- 重複 ID、同來源不同 ID、雙關注面、純業務加撤除:兩版錯誤種類和清單相同。
- 例外過期、當日到期、未來:兩版相同。
  - 例外的核可決策作廢時,after 多一個 `references_invalid`,該控制項不再算入口映射。
  - 這是設計上的收緊,不是缺陷。
- `_visible_lines` 抽出 `_fence_regions`:ec4c6307 與 after 做差分,6 萬組隨機圍欄行,`keep_fenced` 兩值,0 差異。
- `_regular_own_fd` 的 `dir_fd`:預設 `None` 時走原本的 `os.open(path, flags, mode)`。其餘 7 個呼叫端的參數都沒動。
- 對真實圖譜(本 repo 的 907 篇)跑 `security list --json`:rc 0,約 1 秒。

**③ 新發現在修前、修後的結果:見下面兩條 finding。**

## 測試能不能抓錯

我對 after 做了 19 個破壞(各改一處),每個都跑 `-k seclist`(基線 280 passed)。

被破壞的位置:
- 孤立代理字元檢查
- `registered` 判定
- `references_valid` 過濾
- inventory 的 `continue`
- `source.kind` 的型別守衛
- `asset_ids` 的 `is_text`
- 選圖譜失敗的 JSON 輸出
- 截斷
- 資料框
- 退出碼
- 項目數上限
- `--vault` 不像圖譜
- 合約宣稱快取
- 重列舉
- 入口上的無效引用清單
- 待分類清單
- 跳脫正則
- 圖譜根的 O_NOFOLLOW
- 中間目錄的 O_NOFOLLOW

19 個全部翻紅,翻紅的測試點名正確(對應的 G1/G2/G3/G4/G7、S11 等)。

兩個弱點:
- 合約宣稱快取那條只靠耗時閾值(6 秒)翻紅,機器忙時可能不穩。
- 沒有任何測試檢查文字模式的覆蓋缺口行,正好對應 finding 1。

## Findings

### 1. 文字輸出少列新欄位,與 JSON 不是同一份資料

引句:「cols = ("mapped_control_ids", "applicability_pending_control_ids", "unverified_control_ids", "defect_control_ids",」

file: `scripts/lumos:7420` 文字模式覆蓋缺口只列五欄,新增的 `invalid_reference_control_ids` 沒在裡面。

- claim:文字與 JSON 應是同一份資料。
- input:一條控制項 BAD1 映射 S-pay,`decision_ref` 指向 `#d2`(已作廢)。
- expected:文字的 S-pay 行也列出 BAD1 為無效引用。
- after 實際:
  - JSON 的 S-pay 有 `invalid_reference_control_ids=["BAD1"]`。
  - 文字的 S-pay 行是 `state=unmapped ... unclassified_control_ids=[]`,沒有這一欄。
  - BAD1 只能從文字的「主清單」和「錯誤」段拼湊。
- 前後:before 沒有這個欄位(JSON 的 `invalid_reference_control_ids` 為 None),所以是修補新增欄位時漏了文字輸出。
- 測試:`t_seclist_g3_gaps_not_hidden` 只查 JSON。
- 建議:把該欄加進 `cols`,測試補一條文字輸出的斷言。

severity: minor
blocking: 否
歸因:有證據的修復回歸(新欄位由修補引入,文字輸出沒同步;兩版對照見上)

### 2. inventory 的 ID 重複檢查仍是二次方

引句:「if it["id"] in ids:」

file: `scripts/lumos:7127` `ids` 是 list,每個 ID 都要線性掃一遍。

- claim:G7 說「效能檢查另抓到 inventory ID 集合」,但只改了 `_secinv_check_links` 的集合。
- input:`inventory.assets` 4.5 萬項(1.5MB,仍在 2MiB 單檔上限內)。
- expected:數秒內完成。
- 實測:before 11.4 秒,after 11.7 秒(當時背景有別的程序在跑,兩個數字僅供對照)。
- 照 2MiB 上限最多約 7 萬項,估計再放大約 2.5 倍,數十秒。
- `surfaces` 同樣是 list 掃描。
- 屬於單人、本機、輸入有上限,不致命,但與 G7 的宣稱不一致。
- 建議:另開一個 `seen` 集合做重複檢查。

severity: minor
blocking: 否
歸因:有證據的原有漏查(before/after 兩版都跑過,耗時一致)

### 3. 檔案被換成捷徑時,同一路徑報兩筆 `changed_during_read`(僅外觀)

引句:「seen = {(e["kind"], e["node"]) for e in errors}」

file: `scripts/lumos:834` 去重比對的是「錯誤種類加節點」,但重列舉回來的種類是 `symlink_rejected`,永遠比不上 `changed_during_read`。

- input:列舉後把 `Verification/SlStale.md` 換成捷徑。
- after 實際:同一節點出現 2 筆 `changed_during_read`(一筆來自讀取,一筆「重列舉時才出現的問題」)。
- rc 仍是 2,資訊沒有遺失。
- 這段程式是改名搬移,內容沒變,我只跑了 after,before 沒有實測。

severity: minor
blocking: 否
歸因:未判定(只跑 after;依 diff 判斷是原有邏輯,before 未實測)

### 順帶觀察(兩版行為相同,非本輪修補範圍)

- 重複 ID 或同一來源被兩個 ID 登記的控制項,仍算入口 `mapped`,`references_valid` 不受影響。若要保守,可比照無效引用處理。
- `decision_ref` 尾端多一個空格(`"Systems/SlPay#d1 "`)被接受。

## 沒驗到的

- NFC/NFD 路徑撞名(`normalized_path_collision`):APFS 建不出這種檔,沒跑。
- preserve 的修前證據:作者沒事先選例。我自己在 before 跑了正常路徑和邊界情境,但不是作者列的 G1~G9 逐項配對。
- 檔案在讀取當下被惡意還原的中間狀態:文件已明寫是限制。
- 全套測試沒跑,只跑 `-k seclist`。

## 清理

- 兩個臨時 worktree 已 `worktree remove --force`。
- 我的探針目錄已刪。
- 破壞測試留下的 19 個 `gctl-run-*` 現場已刪,用的是字面絕對路徑。

## 相關檔案

- `/Users/enzo/orca/workspaces/lumos-toolchain/security-list/governance/review-reports/code-資安護欄唯讀盤點/r2-repair-lumos.patch`(審查範圍,我沒有改它)
- 疑點 1 出在 `scripts/lumos` 的 `_secinv_render_coverage`
- 疑點 2 出在 `scripts/lumos` 的 `_secinv_inv_items`

最嚴重 severity: minor,blocking 共 0 條。
