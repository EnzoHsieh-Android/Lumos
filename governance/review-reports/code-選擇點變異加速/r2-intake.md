# r2 收貨紀錄(code-選擇點變異加速)

## 派工與收貨

- 2026-11-23 派七席(架構對齊、資安、資源、整合、正確性、通才、邊界),都是 sonnet 全新代理;修補鏡頭:修前 22751fcce → 修後 02fd3bdf5。六席讀修補差異 r2-repair.patch(897 行)加整份凍結材料 r2-snapshot.patch(2790 行),資安席讀整份凍結材料;派工依 r2-dispatch.json。
- 七席收齊才落地,報告從子代理逐字稿存檔(r2-<席>-sonnet.md)。邊界席第一次停在「第二批仍在執行,等通知」沒交報告(子代理結束後收不到背景通知),編排者續談叫回,補交完整報告。
- 收貨三道:report-normalize 七份都已是正規化格式;quote-check 七份全數錨定;refcheck 引用全對得上;seat-check 因派工單沒列材料清單判 vacuous 豁免(派工單形狀問題,記成工具問題)。
- 席位臨時目錄 /tmp/lumos-seat-work/code-選擇點變異加速/ 收齊後已刪除。

## 重現表

| id | 來源 | 重現 | 判定 |
|---|---|---|---|
| g1 | 通才 #1(major) | 編排者在修後 02fd3bdf5 的暫存工作樹把快篩呼叫改回 `max(m_el * 5, c.floor)`,清 __pycache__ 後 `-k t_choice_kill`:223 passed、0 failed | HIT,折入(修正 1) |
| g2 | 通才 #2 | 修後版 `-k t_choice_kill_merge_budget` 中 budget_reestimate 單支約 40–60 秒(機器負載不同) | HIT,折入(修正 2) |
| b1 | 邊界 #1 | 席位改壞 `<` → `<=` 後 `-k choice_kill_merge_budget` 3 passed;編排者讀碼確認既有測試都不卡在門檻值 | HIT,折入(修正 3) |
| rs1 | 資源 #1 | 讀碼確認:量完第一支就重估,樣本只有第一支(含冷編譯);席位臨時腳本實測 `(False, '基準')` | HIT,放行 |
| a1 | 架構對齊 #1 | 讀碼確認 `_kill_merge_singles` 與 `cmd_guard_kill` 各寫一份量單支基準、各寫一次 `max(600.0, floor)` | HIT,放行 |
| in1 | 整合 #1 | 計劃〈做法〉4 末段仍寫「合併快篩一次最長是它的逾時上限(估 2.5–5 分鐘)」,跟同篇快篩上限已加剩下時限打架 | HIT,折入(修正 4) |
| in2 | 整合 #2 | grep 四支新測試名在計劃與 guard-kill 筆記 0 筆;guard-kill 的 PITFALL 一行三個症狀只綁一支 | HIT,折入(修正 4) |
| in3 | 整合 #3 | 計劃〈做法〉1 寫「不改既有的 `_gradle_test_module`」,修補已改成呼叫共用函式(行為不變) | HIT,折入(修正 4) |

## 修補因果(--regression-set)

- in1、in3:修補前那兩句敘述跟程式相符,修補改了程式沒改那兩句,是修補造成的文件回歸。
- rs1:修補前沒有重估,不會因第一支冷編譯停用合併;是修補新增行為帶來的速度代價(不是判定錯誤)。
- g1、g2、b1、in2:修補新增的程式或測試本身的測試缺口與成本,修補前不存在對應行為,不算回歸。
- a1:修補前 `_kill_merge_base` 就有同形狀的量測迴圈,原有漏查。

## 放行理由

- rs1:改成排除第一支(或至少量兩支才重估)會讓第一輪 c1 的情境(每支 6 秒、總時限 11 秒)重新出現:第二支被剩下時限截斷、時限吃光、合併模式交不出列。現在的寫法偏保守,代價只是這次不合併、退回逐支(變慢),判定跟 `--no-merge` 一致,符合計劃「合併只是加速,判定一致或更強」。不修。
- a1:席位自判不到 major;計劃〈做法〉2 要求先量的基準存進同一份 `baselines`、五元組形狀與鍵相同,逐支流程照用。合成一支要動既有逐支流程(`mstate` 的 unsure 等欄位寫法不同),超出這次修補範圍。不修。

## 先查世界

- PRIOR-ART:呼叫端接線沒被測試守住(g1)——查 mutation testing 對「呼叫參數被改」存活變異的處置:要斷言那個參數造成的可觀察效果(回傳、副作用、子程序行為),只測被呼叫的純函式殺不掉呼叫端的變異;採用:端到端案例觀察快篩子程序在剩下時限到時被收掉(假 Gradle 沒寫出 end)。來源:https://nwyin.github.io/irradiate/guide/surviving-mutants/ 、https://tessl.io/registry/testland/mutant-survival-triage
- PRIOR-ART:用真實睡眠湊時限的慢測試(g2)——查 Python 測試的假時鐘做法(time_travel、pyinstrument 的 fake_time_util、looptime):注入可推進的時鐘最穩;本 repo 的量測走真子程序(假 Gradle 是另一個程序),注入時鐘要改產品碼的時間來源,不採用;改成睡眠與時限同比例縮小,卡線測試(b1)則直接呼叫函式、換掉 `_kill_run` 與 `remaining`,完全不睡。來源:https://pypi.org/project/time_travel/1.1.2/ 、https://sources.debian.org/src/python-pyinstrument/5.1.2+ds-1/test/fake_time_util.py 、https://pypi.org/project/looptime/
- 其他組(卡線測試、文件對齊、條款綁定)是本 repo 內部一致性問題,沒有對應的外部做法要查。

## 修補

- 提交 547326dbb(test: 釘住快篩逾時上限的接線與重估卡線、縮短重估測試);測試檔改動使用者 2026-11-23 回「簽」,簽章提交 f395ceb13。
- 修正 1(g1):`t_choice_kill_merge_screen_cap` 加端到端案例:下限 30、總時限 3 秒、壞法 1 的快篩睡 6 秒 → 快篩有 start、沒有 end。改壞呼叫端(改回 `max(m_el * 5, c.floor)`)→ 這條紅;真碼綠。
- 修正 2(g2):`t_choice_kill_merge_budget_reestimate` 睡眠與時限同比例減半(6/11 秒 → 3/5.5 秒,8/6 秒 → 4/3 秒,單價 1 → 0.5);真碼綠。
- 修正 3(b1):新增 `t_choice_kill_merge_budget_edge`,直接呼叫 `_kill_merge_singles`(單支耗時固定 2 秒、剩下時限固定):剩 6.0 照量齊、剩 5.99 收手。`<` 改 `<=` → 6.0 那案紅;拿掉重估 → 5.99 那案紅;真碼綠,0.1 秒。
- 修正 4(in1、in2、in3):計劃〈做法〉1、〈做法〉4 兩句改成現況;S4、S6、S7、S9、S19、S20 補綁五支新測試(只加 `[test:]`,條款文字與預期值表不動);guard-kill 的 PITFALL 拆成三行各配測試。兩篇 lint 0 問題。
- 編排者重跑:`-k t_choice_kill_merge_screen_cap` 6 過 0 紅、`-k t_choice_kill_merge_budget` 8 過 0 紅(批 3 長跑同時在跑 Gradle,耗時偏高)。
