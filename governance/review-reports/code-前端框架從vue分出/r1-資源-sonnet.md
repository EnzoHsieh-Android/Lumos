severity: major

資源鏡頭審完。兩條 major、兩條 minor,另有一段圖譜固定席的回答。

先講白話:新加的「Kotlin 往上找建置檔、判伺服端」那條路,用一條會在連續空白行上變成平方時間的正規式去掃建置檔,而且角色路徑每支 `.kt` 都重掃一次同一份建置檔。建置檔稍微大一點或有一段空白行,派工就會多卡幾秒到幾分鐘,而且不受任何預算約束。

## Findings

**1.**
severity: major
- blocking: 是
- diff 段落:`_KT_BUILD_ANDROID = re.compile(r"com\.android\.|libs\.plugins\.android|^\s*android\s*\{", re.M)`,在 `_kt_flavor_at` 對建置檔全文 `.search`。
- 問題:`^\s*android` 搭 `re.M`,`\s*` 會吞掉換行。遇到連續 N 個空白行,每個行首都往後吞到底再失敗,所以是 O(N²)。這條正規式在這次 diff 之前不存在,是新增的。
- 具體例:`build.gradle.kts` 內容為 `plugins { kotlin("jvm") }`、20000 個空行、`dependencies {}`,檔案只有 20KB。
  - 單次 `.search` 約 0.7s。
  - 實測 `_stack_platform_excluded`(有 `_KT_BUILD_CACHE`,只掃一次)花 0.7s。
  - 實測 `_review_roles(budget=3.0)` 只有 20 支 `.kt`,花 15.0s,`timed_out=False`。外推 300 支約 210s。
  - 純正規式量測:空行 64KB 為 7.5s,128KB 為 30s,512KB(`_ROLE_MAX_BYTES` 上限內)約 480s 以上。
- 預期:建置檔再亂,掃描也不超過幾十毫秒。實際:派工在這一步卡住,`_ROLE_BUDGET` 管不到,因為預算只管 git 讀取,管不到後面的正規式迴圈。
- 重現(正規式本身):`python3.14 -c "import re,time;p=re.compile(r'^\s*android\s*\{',re.M);t=time.time();p.search('\n'*65536);print(time.time()-t)"`,輸出約 7.5。
- 修法:改成 `^[ \t]*android[ \t]*\{`,不吞換行。
- 引句:「_KT_BUILD_ANDROID = re.compile(r"com\.android\.|libs\.plugins\.android|^\s*android\s*\{", re.M)」

**2.**
severity: major
- blocking: 是
- diff 段落:`_kt_role` 與 `_kt_flavor_at` 在角色路徑(`_review_roles` 的分類迴圈)。
- 問題:角色路徑的 reader 是批次讀好的 blobs 字典,沒有像 `_kt_worktree_text` 那樣的 `_KT_BUILD_CACHE`。每支 `.kt` 都把往上找到的同一份建置檔全文重新 `_KT_BUILD_ANDROID.search` 一次。這個迴圈在 `_nodehome_cat_blobs_capped` 之後,不再檢查 budget。
- 具體例:根目錄一份 516,933 位元組的 `build.gradle.kts`(11000 行 `implementation(...)`,沒有 android 或伺服端跡象),300 支改動 `.kt` 分在 300 個子模組。
  - 實測 `_review_roles(budget=3.0)` 總共 5.2s,`timed_out=False`。
  - cProfile 顯示分類迴圈裡 1500 次 `re.search` 共 2.56s,git 讀取約 1.5s。
  - 這個迴圈在這次改動前近乎零成本。預期:超出 `_ROLE_BUDGET=3.0` 時 `timed_out=True` 並退回只看副檔名。實際:靜默超出。
- 修法:在 `_review_roles` 內對建置檔文字做結果記憶(以路徑為鍵),或讓分類迴圈每支檢查剩餘時間。
- 引句:「reader 是派工路徑的批次讀取(起點版);沒給就讀工作樹。」

**3.**
severity: minor
- blocking: 否
- 問題:`specs += [f"{ref}:{rel}" for rel in _kt_build_candidates(p)]` 之後走的 `_nodehome_cat_blobs_capped(root, want, _ROLE_MAX_BYTES, ...)`,`max_total_bytes` 預設 None,只有單檔 512KB 上限,沒有總量上限。
- 理論最壞:300 支 `.kt` 各在獨立模組,每個模組 3 種建置檔名各 512KB,約 900 份建置檔加 300 份原始檔,全部進 `cat-file --batch` 的 stdout,再逐份 decode 成 str,記憶體約數百 MB。
- 未能重現(沒造這麼大的 repo),所以降為 minor。需要的話在這個呼叫傳 `max_total_bytes`。
- 引句:「specs += [f"{ref}:{rel}" for rel in _kt_build_candidates(p)]」

**4.**
severity: minor
- blocking: 否
- 問題:`_KT_BUILD_CACHE` 無上限,值最多 512KB 的建置檔全文。只有 pitfalls 與 hook 的單程序用,300 支上限內是有界的,不構成實際問題。
- 查過沒問題的:`_uses_vitest` 讀整份 package.json 沒有大小上限,只在 init 時跑,`json.loads` 的 `RecursionError` 已被 `_pkg_dep_keys` 接住,20 萬層巢狀實測 0.01s。順手記一筆即可,不要求改。
- 引句:「_KT_BUILD_CACHE = {}                # 鍵 = (讀取來源, 路徑):工作樹與某個版本不互相污染」

## 逐項查證結果(都實測過,沒問題)

- **新的 `node-jest` / `node-vitest` 跑過證據正規式 `Tests:?\s+[^\n]{0,200}?\b[1-9]\d*\s+passed`**:
  - 這條是線性的。
  - `Tests ` 重複 20 萬次共 1.2MB 為 0.42s。
  - 4MB 多行為 0.06s。
  - 一行 `Tests:` 後接 4 萬個 `9`,測試 S35 的情境,也很快。
  - 舊樣式 `.*?` 不限長才是二次方,這次修好了。
- **`min_lines` 與 `_n_hit`**:每行多一輪 4 個樣式,最多是原本的 2 倍,仍線性。`react-parallel` 的 `[\w{}\[\],\s]{1,80}` 與 `[^\n]{0,120}` 都有界。
- **`_linter_config_hits` / `_init_lint_hint`**:只對根目錄做固定檔名的 `is_file`,常數成本。
- **子程序、執行緒、逾時、Ctrl-C**:這次 diff 沒有新增任何子程序或執行緒。唯一的 `git cat-file --batch` 沿用既有的 `subprocess.run(..., timeout=...)`,逾時會被收掉。
- **pitfalls 路徑的批次預取上限**:`_KT_FLAVOR_CAP=300` 與 `_ROLE_READ_CAP=300` 都是依檔數計,不依候選數。300 支 `.kt` 在深度 8 的目錄下做 `_stack_platform_excluded` 只花 0.01s,因為有快取且只有 stat。
- **表態記錄**:`py-memory na` 與 `py-hotpath na` 這次不成立的是 Kotlin 判定的快取與正規式;它們在 diff 外的 Python 工具鏈程式碼,所以表態沒被直接推翻,但「沒有無上限快取」這句對 `_KT_BUILD_CACHE` 不精確(見 4)。

## 圖譜固定席(逐條判)

- **lumos-cli-read、guard-kill、lifecycle(re-inject)、design-loop、測試假綠形態等 ★INVARIANT★ 節點**:這次改動沒有碰 search 預設排除、guard kill 的 rc 與 JSON、re-inject、設計審處置閘或「還原翻紅釘」前置斷言,所以不影響。
- **pitfalls-code-loop ★RISK★、loop-convergence-recording、reversibility-governance-ledger**:不影響記帳與留痕。
- **pitfalls-code-loop 這個家**:裡面關於棧別題庫與角色鏡頭預算的前提,受上面 findings 1 與 2 影響,因為 `_ROLE_BUDGET` 的「角色計算自己最多幾秒」現在不成立。

最嚴重 severity: major,blocking 共 2 條。

相關檔案:`/Users/enzo/orca/workspaces/lumos-toolchain/web-react/scripts/lumos`(`_KT_BUILD_ANDROID`、`_kt_flavor_at`、`_review_roles`、`_nodehome_cat_blobs_capped`)。實驗用的臨時目錄已用字面絕對路徑刪除。
