severity: minor

**1. 放的位置對不對?**
對。規則改動在 `coroutines.yml` 的原分支位置,好例和壞例都在該規則自己的 `samples/good|bad/kt-long-lived-scope-plain-job/` 下。Issue 修好紀錄加在同一篇。沒有放錯層。

**2. 命名與寫法跟鄰居一樣嗎?**
大致一樣,有兩處不同。
- 規則的 `has` 加 `stopBy: end` 與同檔其他處一致(`coroutines.yml:126`、`:130`、`:140`、`:144`)。
- 規則內註解引 Finding 的格式沿用既有寫法(`coroutines.yml:112`)。
- 結案橫幅、修好紀錄、`[closed:…]` 的寫法對照 `worktree裡改檔推不出筆記.md:23`,同一格式。
- `status: done` 在 Issues 目錄用了 33 次,不算新做法。
- 差異一(A1):既有好例 Holder、Holder2、Holder3 和壞例 S3 都在類別前放一行「容易誤報:…」或「括號裡…」的前導註解,類別之間空一行。新增的 Holder4、Holder5、S4 沒有前導註解,也沒空行,說明改塞在行尾。
- 差異二(A2):Issue 在 2026-11-09 結案,`updated:` 卻仍是 2026-11-08。已結案的鄰居都把 `updated:` 改成結案日(`worktree裡改檔推不出筆記.md:5` 是 2026-10-02,結案日相同;`蘋果內建Python3.9跑全套仍紅.md:5` 是 2026-09-29,結案日相同)。

**3. 有沒有引入專案原本沒有的做法?**
沒有。遞迴找用既有的 `stopBy: end`,拿掉特例分支是簡化,沒有第二種做法。新增的樣本沿用 `// GOOD` 與 `// BAD` 行尾標記。Issue 筆記的 `[closed:]` 回頭條件寫法也跟其他 Issue 一致。

**A1**
severity: minor
blocking: 否
引句:「+class Holder4 {」
file: `configs/ast-grep/kotlin-android/samples/good/kt-long-lived-scope-plain-job/src/main/kotlin/kt-long-lived-scope-plain-job.kt:21`(Holder2 前導註解與空行的寫法;壞例檔 S3 前導註解在同目錄 bad 檔 `:21` 附近)

**A2**
severity: minor
blocking: 否
引句:「updated: 2026-11-08」
file: `docs/lumos-toolchain-knowledge/Issues/worktree裡改檔推不出筆記.md:5`
⚠ `updated:` 可能是 `lumos set` 在提交時自動更新;如果是,這條不成立。

不對齊共 2 條,其中 major 0 條
