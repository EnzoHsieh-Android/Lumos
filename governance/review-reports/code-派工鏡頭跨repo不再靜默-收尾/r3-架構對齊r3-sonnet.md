severity: minor

我有看到「lumos 自動附加」段:列了 8 篇有細節的固定席節點,另有 21 篇只列名,共 29 篇。表態記錄 py-eventloop na 的理由跟本案無關,不影響判斷。

## 問 1 分層與依賴方向:對齊
修補只動測試和計劃筆記。測試裡的範圍來源仍是同一個 helper:`_lens_smallest_commit` 取主線上最小的提交,再用 `rev-parse &lt;head&gt;~1^{commit}` 得到 base,組成 `rng`。這跟鄰居測試 `t_codex_s1_r1_fixes` 一樣,後者在 `scripts/test_lumos.py:39789-39794` 用同樣的做法。超時測試在 `scripts/test_lumos.py:17303-17324` 也用同樣的做法。修補沒有新增跨層呼叫。

## 問 2 命名與錯誤處理:有一處不對齊
- `cheap = rng` 只是別名。鄰居(`scripts/test_lumos.py:39789-39794`)直接用 `rng`,不另設別名。這個別名是為了沿用後面四處 `lens("--arm", cheap, ...)`(39696-39711),結構沒問題。
- 註解沒有改乾淨。新加的 `★2026-10-07 起…★` 註解寫「原本的 &lt;upstream&gt;..&lt;upstream&gt; 改成…」,但上方舊註解 39669-39670 仍寫「其餘三次用 &lt;upstream&gt;..&lt;upstream&gt; 這個空 diff…(實測 1.4 秒)」。同一支測試的註解前後矛盾(見 A1)。
- 計劃筆記〈實務隱患〉新增的一條用 `- **粗體標題**:` 加敘事,跟同節其他條的寫法一致。check 訊息沒有改動。

## 問 3 第二種做法:同一套
「後面幾次武裝也用最小提交範圍」跟專案挑鏡頭測試範圍的做法是同一套:`Projects/鏡頭測試範圍固定_計劃` 的 WHY 行寫明兩支認領測試都改用主線最小提交。修補是讓 `t_codex_s1_lens_arm_claim` 回到那一套,沒有引入另一套做法。

## A1 舊的空範圍註解沒有同步更新
severity: minor
blocking: 否
引句:「其餘三次用 &lt;upstream&gt;..&lt;upstream&gt; 這個空 diff——一樣過 base」
佐證:file: `scripts/test_lumos.py:39669`
佐證:file: `scripts/test_lumos.py:39682`
失敗場景:讀註解的人看到前段說後三次用空範圍、實測 1.4 秒,下一段卻說改成最小提交、單支變慢。他可能把 `cheap` 改回空範圍,結果 empty_range 讓測試再次失敗。這條註解同時留下過時的「1.4 秒」數字。
歸因:有證據的修復回歸。查證命令:`grep -n "其餘三次用\|cheap = rng" /tmp/code-lens-tail/t.py` 得到 39669 和 39682。修補只刪掉 `cheap = f"{ml}..{ml}"` 一行,沒有動這段舊註解;`r3-snapshot.patch:500` 顯示這行舊註解仍在。

不對齊共 1 條,其中重大 0 條
總結:這次修補把範圍改成跟鄰居測試同一套做法,結構是對的,只是舊註解還寫著已經不能用的空範圍說法,需要刪掉或改寫。
