import { describe, expect, test } from 'claude-code/testing'
import { HANDOFF_MAIN, HANDOFF_SUB, MARK_MAIN, MARK_SUB, withHandoff } from './register'

// 條款綁在測試標題開頭(Projects/Claude-mod第二批_計劃 條款節)。

describe('壓縮前附交棒要求', () => {
  test('S1 沒有指示時直接附主會談版', () => {
    expect(withHandoff(undefined, false)).toBe(HANDOFF_MAIN)
    expect(withHandoff('', false)).toBe(HANDOFF_MAIN)
    expect(withHandoff('  \n ', false)).toBe(HANDOFF_MAIN)
  })

  test('S1 原本有指示時接在後面,原文一字不改', () => {
    const orig = '只保留第三節的討論\n  縮排也要留著'
    const out = withHandoff(orig, false)
    expect(out.startsWith(orig + '\n\n')).toBe(true)
    expect(out.endsWith(HANDOFF_MAIN)).toBe(true)
  })

  test('S1 附加段第一行是固定標記行', () => {
    expect(HANDOFF_MAIN.split('\n')[0]).toBe(MARK_MAIN)
    expect(HANDOFF_SUB.split('\n')[0]).toBe(MARK_SUB)
  })

  test('S2 已有標記行就不再附', () => {
    const once = withHandoff('先前的指示', false)
    expect(withHandoff(once, false)).toBe(once)
    expect(withHandoff(`  ${MARK_MAIN}  \n其他`, false)).toBe(`  ${MARK_MAIN}  \n其他`)
  })

  test('S2 句中提到標記不算已附', () => {
    const orig = `請別刪掉 ${MARK_MAIN} 這幾個字`
    expect(withHandoff(orig, false)).toBe(`${orig}\n\n${HANDOFF_MAIN}`)
  })

  test('S3 子代理附精簡版,兩種標記各判各的', () => {
    expect(withHandoff(undefined, true)).toBe(HANDOFF_SUB)
    const parent = withHandoff('父會談帶下來的指示', false)
    expect(withHandoff(parent, true)).toBe(`${parent}\n\n${HANDOFF_SUB}`)
    const sub = withHandoff(undefined, true)
    expect(withHandoff(sub, true)).toBe(sub)
  })
})
