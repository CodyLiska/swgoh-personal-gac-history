<template>
  <div class="border-t border-slate-800 px-4 py-3">
    <table class="w-full text-sm">
      <thead>
        <tr class="text-slate-500 text-left">
          <th class="font-normal py-1">Date</th>
          <th class="font-normal py-1">Outcome</th>
          <th class="font-normal py-1 text-right">Banners</th>
          <th class="font-normal py-1 text-right">Duration</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(b, i) in battles" :key="i" class="border-t border-slate-800/50">
          <td class="py-1 text-slate-300">{{ shortDate(b.date) }}</td>
          <td class="py-1">
            <span :class="outcomeColor(b.outcome)">{{ b.outcome }}</span>
          </td>
          <td class="py-1 text-right text-amber-300">{{ b.banners }}</td>
          <td class="py-1 text-right text-slate-400">{{ duration(b.duration_sec) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({ battles: Array })

function shortDate(d) {
  return d ? d.slice(0, 10) : '—'
}
function duration(sec) {
  if (!sec) return '—'
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return m ? `${m}m ${s}s` : `${s}s`
}
function outcomeColor(o) {
  return {
    Win: 'text-emerald-400',
    Loss: 'text-red-400',
    Retreat: 'text-orange-400',
    Draw: 'text-slate-400',
  }[o] || 'text-slate-300'
}
</script>
