severity: major

審查範圍:`r2-repair.patch`,對照倉庫 HEAD `87e706d42` 的 `scripts/lumos`。修補了大部分上輪的洞,但有一處修補實際上沒生效,另有三處較小的問題。

---

severity: major
blocking: 是
`scripts/lumos:79611`:上輪 F4「分析依賴編譯」的修補是空操作。腳本在 Gradle 的 Groovy 裡寫成 `it.name in ["compile${v}Kotlin", ...]`。Groovy 對 List 做 `in` 時是 `list.contains(字串)`,也就是 `String.equals(GString)`,永遠是 false,所以 `dependsOn` 一個任務都沒掛上。
場景:續跑時所有覆蓋資料檔都命中快取,這棵隔離工作樹沒編譯過,分析在空樹上跑,輸出 `noclasses: true`,每個壞法都記「分析失敗」,整批退回跑全部守的測試。續跑快取在它最需要的情境下完全沒用。
測試也抓不住:`t_choice_cov_init_scripts` 只檢查字串含 `"dependsOn"` 和 `"lumosCovVariant"`。
最小重現(已用 Android Studio 內附的 groovy.jar 跑過),會印出 `false` 與 `true`:
```
def v='Debug'; def n='compileDebugKotlin'
println(n in ["compile${v}Kotlin","compile${v}JavaWithJavac"])
println(n in ["compile${v}Kotlin".toString()])
```
改法:對 GString 做 `.toString()`,或改用 `it.name == "compile${v}Kotlin" || ...`。
引句:「if (v) dependsOn(proj.tasks.matching { it.name in ["compile${v}Kotlin", "compile${v}JavaWithJavac"] })」

---

severity: minor
blocking: 否
`scripts/lumos:79792` 附近的 `_choice_cov_parse`:分析輸出缺 `nolines` 或 `noclasses` 時照常通過(fail-open)。上輪只補了 `hits` 缺鍵。
場景:輸出是 `{"hits":{"0":[]}}`,沒有 `noclasses` 就當樹上有類別,沒有 `nolines` 就當空清單,每支測試被判「沒經過」,結果是 `none`。不跑壞法就記存活。
目前只有分析腳本自己會寫這份輸出,所以實際機率低,但缺兩個鍵本來應該算分析失敗。
引句:「nol = doc.get("nolines") if isinstance(doc.get("nolines"), list) else []」

---

severity: minor
blocking: 否
`scripts/lumos:79825` 的 `_choice_cov_prune`:清舊發生在建立本次 at_sha 資料夾之前。本次是新的 at_sha 時,先留下另外 2 個,再建第 3 個,所以硬碟上穩定是 3 個,不是計劃第 111 行的「只留最近 2 個」。
這條上輪 F14 的修補整支沒有測試:`test_lumos.py` 沒有任何一處呼叫 `_choice_cov_prune`,符號連結拒刪也沒有案例。
引句:「for x in subs[_CHOICE_COV_KEEP:]:」

---

severity: minor
blocking: 否
`scripts/lumos`,`_KillCovBase.store` 與 `cached`:Robolectric 專案類別有紀錄數為 0 的覆蓋資料檔,也會先存進續跑快取,下次 `cached()` 照單全收。
場景:某次暫時性失敗讓 Robolectric 測試的 exec 沒有專案類別,記成「覆蓋接不起來」。`--reach-only` 把這個原因列為暫時性、會重補,但它重讀的是同一份壞資料,結果永遠一樣,除非 at_sha 變了或手動清快取。
引句:「data = _choice_cov_read(cp) if cp and os.path.isfile(cp) else None」

---

上輪重點裡,我沒找到問題的邊界:
- 斷路器:剛好 5 支、不足 5 支(量完才判)、0 支 Robolectric。
- 時限門檻:剩下時限剛好等於門檻時是通過,這個用 `<` 的寫法可接受。
- `_choice_cov_sha` 與 reach 有效性:不明標記回 `None`,與 `""` 不會互相比對成相同。
- 多變體 flavor:`-PlumosCovVariant` 的取法正確,純 JVM 模組(沒有 `test<V>UnitTest`)會回 `None` 並安全退回。
- `package` 取宣告值,跟資料夾無關。

總結:最高等級是 major(`lumosCovAnalyze` 的 GString `in` 比對讓編譯依賴整個失效)
