<template>
  <div class="flex flex-wrap items-center gap-4">
    <!-- Match mode toggle -->
    <div class="inline-flex rounded-md overflow-hidden border border-slate-700">
      <button
        v-for="m in matchModes"
        :key="m.key"
        @click="$emit('update:matchMode', m.key)"
        :class="[
          'px-3 py-1.5 text-sm',
          matchMode === m.key
            ? 'bg-blue-600 text-white'
            : 'bg-slate-800 text-slate-300 hover:bg-slate-700',
        ]"
      >
        {{ m.label }}
      </button>
    </div>

    <!-- Game-mode facets -->
    <div class="inline-flex rounded-md overflow-hidden border border-slate-700">
      <button
        v-for="m in MODES"
        :key="m.key"
        @click="$emit('update:modeFilter', m.key)"
        :class="[
          'px-3 py-1.5 text-sm',
          modeFilter === m.key
            ? 'bg-indigo-600 text-white'
            : 'bg-slate-800 text-slate-300 hover:bg-slate-700',
        ]"
      >
        {{ m.label }}
      </button>
    </div>

    <!-- Min sample badge threshold -->
    <label class="flex items-center gap-2 text-sm text-slate-400">
      Flag below
      <input
        type="number"
        min="1"
        :value="minSample"
        @input="$emit('update:minSample', Number($event.target.value) || 1)"
        class="w-16 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-slate-100"
      />
      battles
    </label>
  </div>
</template>

<script setup>
import { MODES } from '../composables/useCounters'

defineProps({
  matchMode: String,
  modeFilter: String,
  minSample: Number,
})
defineEmits(['update:matchMode', 'update:modeFilter', 'update:minSample'])

const matchModes = [
  { key: 'leader', label: 'Match by leader' },
  { key: 'team', label: 'Match exact team' },
]
</script>
