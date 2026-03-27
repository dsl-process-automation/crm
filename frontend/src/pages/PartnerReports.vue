<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between border-b px-5 py-3">
      <h1 class="text-xl font-semibold text-ink-gray-9">
        {{ __('Partner Reports') }}
      </h1>
      <Button
        variant="solid"
        :label="__('New Report')"
        icon-left="plus"
        @click="createNew"
      />
    </div>

    <!-- Loading -->
    <div v-if="reports.loading" class="flex flex-1 items-center justify-center">
      <LoadingIndicator class="h-6 w-6 text-ink-gray-4" />
    </div>

    <!-- Empty state -->
    <div
      v-else-if="!rows.length"
      class="flex flex-1 flex-col items-center justify-center gap-3 text-ink-gray-5"
    >
      <PartnerReportIcon class="h-12 w-12 opacity-30" />
      <p class="text-base">{{ __('No partner reports yet') }}</p>
      <Button variant="subtle" :label="__('Create First Report')" @click="createNew" />
    </div>

    <!-- Table -->
    <div v-else class="flex-1 overflow-auto">
      <table class="w-full text-sm">
        <thead class="sticky top-0 bg-surface-gray-1 text-ink-gray-5">
          <tr>
            <th class="px-4 py-2.5 text-left font-medium">{{ __('Partner') }}</th>
            <th class="px-4 py-2.5 text-left font-medium">{{ __('Reporting Month') }}</th>
            <th class="px-4 py-2.5 text-left font-medium">{{ __('Partner Satisfaction') }}</th>
            <th class="px-4 py-2.5 text-left font-medium">{{ __('Group Satisfaction') }}</th>
            <th class="px-4 py-2.5 text-left font-medium">{{ __('Submitted By') }}</th>
            <th class="px-4 py-2.5 text-left font-medium">{{ __('Created') }}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-outline-gray-1">
          <tr
            v-for="row in rows"
            :key="row.name"
            class="cursor-pointer hover:bg-surface-gray-1 transition-colors"
            @click="openReport(row.name)"
          >
            <td class="px-4 py-3 font-medium text-ink-gray-9">{{ row.partner }}</td>
            <td class="px-4 py-3 text-ink-gray-7">{{ formatMonth(row.reporting_month) }}</td>
            <td class="px-4 py-3">
              <SatisfactionBadge :value="row.partner_satisfaction" />
            </td>
            <td class="px-4 py-3">
              <SatisfactionBadge :value="row.group_satisfaction" />
            </td>
            <td class="px-4 py-3 text-ink-gray-6">{{ row.submitted_by }}</td>
            <td class="px-4 py-3 text-ink-gray-5">{{ formatDate(row.creation) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Load more -->
      <div v-if="hasMore" class="flex justify-center py-4">
        <Button
          variant="ghost"
          :label="__('Load more')"
          :loading="reports.loading"
          @click="loadMore"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, Button, LoadingIndicator } from 'frappe-ui'
import PartnerReportIcon from '@/components/Icons/PartnerReportIcon.vue'
import SatisfactionBadge from '@/components/PartnerReports/SatisfactionBadge.vue'

const router = useRouter()

const page = ref(1)
const PAGE_LENGTH = 25

const reports = createResource({
  url: 'crm.api.partner_report.get_partner_reports',
  params: { page: page.value, page_length: PAGE_LENGTH },
  auto: true,
})

const rows = computed(() => reports.data?.reports || [])
const total = computed(() => reports.data?.total || 0)
const hasMore = computed(() => rows.value.length < total.value)

function loadMore() {
  page.value++
  reports.update({ params: { page: page.value, page_length: PAGE_LENGTH } })
  reports.reload()
}

function createNew() {
  router.push({ name: 'PartnerReport', params: { reportId: 'new' } })
}

function openReport(name) {
  router.push({ name: 'PartnerReport', params: { reportId: name } })
}

function formatMonth(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long' })
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}
</script>
