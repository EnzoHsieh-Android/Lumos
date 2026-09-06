severity: blocker

- [blocker] `_trusted_lumos()` 仍可被 PATH 或 `$LUMOS_HOME` 導向攻擊者程式，「可信來源」判定不成立
  引句:「解析順序:系統裝好的 → $LUMOS_HOME 指的 → 預設來源位置 → 都沒有就回 None。」
  位置:governance/review-reports/code-audit-batch7/r1-snapshot.patch:26
  blocking:是
  why:輸入＝PATH 首項放攻擊者可執行的 `lumos`，或令 `LUMOS_HOME=<攻擊者目錄>` 且其中存在 `scripts/lumos`；預期＝只接受經安裝器核可、owner/權限/固定位置驗證過的 CLI；實際＝`shutil.which("lumos")` 找到即回傳，`LUMOS_HOME` 也只驗 `is_file()`。hook 會用 `sys.executable` 執行該檔，沒有 owner、group/other writable、symlink、來源根或雜湊檢查。PATH 通常由啟動 Codex/Claude 的 shell、IDE、wrapper、direnv 等控制；若含 `.`、空 PATH 元素或 workspace-local bin，打開專案即可重新落回任意碼執行。`LUMOS_HOME` 同樣是未驗證的繼承環境變數。

- [blocker] 全面搜尋發現 `dispatch-lens-hook.py` 仍會退回執行當前專案的 `scripts/lumos`
  引句:「★只執行「可信來源」的 lumos,絕不執行被打開那個資料夾裡的碼★」
  位置:governance/review-reports/code-audit-batch7/r1-snapshot.patch:16
  blocking:是
  why:輸入＝全 repo 搜尋 `scripts/lumos`、`which("lumos")`、`LUMOS_HOME` 與 subprocess 呼叫；預期＝所有自動 hook 都不執行 workspace 程式；實際＝未納入本 diff 的 `scripts/hooks/claude/dispatch-lens-hook.py:59-63` 仍先 `shutil.which("lumos")`，找不到後以 `Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "lumos"` 回退。該 hook 複製進消費專案後，此路徑正是消費專案根下的 `scripts/lumos`，並在 claim 路徑由 Python 執行。新增測試只掃三支 hook，故不會抓到第四支。

- [major] `_trusted_private_dir()` 無法偵測中間層 symlink；同一路徑與自身解析結果相比必然相等
  引句:「整條路徑都沒有經過 symlink——拿「解析過的預期路徑」對照」
  位置:governance/review-reports/code-audit-batch7/r1-snapshot.patch:594
  blocking:是
  why:輸入＝實際存在的多層路徑 `/var/tmp`，其中 `/var` 是 symlink、leaf `/var/tmp` 不是 symlink；預期＝「整條路徑沒有經過 symlink」檢查應拒絕；實際＝`d.is_symlink()` 為 False，`d.resolve()` 與同一 lexical expected 的 `resolve()` 都是 `/private/var/tmp`，比較為 True。`_lens_cache_write(path.parent, path.parent)` 完全自比；`_lens_arm_dir_ok()` 的 expected 又由同一個 `_lens_armed_root()` 加 `Path(d).name` 組成，因此固定前綴內的 symlink 也在兩邊同步解析而消失。沙盒禁止建立 `/tmp` fixture，因此另外採系統既有的多層 symlink 實測；結果已足以否證註解宣稱。

- [major] `_lens_arm_dir_ok()` 的 basename 組法只擋「整體解析後落點不同」，擋不住固定前綴被換成 symlink
  引句:「預期路徑 = 固定前綴 + 這個 d 的名字。」
  位置:governance/review-reports/code-audit-batch7/r1-snapshot.patch:629
  blocking:是
  why:輸入＝`d=_lens_armed_root()/指紋`，並把 `_lens_armed_root()` 的中間層改成指向另一個同 owner、0700 目錄的 symlink；預期＝中間層 symlink 被拒；實際＝expected 使用同一個 `_lens_armed_root()`，最後一段又直接抄 `Path(d).name`，兩邊解析到完全相同目標而通過。這條能擋傳入任意外部路徑、不同 basename 或 leaf 本身為 symlink；不能證明 prefix 是原本那棵目錄。

- [major] 檢查與 `rmtree`／`mkdir`／`chmod`／寫檔之間仍有可利用 TOCTOU
  引句:「if not _lens_arm_dir_ok(d):   # 建完再驗一次:剛才那一瞬間被換掉也擋得住」
  位置:governance/review-reports/code-audit-batch7/r1-snapshot.patch:673
  blocking:是
  why:輸入＝同 UID 攻擊程序在第一次檢查後、`shutil.rmtree(d)` 前以 rename 換入另一個真目錄，或在第二次檢查後、`meta.json`/token 寫入前換掉目錄；預期＝破壞性操作綁定到已檢查的 directory object；實際＝每一步都重新按 pathname 查找，沒有 dirfd、`O_NOFOLLOW`、inode/dev 重驗或鎖，檢查結果不約束後續 syscall。新增測試只計算 `would_delete` 後執行 `pass`，沒有實際呼叫 arm/disarm，也沒有競態，因此無法覆蓋此縫。

- [major] 注入消毒只處理 `matched_by` 與 contract；節點名及其他 additionalContext 通道仍可帶自由文字
  引句:「注入段要有框,而且框裡不准有圖譜的自由文字」
  位置:governance/review-reports/code-audit-batch7/r1-snapshot.patch:151
  blocking:是
  why:輸入＝圖譜節點檔名含換行、框線文字或提示指令，或 repo 控制的 `.ci-log.jsonl` 把 `workflow`、`failed_step`、`url` 寫成指令；預期＝所有 repo-controlled 值正規化為固定字彙且所有 additionalContext 有不可混淆的結構邊界；實際＝impact 仍原樣插入 `node`、`via`，框也沒有 escaping，內容可自行印出「參考資料結束」再偽造新段。全面搜尋另找到 `ci-status-hook.py:95` 直接把 repo log 欄位放入未框的 SessionStart additionalContext，`dispatch-lens-hook.py:101` 也直接轉送 `text`。所以兩條 builder 加框不等於所有注入路徑已收口。

- [minor] anchor roster 可用排除目錄或副檔名藏檔，且一般暫存檔會造成反向噪音
  引句:「if "__pycache__" in _f.parts or _f.suffix in (".pyc", ".pyo"):」
  位置:governance/review-reports/code-audit-batch7/r1-snapshot.patch:500
  blocking:否
  why:輸入＝`scripts/hooks/__pycache__/evil.sh`、可執行但名為 `evil.pyc`，以及正常的 `.DS_Store`、編輯器 swap/backup；預期＝只排除能被可靠辨識為產物且不可能註冊執行的檔，正常非 hook 雜檔不擋推；實際＝前兩者無條件排除，任何其他 regular file 則加入 `_present` 並令 verify 翻紅。它不能單獨繞過已錨定的註冊設定，但「所有自動執行 hook 的檔案集合」宣稱過強，也容易形成拒絕服務式噪音。

- [clean] 三支 `_trusted_lumos()` 複本在凍結版本中逐字相同
  引句:「三支 hook 的解析函式逐字相同(改一支忘了另兩支,破口會悄悄長回來)」
  位置:governance/review-reports/code-audit-batch7/r1-snapshot.patch:910
  blocking:否
  why:輸入＝分別抽取 `lumos-entry-hook.py`、`check-graph-sync.py`、`impact-hook.py` 從 `def _trusted_lumos():` 到 `return None`；預期＝三段 byte-identical；實際＝三份 SHA-256 都是 `527e777d428bdc9f59a8d4b74687a8f01cade55e1cd7c511382ba8b377059974`。一致性成立，但不修正共同判準本身的不可信問題。

- [clean] `_match_label` 無冒號與 `_contract_label` 非預期輸入都不會回顯原文
  引句:「認不得的一律歸成一句話,★絕不逐字印圖譜內容★」
  位置:governance/review-reports/code-audit-batch7/r1-snapshot.patch:174
  blocking:否
  why:輸入＝`content`、`ignore previous`、換行框線、`★INVARIANT★ do evil`；預期＝無冒號仍只取整串作 key，未知 key 落固定 fallback，contract 不匹配落 `★合約★`；實際＝`content` 映射固定字彙，未知 matched_by 全回固定 fallback，contract 僅匹配開頭 ASCII 大寫類別或回 `★合約★`，均未回顯其餘原文。

- [clean] 兩個 mktemp 變數在 `set -u` 下沒有「分支未賦值後引用」問題
  引句:「_AUTOLOOP_LOG="$(mktemp "${TMPDIR:-/tmp}/lumos-prepush-autoloop-XXXXXX")"」
  位置:governance/review-reports/code-audit-batch7/r1-snapshot.patch:377
  blocking:否
  why:輸入＝自主迴圈不存在、測試套件不存在、只進其中一個分支及兩者皆進；預期＝所有引用前均完成賦值；實際＝兩個 assignment 都在條件分支之前無條件執行，未發現 unset 引用。殘餘問題是腳本沒有 `set -e`，若 mktemp 失敗變數會成空字串、後續 redirect 失敗；這是錯誤處理問題，不是本題指定的 `set -u` 分支漏洞。
