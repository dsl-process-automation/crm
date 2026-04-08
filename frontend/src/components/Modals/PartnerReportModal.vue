<template>
  <Dialog v-model="show" :options="{ size: '7xl' }">
    <template #body-title>
      <div class="flex items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
            {{ reportId === 'new' ? __('New Partner Report') : __('Partner Report') }}
          </h3>
          <div v-if="canNavigate" class="flex items-center gap-2">
            <Button
              variant="subtle"
              size="sm"
              icon-left="arrow-left"
              :label="__('Previous')"
              :disabled="!hasPrevious"
              @click="goToPrevious"
            />
            <Button
              variant="subtle"
              size="sm"
              :label="__('Next')"
              icon-right="arrow-right"
              :disabled="!hasNext"
              @click="goToNext"
            />
          </div>
        </div>
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
import { computed } from 'vue'

const show = defineModel({ type: Boolean })

const props = defineProps({
  reportId: {
    type: String,
    default: 'new',
  },
  reportIds: {
    type: Array,
    default: () => [],
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

const emit = defineEmits(['submitted', 'saved', 'update:reportId'])

const currentReportIndex = computed(() => props.reportIds.indexOf(props.reportId))
const canNavigate = computed(
  () => props.reportId !== 'new' && props.reportIds.length > 1 && currentReportIndex.value !== -1,
)
const hasPrevious = computed(() => currentReportIndex.value > 0)
const hasNext = computed(
  () => currentReportIndex.value !== -1 && currentReportIndex.value < props.reportIds.length - 1,
)

function goToPrevious() {
  if (!hasPrevious.value) return
  emit('update:reportId', props.reportIds[currentReportIndex.value - 1])
}

function goToNext() {
  if (!hasNext.value) return
  emit('update:reportId', props.reportIds[currentReportIndex.value + 1])
}

function handleSubmitted(name) {
  emit('submitted', name)
  show.value = false
}

function handleSaved(name) {
  emit('saved', name)
  show.value = false
}
</script>