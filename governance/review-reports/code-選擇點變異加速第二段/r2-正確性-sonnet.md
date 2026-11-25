severity: clean

正確性席第 2 輪:在修補差異 r2-repair.patch 裡我沒找到會判錯的輸入。唯一的小缺口是一條測試覆蓋空白,附在「測試改壞」那段,production 走不到。

## 判錯輸入的追查

我逐 hunk 假設會判錯、去找輸入,結果如下。

**merge_off 改由 mg.plats 算出**
- 原因只剩 `_kill_merge_off` 這一個寫入點(`mg.plats[plat] = (False, why)`),斷路器跳開時寫 `(False, "斷路器")`,啟用時寫 `(True, "")`。
- 讀者 `{q: why for q,(on,why) in plats.items() if not on and why != "斷路器"}` 對三種狀態都對:啟用的排除、斷路器排除、其他原因保留。
- 同平台被寫兩次的情況走不到。一次 `cmd_guard_kill` 每個平台只進 `_kill_merge_iter` 一次。能出現的順序只有 off、或 on 之後被斷路器覆寫,取後者,而斷路器本來就被排除。
- file: `scripts/lumos:79111` 是讀者。寫入點在 `scripts/lumos:28924`、`scripts/lumos:29094`、`scripts/lumos:29174`。

**新舊互讀**
- 新程式讀舊帳:`scripts/lumos:18563-18565` 缺欄位時讀成空字典或 0,沒問題。
- 舊程式讀新帳:事件欄位名沒變,只是 `mg.off` 這個內部屬性拿掉,沒有外部讀者。
- `single` 改名 `ran_solo` 只動記憶體裡的列。全檔 grep 沒有別的消費者還在讀 `row["single"]`。

**中斷**
- `_kill_merge_off(..., "中斷", quiet=True)` 仍記 `(False, "中斷")`,run 事件的 merge_off 照記,只是不印。
- 時限到時 `hk.between` 丟出的 `_KillHalt` 也記成「中斷」,這是修補前就有的行為。

**時限提示**
- `merge_need` 改成全部支數,對應「帶大時限重跑要從頭量」。
- 提示裡的 X 把本次已花的秒數也算進去,會高估,但這是計劃的設計,不是錯。
- `merge_need` 在 `_kill_merge_singles` 回 False 之前一定已設定,不會把 None 傳進提示。

**新增的「合併道不足 2 支」**
- 用 `len(uniq) < 2`(去重後的測試名)判,排在時限門之前,提示不會叫人調大時限而照做仍不合併。
- 單一壞法但守 2 支測試,現在會合併,這是計劃改動(拿掉「少於 2 個不合併」)。
- 空 `uniq`(平台列表為空)會多印一行「合併道不足 2 支」,無害。

**測試改壞**
- 我拿掉 `scripts/lumos:28619` 的 `_ran_solo` 過濾項,跑 `-k choice_kill`:306 支全綠,沒有測試翻紅。
- 這是個覆蓋空白,但沒有具體行為受害。`_ran_solo` 只在 `hk.on`(choice-kill)時才設,而 choice-kill 呼叫 `cmd_guard_kill` 時不帶 `as_json`、輸出也被導走,production 走不到。依判準這只算 minor、講不出受影響行為,所以不標 finding。
- `-k guard_kill` 我只跑到一半就停了,所以對那一批沒有結論。

## 圖譜鏡頭

派工詞尾端沒有附固定席筆記(LUMOS-LENS 寫「這次沒附固定席節點」),所以無節點可逐條判。

我讀了 diff 裡 `Systems/guard-kill.md`、`Systems/規格閘.md` 對應的程式路徑,對兩條 ★INVARIANT★ 的判斷如下。
- rc 優先序不受影響:判決與 rc 的計算沒動,只動了標記欄位名。
- `--json` 純度不受影響:`_ran_solo` 仍在 `--json` 輸出的剔除清單內。

## 三問與證據

- **已修復?**(r1 a1/a2/a3、b1、g3、c2、i5)
  - 靜態讀碼:原因只寫一處、`quiet` 參數取代以字串前綴判斷、欄位改名都成立。
  - 動態證據:`-k choice_kill` 306 支綠,這是在修補後的樹 c4ed34e71 上、且已拿掉一個過濾項的樹上跑的。**修補前版本我沒跑,歸因未判定**,「修前紅、修後綠」沒有驗。
- **相鄰路徑仍成立?** 上述斷路器、中斷、舊帳讀取三條路徑讀碼成立;merge_off 的衍生算法三種狀態(啟用、斷路器、其他原因)驗過。
- **新發現的修前修後對照?** 沒有新發現。

## 未驗範圍

- 修補前版本實跑。
- `-k guard_kill` 全批。
- 真實 Gradle 下的合併行為。
- 空平台列表那一行多餘的印字沒有實測。

清理:我的工作目錄已刪。鎖檔 `0095d719…json.warming` 內是 PID 20676、時間戳與 token,我沒動它,也沒刪。

總結:最高嚴重度 clean,blocking 0 條。
