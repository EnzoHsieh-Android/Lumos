severity: major

## 查證摘要

- 錯誤訊息改成 `"、".join(_B4_SKIP)` 之後,我沒找到別處(測試、其他函式)比對舊訊息字面。
- 新加的兩條斷言裡,訊息那條只防得住「把訊息改回寫死」。我沒有再單獨記一條 finding。
- API-9:型錄列的 `androidx:UnsafeRepeatOnLifecycleDetector` 是 androidx.fragment 那條 Lint,官方頁寫「The repeatOnLifecycle APIs should be used with the viewLifecycleOwner in Fragments as opposed to lifecycleOwner.」。它能擋壞例裡「Fragment 用自己的 lifecycle 而不是 viewLifecycleOwner」的 `repeatOnLifecycle` 變體,擋不到 `GlobalScope` 和當場 `CoroutineScope`。這算部分涵蓋,我判成標批四可接受。
- UI-3:`cr:compose:lambda-param-in-effect` 能擋壞例 `LaunchedEffect(Unit) { delay(..); onTimeout() }`。compose-rules 文件第 227 行有 `compose:lambda-param-in-effect`,文件範例的壞寫法就是 `LaunchedEffect(Unit){ delay; onClick() }`。標批四成立。

## Finding 1:ARCH-17 型錄列自己寫「不管單純呼叫」,卻靠「只管」字樣照算接電

file: `skills/kotlin-idioms/checks-catalog.md:460`

severity: major
blocking: 是

具體失敗場景:

1. ARCH-17 的壞寫法只有 `lifecycleScope.launchWhenStarted { flow.collect { } }`,裡面沒有 finally/catch。
2. 上一輪修補把註記改成「只管 finally/catch 碰 UI,不管單純呼叫 launchWhenStarted」,等於型錄自己承認 `UnsafeLifecycleWhenUsage` 擋不到這個壞寫法。
3. 官方頁證實了這點。檢查頁 https://googlesamples.github.io/android-custom-lint-rules/checks/UnsafeLifecycleWhenUsage.md.html 的摘要是「Unsafe UI operation in finally/catch of Lifecycle.whenStarted of similar method」,內文是「you should check the `Lifecycle.isAtLeast` before accessing the UI」。
4. 這個口徑區分「相關/間接/需標註」(擋不到,不算接電)和「只管…」(擋得到一部分,算接電)。ARCH-17 的註記字面是「只管」,所以口徑算它接電,通電批次寫「批一、批四(CI 範本:Android Lint)」。
5. 照型錄做的人會以為接了 Android Lint 之後 `launchWhenStarted` 會被擋,實際不會。
6. 這跟上一輪把 STATE-5 退回批一的理由完全相同(檢查擋不到這列壞寫法)。同一個缺陷在 STATE-5 被修掉,在 ARCH-17 只被補了一句註記,沒有退回。

可翻紅的重現(我跑過):

```
ck.batch4_expected_tags("EXTRAS:kt-launch-when-deprecated;androidx:UnsafeLifecycleWhenUsage(只管 finally/catch 碰 UI,不管單純呼叫 launchWhenStarted);API 已棄用(編譯警告)")
  -> ['CI 範本:Android Lint']
把「只管」換成「相關:只管」之後
  -> []
```

兩種寫法只差一個詞,但實際擋不擋的內容一樣。這顯示判準靠措辭,不靠實際能不能擋。

建議修法:ARCH-17 退回只標批一。「API 已棄用(編譯警告)」是編譯器警告,不是 Android Lint,不在 `_B4_LINT` 的前綴裡。

引句:「androidx:UnsafeLifecycleWhenUsage(只管 finally/catch 碰 UI,不管單純呼叫 launchWhenStarted)」

佐證:
- file: `skills/kotlin-idioms/checks-catalog.md:460`
- file: `configs/ast-grep/kotlin-android/check.py:115`(`_B4_LINT` 會認 `androidx:` 後接大寫開頭的規則碼)

## Finding 2:筆記 WHY 仍列 STATE-5 為補成批四的列

file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:57`

severity: minor
blocking: 否

為什麼標 minor:這是筆記裡的歷史敘述,不影響行為。但下一個 session 的 AI 讀到會以為 STATE-5 是批四。

具體失敗場景:這輪修補把 STATE-5 退回只標批一,並改了同一行 WHY 的口徑句。同一行裡「補了 8 列(…STATE-5…)」沒有跟著改,現在是 7 列。另外 `Projects/Android資安靜態檢查補齊第二批_計劃.md` 的 `[closed:2026-11-08 …11 列補成批一、批四]` 也沒更正。

引句:「2026-11-08 補了 8 列(API-9、STATE-5、UI-3、UI-10、UI-16、ARCH-16、ARCH-17、ARCH-44)」

佐證:
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:57`
- file: `docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:98`

## Finding 3:口徑句斷言被另一行遮住「待查」

file: `scripts/test_lumos.py`(新斷言「r2 折入 型錄〈輸入與口徑〉列出口徑的每個排除字樣」)

severity: minor
blocking: 否

為什麼標 minor:守衛只是漏抓一個字樣,不影響現有型錄內容。

具體失敗場景:斷言用 `cat.split("## 來源縮寫")[0]` 檢查整個標頭區是否含 `「待查」`。口徑句在標頭第 11 行,但標頭第 15 行也有「現成規則欄的「待查」…」。把第 11 行口徑句的「待查」刪掉,斷言仍綠,因為第 15 行的「待查」滿足了它。其餘六個字樣只出現在第 11 行,不受影響。

引句:「check("r2 折入 型錄〈輸入與口徑〉列出口徑的每個排除字樣", all(f"「{w}」" in head for w in ck._B4_SKIP),」

佐證:
- file: `skills/kotlin-idioms/checks-catalog.md:11`
- file: `skills/kotlin-idioms/checks-catalog.md:15`

## 圖譜鏡頭

- 動到的 `scripts/test_lumos.py` 屬於 `Systems/測試假綠形態`(★INVARIANT★)。新斷言有 `★前置★` 先證明「相關」那段真的被判成排除,所以第 4 型假綠(現場走不到被測分支)成立不了。這份 diff 沒有破壞該合約。
- `Systems/授權與歸屬`、`lumos-cli-read`、`design-loop` 的合約只牽連 `test_lumos.py` 裡不相關的部分,這份 diff 沒碰。
- `Systems/kotlin規則包` 是 `check.py` 的家。除 Finding 2 外沒有矛盾。
- 角色卡:後端兩題(be-api-compat、be-authz)不適用。這份 diff 只改內部型錄自檢和 markdown,沒有對外 API 欄位,也沒有端點授權。

最高等級 major;blocking 1 條
