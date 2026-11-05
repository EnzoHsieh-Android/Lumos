severity: major

整份讀完。我把 spec 的每個假設對照 `.github/workflows/ci.yml`、`cmd_ci_wait` 和 `_ci_list_runs` 查過。發現 2 條會擋的問題和 5 條小問題。

## 做法 1(CI 推分支也跑全套)

severity: major
blocking: 是(照字面只改觸發條件,功能分支推送的 CI 環境會跟 main 不同,可能整批紅或測不到該測的)
spec 段落:做法 1、驗收條款 S6
問題:spec 只說把 `push` 觸發擴大到所有分支,沒處理「功能分支的 push 事件在 CI 裡沒有本機 `main`」。現行 ci.yml 的 `shards`、`gates`、`prep` 三個工作,都只在 `pull_request` 事件補一個追蹤 origin/main 的本機 `main`。ci.yml 自己的註解寫明:沒有本機 main,「找主線的測試(main@{upstream})會整支紅」。以前 push 觸發只有 main,本機 main 天然存在。改成所有分支後,`actions/checkout` 對功能分支只建那條分支,不會建 `main`。
- `shards` 的測試可能整批紅。
- `prep` 的 `pitfalls --diff` 和 `gates` 的 `code-loop check` 找不到主線。前者算不出就退成全套,後者可能用空樹。
- `gates` 的 code-loop、note-shape、drift check 現在也會在功能分支的每次 push 跑,而且都是會擋的步驟。note-shape 步驟的註解寫著「本 workflow 只在推 main 時跑這步」,這個前提被推翻了。首推 `BEFORE` 是 40 個 0,範圍語意也沒人驗過。
- 這會把 RETIRE-IF 的「紅的比例」灌水。紅的原因不是測試壞,是環境不對。
- S6 只驗 yaml 文字(觸發範圍和 concurrency),抓不到這件事。

引句:「`ci.yml` 的 `push` 觸發從 `branches: [main]` 改成所有分支」
引句:「prep 判範圍照現行(push 事件問 lumos,只改文件就文件子集,其他全套)」
佐證:`.github/workflows/ci.yml:84-86`(shards 的補 main 步驟,`if: github.event_name == 'pull_request'`)、`.github/workflows/ci.yml:163-165`(gates 同樣)、`.github/workflows/ci.yml:~188`(note-shape 註解「本 workflow 只在推 main 時跑」)。
建議:做法 1 要加一條「push 事件非 main 時也補本機 main」。`gates` 的 code-loop 步驟要在功能分支首推(`BEFORE` 為 0)的情境實測一次。

## 合併前判定的流程(ci-wait 等哪個 run)

severity: major
blocking: 是(spec 唯一的把關是「ci-wait 判 green」,但 green 不保證那個提交上跑過全套)
spec 段落:實務隱患「守衛面」、做法 1、現況「lumos ci-wait」
問題:`ci-wait` 是依提交編號查 run(`gh run list --commit <sha>`),判的是「那個 sha 的 run 全綠」。但 push 事件的 prep 範圍是用 `github.event.before..sha` 判的,只看這一次推送的差異,不看整條分支相對 main 的差異。典型流程:
1. 推 A(改程式)。首推 `BEFORE` 是 0,全套。
2. A 的 CI 紅,或還在跑。
3. 隨手推 B(只改 README 或 docs)。B 的 push 差異只有文件,prep 判 docs,只跑文件子集,很快綠。
4. `lumos ci-wait` 預設查 HEAD(B),回 green。但 B 這個提交上全套從沒跑過,A 上跑的那一次還沒綠或是紅。

spec 說「CI 由推送本身觸發,所以只要推上去就有全套」,這句只對首推和碰程式的推送成立。守衛檔(`governance/code-loop/`、`anchor-baseline.json`)會讓判定退成全套,所以帳本提交那一步不受影響。問題在「純文件的後續提交」。

本機不再跑全套之後,「ci-wait 判 green」成了唯一證據,而它的語意是逐提交的。spec 沒規定合併前要看的是哪個提交、要看全套那一次。

引句:「CI 由推送本身觸發,所以只要推上去就有全套;」
引句:「prep 判範圍照現行(push 事件問 lumos,只改文件就文件子集,其他全套)」
佐證:`.github/workflows/ci.yml:98-108`(`BEFORE..$SHA` 判 suite)、`scripts/lumos:62971-62994`(`_ci_list_runs` 用 `--commit`)、`scripts/lumos:63118-63150`(done 全綠就判 green,沒看是不是全套)。
建議:二選一。一是功能分支的 push 事件 prep 改成「分支相對 main 的 merge-base..sha」,等於 PR 的語意。二是規定合併前要等「該分支上最後一個程式提交」的 run,或乾脆要求開 PR、看 PR 事件那次(PR 事件一律全套)。

## 做法 1 的觸發寫法

severity: minor
blocking: 否(spec 沒寫死樣式,不照字面也不一定做錯,是陷阱)
spec 段落:做法 1、S6
問題:spec 只說「涵蓋所有分支」,沒寫樣式。現行 tags 用的是 `'*'`,照抄成 `branches: ['*']` 會漏掉含 `/` 的分支,因為 GitHub 的 `*` 不匹配 `/`,要 `**`。這個 repo 的分支就帶斜線(目前這條是 `EnzoHsieh-Android/lumos-frontier-research-survey`,orca worktree 也是)。S6 的測試名只說「涵蓋所有分支」,沒說測什麼樣式。
引句:「`push` 觸發 應 涵蓋所有分支、push 事件的 concurrency 應 以提交編號分組且不取消」
建議:S6 明寫必須是 `'**'`,並加一條含 `/` 的分支名樣本。

## 多會談併發與 concurrency 群組

severity: minor
blocking: 否(影響是後續判定失準,不是首次放行錯誤)
spec 段落:實務隱患「併發」
問題:群組鍵是 `ci-push-<sha>`,沒有 ref。同一個提交推到功能分支又快轉合併進 main 時,兩個 run 同組。
- 功能分支那次在跑,main 那次會排在後面(沒有 cancel-in-progress)。
- 同組再來一個同 sha 的推送(例如另一個會談把同提交推到別的分支名),排隊中的 main 那次會被換掉,變成 cancelled。
- 另一個後果:`ci-wait` 在 main 的 sha 上查,馬上就看得到功能分支那次已完成的綠 run。main 的 run 還沒註冊時,`ci-wait` 靠「全部 done」加一個 30 秒的緩衝窗就回 green,「合併後那一次」可能根本沒被等到。

spec 的「互不取消」只對不同提交成立。
引句:「併發:多個會談各自推分支,各自觸發 CI,互不取消(以提交編號分組)。」
佐證:`.github/workflows/ci.yml` concurrency 段(`github.sha`)、`scripts/lumos:63118-63150`。
建議:群組鍵加 `github.ref`,或在實務隱患承認快轉合併的同 sha 情境。

## GitHub Actions 同時排隊上限

severity: minor
blocking: 否(spec 對「不花人的等待」的宣稱偏樂觀,但不會造成錯誤放行)
spec 段落:實務隱患「機器時間」
問題:每次 CI 是 prep、8 台 shards、gates 共 10 個工作,開了 PR 的提交 push 加 PR 共 20 個。GitHub 免費帳號同時執行的工作上限是 20 個(以我記得的官方文件為準,我沒有重新查證),帳號層級,不分 repo。兩個會談各推一次加一個 PR,第二批就要排隊。
- 排隊期間 `ci-wait` 默認逾時 1800 秒,回 `timeout`、rc 0。
- 實測的 1217 秒是 runner 空閒時的數字。
- 「不讓人等」不成立:合併前就是要等這次 CI。

另外,spec 說公開 repo 不計費,但沒有查證 repo 是不是公開。我這邊沒辦法確認,README 沒寫可見性。
引句:「不讓人等,但 GitHub Actions 的用量會變多」
建議:實務隱患補一句併發上限與排隊,以及 `ci-wait` 逾時後該怎麼做。

## fork 的 PR

已讀,無 finding。push 事件只在來源 repo 觸發,fork 的 PR 走 `pull_request`,不會讓推功能分支的新行為擴到外部。這是單人 repo,fork 是低風險。

## 使用者全域 CLAUDE.md〈推送前〉與新行為

severity: minor
blocking: 否(Q1 正好是 spec 自己列的未決問題,不阻擋,但上線時序要講清楚)
spec 段落:Q1、做法 5
問題:全域〈推送前〉要求「推送前跑完專案的本機閘」,又說「全套在對話裡跑不完時,交給推送前的閘與 CI,但要等 CI 結果出來才回報完成」。新行為本機閘改成只跑子集,字面上不衝突,因為閘就是專案掛鉤。但有三點要處理:
- Q1 狀態是「待查」,spec 規定 AI 不改這句,而做法 5 同步改了專案 CLAUDE.md 與範本。上線後會有一段時間兩邊字面不一致,spec 沒寫過渡期怎麼辦。
- 全域「要等 CI 結果出來才回報完成」現在變成每次推功能分支的常態,不是例外。做法 4 的訊息只講合併前要等,沒講「回報完成」也要等。
- 使用者記憶裡有幾條會變成舊說法(例如「推前本機跑完整閘」、「全套一律切片」、「別重跑驗過的」)。記憶是衍生層,按專案 CLAUDE.md 規則 6 不算真相,但 spec 沒列出要不要清。

引句:「使用者全域 CLAUDE.md 那句是 Q1,不由 AI 改。」
建議:Q1 的處置在上線前先拿到使用者的答覆,或在做法 4 的訊息裡加上「回報完成要等 CI」。

## RETIRE-IF 的量法

severity: minor
blocking: 否(撤除條件仍量得到,只是口徑會混)
spec 段落:RETIRE-IF
問題:「紅」按 GitHub run 的 conclusion 數,run 紅可能是 `gates` 裡的 code-loop、note-shape、drift check 等閘紅,不一定是測試紅。再加上第一條 finding 說的環境問題,比例會被灌水。分母「這類推送次數」也沒說是 run 數還是 push 數。同一個提交開了 PR 後事件不同,是不是要排除也沒寫。
引句:「功能分支推送觸發的 CI 全套紅的次數超過這類推送次數的三成」
建議:寫明數 shards 工作的 conclusion,或把 prep 判 docs 的 run 排除。

## 其他節

已讀,無 finding:範圍、驗收條款 S1–S5 與 S7(各自的條件與測試名一致)、回退、舊否決對照。

總結:最嚴重等級為 major,會擋的問題共 2 條(CI 功能分支環境缺本機 main、逐提交判 green 與只看本次差異的 suite 組合)。
