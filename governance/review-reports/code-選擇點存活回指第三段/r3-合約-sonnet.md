severity: minor

背景那條指令跑完了,補上我先前沒看到的完整結果:`-k t_choice_layer` 是 56 passed、0 failed,所以先前「完整通過計數沒看到」的缺口補上了。`-k t_docs_command_count` 是 4 passed、0 failed,`-k t_choice_plan_sections` 是 8 passed、0 failed。

我沒有改動原本的發現,仍只有一條。

severity: minor
blocking: 否
`scripts/lumos:81077`(`_CHOICE_LAYER_NOT_BODY_RE`)改成整行標題比對後,`docs/lumos-toolchain-knowledge/Projects/intake守衛_計劃.md:80` 的 `## r1/r2 審計修正紀錄` 不再被排除。它的前綴 `r1/r2` 不是 `§數字`,也不是大寫字母加數字,上一輪的寬鬆前綴會吃掉它。這個節會當成正文混進判讀材料。我掃了 Projects 下所有同類標題,只有這一條掉出去。計劃與 Systems/規格閘 的字面都寫「§數字或大寫代號」,跟程式一致,所以這是涵蓋面窄,不是文字與程式不符。
引句:「(?:(?:§\d+|[A-Z]+\d+)\s+)?(?:驗收條款|預期值表|審計修正紀錄)\s*(?:[(（][^\n]*[)）]\s*)?」
最小重現:對含 `## r1/r2 審計修正紀錄` 的計劃文字呼叫 `_choice_plan_sections`,該節會出現在回傳清單裡。上一輪版本則不會。

總結:最高等級是 minor
