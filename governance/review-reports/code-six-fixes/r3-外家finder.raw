severity: minor
blocking: 否
引句:「r2 = _sp.run([sys.executable, GRAPHCTL, "delguard", "--staged", "--json"], cwd=str(root), capture_output=True, text=True, timeout=120, env=dict(os.environ, LUMOS_DELGUARD_DEADLINE="0.0001"))」
file: `scripts/test_lumos.py:25825`
場景: 0.1ms 幾乎必在 `git diff` 完成後的 `_over()` 就走 `_degraded_json("timeout")`，根本未進 vault scan；即使 `_trunc["hit"]` 或 `timeout-partial` 行為日後壞掉，此測試仍會綠，具體可翻紅鑑別方式是加斷言 `j2["reason"] == "timeout-partial"`，現行測試會得到 `"timeout"`。

max severity: minor
