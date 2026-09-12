severity: blocker

# 推筆記認家 r1 審查——合約與圖譜一致

1. **★家★標記跟種類標記黏在一起沒有空格,四個顯示點全中**——`impact-hook.py` 的必看段與可能相關段、`scripts/lumos` 的 `impact --file`/`impact --diff` 人讀輸出,四處都用 `f"{ab}{mk}..."` 直接串接,沒有分隔空白。凡是「確認過的家」同時又被既有的直接/間接/事故偵測命中(這是常見情況,因為家的確認條件本身就重用了直接偵測那套反引號抽取),畫面就會印成「★家★直接」黏成一串。實際重現:在乾淨 repo 跑 `python3 scripts/lumos impact --file src/pay.py --ranked` 印出 `0.30 ★家★直接 Systems/計價規則.md [固定]`;`impact --diff HEAD~1..HEAD` 印出 `★家★直接 Systems/計價規則.md [固定]`;`impact-hook.py` 的 `build_ranked_context` 對 `{"kind":"direct","pinned":True,"home":True,"contract":"INVARIANT"}` 印出 `★家★直接 ★INVARIANT★ Systems/combo.md`。既有測試 `t_impact_hook_shows_home_label` 裡「大檔的家」那筆 fixture 本身就是 `kind:"direct", home:True` 這個組合,但斷言只寫 `"★家★" in l_free`(子字串比對),所以黏字串照樣判過——這正是本 repo 自己記過的「測試存在但沒在驗它宣稱要驗的」那個坑再犯一次。
引句:「lines.append(f"  {ab}{mk}{ct} {_plain_label(x.get('node'))}{mb}".replace("  ★家★", " ★家★"))」
引句:「lines.append(f"  {x.get('score',0):.2f} {ab}{mk} {_plain_label(x.get('node'))}")」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/scripts/lumos:22072-22073`(`hm = "★家★" if r.get("home") else ""` 與 `f"  {r['score']:5.2f} {hm}{mk} {r['node']}{ct}{pin}"`,同一模式在 22354-22355 的 `--diff` 輸出重複一次)
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/scripts/test_lumos.py:36894-36897`(`t_impact_hook_shows_home_label` 的斷言只用 `in`,驗不到黏字串)
severity: blocker
blocking: 是

2. **這支 hook 自己的家沒被寫回,現況描述已經跟改完的程式碼對不上**——`check-graph-sync.py`(Stop hook)這次把「跟改動的碼直接相關、卻沒動的筆記」點名文字從只講合約/事故改成也講家,但它的家 `Systems/graph-sync-coverage.md` 完全沒被這次提交碰過。該篇仍寫「即使這輪動過圖譜,仍點名『直接相關且帶合約/事故、這輪沒動』的篇」,對照實際邏輯——`_impact_missing` 呼叫 `impact --diff HEAD --sync-check --json` 取的 `sync.missing` 就是同一份 `pins`,而 `pins` 現在會含 `kind=home` 的項——現況已經是三種理由(家/合約/事故)而不是這篇寫的兩種。這正是「每支檔有家」自己承認的天花板(機械只驗「有沒有家」,驗不出「寫回有沒有落到跟這次改動語意相關的那個家」),而這次剛好在同一個 PR 裡真的踩到。
引句:「即使這輪動過圖譜,仍點名「直接相關且帶合約/事故、這輪沒動」的篇」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:43`
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/scripts/hooks/claude/check-graph-sync.py:605-607`(`miss = [m for m in (d.get("sync") or {}).get("missing", []) if m.get("pinned")]` 直接吃 `impact --sync-check` 的 `pins`,而 `pins` 現在含 home 項——`/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/scripts/lumos:22314-22317`)
severity: major
blocking: 是

3. **姊妹計劃筆記裡「about_code 只做排序」的現況描述,沒有跟著這次翻案更新**——`消費專案接入靜默失效_計劃` 的 KEY 行拿「about_code 只做固定席排序不做連結,是 2026-08-23 Enzo 裁的甲案收窄,設計正確」當它自己「不動 about_code 範圍裁定」的立論基礎,現在這個前提已經被本案的 d1 部分翻掉(確認過的家會直接進必推名單,不再只是排序)。這篇不在本次 diff 的改動清單裡,读到的人會以為「about_code 只排序、不連結」仍是現況。
引句:「about_code 只做固定席排序不做連結是 2026-08-23 Enzo 裁的甲案收窄,設計正確」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/docs/lumos-toolchain-knowledge/Projects/消費專案接入靜默失效_計劃.md:28`
severity: major
blocking: 否

4. **新引入的「兩套來源會分岔、沒有機械守衛」風險,回頭條件沒接住這一款**——`_home_map_from_notes`(原本只有「每支檔有家」單一呼叫端)這次被改成兩個呼叫端共用:每支檔有家從 git 提交快照餵、推筆記認家從已載入的工作目錄圖譜餵,docstring 自己寫「兩套算法一定分岔,而分岔時沒有東西會翻紅」。`推筆記認家_計劃` 的「回頭條件」段列了 7 條 REVISIT(門檻 8、寫錯的家、消費專案效果、正文沒提到提醒、抽查單次量測、沒確認的家),沒有一條是在講「兩個資料來源(提交快照 vs 工作目錄)算出來的家對照表可能不一樣」這件事——這是本案新增的風險,不是延用舊案已經接住的那個(舊案「兩套算法分岔」講的是另一支——反引號抽取——的複用,不是這支)。
引句:「每支檔有家從提交快照餵、改檔前推筆記從已載入的圖譜餵,★兩邊共用這一支★——兩套算法一定分岔,而分岔時沒有東西會翻紅。」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/docs/lumos-toolchain-knowledge/Projects/推筆記認家_計劃.md:116-140`(回頭條件段全 7 條逐一核對,無一條覆蓋此風險)
severity: major
blocking: 否

5. **一篇量測固定席噪音的既有驗證紀錄,沒有被這次「六篇標 stale」的判斷收進去,也沒被排除的理由**——`2026-08-24_固定席降噪A層落地` 量的是「固定席」的噪音組成(held 固定席噪音 82→39),這次 pins 集合新增了 `kind=home` 的項,理論上會改變同一份「固定席」的噪音基數。它沒被列進這次標 stale 的六篇,而它的 `revalidate_when` 也完全沒提「固定席」或 about 語意變更(跟另六篇的 `revalidate_when` 明寫這條不同)。★這條我沒能找到量測程式(棘輪計算在 governance/eval 找不到關鍵字)來確認 home 加入後這篇的數字是否真的會變,所以降級處理★——不確定是漏標還是本來就不受影響,標記交編排者判。
引句:「revalidate_when: 語料大改或標註刷新後重跑考卷;LANE_N 要調時(train 上 2/3/5 目前不敏感);lane 顯示格式改時」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/docs/lumos-toolchain-knowledge/Verification/2026-08-24_固定席降噪A層落地.md:5`
severity: minor
blocking: 否

## 機械重現指令(供編排者複核)

```
cd <clone> && python3 scripts/lumos impact --file <一支「確認過的家」同時也是直接命中的檔> --ranked
# 觀察輸出裡 "★家★" 與種類詞(直接/hop1/⚠事故)之間有沒有空格

python3 scripts/test_lumos.py -k impact_home        # 36 passed(既有測試不會抓到 finding 1)
python3 scripts/test_lumos.py -k hook_shows_home    # 6 passed(同上)
python3 scripts/lumos doctor                        # 0 issues(finding 2、3 不會被機械擋)
```

## 沒有查到問題、值得記一句的部分

- 舊裁定翻案留痕做得到位:`固定席扇出降權_計劃` d4 的 context 欄有 `★2026-09-12 已由 [[Projects/推筆記認家_計劃]] d1 重開,依據改寫★` 標註,`推筆記認家_計劃` d1 四欄(context/alternatives/why_chosen/trade_offs)齊備、三個替代方案都寫了。
- SOP 文件講「還原節點蓋了 regen 章卻一支檔都不管會被擋」跟程式碼行為一致(`scripts/lumos:18366-18372` 的 `blocks.append(("regen-no-home", rel))` 確認是硬擋,不是提醒)。
- 六篇新標 stale 的驗證紀錄裡,除了 finding 5 那篇,其餘判斷跟各自的 `revalidate_when` 對得上,沒抓到誤標。
- 新驗證紀錄 `2026-09-12_推筆記認家落地` 的「還沒做到的」一段誠實(單家審查、消費專案零實證、獨立性降級都寫了 REVISIT 日期),沒有「只提醒不擋」卻沒附回頭條件的漏網。
