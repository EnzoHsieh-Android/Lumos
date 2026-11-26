severity: major

**Finding 1:斷路器恢復(半開)時沒有把 `hang_streak` 歸零,恢復後只要再掛住一次就立刻重新跳開**

severity: major
blocking: 是

引句:「mg.hang_streak[plat] = mg.hang_streak.get(plat, 0) + 1」

- 位置:`_kill_merge_breaker`。
- 路徑:停用中收到試探快篩時,pass/fail 走恢復那段,設好 `streak=0` 後 `return`。新加的「通過或有失敗歸零」那段(`if kind in ("pass", "fail"): mg.hang_streak[plat] = 0`)在 return 之後,走不到。
- 跳開時也沒有清 `hang_streak`。原本的 `streak` 靠恢復時 `streak=0` 重來,`hang_streak` 沒有對應的重置。
- 走一遍:
  1. 同一平台連續 15 次跑到測試後逾時,`hang_streak=15`,跳開。
  2. 之後試探快篩通過,恢復合併。`hang_streak` 仍是 15。
  3. 下一個壞法快篩又掛住一次,`hang_streak=16 >= 15`,立刻再跳開,`trips` 變 2。
- 後果:設計宣稱「連續 15 次才跳開」,恢復之後實際變成「1 次就跳開」。`merge_trips` 計數也被灌水。每次恢復只換到一個壞法的合併機會。
- 最小重現(已跑過,輸出如下):

```python
mg=_KillMerge(...); mg.plats["k"]=(True,"")
15 次 _kill_merge_breaker(mg,"k","unclean",False,"逾時(跑到測試後掛住)")  # → (False,'斷路器') hang_streak 15
_kill_merge_breaker(mg,"k","pass",False,"")                                # → (True,'') hang_streak 仍 15
_kill_merge_breaker(mg,"k","unclean",False,"逾時(跑到測試後掛住)")          # → (False,'斷路器') hang_streak 16 trips 2
```

- 為什麼測試照綠:`t_choice_kill_merge_hang_breaker` 的直接呼叫案都是單一方向的序列,沒有「跳開 → 恢復 → 再掛」這一案。
- 修法:恢復分支同時設 `hang_streak[plat]=0`。也可以把歸零那段移到 `if mg.plats.get(plat) == ...` 之前。

**Finding 2:帶事件腳本的合併基準失敗後,不帶腳本重跑沿用同一個 `cap`,沒有重算剩餘時限**

severity: minor
blocking: 否

引句:「mcmd, el, kind, why = _kill_merge_base_run(mg, c, sh, lane, nf, cap, None)」

- 位置:`_kill_merge_base`。
- `cap` 在第一次跑之前,用 `max(mg.remaining(), 1.0)` 算出。第一次沒產生結果檔(通常很快就失敗)之後重試,上限仍是原值。
- 走一遍:剩餘時限只剩一點,第一次耗掉一部分,重試仍給整個 `cap`。合併基準最壞耗時可到 `cap` 加上第一次耗時,超出總時限。
- 代價:偶發的總時限小幅超支。重試只發生在「找不到結果檔」,多半是 Gradle 拒收腳本而立刻失敗,所以影響很小。
- 修法:重試前用 `min(cap, max(mg.remaining(), 1.0))` 重算。

**其餘角度,逐項判無問題**

- **pitfalls manifest(1 條):`scripts/lumos:29050` 的 `open(`。** 判不成立。新增的 `_choice_merge_init_write` 是 `with open(...) as fh:`,確定關閉,`except OSError` 也有處理。
- **`_isolated_worktree` 多 `scratch`:**
  - 兩個呼叫端:修正關卡(`scripts/lumos:23663`)與 `cmd_guard_kill`。
  - 多一個屬性,不影響修正關卡既有用法。
  - `keep` 與清理仍整個 `parent` 一起處理,沒有破壞行為。
  - `getattr(_iw, "scratch", None)` 對舊物件也安全。
- **`_choice_merge_cmd` 的 `init` 位置:** 插在 `--tests` 段之後、`_run_cmd_expand` 代換的尾段之前,路徑不會被當成佔位符展開。`init=None` 時輸出與舊版相同。
- **事件解析 `_choice_merge_events`:**
  - JUnit5 的 `alphaCase()` 經 `_choice_merge_fullname` 去掉括號後可以對到。
  - 截斷標記與 `_kill_cap` 輸出的 `...[truncated N bytes]...` 字面一致。
  - 參數化的紅層優先也正確。
- **圖譜鏡頭(固定席):**
  - guard-kill 的兩條 INVARIANT(rc 優先序、`--json` 純度):新增輸出全走 stderr,不改 rc,所以不影響。
  - 其餘固定席(bound-tests-gate、lumos-cli-read、測試假綠形態、lumos-cli-lifecycle 等)針對的是別的行為,本次沒有碰,判不影響。
  - 尾端沒有「這次新增的殘留」段,殘留問答的編號與重問無需判。

最高 major,blocking 1 條
