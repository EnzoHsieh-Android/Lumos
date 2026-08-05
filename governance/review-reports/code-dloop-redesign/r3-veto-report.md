- severity: major — `scripts/lumos:8167`  
  具體失敗場景：先寫一筆 round-less、帶完整處置帳的合法記錄，系統產生內部鍵 `__seq0`；下一筆再使用合法且未受限制的 `--round __seq0`，會因 `groups.setdefault(rid_, [])` 被併入上一筆，而不是成為新的判定輪。若第二筆留痕與 hash 合法但沒有 `findings_set`，舊 carrier 仍可替最新記錄提供處置帳，使 disposal gate 偽 PASS。新增測試只覆蓋兩筆皆 round-less，未覆蓋使用者 round-id 與內部鍵碰撞。內部鍵應使用不可能與外部 round-id 相等的型別，或拒絕保留前綴。  
  引句：「groups[f"__seq{len(groups)}"] = [r]」

max severity: major
