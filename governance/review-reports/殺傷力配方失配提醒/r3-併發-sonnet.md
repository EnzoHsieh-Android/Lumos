severity: major

# r3 併發-sonnet(併發與資源鏡頭)

## F1 kill-rm 只說「原子寫入」沒說上筆記庫寫入鎖,與 kill-add、set、append 同時改同一篇會互相蓋掉
severity: major
blocking: 是
引句:「同檔原子寫入(同 kill-add 的寫法)。」
file: `scripts/lumos:15122`
1. 程式現況:`_write_lf` 的說明明寫「read-modify-write 的併發:set/append/remove 由呼叫端上鎖(_vault_write_lock),其他寫入指令仍是 last-write-wins」。`cmd_guard_kill_add`(scripts/lumos:12886 起)整個函式裡沒有任何 `_vault_write_lock`,主分派 `args.gcmd == "kill-add"`(約 41074 行)也沒包鎖。它是「先 `_kill_read_recipes` 讀進整串配方、記憶體裡改、最後 `atomic_write_verify` 換名」。「原子」只擋半截檔,擋不住「讀了舊版、寫回去蓋掉別人剛寫的新版」。
2. spec 把 kill-rm 的寫入寫成「同 kill-add 的寫法」,等於照抄一個沒鎖的讀—改—寫。照字面實作的失敗場景:A 跑 `kill-rm 節點 --id 失配配方`(讀進 73 條、拿掉 1 條),B 同時跑 `kill-add` 為同一篇另一個合約新增配方(讀進同樣 73 條、加 1 條);兩邊各自換名,後換名的整串覆蓋先換名的,結果不是「少 1 條」就是「多 1 條」,另一邊的動作悄悄消失、兩邊都印成功。最嚴重的是 kill-rm 後到:被移除的失配配方復活(P2 照舊唸,人以為修過了),或 kill-add 後到:剛移除又被寫回。
3. kill-rm 比 kill-add 更需要鎖:它還會連動改 KEY 行的 `[kill:recipes]` 標記(「剩下的配方沒有任何一條對得到那一行就拿掉標記」)。標記是否拿掉取決於「剩下哪些配方」,這個判斷是用讀進來的快照算的;若快照已過期(另一個 kill-add 剛為同一條合約加了配方),會把標記拿掉卻留著配方,或相反,而 `atomic_write_verify` 的 check 只驗自己寫的那份,驗不出別人的更新被蓋掉。
4. 另一個會跟它同時寫同一篇的寫入者是 `lumos set`、`append`(有上鎖),但 kill-add/kill-rm 不上鎖,鎖的互斥對它們不成立,同樣會被蓋掉。多個會談同時在同一個圖譜工作是本專案的常態(CLAUDE.md 與記憶都提到同工作區多會談)。
5. 折法要在 spec 寫明:kill-rm 的「讀 `_kill_read_recipes`、算標記、`atomic_write_verify`」整段包在 `with _vault_write_lock(env.vault):` 裡(鎖可重入、等 60 秒會丟 `RuntimeError`,要照 kill-add 現有 `except (ValueError, RuntimeError)` 的樣子擋下回 2);鎖內要重新讀檔,不能用鎖外讀的快照。kill-add 這次既然已經要動它(插入提醒),建議一併把「讀—判重—寫」包進同一把鎖,否則 spec 新增的 kill-rm 與既有 kill-add 之間的互斥還是不成立;若決定 kill-add 維持現狀,spec 得在〈實務隱患〉明講「kill-rm 與 kill-add 同時寫同一篇仍是 last-write-wins」並附回頭條件。判斷函式(含 git 子行程與讀檔)要放鎖外或確認鎖內耗時遠低於 30 秒過期門檻(`_VAULT_LOCK_STALE_SEC`),否則鎖被當成死鎖接手。

## 其餘各節
- 路徑解析器逐段 lstat/readlink 的成本(rtb 73 條配方):每條約數段、至多 40 次連結跟隨,加上每個平台根一次 `git rev-parse`,規模在百分之一秒到一秒級,已讀,無 finding。
- 檔案快取(同一實際路徑只讀一次、一次判定內有效):已讀,無 finding。快取只在單次判定內活著,P2 期間檔案被改只會造成一次誤報,spec〈讀到寫到一半的檔〉已涵蓋;`_write_lf` 是換名寫入,doctor 不會讀到半截檔。
- doctor 期間筆記被 kill-rm 改動:P2 讀的是 `_kill_read_recipes` 重新讀盤、不是 doctor 開頭載入的快照,最壞是少列或多列一次,已讀,無 finding。

最高等級:major;blocking 共 1 條
