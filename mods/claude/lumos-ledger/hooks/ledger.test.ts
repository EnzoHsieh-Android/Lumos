import { describe, expect, test } from 'claude-code/testing'
import { BUF_MAX, FLUSH_AT, createLedger, pickMain, sessionOk, seatOf, spawnEvent, spawnFields, toolExtra, vaultIn, type Io } from './register'
import { RULES } from './rules-fixture'
import { SEAT_CASES } from './seat-fixture'

// S13:並行、重新載入、/clear;另驗位置判定、寫入失敗與暫時失敗(Projects/Lumos事件帳_計劃 做法第 2 節)。
// 讀寫檔與 git 全用假的:測的是緩衝、塊名、串行佇列這些自己的邏輯,不是引擎。

const MAIN = '/repo'
type FakeOpts = {
  git?: 'ok' | 'not-git' | 'boom' | 'worktree' | 'dubious'
  vault?: boolean
  failWrites?: number
  writeDelay?: boolean
  randDown?: boolean
  gate?: { wait: Promise<void> | null }
  tempCwds?: Set<string> // 這些 cwd 的 git 一律逾時(暫時失敗)
  links?: Record<string, string> // 路徑 → 連結目標(檢查連結用)
  dangling?: Set<string> // 懸空連結:列目錄看得到是連結,stat 跟過去卻不存在
  gitGate?: { wait: Promise<void> | null } // 第一次 git 卡住,用來在判定期間塞事件
}

function fakeIo(opts: FakeOpts = {}) {
  const files = new Map<string, string>()
  const writes: string[] = []
  let clock = 1_000_000
  let seq = 0
  let failLeft = opts.failWrites ?? 0
  let gitCalls = 0
  const isLinkPath = (p: string) => Object.keys(opts.links ?? {}).includes(p)
  const io: Io = {
    run: async (_argv, cwd) => {
      gitCalls += 1
      if (opts.gitGate?.wait) await opts.gitGate.wait
      const g = opts.git ?? 'ok'
      if (g === 'boom' || opts.tempCwds?.has(cwd)) throw new Error('timeout')
      if (g === 'dubious') return { exitCode: 128, stdout: '', stderr: "fatal: detected dubious ownership in repository at '/repo'" }
      if (g === 'not-git') return { exitCode: 128, stdout: '', stderr: 'fatal: not a git repository (or any of the parent directories): .git' }
      const top = g === 'worktree' ? '/wt/x' : MAIN
      return { exitCode: 0, stdout: `${top}\n${MAIN}/.git\n`, stderr: '' }
    },
    list: async path => {
      // 依已知的檔、連結推出每一層有什麼:連結本身標 isLink、不往下;其他上層當一般資料夾
      const linkSet = new Set([...Object.keys(opts.links ?? {}), ...(opts.dangling ?? [])])
      const known = [...files.keys(), ...linkSet, `${MAIN}/docs/x`]
      if (path === `${MAIN}/docs`) return opts.vault === false ? [] : [{ name: 'demo-knowledge', kind: 'dir', isLink: false }]
      const pre = `${path}/`
      const out = new Map<string, { name: string; kind: string; isLink: boolean }>()
      for (const k of known) {
        if (!k.startsWith(pre)) continue
        const name = k.slice(pre.length).split('/')[0]
        const full = pre + name
        if (linkSet.has(full)) out.set(name, { name, kind: 'other', isLink: true })
        else if (!out.has(name)) out.set(name, { name, kind: files.has(full) ? 'file' : 'dir', isLink: false })
      }
      if ([...linkSet].some(l => path === l || path.startsWith(`${l}/`))) throw new Error('ENOENT') // 不跟連結
      if (out.size) return [...out.values()]
      throw new Error('ENOENT')
    },
    stat: async path => {
      if (isLinkPath(path)) return { kind: 'dir', isLink: true }
      if (files.has(path)) return { kind: 'file', isLink: false }
      if ([...files.keys()].some(p => p.startsWith(`${path}/`))) return { kind: 'dir', isLink: false }
      return null
    },
    exists: async path => files.has(path),
    write: async (path, text) => {
      if (opts.writeDelay) await Promise.resolve()
      if (opts.gate?.wait && !path.endsWith('.gitignore')) await opts.gate.wait
      if (failLeft > 0 && !path.endsWith('.gitignore')) {
        failLeft -= 1
        throw new Error('EACCES: read-only')
      }
      writes.push(path)
      files.set(path, text)
    },
    now: () => clock,
    // randDown:隨機字串遞減,塊名的先後只能靠毫秒那一段排
    rand8: () => (opts.randDown ? 0xffffffff - seq++ : seq++).toString(16).padStart(8, '0'),
  }
  return {
    io,
    files,
    writes,
    tick: (ms: number) => { clock += ms },
    setClock: (ms: number) => { clock = ms },
    gitCalls: () => gitCalls,
  }
}

const chunks = (files: Map<string, string>) =>
  [...files.keys()].filter(p => p.endsWith('.jsonl')).sort()
const events = (files: Map<string, string>, path: string) =>
  files.get(path)!.trim().split('\n').map(l => JSON.parse(l))
const allIds = (files: Map<string, string>) =>
  chunks(files).flatMap(c => events(files, c).filter(e => e.ev !== 'ledger_error').map(e => e.id))

describe('lumos-ledger 寫入', () => {
  test('S13 主迴圈與兩個子代理同時送事件:每筆恰好出現在一個塊、順序照到達、沒有塊被改寫、沒有空塊、塊名嚴格遞增', async () => {
    const f = fakeIo({ writeDelay: true })
    const l = createLedger(f.io)
    const sent: string[] = []
    const jobs: Promise<void>[] = []
    for (let i = 0; i < 3 * FLUSH_AT + 7; i++) {
      for (const agent of [null, 'a1', 'a2']) {
        const id = `${agent ?? 'main'}-${i}`
        sent.push(id)
        l.add('S1', '/repo', { v: 1, ev: 'tool', agent, id })
      }
      if (i % 20 === 0) jobs.push(l.flushSession('S1'))
    }
    jobs.push(l.flushSession('S1'))
    await Promise.all(jobs)
    const cs = chunks(f.files)
    expect(allIds(f.files)).toEqual(sent)
    expect(new Set(f.writes).size).toBe(f.writes.length)
    for (const c of cs) expect(events(f.files, c).length).toBeGreaterThan(0)
    const names = cs.map(c => c.split('/').pop()!)
    for (let i = 1; i < names.length; i++) expect(names[i] > names[i - 1]).toBe(true)
  })

  test('S13 同一回合裡 cwd 來回換(cd sub、cd ..):照到達順序寫,不拆成亂序的兩桶', async () => {
    const f = fakeIo()
    const l = createLedger(f.io)
    const sent: string[] = []
    for (let i = 0; i < 6; i++) {
      sent.push(`e${i}`)
      l.add('S1', i % 2 === 0 ? '/repo/sub' : '/repo', { v: 1, ev: 'tool', id: `e${i}` })
    }
    await l.flushSession('S1')
    expect(allIds(f.files)).toEqual(sent)
  })

  test('S13 同一行程時鐘不動或倒退:塊名仍嚴格遞增(不靠隨機字串排序)', async () => {
    const f = fakeIo({ randDown: true })
    const l = createLedger(f.io)
    for (let i = 0; i < 5; i++) {
      l.add('S1', '/repo', { v: 1, ev: 'tool', id: i })
      await l.flushSession('S1')
      if (i === 2) f.setClock(10) // 倒退
    }
    expect(allIds(f.files)).toEqual([0, 1, 2, 3, 4])
  })

  test('S13 寫到一半又有事件進來:新事件留在新緩衝,不被吃掉也不重寫', async () => {
    let release: () => void = () => {}
    const gate: { wait: Promise<void> | null } = { wait: new Promise<void>(r => { release = r }) }
    const f = fakeIo({ gate })
    const l = createLedger(f.io)
    l.add('S1', '/repo', { v: 1, ev: 'tool', id: 'first' })
    const p1 = l.flushSession('S1')
    for (let i = 0; i < 5; i++) await Promise.resolve() // 讓第一塊卡在寫檔
    l.add('S1', '/repo', { v: 1, ev: 'tool', id: 'during' })
    gate.wait = null
    release()
    await p1
    await l.flushSession('S1')
    expect(allIds(f.files)).toEqual(['first', 'during'])
  })

  test('S13 重新載入後再寫(時鐘倒退):不覆蓋任何既有塊,新塊排在舊塊之後', async () => {
    const f = fakeIo({ randDown: true })
    const before = createLedger(f.io)
    before.add('S1', '/repo', { v: 1, ev: 'tool', id: 'old' })
    await before.flushSession('S1')
    const old = new Map(f.files)
    f.setClock(500) // 新載入的模組從零開始,時鐘還倒退
    const after = createLedger(f.io)
    after.add('S1', '/repo', { v: 1, ev: 'tool', id: 'new' })
    await after.flushSession('S1')
    for (const [p, t] of old) expect(f.files.get(p)).toBe(t)
    expect(new Set(f.writes).size).toBe(f.writes.length)
    expect(allIds(f.files)).toEqual(['old', 'new'])
  })

  test('S13 /clear:換會談前收到的事件寫在舊會談的資料夾', async () => {
    const f = fakeIo()
    const l = createLedger(f.io)
    l.add('OLD', '/repo', { v: 1, ev: 'tool', id: 'before-clear' })
    l.add('NEW', '/repo', { v: 1, ev: 'tool', id: 'after-clear' })
    await l.flushSession('OLD')
    await l.flushSession('NEW')
    const byDir = chunks(f.files).map(c => [c.split('/').slice(-2, -1)[0], events(f.files, c)[0].id])
    expect(byDir).toContainEqual(['OLD', 'before-clear'])
    expect(byDir).toContainEqual(['NEW', 'after-clear'])
  })

  test('收事件不交回寫入佇列:add 不回傳任何東西,主流程不必等寫檔', () => {
    const f = fakeIo({ gate: { wait: new Promise<void>(() => {}) } })
    const l = createLedger(f.io)
    for (let i = 0; i < FLUSH_AT + 5; i++) expect(l.add('S1', '/repo', { v: 1, ev: 'tool' }) as unknown).toBe(undefined)
  })

  test('會談編號不是單層名稱:不收', async () => {
    const f = fakeIo()
    const l = createLedger(f.io)
    for (const s of ['../x', '', '.hidden', 'a/b']) l.add(s, '/repo', { v: 1, ev: 'tool' })
    await l.flushSession('../x')
    expect(f.files.size).toBe(0)
  })
})

describe('lumos-ledger 位置判定', () => {
  test('S2 不在 git repo 或沒有圖譜:不寫任何檔、緩衝不累積、之後不再每筆跑 git', async () => {
    for (const opts of [{ git: 'not-git' as const }, { vault: false }]) {
      const f = fakeIo(opts)
      const l = createLedger(f.io)
      l.add('S1', '/tmp/x', { v: 1, ev: 'tool' })
      await l.flushSession('S1')
      const calls = f.gitCalls()
      for (let i = 0; i < 10; i++) l.add('S1', '/tmp/x', { v: 1, ev: 'tool' })
      expect(l._state.pending('S1')).toBe(0) // 還沒寫就不累積
      for (let i = 0; i < 200; i++) l.add('S1', '/tmp/x', { v: 1, ev: 'tool' })
      await l.flushSession('S1')
      expect(f.files.size).toBe(0)
      expect(f.gitCalls()).toBe(calls)
      expect(l._state.pending('S1')).toBe(0)
    }
  })

  test('S2 在 worktree 裡:寫到主 checkout,事件帶 worktree;第一次寫補 .gitignore', async () => {
    const f = fakeIo({ git: 'worktree' })
    const l = createLedger(f.io)
    l.add('S1', '/wt/x/sub', { v: 1, ev: 'tool' })
    await l.flushSession('S1')
    const [c] = chunks(f.files)
    expect(c.startsWith('/repo/governance/runtime/events/S1/')).toBe(true)
    expect(events(f.files, c)[0].worktree).toBe('/wt/x')
    expect(f.files.get('/repo/governance/runtime/events/.gitignore')).toBe('*\n')
  })

  test('事件帳路徑任一層是符號連結:不寫(寫到 repo 外的資料夾讀取端也不讀)', async () => {
    for (const link of ['/repo/governance', '/repo/governance/runtime', '/repo/governance/runtime/events',
                        '/repo/governance/runtime/events/S1']) {
      const f = fakeIo({ links: { [link]: '/outside' } })
      const l = createLedger(f.io)
      l.add('S1', '/repo', { v: 1, ev: 'tool' })
      await l.flushSession('S1')
      expect(f.writes).toEqual([])
    }
  })

  test('暫時判不了位置:緩衝留著、超過上限丟最舊的並記下丟了幾筆', async () => {
    const f = fakeIo({ git: 'boom' })
    const l = createLedger(f.io)
    for (let i = 0; i < BUF_MAX + 3; i++) l.add('S1', '/repo', { v: 1, ev: 'tool', id: i })
    await l.flushSession('S1')
    expect(f.files.size).toBe(0)
    expect(l._state.pending('S1')).toBe(BUF_MAX)
    expect(l._state.dropped('S1')).toBe(3)
  })

  test('中途某個 cwd 暫時判不了:前面的照寫,那一筆起的事件留著,順序不亂', async () => {
    const f = fakeIo({ tempCwds: new Set(['/repo/stuck']) })
    const l = createLedger(f.io)
    l.add('S1', '/repo', { v: 1, ev: 'tool', id: 'a' })
    l.add('S1', '/repo/stuck', { v: 1, ev: 'tool', id: 'b' })
    l.add('S1', '/repo', { v: 1, ev: 'tool', id: 'c' })
    await l.flushSession('S1')
    expect(allIds(f.files)).toEqual(['a'])
    expect(l._state.pending('S1')).toBe(2)
  })

  test('git 回其他錯誤(例如 dubious ownership):當暫時失敗,緩衝留著,不當成這裡不記', async () => {
    const f = fakeIo({ git: 'dubious' })
    const l = createLedger(f.io)
    l.add('S1', '/repo', { v: 1, ev: 'tool', id: 'kept' })
    await l.flushSession('S1')
    l.add('S1', '/repo', { v: 1, ev: 'tool', id: 'kept2' })
    expect(f.files.size).toBe(0)
    expect(l._state.pending('S1')).toBe(2)
  })
})

describe('lumos-ledger 收尾與邊角', () => {
  test('判定等待期間緩衝溢位:沒查過判定的事件不被取走,每一筆都寫出、留著或記成丟了', async () => {
    let release: () => void = () => {}
    const gitGate: { wait: Promise<void> | null } = { wait: new Promise<void>(r => { release = r }) }
    const f = fakeIo({ gitGate })
    const l = createLedger(f.io)
    l.add('S1', '/repo', { v: 1, ev: 'tool', id: 'first' })
    const p = l.flushSession('S1')
    for (let i = 0; i < 5; i++) await Promise.resolve()
    for (let i = 0; i < BUF_MAX; i++) l.add('S1', `/repo/new${i % 2}`, { v: 1, ev: 'tool', id: `n${i}` })
    gitGate.wait = null
    release()
    await p
    const written = allIds(f.files).length
    expect(written + l._state.pending('S1') + l._state.dropped('S1')).toBe(BUF_MAX + 1)
  })

  test('懸空的符號連結、或最後一層的 .gitignore 是連結:都不寫', async () => {
    for (const d of ['/repo/governance', '/repo/governance/runtime/events/.gitignore']) {
      const f = fakeIo({ dangling: new Set([d]) })
      const l = createLedger(f.io)
      l.add('S1', '/repo', { v: 1, ev: 'tool' })
      await l.flushSession('S1')
      expect(f.writes).toEqual([])
    }
  })

  test('遇到連結不寫時:之前累積的錯誤與丟失筆數保留,這段也算進丟失', async () => {
    const f = fakeIo({ failWrites: 1 })
    const l = createLedger(f.io)
    l.add('S1', '/repo', { v: 1, ev: 'tool', id: 'lost' })
    await l.flushSession('S1')
    const g = fakeIo({ links: { '/repo/governance': '/outside' } })
    ;(f.io as any).list = g.io.list
    ;(f.io as any).stat = g.io.stat
    l.add('S1', '/repo', { v: 1, ev: 'tool', id: 'blocked' })
    await l.flushSession('S1')
    expect(l._state.lost('S1')).toBe(2)
  })
})

describe('lumos-ledger 出錯看得見', () => {
  test('S3 寫入失敗:會談照常,下一塊開頭補一筆 ledger_error,帶原因與丟了幾筆', async () => {
    const f = fakeIo({ failWrites: 1 })
    const l = createLedger(f.io)
    l.add('S1', '/repo', { v: 1, ev: 'tool', id: 'lost1' })
    l.add('S1', '/repo', { v: 1, ev: 'tool', id: 'lost2' })
    await l.flushSession('S1')
    expect(chunks(f.files).length).toBe(0)
    l.add('S1', '/repo', { v: 1, ev: 'tool', id: 'next' })
    await l.flushSession('S1')
    const [c] = chunks(f.files)
    const evs = events(f.files, c)
    expect(evs[0].ev).toBe('ledger_error')
    expect(String(evs[0].what)).toContain('read-only')
    expect(evs[0].lost).toBe(2)
    expect(evs[evs.length - 1].id).toBe('next')
  })

  test('工具呼叫中途丟錯(例如被中斷):照樣記一筆 ok=false、interrupted=true', () => {
    expect(toolExtra({ tool: 'Bash', command: 'sleep 9' }, undefined, true)).toEqual(
      { tool: 'Bash', ok: false, denied: false, interrupted: true, cmd: 'sleep 9', cmd_len: 7 })
    expect(toolExtra({ tool: 'Read', file_path: '/a' }, { isError: true }, false)).toEqual(
      { tool: 'Read', ok: false, denied: false, paths: ['/a'] })
  })

  test('S12 子代理派孫代理:spawn 事件的 agent 欄是發起的子代理(parentAgentId),不是空的', () => {
    const child = spawnFields({ parentAgentId: 'sub-1', subagentType: 'general-purpose' }, { model: 'm', agentId: 'grand-1' })
    expect(child.agent).toBe('sub-1')
    expect(child.extra.child).toBe('grand-1')
    const top = spawnFields({ subagentType: 'Explore' }, { deny: 'no' })
    expect(top.agent).toBe(null)
    expect(top.extra.denied).toBe(true)
  })

  test('S12 交給 record 的整組參數:發起方是 parentAgentId,不是子代理自己的 agentId', () => {
    expect(spawnEvent({ parentAgentId: 'sub-1', agentId: 'wrong' }, { agentId: 'grand-1' }))
      .toEqual(['sub-1', 'spawn', { agent_type: null, model: null, child: 'grand-1', denied: false, cwd: null, seat: null }])
  })

  test('補記 S1 Grep、Glob 記 pattern、glob(各前 200 字)與 output_mode;不是字串不記', () => {
    const g = toolExtra({ tool: 'Grep', pattern: 'x'.repeat(250), glob: '*.ts', output_mode: 'content', path: '/r' }, {}, false)
    expect(g.pattern).toBe('x'.repeat(200))
    expect(g.glob).toBe('*.ts')
    expect(g.output_mode).toBe('content')
    expect(g.paths).toEqual(['/r'])
    const gl = toolExtra({ tool: 'Glob', pattern: '**/*.md' }, {}, false)
    expect(gl.pattern).toBe('**/*.md')
    expect('glob' in gl || 'output_mode' in gl).toBe(false)
    const bad = toolExtra({ tool: 'Grep', pattern: 5, glob: null, output_mode: {} }, {}, false)
    expect('pattern' in bad || 'glob' in bad || 'output_mode' in bad).toBe(false)
    expect('pattern' in toolExtra({ tool: 'Read', pattern: 'x', file_path: '/a' }, {}, false)).toBe(false)
  })

  test('補記 S2 Bash 記整條指令的長度', () => {
    const e = toolExtra({ tool: 'Bash', command: 'y'.repeat(800) }, {}, false)
    expect(e.cmd).toBe('y'.repeat(500))
    expect(e.cmd_len).toBe(800)
  })

  test('補記 S3 派工記 cwd 與合格的席位標記值,不記派工詞其他內容', () => {
    const a = spawnFields({ prompt: '\n  LUMOS-SEAT: 迴圈/r1/正確性-sonnet\n請審查這份 diff', cwd: '/w' }, { agentId: 'c1' })
    expect(a.extra.seat).toBe('迴圈/r1/正確性-sonnet')
    expect(a.extra.cwd).toBe('/w')
    expect(JSON.stringify(a.extra).includes('請審查')).toBe(false)
    const long = spawnFields({ prompt: 'LUMOS-SEAT: a/r1/' + 'z'.repeat(300) }, {})
    expect(long.extra.seat).toBe(('a/r1/' + 'z'.repeat(300)).slice(0, 200))
    for (const prompt of ['請審查', 'lumos-seat: a/r1/b', '說明\nLUMOS-SEAT: a/r1/b', 'LUMOS-SEAT: a b', 42, undefined]) {
      expect(spawnFields({ prompt }, {}).extra.seat).toBe(null)
    }
    expect(spawnFields({ cwd: 7 }, {}).extra.cwd).toBe(null)
  })

  test('補記 S3 席位標記的共用案例:跟審查席隔離外掛認的一致', () => {
    for (const c of SEAT_CASES) expect([c.prompt, seatOf(c.prompt)]).toEqual([c.prompt, c.seat])
  })

  test('空緩衝不寫空塊', async () => {
    const f = fakeIo()
    const l = createLedger(f.io)
    await l.flushSession('S1')
    l.add('S1', '/repo', { v: 1, ev: 'tool' })
    await l.flushSession('S1')
    await l.flushSession('S1')
    expect(chunks(f.files).length).toBe(1)
  })
})

describe('跟 Python 讀取端共用的規則(rules-fixture.ts)', () => {
  test('會談編號:案例全對', () => {
    for (const s of RULES.session.ok) expect(sessionOk(s)).toBe(true)
    for (const s of RULES.session.bad) expect(sessionOk(s)).toBe(false)
  })

  test('圖譜判定:案例全對(連結的資料夾跟著連結走,跟 _vault_in 一樣)', async () => {
    for (const c of RULES.vault) {
      const links: Record<string, string> = (c as any).links ?? {}
      const dirs = new Set<string>([...c.dirs, ...Object.keys(links)])
      const io = {
        list: async (p: string) => {
          const pre = p === '/v' ? '' : `${p.slice('/v/'.length)}/`
          const names = new Set<string>()
          for (const d of dirs) if (d.startsWith(pre)) names.add(d.slice(pre.length).split('/')[0])
          return [...names].map(n => {
            const full = pre + n
            return { name: n, kind: full in links ? 'other' : 'dir', isLink: full in links }
          })
        },
        stat: async (p: string) => {
          const rel = p.slice('/v/'.length)
          return dirs.has(rel) ? { kind: 'dir', isLink: rel in links } : null
        },
      }
      expect(await vaultIn(io as any, '/v')).toBe(c.want)
    }
  })

  test('主 checkout 判定:案例全對', () => {
    for (const c of RULES.main) expect(pickMain(c.top, c.common)).toBe(c.want)
  })
})
