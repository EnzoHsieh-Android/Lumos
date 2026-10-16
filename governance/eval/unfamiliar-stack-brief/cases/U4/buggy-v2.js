import assert from 'node:assert/strict';
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

async function processAll(items, worker) {
  return Promise.all(items.map(worker));
}

async function run(count) {
  let active = 0;
  let peak = 0;
  const items = Array.from({ length: count }, (_, index) => index + 1);
  const result = await processAll(items, async value => {
    active += 1;
    peak = Math.max(peak, active);
    await delay(value % 2 ? 8 : 1);
    active -= 1;
    return value * 2;
  });
  assert.deepEqual(result, items.map(value => value * 2));
  assert.deepEqual(await processAll([], async value => value), []);
  return peak;
}

const normal = process.argv[2] === 'normal';
const peak = await run(normal ? 2 : 20);
process.exit(normal ? (peak <= 3 ? 0 : 3) : (peak <= 3 ? 0 : 1));
