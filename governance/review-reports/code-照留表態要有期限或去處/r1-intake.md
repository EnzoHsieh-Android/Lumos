# code-照留表態要有期限或去處 r1 收貨

兩席:正確性-sonnet(1 major、2 minor)、架構對齊-sonnet(3 minor)。三道:引句全錨、refcheck 無缺檔越界、報告已正規化。輪內有 major,全部折。

| id | 一句 | 重現 | 去向 |
|---|---|---|---|
| c-F1 | `_drift_note_state` 沒有測試守,改成永遠回 None 測試照綠 | HIT:席位實跑;補測試前照做翻不紅 | 折:補 scan 與 doctor 綁去處開著/收尾的測試 |
| c-F2 | doctor 用實體行比對,多行 RULE 的 retire 照留永遠不報 | HIT:retire 表態記接回續行的整條 | 折:改用同 `_drift_ack_text` 的口徑 |
| c-F3 | 「old is None 也標 born_now」的翻紅釘沒釘住 | HIT:席位改成 old is not True 測試照綠 | 折:補直接驗 `_drift_probe_check` 無起點不標的測試 |
| a-F1 | 同 c-F2 | HIT | 折(同 c-F2) |
| a-F2 | 計劃開著的寫法跟鄰居 `not in _DRIFT_CLOSED` 不同 | HIT | 折:改成在狀態表內而且不在 `_DRIFT_CLOSED` |
| a-F3 | 表態端另取狀態、沒防讀不出;同一支裡取日期兩種寫法 | HIT | 折:表態端改用 `_drift_note_state`;期限從表態日 `date` 算 |
