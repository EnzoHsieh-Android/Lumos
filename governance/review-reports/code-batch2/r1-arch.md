### arch-f1 五條退場告示漏指回裁定筆記——同 diff 內 skill 版有附、code 版沒附,兩處對不齊
severity: minor
引句:「# ⛔ mutate 家族已退場(2026-08-26 建了沒人跑批次裁定:消費者 2026-08-08 已裁死、治理帳 0 次;復活=有真消費者立案從 git 史撿回)」
佐證:file: `scripts/lumos:10534`
佐證:file: `scripts/lumos:3984`

### arch-f2 roster_flag 尾綴命名是全檔唯一,同族布林全裸字——diff 自開新例
severity: minor
引句:「def _loop_status_disposal(rounds, loop_id, spec, n_badlines=0, root=None, bad_linenos=None, env=None, roster_flag=False, repo=None):」
佐證:file: `scripts/lumos:4666`

## 對齊良好的面
_roster_tail 巢狀=同檔 30+ 例慣例且無第二呼叫方(不重蹈 beats);_lint_load_and_validate 擺位正確;anomalies 單一消費者、與 quiet= 先例同模;[F] 訊息三段式同 Check N;if True: 分段有先例;撿回 fixture 無孤立。
