severity: major

我的立場是三個月後接手的人,看合約與圖譜是否一致。審了 `r1-pack-test.patch` 和 `r1-pack-code.patch`,並在 `/Users/enzo/harness/lumos-reach3`(HEAD d5f1970d8)實跑。`-k t_choice_layer_` 37 條全過;5 篇動過的筆記 `lumos lint` 都 0 問題;筆記裡的 `[test:]` 名稱都存在。兩支 `drift scan` 報的問題都跟這次新增的行無關。

severity: major
blocking: 是
`ARCHITECTURE.md:108`、`ARCHITECTURE.md:112`、`ARCHITECTURE.md:142`、`skills/lumos-project-notes/reference.md:119`、`skills/lumos-project-notes/reference.md:1266`:這次新增了頂層指令 `choice-layer`,argparse 實數變成 103,但這五處文件仍寫「102 個頂層命令」。diff 只改了 `commands/INDEX.md`,沒動這兩份。
失敗場景:`t_docs_command_count` 轉紅,全套測試閘與 CI 都會擋推送。
最小重現:`python3.14 scripts/test_lumos.py -k t_docs_command_count`,輸出 `✗ ARCHITECTURE.md 命令數與 argparse 同步  claim={'102'} actual=103`,`reference.md` 同樣紅。
修法:兩份文件的 102 都改成 103。
引句:「choice-points·choice-kill·choice-layer(改動選擇點與存活判讀)」

severity: minor
blocking: 否
`skills/lumos-code-loop/SKILL.md` 的「改動選擇點」那一條:新加的步驟標成③,後面原本的「存活要人處置」也還是③,接著是④,編號重複。照著做的人分不清判讀分層和人工處置誰先誰後。
引句:「③存活先判讀分層(四步,[[Projects/選擇點存活回指條款_計劃]])」

severity: minor
blocking: 否
`scripts/test_lumos.py` 的 `t_choice_layer_template`:條款 S13 字面要求「記下第 1 份之後 `--part 2 --list` 仍取到原本的第 2 份」。端到端測試只造了 1 份清單,所以只驗到 `--part 1` 不變,`--part 2` 只驗「沒有那一份就 rc2」。第 n 份(n≥2)的讀取如果壞了,例如固定回第 1 份,測試仍全綠。分份邏輯只用 `_choice_layer_split` 的單元案例驗了 `[20, 2, 3, 2]`。
引句:「check("S13 --part 2(沒有那一份)→ rc2", _ckl_cmd(root, fake, "--part", "2", "--list", lid).returncode == 2, "")」

severity: minor
blocking: 否
`scripts/lumos` 的 `_BOOKKEEPING_DIRS`:新加的 `governance/choice-layers/` 讓提交判讀檔不使代碼審留痕失效,但沒有測試守住。`reread-verdicts` 有三道測試(在清單裡、不算改動量、不讓留痕失效),這個資料夾一道都沒有,日後被誤刪或改名也不會翻紅。計劃範圍 9 寫了這個行為,但沒有對應條款綁測試。
引句:「"governance/choice-layers/",」

我另外看過、沒發現問題的合約面:
- guard-kill rc 優先序和 `--json` 純淨:`_kill_revert` 與原本逐支流程的等秒、checkout、讀回修改時間完全同序;`_kill_target` 多擋 `.git` 的行為已寫進 `Systems/guard-kill.md` 的 WHY。
- `_kill_cap` 在符合行 20 條以內時行為不變,bound-tests 閘的證據行保留不受影響。
- 新欄位 `layer`、`judgment`、`judgment_sha`、`deps_sha` 已進 `_GOV_FIELD_TYPES`;`("choice-kill","layer")` 已進 `LOOP_NOT_CLOSE_EVENTS`;`_note_audit_write_verdict` 新增的參數都有預設值,既有呼叫端不受影響。
- 推送閘:`存活` 拆成子原因後,擋不擋與回報上限不看層,S9 與 S16 的測試有比對 rc 與擋下清單。

總結:最高等級是 major
