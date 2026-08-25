# loop-friction-v2 r1 收貨紀錄(2026-08-25)

## 引句機械收貨
- s1/s3/ext:quote-check 全數錨定。
- s2 #2:截為「…」(快照自身巢狀「」);其唯一實質引句(refcheck 正則)已錨定,#2 對應主張(rewrite 帳)由下列重現覆蓋 → HIT。
- arch:引句抽取器 0 命中(其行文以 file: 佐證為主);內文引號片段 17 段中 3 段可錨回快照(python 正規化比對:「r1-intake 慣例本案起用」「裁甲當日先行落地並釘測試」「正本歸屬循既有聲明…」全 HIT);其跨檔主張與 s2(refcheck 實測/治理帳 rewrite 事件)、s3(21 條核銷)獨立結論一致 → 收貨成立。

## 佐證抽驗(命令+輸出+結論)
- rewrite 事件在帳:`grep -c '"kind": "rewrite"' docs/.governance-log.jsonl` → 1(note 含 prev=loop-friction;successor=loop-friction-v2)→ HIT。
- 兩守衛紅→綠(s1F1):修前 in-process 跑 `t_command_index_complete`/`t_every_subcommand_has_when` → `✗ 缺: ['loop rewrite']` ×2;補 HELP_WHEN+commands/05 後重跑 → 兩支 ✓ → HIT(先紅後綠)。
- s2「refcheck 只認反引號」:席位自建樣本實測(有/無反引號各一條,無反引號連 manifest 不進)→ 採信,HIT。
