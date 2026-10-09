severity: minor

## Finding 1：部署错误测试没有确认实际错误原因

severity: minor  
blocking: 否

引句:「self.assertEqual(report["verdict"], "not_assessed")」

佐证 file: `scripts/test_test_quality_cli.py:743`

- input：删除 `test_quality_scan.py` 后，以全局 `--vault` 执行 `test-quality scan sample.py --json`；但夹具没有建立 `sample.py`。
- expected：除了 rc2、`complete=false`、`verdict=not_assessed`，还应确认错误原因明确指向缺少 scanner sidecar／部署不完整，而不是输入文件不存在等无关错误。
- 判准出处：方法名 `test_global_vault_option_retains_structured_deployment_error` 及固定 boundary source 对该案例的定义。
- case_source：
  - boundary source SHA-256：`66a1f8fe3d19174c21fc7104e0e3f38e0b651387893569752828908009d1c35a`
  - 修后测试文件 SHA-256：`9e6cd515c059e20b0b385a855c28d1aafd170ea94dfe63521542352914e7cbbc`
- comparison：修前没有该测试；修后新增，但当前断言只核对通用失败形状与没有 traceback。产品若因为 `sample.py` 不存在而返回同样形状，测试仍会通过。
- attribution：这是修后测试本身的鉴别力缺口，不代表产品现时确实走错错误分支。
- before/after 动态结果：未判定。固定版本实验目录无法建立，因此没有实际载入任一版本产品，也没有产品 rc。

## 修订轮三问

1. 原问题修复效果：静态上新增了混合 sidecar、缓存逃逸、旧 scanner、畸形 Semgrep、UTF-16 与全局参数案例；动态修前/修后效果未能执行确认。
2. 正常／错误／相邻路径保留：
   - 正常：纯 UTF-16 JUnit 预期 rc0、`executed`。
   - 错误：DTD、畸形 Semgrep、混合 sidecar 预期 rc2。
   - 相邻：旧 scanner 下 `--help` 预期 rc0；外部 symlink 缓存必须保留。
   - 这些方法静态上会调用复制后的 `scripts/lumos`、`run_cli`，或直接载入真实 `scripts/lumos`；没有把实现替换成测试内假对象。动态结果未判定。
3. 新发现同一案例修前／修后：全局 vault 案例修前不存在、修后存在，但没有隔离并确认 deployment-error 原因；产品行为未执行，不能宣称修前失败或修后通过。

## 实际执行与环境

- 实验目录建立：
  - cwd：`/tmp`
  - 命令：`mkdir -p /tmp/lumos-seat-work/code-test-quality-native-push/boundary-b`
  - rc：1
  - 行为：`Operation not permitted`；没有建立副本、没有载入产品。
- 单测探测：
  - cwd：`/tmp/lumos-readme-oct-audit`
  - 命令：`python3.14 scripts/test_test_quality_cli.py -k test_plain_utf16_report_retains_valid_capture`
  - rc：1（unittest harness）
  - 行为：`setUp` 在建立 `TemporaryDirectory` 时即因没有可写临时目录失败；未进入 `run_cli`，不是产品红灯。
- 因此前后版本产品 rc、真实行为与动态 attribution 均为未判定。

## 固定图谱镜头

- vendored 测试套件假红：混合 sidecar 与旧 scanner-help 案例静态覆盖相关边界；未动态确认。
- lumos-cli-lifecycle：本席方法未覆盖 re-inject 合约，未发现冲突。
- lumos-deinit：缓存 symlink 逃逸案例要求外部 artifact 保持不变；未动态确认。
- lumos-cli-read：本席没有 search/superseded 路径案例。
- bound-tests-gate：没有实际跑到测试入口，因此不能主张绑定测试已通过。
- guard-kill：本席没有覆盖 rc 优先序或 JSON purity。
- 授权与归属：缓存案例只覆盖外部 bytecode，不覆盖 LICENSE/COPYING/NOTICE 合约。
- 测试假绿形态：混合 sidecar 夹具用 `assertNotEqual` 确认旧核心确实移除了 summary validation，并要求拒绝产出 capture；但本轮没有实际重播。

## 覆盖与阅读量

实际覆盖：

- 固定 binding source、boundary source、CLAUDE.md、66 行人工镜头。
- `r3-repair.patch` 中 `scripts/test_test_quality_cli.py` 的完整相关 diff。
- `r3-snapshot.patch`、`r3-product-snapshot.patch` 的目标文件入口定位。
- 修后测试的 `capture` 调用链及全局 vault 方法。
- manifest 仅提取 `required_paths`。
- 阅读／搜索／重读输出合计约 1,739 行，未超过 1,800 行。

未验范围：

- `archive_only`、r1/r2 报告、作者 intake。
- 固定清单外的程序与其他席负责文件。
- Windows 原生路径。
- 三份大型 snapshot 的其他文件内容。
- 所有需要可写临时目录的修前／修后动态实验。