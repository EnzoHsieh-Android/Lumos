severity: minor

我在 d6bb423f 的臨時副本上實測,沒找到會擋合併的併發或資源問題。只有一條筆記殘留的小問題。

## Finding 1:筆記還寫著已不存在的 `_vault_locked`
severity: minor
blocking: 否

`Systems/lumos-cli-write.md` 的待決問題小節有一行 WHY,寫的是「所有讀改寫開頭欄位的入口都經 `_vault_locked` 拿鎖」。這次修補把裝飾器撤掉了,`scripts/lumos` 在 d6bb423f 已沒有任何 `_vault_locked`(grep 得 0)。同一小節下一行的 WHY 已經改成新寫法,所以同一份筆記內部自相矛盾。

引句:「2026-10-12 起所有讀改寫開頭欄位的入口都經 `_vault_locked` 拿鎖」

佐證:`docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:150`。計劃筆記 `Projects/待決問題改存開頭欄位_計劃.md:168` 的 r2 紀錄也提到它,但那是歷史紀錄,可不改。

歸因:有證據的修復回歸。
- 修前 `git show 646dc3a8:scripts/lumos | grep -c _vault_locked` 得 11,筆記當時是對的。
- 修後 `grep -c _vault_locked scripts/lumos` 得 0,筆記沒跟著改。

## 實測結果(鏡頭四項)
- **可重入**:外層拿鎖、內層再拿,內層正常結束、改用不同寫法的同庫路徑、內層丟例外,三種情況之後外層的 `_vault_lock_held_for` 都仍為 True,外層寫入成功。`_VAULT_LOCK_VAULTS` 只有最外層會 pop,外層結束後兩張表都清空。
- **前綴比對**:拿 `/x/kg` 的鎖時,`/x/kg2/b.md` 回 False,`/x/kg/a.md` 回 True。`/x/kg` 內指向 kg2 的符號連結回 False,寫 kg2 的檔會被拒寫。符號連結檔現在會被拒寫,這是偏保守的行為,不是誤放行。
- **amend 鎖外檢查**:鎖內讀改寫是從磁碟重讀,鎖外只做遠端是否已有這條決策的比對。檢查到寫入之間若有人推上遠端,這條決策會被改到。這個空窗修前也存在(修前整段在鎖內,但推送本來就不受這把鎖管),所以不算新增問題。這段檢查現在不佔鎖,fetch 慢時不再擋別的寫入。
- **併發與逾時**:
  - 9 個程序同時跑:3 個 decision-amend、3 個 guard bind、2 個 question-add、1 個 decision-add,全部 rc0,資料都在。
  - 另跑 3 回合 4 個 amend、4 個 question-add 和 1 個 `reindex --all`,每回合 rc 全 0、4 題 4 改全在。
  - 放假鎖檔(隔離 HOME)後,13 個寫入指令中 12 個等 60 秒後回「擋下」rc2,沒有 Traceback。這 12 個涵蓋 amend、guard bind/audit/kill-rm、decision-refs add-ai/promote、question-add/set、decision-add/supersede/reindex、set。另一個 `decision-refs prune` 回 0,因為那條 ref 本來就不在,不寫檔,所以沒拿鎖,屬正常。

## 三問
1. **原問題的修復效果有何行為證據?** 拿 A 庫的鎖寫 B 庫會被拒寫。同庫的 8 到 9 個程序併發寫入不丟資料(見上)。鎖逾時時各入口都回擋下 rc2。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 都成立:正常路徑、可重入、內層例外、前綴相近的另一庫、符號連結、鎖逾時、鎖外的 amend 遠端檢查都實測過。
3. **新發現的同一案例在修前、修後各是什麼結果?** 只有 Finding 1 一條:修前筆記與程式一致,修後筆記留著舊名。查證命令見該條。

總結:這輪修補通過併發與資源鏡頭,只剩一條筆記殘留舊名的小問題,不擋合併。

臨時檔都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r4-併發資源-sonnet/`,按規定由編排者收貨後刪。
