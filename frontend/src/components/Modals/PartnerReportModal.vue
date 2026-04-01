<template>
  <Dialog v-model="show" :options="{ size: '7xl' }">
    <template #body-title>
      <div class="flex items-center justify-between gap-3">
        <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
          {{ reportId === 'new' ? __('New Partner Report') : __('Partner Report') }}
        </h3>
        <Button variant="ghost" class="w-7" icon="x" @click="show = false" />
      </div>
    </template>
    <template #body-content>
      <div class="-mx-4 -mb-4 flex h-[82vh] min-h-0 flex-col overflow-hidden sm:-mx-6">
        <PartnerReport
          :report-id="reportId"
          :in-dialog="true"
          :initial-partner="initialPartner"
          :initial-partner-label="initialPartnerLabel"
          :lock-partner="lockPartner"
          @submitted="handleSubmitted"
          @saved="handleSaved"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import PartnerReport from '@/pages/PartnerReport.vue'
import { Button } from 'frappe-ui'

const show = defineModel({ type: Boolean })

defineProps({
  reportId: {
    type: String,
    default: 'new',
  },
  initialPartner: {
    type: String,
    default: '',
  },
  initialPartnerLabel: {
    type: String,
    default: '',
  },
  lockPartner: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['submitted'])

function handleSubmitted(name) {
  emit('submitted', name)
  show.value = false
}

function handleSaved(name) {
  emit('saved', name)
  show.value = false
}
</script>