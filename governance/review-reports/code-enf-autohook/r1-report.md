severity: major

# code-enf-autohook r1(session 開場 enforcement hook)

一席 standard。審 lumos enforcement 接進 SessionStart 入口 hook。

## 折入(已修+綁測試)
1. **[major] 內部 timeout 20s > 外層 hook 天花板 10s**:enforcement 一卡住,Claude Code 外層在 10s SIGKILL 整支 hook(繞過 try/except),連核心「先查圖譜」提醒都被吃掉。引句:「timeout=20, cwd=str(root))」。修:降到 3s(正常 0.2s 的 15 倍餘裕,卡住快速放棄回 None、核心訊息照印)。
2. **[major] _enforcement_line 的 fail-open 分支零測試覆蓋**:原測試只測純函式 _enforcement_alert。修:新增 t_entry_hook_enforcement_failopen——用真 python stub(exit1/非JSON/time.sleep(999))跑真 hook,斷言核心訊息照印+rc0+不追提醒行;逾時那條真的跑滿 3s 驗證優雅降級。

## 核過無誤
- _enforcement_alert 選層(只 inactive/degraded、排除 unknown/active)對;無 vendored CLI 不誤跑;無遞迴/自觸發;env 不洩漏 LUMOS_ENTRY_HOOK_OFF;正常成本 0.21s 可接受。

## 收尾提醒(非 finding)
- test_lumos.py 是錨點檔,本批改了要 lumos anchor approve;本 repo 現在會自觸發 anchor-baseline degraded 提醒(正是新功能該抓的,簽名後解除)。
