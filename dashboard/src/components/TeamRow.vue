<template>
  <li class="bg-slate-900 border border-slate-800 rounded-lg">
    <button
      @click="open = !open"
      class="w-full flex items-center gap-4 px-4 py-3 text-left hover:bg-slate-800/50 rounded-lg"
    >
      <span class="text-slate-500 w-6 text-sm shrink-0">#{{ rank }}</span>

      <span class="flex-1 min-w-0">
        <span class="font-medium text-slate-100">{{ team.leader }}</span>
        <span class="text-slate-400 text-xs block truncate">
          {{ team.members.join(', ') }}
        </span>
      </span>

      <span class="text-right shrink-0">
        <span :class="['font-semibold', winColor]">{{ winPct }}%</span>
        <span class="text-slate-500 text-xs block">win rate</span>
      </span>

      <span class="text-right shrink-0 w-20">
        <span class="font-semibold text-amber-300">{{ avgBanners }}</span>
        <span class="text-slate-500 text-xs block">avg banners</span>
      </span>

      <span class="text-right shrink-0 hidden sm:block w-28">
        <span class="text-slate-300 text-sm">{{ record }}</span>
        <span class="text-slate-500 text-xs block">W-L-R-D</span>
      </span>

      <span
        v-if="agg.lowSample"
        class="shrink-0 text-amber-400 text-xs border border-amber-700/50 rounded px-1.5 py-0.5"
        title="Small sample — low confidence"
      >
        n={{ agg.attempts }}
      </span>
    </button>

    <BattleDetail v-if="open" :battles="agg.battles" />
  </li>
</template>

<script setup>
import { ref, computed } from 'vue'
import BattleDetail from './BattleDetail.vue'
import { useUnits } from '../composables/useUnits'

const props = defineProps({
  rank: Number,
  agg: Object,
})

const { teamNames } = useUnits()
const open = ref(false)

const team = computed(() => teamNames(props.agg.leader, props.agg.members))
const winPct = computed(() => Math.round(props.agg.winRate * 100))
const avgBanners = computed(() => props.agg.avgBanners.toFixed(1))
const record = computed(
  () => `${props.agg.wins}-${props.agg.losses}-${props.agg.retreats}-${props.agg.draws}`,
)
const winColor = computed(() => {
  const p = winPct.value
  if (p >= 75) return 'text-emerald-400'
  if (p >= 50) return 'text-yellow-400'
  return 'text-red-400'
})
</script>
