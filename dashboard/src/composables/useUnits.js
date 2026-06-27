import { ref } from 'vue'

// base_id -> display name, loaded once from the build output.
const units = ref({})
let loaded = false

function prettify(baseId) {
  if (!baseId) return ''
  // Fallback only — the build maps every id we've seen, so this is rarely hit.
  return baseId.charAt(0) + baseId.slice(1).toLowerCase()
}

export function useUnits() {
  async function loadUnits() {
    if (loaded) return
    const res = await fetch('/data/units.json')
    units.value = await res.json()
    loaded = true
  }

  function unitName(baseId) {
    return units.value[baseId] || prettify(baseId)
  }

  // Render a team as readable names: leader first (already readable), then members.
  function teamNames(leader, charIds) {
    const memberNames = (charIds || []).map(unitName)
    return { leader: leader || memberNames[0] || '—', members: memberNames }
  }

  return { units, loadUnits, unitName, teamNames }
}
