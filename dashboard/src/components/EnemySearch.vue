<template>
  <div class="relative">
    <input
      v-model="query"
      @focus="open = true"
      :placeholder="placeholder"
      class="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
    />

    <ul
      v-if="open && filtered.length"
      class="absolute z-10 mt-1 w-full max-h-80 overflow-auto bg-slate-800 border border-slate-700 rounded-md shadow-lg"
    >
      <li
        v-for="opt in filtered"
        :key="opt.key"
        @click="select(opt)"
        class="px-3 py-2 cursor-pointer hover:bg-slate-700 flex items-center justify-between gap-3"
      >
        <span class="truncate">
          <span class="text-slate-100">{{ label(opt) }}</span>
          <span v-if="matchMode === 'team'" class="text-slate-400 text-xs block truncate">
            {{ membersText(opt) }}
          </span>
        </span>
        <span class="text-xs text-slate-400 shrink-0">{{ opt.count }} battles</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useUnits } from '../composables/useUnits'

const props = defineProps({
  options: Array,
  matchMode: String,
  modelValue: String,
})
const emit = defineEmits(['update:modelValue'])

const { unitName } = useUnits()
const query = ref('')
const open = ref(false)

const placeholder = computed(() =>
  props.matchMode === 'team'
    ? 'Search enemy team by any character…'
    : 'Search enemy leader…',
)

function label(opt) {
  return opt.leader || unitName(opt.members?.[0])
}
function membersText(opt) {
  return (opt.members || []).map(unitName).join(', ')
}
function haystack(opt) {
  return `${label(opt)} ${membersText(opt)}`.toLowerCase()
}

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  const opts = props.options
  if (!q) return opts.slice(0, 50)
  return opts.filter((o) => haystack(o).includes(q)).slice(0, 50)
})

function select(opt) {
  emit('update:modelValue', opt.key)
  query.value = label(opt)
  open.value = false
}

// Reset the box when the selection is cleared elsewhere (e.g. mode switch).
watch(
  () => props.modelValue,
  (v) => {
    if (!v) query.value = ''
  },
)
</script>
