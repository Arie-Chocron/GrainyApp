<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{ class?: HTMLAttributes['class'] }>()
</script>

<template>
  <div
    data-slot="card"
    :class="cn('rounded-lg border-2 border-ink bg-card text-card-foreground shadow-[6px_6px_0_0_var(--ink)]', props.class)"
  >
    <slot />
  </div>
</template>
