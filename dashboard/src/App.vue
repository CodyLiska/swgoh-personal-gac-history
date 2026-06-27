<template>
  <div class="min-h-full max-w-5xl mx-auto px-4 py-6">
    <header class="mb-6">
      <h1 class="text-2xl font-bold tracking-tight">GAC Counter Lookup</h1>
      <p class="text-sm text-slate-400 mt-1">
        Pick an enemy team — see which of your teams beat it historically.
        <span v-if="battles.length" class="text-slate-500">
          ({{ offenseCount }} of your attacks across {{ battles.length }} battles)
        </span>
      </p>
    </header>

    <div v-if="loading" class="text-slate-400">Loading battle history…</div>
    <div v-else-if="error" class="text-red-400">{{ error }}</div>

    <template v-else>
      <FacetBar
        v-model:matchMode="matchMode"
        v-model:modeFilter="modeFilter"
        v-model:minSample="minSample"
      />

      <EnemySearch
        :options="enemyOpts"
        :match-mode="matchMode"
        v-model="selectedKey"
        class="mt-4"
      />

      <CounterResults
        :results="results"
        :match-mode="matchMode"
        :selected="selectedEnemy"
        class="mt-6"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import FacetBar from './components/FacetBar.vue'
import EnemySearch from './components/EnemySearch.vue'
import CounterResults from './components/CounterResults.vue'
import { useUnits } from './composables/useUnits'
import { enemyOptions, computeCounters } from './composables/useCounters'

const { loadUnits } = useUnits()

const battles = ref([])
const loading = ref(true)
const error = ref('')

const matchMode = ref('leader') // 'leader' | 'team'
const modeFilter = ref('all')
const minSample = ref(2)
const selectedKey = ref('')

const offenseCount = computed(
  () => battles.value.filter((b) => b.battle_type === 'your_attack').length,
)

const enemyOpts = computed(() =>
  enemyOptions(battles.value, {
    matchMode: matchMode.value,
    modeFilter: modeFilter.value,
  }),
)

const selectedEnemy = computed(
  () => enemyOpts.value.find((o) => o.key === selectedKey.value) || null,
)

const results = computed(() =>
  computeCounters(battles.value, {
    matchMode: matchMode.value,
    modeFilter: modeFilter.value,
    selectedKey: selectedKey.value,
    minSample: minSample.value,
  }),
)

// Changing the match mode or facet can invalidate the current selection.
watch([matchMode, modeFilter], () => {
  if (!enemyOpts.value.some((o) => o.key === selectedKey.value)) {
    selectedKey.value = ''
  }
})

onMounted(async () => {
  try {
    await loadUnits()
    const res = await fetch('/data/battles.json')
    if (!res.ok) throw new Error(`battles.json ${res.status}`)
    battles.value = await res.json()
  } catch (e) {
    error.value = `Failed to load data: ${e.message}. Run the build scripts first.`
  } finally {
    loading.value = false
  }
})
</script>
