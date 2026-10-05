<script setup lang="ts">
import { ref } from 'vue'
import { Hand, Loader2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import grainy from '@/assets/grainy.gif'

const message = ref('')
const error = ref('')
const loading = ref(false)

async function greet() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch('/api/hello')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data: { message: string } = await res.json()
    message.value = data.message
  } catch {
    message.value = ''
    error.value = 'No pude contactar la API. Revisa que el contenedor "api" esté corriendo.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="mx-auto grid min-h-screen max-w-5xl items-center gap-10 px-6 py-12 md:grid-cols-2">
    <section class="order-2 md:order-1">
      <h1 class="text-5xl font-bold leading-tight tracking-tight md:text-6xl">
        Bienvenido a bordo
      </h1>
      <p class="mt-4 max-w-md text-lg text-muted-foreground">
        Este es el punto de partida del proyecto. Saluda a Grainy para comprobar que el
        frontend y la API se están hablando.
      </p>

      <Button class="mt-8" size="lg" :disabled="loading" @click="greet">
        <Loader2 v-if="loading" class="animate-spin" />
        <Hand v-else />
        Saludar a Grainy
      </Button>

      <Card class="mt-8 max-w-md p-5" aria-live="polite">
        <p v-if="message" class="text-xl font-semibold">{{ message }}</p>
        <p v-else-if="error" class="font-medium text-destructive">{{ error }}</p>
        <p v-else class="text-muted-foreground">Grainy todavía no ha dicho nada.</p>
      </Card>
    </section>

    <section class="order-1 flex justify-center md:order-2">
      <div
        class="aspect-square w-full max-w-md overflow-hidden rounded-[2.5rem] border-2 border-ink bg-secondary shadow-[8px_8px_0_0_var(--ink)]"
      >
        <img :src="grainy" alt="Grainy, personaje de pelo azul con corona y sudadera roja" class="size-full object-contain p-6" />
      </div>
    </section>
  </main>
</template>
