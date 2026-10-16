const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

async function processAll(items, worker, limit = 3) {
  let next = 0;
  async function consume() {
    while (next < items.length) {
      const index = next++;
      await worker(items[index]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, consume));
}

async function run(count) {
  let active = 0;
  let peak = 0;
  await processAll(Array.from({ length: count }), async () => {
    active += 1;
    peak = Math.max(peak, active);
    await delay(5);
    active -= 1;
  });
  return peak;
}

const normal = process.argv[2] === 'normal';
const peak = await run(normal ? 2 : 20);
process.exit(normal ? (peak <= 3 ? 0 : 3) : (peak <= 3 ? 0 : 1));
