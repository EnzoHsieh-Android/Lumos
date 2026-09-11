severity: major

### F1 Gradle 測試資料夾判定沒有限定 JVM 副檔名,同模組混語言時會讓真程式檔被誤判成測試而免家
severity: major
blocking: 是 — 「每支檔有家」的用途是擋住沒人管的真程式檔,這個缺口讓它在特定條件下被靜默繞過,而且是這次改動新引入、既有測試沒蓋到的路徑。

- `_nodehome_stack_test_dirs()` 的 Gradle 分支(`rglob_under == "src"`)只收資料夾名(`under_src |= names`),沒有像上面 `suffix` 分支那樣同時收該棧的 `exts`;`_nodehome_in_stack_test_dir` 的 androidTest/test 判定因此完全不看副檔名屬於哪個棧,只看 `_nodehome_layout` 統計出的「同模組 `src/main` 底下出現過哪些副檔名」(來源是 `all_paths`=全部受版控路徑,不分是不是程式檔)。
- 結果:只要同一個 Gradle 模組的 `src/main` 底下剛好混了一支非 JVM 副檔名的檔(例如一支 Python 建置腳本),`src/androidTest` 底下同副檔名的檔就會被判成測試、免家——這正是文件與測試自己講「只該收 Kotlin/Java」的那條界線被打穿。
- 現有 `t_nodehome_stack_test_dirs_not_required` 的 ④f 案例(`tools/src/androidTest/backdoor.py`)沒有讓 `tools/src` 這個模組的 `src/main` 也放一支 `.py`,所以測不到這個缺口;我在乾淨暫存目錄直接呼叫 `_nodehome_layout`/`_nodehome_is_test` 重現:

```
all_paths = [
    "app/src/main/java/com/x/Main.kt",       # 真的 JVM 主程式
    "app/src/main/scripts/gen.py",           # 同模組 src/main 底下剛好有一支 .py
    "app/src/androidTest/scripts/evil.py",   # 應該照舊要家的 .py 檔
]
layout = mod._nodehome_layout(all_paths)
# layout = ({'app': {'.py', '.kt'}}, {'app/src': {'.py', '.kt'}})
mod._nodehome_is_test("app/src/androidTest/scripts/evil.py", layout)
# → True (被判成測試,免家——錯誤;.py 不是這條規則該收的棧)
```

引句:「if parts[i] in under_src and parts[i - 1] == "src" and ext in main_exts.get("/".join(parts[:i]), ()):」

佐證:
- file: `scripts/lumos:17796` `_nodehome_stack_test_dirs()` 的 Gradle 分支只做 `under_src |= names`,沒收 `prof.get("exts")`,跟上面 `suffix` 分支(17795 行 `sufs.setdefault(d, set()).update(prof.get("exts", ()))`)不對稱。
- file: `scripts/lumos:17812-17823` `_nodehome_layout` 把 `all_paths` 裡每一支檔的副檔名都收進 `main_exts`,不分棧屬。
- file: `scripts/lumos:17886` `_NodehomeSide` docstring 明講 `all_paths=所有受版控路徑`,不是只收程式副檔名的子集。
- file: `scripts/test_lumos.py:36744` 測試自己的敘述「Kotlin、Java 都算」,證實設計意圖是收窄到 JVM 語言,不是任何棧都能借道免家。

## 逐項判定

- 風險掃描(延遲快取 `_NODEHOME_STACK_TEST_DIRS` 沒鎖保護)→ **誤報**:整支 `scripts/lumos` 沒有 `import threading`,`lumos` 每次呼叫是獨立行程,沒有執行緒共用這塊模組層狀態;`_nodehome_stack_test_dirs()` 只是對靜態的 `TEST_PROFILES` 做純函式運算,就算真的重入兩次也算出同一個 immutable 值(冪等),跟同檔案既有的 `_TESTMAP_DIR_RE` 這類模組層惰性快取(scripts/lumos:19891)用同一種不加鎖寫法——不是這次新引入的隱患。
- 圖譜鏡頭(r3-lens.txt 列出的固定席節點:bound-tests-gate、canary-audit、guard-kill、slim-get-一行安裝、slim-install-安裝器、slim-uninstall-一行卸載、授權與歸屬、測試假綠形態,以及超出上限只列名的 lumos-cli-read/lumos-cli-lifecycle/design-loop/pitfalls-code-loop/loop-convergence-recording/節點範圍與索引守衛/lumos-deinit/reversibility-governance-ledger/lumos-refcheck/doctor-irreversible-hint/core-invariant-baseline/check-r-guard/check-t-sentinel/cochange-guard/judge-severity-gate)→ **全部不影響**:這些節點跟這份 diff 只是「間接相依」——lens 附檔本身就標明牽連原因是共用 `scripts/lumos`、`scripts/test_lumos.py` 這兩支巨型檔案,不是函式層真的相依。這次改動只碰 `_nodehome_stack_test_dirs`/`_nodehome_top_dirs`/`_nodehome_layout`/`_nodehome_in_stack_test_dir`/`_nodehome_is_test`/`_nodehome_required` 這一組「每支檔有家」測試資料夾判定函式,沒有碰任何安裝/解除安裝(slim-*)、canary 落盤、guard kill rc 優先序、授權白名單、mutation-testing 相關的程式碼或呼叫路徑,對應的 `[test:]` 這次也沒被移除或改寫成假證據(`t_nodehome_stack_test_dirs_not_required` 本地全綠、`-k nodehome` 182 passed/0 failed)。

總結:最高 severity major,blocking 共 1 條
