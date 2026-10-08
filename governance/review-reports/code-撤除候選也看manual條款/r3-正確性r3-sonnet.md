severity: minor

## F1 同編號定義兩次時,只有第一條定義行被看,第二條(含重複的第三條)掛 [manual:] 且下一層寫撤除會漏列
severity: minor
blocking: 否
引句:「+        if not r.get("defined") or not 0 < no <= len(lines):」
佐證:clause_bindings 對重複編號只回一列,line 是 defined[cid][0](第一次定義行):``scripts/lumos: `7150-7230` ``(dup 分支 `"line": defined[cid][0]`)。新函式迴圈只迭代這些列,所以重複的後續定義行不會被走到。
失敗場景:計劃寫「- [S1] 當 x 時應 y」(未標)、「- [S1] 當 z 時應 w [manual:開頁面目測一次]」、其下一層「  - 裁定:撤除這條」。_ns_tr_manual_clauses 只處理第一行(未標),第二行永遠不被判,S20 不列。「兩條都掛 manual 且第二條才寫撤除」(probe C)與三重複的中間條(probe M)同樣漏。
歸因:有證據的原有漏查(非修復回歸)。修前 b(280085c9)與修後 a(4b5f283d)在 B/C/M 三例都回 []。同一缺口在 [test:] 路徑也存在:probe P(第二條掛 [test:] 且下一層寫撤除)修前修後皆 [],所以跟既有 [test:] 路徑同口徑、不是 manual 專屬。重複編號另有條款檢查在擋,實際傷害小。
重現(修前修後都跑):`python3.14 probe.py a`、`python3.14 probe.py b`(probe.py 在 /tmp/lumos-seat-work/code-撤除候選也看manual條款/正確性r3-sonnet/),案例 B/C/M/P。

其餘無 finding。

## 三問

1) 原問題(重複定義時掛 [manual:] 的第一條漏列)修好了嗎?
修好了,有修前修後對照。命令 `python3.14 probe.py b` 與 `python3.14 probe.py a`:
- A(第一條掛 manual、下一層撤除、第二條也是重複定義):修前 [],修後列。
- D(兩條都掛 manual、第一條下一層寫撤除):修前 [],修後列。
- F(第一條是表格列)、G(標題式 `## [S1]`)、H(兩條都寫撤除,只列一次):修前 [],修後各列一次,沒有重複列。
- I、J(shadowed 狀態:第二處是 `一、[S1]` 或 `* * [S1]` 這種像清單卻認不得的行):修前 [],修後列。
- 對照:E(第一條已標作廢)、K(第一條 `[manual:已撤除,…]`)修前修後都 [],沒有誤列。
- 對照:L、O(第一條掛 [test:] 或 test+manual)修前修後都只列一次、以 [test:] 為準。
- 單一定義(N)修前修後都列。

2) 修補處相鄰路徑(preserve)還成立嗎?
成立。在修後樹跑 `python3.14 scripts/test_lumos.py -k s20`,結果 38 passed, 0 failed,包含 t_doctor_s20_prose_retire_manual(①–⑨)與既有 t_doctor_s20_prose_retire_* 各測。我另補的 A、D、E、F、G、H、I、J、K、L、N、O 各格都符合預期且沒有同行列兩次。二次解析只拿單行丟給 clause_bindings,該行仍須通過 _CLAUSE_LEAD_RE,所以不會多出非定義行;`r.get("defined")` 守住了 undefined 列。例外路徑:再解析回空時用 `next(iter(...), {})`,不會丟 StopIteration。

3) 新發現的同一案例修前、修後各是什麼結果?
F1(B/C/M)修前 [],修後 [],歸因為原有漏查;[test:] 路徑 P 同為 [](兩版一致)。沒有發現修補造成的新回歸。

總結：最高等級 minor,本輪修補對 ⑨ 範圍有效,僅留一個與 [test:] 路徑同口徑的重複定義第二條漏列(原有漏查)。
