severity: minor

## F1 計劃開著改寫後,「已收尾的計劃」這條分支沒有任何測試守
severity: minor
blocking: 否
引句:「        return status in _STATUS_ENUM["project"] and status not in _DRIFT_CLOSED」
這行是本輪改的。在臨時副本把它改成只剩 `status in _STATUS_ENUM["project"]`(即 done/superseded 的計劃也算開著),跑 `-k drift_ack`、`-k drift_check`、`-k drift_doctor` 共 112 條斷言全綠。
`t_drift_ack_routed_rejects` 只測已收尾的 Issue、沒狀態欄的計劃;`t_drift_ack_routed_tracked_state` 只用 Issue。結果是綁到 done 或 superseded 的計劃,表態會被收下,scan 與 doctor 也當它還開著,而修正宣稱要擋的正是這種。
行為本身正確:新寫法與舊寫法等價,沒有 status 或 status 不在表內回 False,superseded 回 False。
建議:補一條綁 done 或 superseded 計劃的 rc2 斷言,以及 scan 判已收尾的斷言。
file: `scripts/test_lumos.py:32393`

## 其他鏡頭(逐項走過,無洞)
severity: clean
blocking: 否
- 正確性:`_ns_summary_logical(body).values()` 回「接回續行、以空白連接」的字串,不含縮排前綴,也不含非摘要區的行。`_drift_ack_text` 用的是同一支函式的同一個 `.get(line)`,所以形狀一致。引句:「        if text not in {ln.strip() for ln in body.split("\n")} | set(_ns_summary_logical(body).values()):」
- `rec["date"]` 在 `rec` 建構時就寫入,早於 `_drift_ack_route`。`_drift_ack_route` 只有 `cmd_drift_ack` 一個呼叫點。引句:「rec["until"] = (_dt.date.fromisoformat(rec["date"]) + _dt.timedelta(days=_DRIFT_ACK_DAYS)).isoformat()」
- `_drift_note_state` 吃 `vault_rel/nfc(trel)`。`env.notes` 的鍵在 `load_vault` 就 NFC 化,查得到。unreadable 的筆記改走 None,回 `("", "")` 被擋,訊息顯示「沒有類型/沒有狀態」,略不精確,但沒有失敗場景。引句:「typ, st = _drift_note_state(env, vault_rel)(f"{vault_rel}/{nfc(trel)}") or ("", "")」
- 測試假綠檢查:在臨時副本逐一改壞,都有測試翻紅。
  - doctor 拿掉 `_ns_summary_logical`:`t_drift_doctor_dead_acks` ③ 紅。
  - 去處判斷一律當開著:`t_drift_ack_routed_rejects` ②③④⑤ 紅。
  - 期限多加 1 天:`t_drift_ack_routed_fields` 紅。
  - `_drift_note_state` 拿掉 `_note_unreadable` 判斷:`t_drift_ack_routed_tracked_state` ③ 紅。
  - 唯一沒翻紅的是 F1 那個變異。
  引句:「check("④沒有起點:不標 born_now;有起點的新寫:標", nob and not any(x.get("born_now") for x in nob)」

最高等級 minor,blocking 0 條。
