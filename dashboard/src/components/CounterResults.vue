<template>
  <section>
    <div v-if="!selected" class="text-slate-400">
      Search and select an enemy above to see your best counters.
    </div>

    <div v-else>
      <h2 class="text-lg font-semibold mb-1">
        Best counters vs
        <span class="text-blue-400">{{ enemyLabel }}</span>
      </h2>
      <p class="text-sm text-slate-400 mb-4">
        {{ results.length }} of your team{{ results.length === 1 ? '' : 's' }} have
        attacked this {{ matchMode === 'team' ? 'exact team' : 'leader' }}.
      </p>

      <div v-if="!results.length" class="text-slate-400">
        No attack history against this enemy yet.
      </div>

      <ul v-else class="space-y-2">
        <TeamRow
          v-for="(r, i) in results"
          :key="i"
          :rank="i + 1"
          :agg="r"
        />
      </ul>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import TeamRow from './TeamRow.vue'
import { useUnits } from '../composables/useUnits'

const props = defineProps({
  results: Array,
  matchMode: String,
  selected: Object,
})

const { unitName } = useUnits()

const enemyLabel = computed(() => {
  if (!props.selected) return ''
  if (props.matchMode === 'team') {
    return (props.selected.members || []).map(unitName).join(', ')
  }
  return props.selected.leader
})
</script>
