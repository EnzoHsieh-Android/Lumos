severity: major

# 代碼審第 3 輪 正確性席(正確性-opus)

主審材料:r3-delta.patch(a660e0f6..97f57017)。實驗都在自己的 clone(`pcc-r3-work-正確性-opus/repo`,HEAD 97f57017)跑,
對照組 `lumos_base_a660`(第 2 輪修正前)與 `lumos_pre_d8b0`(整個功能之前),實驗腳本留在 `pcc-r3-work-正確性-opus/` 下。

## 已核對、沒問題的部分

- 加入與移出用的是同一個字串:兩處都是 `target`(`os.path.realpath(os.path.join(wt, file))`)。實測第一條寫 `a.py`、第二條寫 `./a.py`:
  第一條還原沒錯開 → 第二條重寫成功就移出,第二、三條記成強證據(第 2 輪前的版本第二條仍記弱);判斷正確,壞法寫入時間全新、Python 會重編。
- 寫後確認成功時移出、在檢查「清單是否非空」**之前**移出:這一條自己重寫的那支檔不會把自己標成弱,正確。
- 清單非空時被判 drifted、路徑逃逸、test 名不合法、檔開不了的那幾條沒記弱:這幾條都不是 killed,背書只認「非弱的 killed」
  (`_backing_judge_groups` 裡 `r["verdict"] == "killed" and r["weak"] is not True`),所以不記也不會漏;drifted 是讀原始碼文字判的,不經編譯快取。
  例外是 abort(baseline 要跑測試),見 F1。
- 多平台:`mstate` 在每一組的迴圈裡重建,各組各自一個 worktree,清單不跨組。
- 還原失敗 `break`:在加入清單之前就跳出,本組後面不再跑,清單不再被用到,沒問題。
- 重試函式單調性:`state["w"]` 只增不減,任何之後「確認成功」的寫入修改時間都嚴格大於舊快取記的那個秒,所以「重寫成功就移出」這個前提成立。

## F1 清單非空時跑出來的 baseline 會被快取,清單清空後的配方沿用它,做出假的強證據 killed
severity: major
blocking: 是
引句:「mt_ok = mt_ok and not mstate["unsure"]」
file: `scripts/lumos:13955`
file: `scripts/lumos:13958`
file: `scripts/lumos:13960`

1. 第 2 輪修正的前提是「舊快取只留在那支檔裡,那支檔重寫成功就乾淨了」。但污染還有第二條出路:同一組裡第一次出現某個測試指令時要先跑 baseline,
   baseline 結果存進 `baselines[cmd]`,之後同指令的配方一律沿用、不重跑。清單非空時跑的 baseline 會吃到還原沒還乾淨的舊快取,這個結果被快取下來;
   等那支檔重寫成功、清單清空後,後面沿用這份 baseline 的配方就記成強證據。
2. 會判錯的方向:HEAD 上本來就紅的測試,在舊快取(殘留的壞法)下碰巧是綠的 → baseline 誤判成綠 → 本該 `abort`(rc2)的配方被拿去跑壞法,
   測試本來就紅所以必定 `killed`,而且清單已清空 → `weak=false`,進背書成為強證據。反方向(baseline 誤判成紅)只會 abort,是擋下的方向,不算漏。
3. 重現(`exp_baseline.py`,用替身把第一條「還原」的修改時間設回壞法那一秒並回 False,等同粗精度檔案系統上真的撞秒,大小也相同,Python 會真的載入舊的 .pyc):
   - 三條配方:①`a.py` `A = 1`→`A = 2`,測 TestOne(A==1);②`b.py` `B = 1`→`B = 2`,測 TestTwo(A==2 且 B==1,**HEAD 上本來就紅**);
     ③`a.py` `A = 1`→`A = 1 `(只加空白,語意不變),測 TestTwo。
   ```
   $ python3 exp_baseline.py repo/scripts/lumos collide      # 97f57017
   rc = 0
   TestOne a.py 'A = 2' killed weak= True
   TestTwo b.py 'B = 2' killed weak= True
   TestTwo a.py 'A = 1 ' killed weak= False      ← 只加空白的壞法、測試本來就紅,卻記成強證據
   $ python3 exp_baseline.py repo/scripts/lumos normal       # 同一份程式、不撞秒 = 正確答案
   rc = 2
   TestOne a.py 'A = 2' killed weak= False
   TestTwo b.py 'B = 2' abort weak= False baseline 非綠(rc=1)
   TestTwo a.py 'A = 1 ' abort weak= False baseline 非綠(rc=1)
   ```
   第 2 輪修正前(a660e0f6)跑 collide 結果一樣(rc0、第三條 weak=False),所以不是這次修正新引進的,但這次修正宣稱的保證
   「清單非空時這一組後面每一條都記弱證據、檔重寫成功才移出」因此不完整:污染經 baseline 快取帶到清單清空之後。
4. 觸發要同時成立:寫後確認失敗(粗精度檔案系統或時鐘異常)+ HEAD 上有本來就紅、但在殘留壞法下會變綠的測試。機率低,但輸出正好是這個功能要防的那一類錯(假的強殺進背書)。
5. 建議改法(擇一,都很小):baseline 存進快取時一併記「跑的當下清單是否非空」,沿用這份 baseline 的配方一律記弱;
   或清單從非空變空的那一刻,把清單非空期間跑出的 baseline 從 `baselines` 拿掉,下一條重跑。補一支對應的釘(上面的三條配方即可)。

## F2 還原用配方原字串、寫入與確認用 realpath:配方檔是符號連結時根本沒還原,寫後確認還把它「碰」成功,後面每一條都在壞掉的樹上跑
severity: major
blocking: 是
引句:「rv = subprocess.run(["git", "-C", wt, "checkout", "--", r.get("file", "")],」
file: `scripts/lumos:13965`
file: `scripts/lumos:13995`

1. 派工詞問「realpath 跟還原用的路徑一致嗎」:清單的加入/移出彼此一致(都用 `target`),但**還原本身**不一致。壞法寫進 `target`(realpath),
   還原卻是 `git checkout -- <配方原字串>`。配方的 file 是 git 追蹤的符號連結(指向 worktree 內另一支檔)時,路徑圍欄放行,
   壞法寫進連結指向的真檔;checkout 只還原連結本身(本來就沒變),回傳 0;真檔維持壞法。
2. 本次改動讓這個舊洞更隱形:還原後的 `_kill_after_write(target, …)` 讀到真檔修改時間沒變(還是壞法那一秒)→ 等 1 秒、`os.utime` 碰成現在 → 回 True,
   等於替一個沒發生的還原「確認成功」,也不會進清單、不會記弱。
3. 重現(`exp_symlink.py`,不用任何替身):`link.py -> real.py` 進版控;①file=`link.py` `R = 1`→`R = 2` 測 TestOne(R==1);
   ②file=`b.py` `B = 1`→`B = 1 `(只加空白)測 TestOne,正確答案是 survived(rc1)。
   ```
   $ python3 exp_symlink.py repo/scripts/lumos       # 97f57017
   rc = 0 | stderr:
   TestOne link.py 'R = 2' killed weak= False
   TestOne b.py 'B = 1 ' killed weak= False        ← 語意不變的壞法記成強殺,因為 real.py 還停在 R = 2
   $ python3 exp_symlink.py lumos_pre_d8b0          # 整個功能之前
   (同上,rc = 0、兩條都 killed weak=False)
   ```
4. 這是功能之前就有的洞(d8b02331 一樣重現),不是本輪修正引進;放在這裡是因為它正落在派工詞點名的「realpath 跟還原用的路徑」,
   而且本次新增的寫後確認把它從「修改時間對不上」的潛在訊號變成主動確認成功。收貨端若依規則把舊洞轉 Issue,請在 Issue 附上面的重現。
5. 建議改法:還原改用 `os.path.relpath(target, wt_real)`(跟寫入同一支真檔);或在圍欄那一步就拒收「`os.path.join(wt, file)` 的 realpath 不等於它自己的正規化路徑」的配方(符號連結一律不收)。

## F3 「重寫成功就移出」這條路沒有測試釘住:兩處移出都拔掉,guard_kill 全部 254 支照綠
severity: minor
blocking: 否
引句:「mstate["unsure"].discard(target)」
file: `scripts/test_lumos.py:60616`

1. 新的第 ④ 項只驗「a.py 之後沒被重寫 → 三條都弱」(加入的方向);沒有任何一項驗「那支檔重寫成功後,後面恢復強證據」(移出的方向)。
2. 翻紅實驗:在 clone 裡把兩處 `mstate["unsure"].discard(target)` 都換成 `pass`、清 `__pycache__`,跑 `python3 scripts/test_lumos.py -k guard_kill` → `254 passed, 0 failed`。
   同一份拔掉移出的程式跑 `exp_clear.py`(第一條還原撞秒、第二條 `./a.py` 重寫、第三條改 b.py)三條全變 weak=True;正確版本是後兩條 weak=False。
3. 後果是單向的(只會多記弱、不會漏記),但多記弱會讓背書失去本來有的強證據。補一支「還原撞秒 → 同一支檔下一條重寫成功 → 之後恢復強證據」的釘即可(上面的 exp_clear 三條配方可直接搬)。

最高等級:major
