// Pure aggregation over the flat battle list. No Vue reactivity here — App.vue
// wraps these in computed(). All functions work on raw ids; display-name
// resolution happens in components via useUnits.

export const MODES = [
  { key: 'all', label: 'All' },
  { key: 'squad_5v5', label: '5v5' },
  { key: 'squad_3v3', label: '3v3' },
  { key: 'fleet', label: 'Fleet' },
]

const OFFENSE = 'your_attack'

function teamKey(charIds) {
  return [...(charIds || [])].sort().join('|')
}

// One toggle (matchMode) controls both how the enemy is grouped and how YOUR
// teams are grouped: by leader, or by exact composition.
export function enemyKeyOf(b, matchMode) {
  return matchMode === 'team' ? teamKey(b.defender_chars) : b.defender
}
export function myKeyOf(b, matchMode) {
  return matchMode === 'team' ? teamKey(b.attacker_chars) : b.attacker
}

function applyMode(battles, modeFilter) {
  const off = battles.filter((b) => b.battle_type === OFFENSE)
  return modeFilter === 'all' ? off : off.filter((b) => b.mode === modeFilter)
}

// Distinct enemies for the search list, with a representative team + count.
export function enemyOptions(battles, { matchMode, modeFilter }) {
  const pool = applyMode(battles, modeFilter)
  const map = new Map()
  for (const b of pool) {
    const key = enemyKeyOf(b, matchMode)
    if (!key) continue
    let opt = map.get(key)
    if (!opt) {
      opt = {
        key,
        leader: b.defender,
        members: b.defender_chars,
        mode: b.mode,
        count: 0,
      }
      map.set(key, opt)
    }
    opt.count++
  }
  return [...map.values()].sort((a, b) => b.count - a.count)
}

function blankAgg(b) {
  return {
    leader: b.attacker,
    members: b.attacker_chars,
    wins: 0,
    losses: 0,
    retreats: 0,
    draws: 0,
    attempts: 0,
    bannerSum: 0,
    lastSeen: null,
    battles: [],
  }
}

// For the selected enemy, rank YOUR teams by win-rate then avg banners.
export function computeCounters(battles, { matchMode, modeFilter, selectedKey, minSample }) {
  if (!selectedKey) return []
  const pool = applyMode(battles, modeFilter).filter(
    (b) => enemyKeyOf(b, matchMode) === selectedKey,
  )

  const groups = new Map()
  for (const b of pool) {
    const key = myKeyOf(b, matchMode)
    if (!key) continue
    let g = groups.get(key)
    if (!g) {
      g = blankAgg(b)
      groups.set(key, g)
    }
    g.attempts++
    g.bannerSum += b.banners || 0
    if (b.outcome === 'Win') g.wins++
    else if (b.outcome === 'Loss') g.losses++
    else if (b.outcome === 'Retreat') g.retreats++
    else if (b.outcome === 'Draw') g.draws++
    if (!g.lastSeen || (b.date && b.date > g.lastSeen)) g.lastSeen = b.date
    g.battles.push(b)
  }

  return [...groups.values()]
    .map((g) => ({
      ...g,
      winRate: g.attempts ? g.wins / g.attempts : 0,
      avgBanners: g.attempts ? g.bannerSum / g.attempts : 0,
      lowSample: g.attempts < (minSample || 1),
      battles: g.battles.sort((a, b) => (b.date || '').localeCompare(a.date || '')),
    }))
    .filter((g) => g.attempts >= 1)
    .sort((a, b) => b.winRate - a.winRate || b.avgBanners - a.avgBanners)
}
