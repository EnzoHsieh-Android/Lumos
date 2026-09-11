# skills 提示工程優化調研——讀過的來源(2026-09-11)

每條:來源、日期、讀到的原話或數字、跟本題的關係。原話照抄英文,中文是我的轉述。

## Anthropic 官方

1. The new rules of context engineering for Claude 5 generation models(Thariq Shihipar,2026-07-24)
   https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models
   - "removed over 80% of Claude Code's system prompt for models like Claude Opus 5 and Claude Fable 5 with no measurable loss on our coding evaluations"(沒公開評測指標)
   - 六個轉變:rules→judgement、examples→interface design、upfront context→progressive disclosure、repetition→simple descriptions、manual memory→auto-memory、simple specs→rich references
   - "Keep your CLAUDE.md lightweight and briefly describe what your repo is for, but spend most of the tokens on gotchas inside of the codebase."
   - "Think of skills as lightweight guides to let Claude find information when needed. Avoid making them overconstrained, except in highly important areas."
   - 本 repo 07-29 的上下文瘦身已照這篇做過一輪。

2. Prompting best practices(現行版,涵蓋 Fable 5.1 / Opus 5 / Sonnet 5 等)
   https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
   - "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals"
   - Opus 4.5/4.6 對系統提示更敏感:"The fix is to dial back any aggressive language. Where you might have said "CRITICAL: You MUST use this tool when...", you can use more normal prompting"
   - "Prefer general instructions over prescriptive steps. A prompt like "think thoroughly" often produces better reasoning than a hand-written step-by-step plan."
   - "Claude Opus 5 is the exception: it verifies its own work well without explicit instruction, and verification instructions carried over from prompts tuned for earlier models can cause over-verification"

3. Prompting Claude Opus 5
   https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5
   - Task scope and over-verification:"If your prompt contains explicit verification instructions ("include a final verification step for any non-trivial task," "use a subagent to verify"), remove them: instructions like these cause over-verification on Claude Opus 5, and removing them reduces wasted tokens with no loss in quality."(沒附數字)
   - Code review:"If your review prompt says "only report high-severity issues" or "be conservative," the model may follow that instruction literally and report less; ask it to report everything and filter in a separate pass instead."
   - Self-correction:"Avoid instructing re-checks it already performs ("double-check your answer," "re-verify before responding")"
   - 回覆與寫進磁碟的文件都比前代長,要明講長度;更愛派子代理,要明講什麼情況才派。

4. Prompting Claude Sonnet 5
   https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5
   - Code review harnesses:"When a review prompt says things like "only report high-severity issues," "be conservative," or "don't nitpick," Claude Sonnet 5 may follow that instruction more faithfully than earlier models did ... Precision typically rises, but measured recall can fall"
   - 建議措辭:"Report every issue you find, including ones you are uncertain about or consider low-severity. Do not filter for importance or confidence at this stage - a separate verification step will do that. ... For each finding, include your confidence level and an estimated severity so a downstream filter can rank them."
   - "Iterate on prompts against a subset of your evals or test cases to validate recall or F1 score gains."
   - 字面遵循:"It does not silently generalize an instruction from one item to another"

5. Skill authoring best practices
   https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
   - "Default assumption: Claude is already very smart. Only add context Claude doesn't already have."
   - 自由度配脆弱度(窄橋給精確指令、空地給方向)
   - "Keep SKILL.md body under 500 lines";"Keep references one level deep from SKILL.md";長於 100 行的參考檔開頭放目錄
   - "Avoid time-sensitive information"——舊做法放 "Old patterns" 區塊
   - "Create evaluations BEFORE writing extensive documentation";至少三個評測、跨 Haiku/Sonnet/Opus 測

## 研究

6. Gloaguen, Mündler, Müller, Raychev, Vechev(ETH),Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?,arXiv 2602.11988,2026-02-12
   https://arxiv.org/abs/2602.11988
   - "providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average"
   - "instructions in the context files are well followed by coding agents, repository overviews ... are not helpful"
   - "context files are useful for specifying non-standard coding practices"
   - 二手摘要另稱:LLM 產的檔成功率約 −3%、開發者寫的約 +4%(原文數字本次沒讀到全文,只引摘要)

7. McMillan,Instruction Adherence in Coding Agent Configuration Files: A Factorial Study of Four File-Structure Variables,arXiv 2605.10039,2026-05-11
   https://arxiv.org/abs/2605.10039
   - 1,650 場 Claude Code 工作階段、Sonnet 4.6 為主:檔案大小、規則位置、拆檔方式、相鄰檔矛盾,四個變數對「照做一條簡單標註」的遵守率都量不到效果
   - "each additional function the agent generates is associated with approximately 5.6% lower odds of compliance per step (OR = 0.944)"

8. Jaroslawicz 等,How Many Instructions Can LLMs Follow at Once?(IFScale),arXiv 2507.11538,2025-07
   https://arxiv.org/abs/2507.11538
   - 500 條指令時最好的模型 68%;漏做是主要失敗;推理模型到 100–250 條前近乎滿分

## 沒查的

- 使用者貼文裡的「計費斷崖」與 Claude 現行長上下文計價:沒查,本題結論不依賴它。
- 席位用的 `sonnet` 別名目前對到哪一版:沒查。
