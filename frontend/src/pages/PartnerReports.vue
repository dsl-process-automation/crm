<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Partner Reports" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="tabIndex === 0 && partnerReportsListView?.customListActions"
        :actions="partnerReportsListView.customListActions"
      />
      <Button
        v-if="tabIndex === 0 && permissions.data?.permissions?.create"
        variant="solid"
        :label="__('New Report')"
        iconLeft="plus"
        @click="createNew"
      />
    </template>
  </LayoutHeader>
  <Tabs
    v-model="tabIndex"
    as="div"
    :tabs="tabs"
    class="flex h-full flex-1 flex-col overflow-hidden [&_[role='tab']]:px-0 [&_[role='tablist']]:gap-7.5 [&_[role='tablist']]:border-b [&_[role='tablist']]:px-5 [&_[role='tabpanel']:not([hidden])]:flex [&_[role='tabpanel']:not([hidden])]:min-h-0 [&_[role='tabpanel']:not([hidden])]:grow"
  >
    <template #tab-panel>
      <template v-if="tabs[tabIndex]?.name === 'Partner Reports'">
        <ViewControls
          ref="viewControls"
          v-model="partnerReports"
          v-model:loadMore="loadMore"
          v-model:resizeColumn="triggerResize"
          v-model:updatedPageCount="updatedPageCount"
          doctype="CRM Partner Report"
          :options="{
            defaultViewName: __('Partner Reports View'),
            allowedViews: ['list', 'group_by'],
          }"
        />
        <PartnerReportsListView
          v-if="partnerReports.data && rows.length"
          ref="partnerReportsListView"
          v-model="partnerReports.data.page_length_count"
          v-model:list="partnerReports"
          :rows="rows"
          :columns="columns"
          :options="{
            showTooltip: false,
            resizeColumn: true,
            rowCount: partnerReports.data.row_count,
            totalCount: partnerReports.data.total_count,
            canDelete: permissions.data?.permissions?.delete,
          }"
          @loadMore="() => loadMore++"
          @columnWidthUpdated="() => triggerResize++"
          @updatePageCount="(count) => (updatedPageCount = count)"
          @showReport="showReport"
          @applyFilter="(data) => viewControls.applyFilter(data)"
          @selectionsChanged="(selections) => viewControls.updateSelections(selections)"
        />
        <EmptyState
          v-else-if="partnerReports.data && !rows.length"
          name="Partner Reports"
          :icon="PartnerReportIcon"
          :description="__('It appears that there are currently no Partner Reports available. You can create a Partner Report using the New Report button.')"
        />
      </template>
      <PartnerReportAnalysisTab
        v-else-if="tabs[tabIndex]?.name === 'Group Number Analysis'"
        metric-group="group"
      />
      <PartnerReportAnalysisTab v-else metric-group="backup" />
    </template>
  </Tabs>
  <PartnerReportModal
    v-if="showPartnerReportModal"
    v-model="showPartnerReportModal"
    v-model:reportId="selectedReportId"
    :report-ids="visibleReportIds"
    :report-id="selectedReportId"
    @submitted="handleSubmitted"
    @saved="handleSaved"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import PartnerReportIcon from '@/components/Icons/PartnerReportIcon.vue'
import PartnerReportModal from '@/components/Modals/PartnerReportModal.vue'
import PartnerReportsListView from '@/components/ListViews/PartnerReportsListView.vue'
import PartnerReportAnalysisTab from '@/components/PartnerReports/PartnerReportAnalysisTab.vue'
import ViewControls from '@/components/ViewControls.vue'
import EmptyState from '@/components/ListViews/EmptyState.vue'
import { usersStore } from '@/stores/users'
import { formatDate, timeAgo } from '@/utils'
import { Button, Tabs, createResource } from 'frappe-ui'
import { computed, ref } from 'vue'

const { getUser } = usersStore()

const partnerReports = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)
const partnerReportsListView = ref(null)
const showPartnerReportModal = ref(false)
const selectedReportId = ref('new')
const tabIndex = ref(0)

const tabs = [
  { name: 'Partner Reports', label: 'Partner Reports' },
  { name: 'Group Number Analysis', label: 'Group Number Analysis' },
  { name: 'Back Up Rate Analysis', label: 'Back Up Rate Analysis' },
]

const visibleReportIds = computed(() => rows.value.map((report) => report.name).filter(Boolean))

const permissions = createResource({
  url: 'crm.api.partner_report.get_partner_report_permissions',
  auto: true,
  initialData: { permissions: {} },
})

const rows = computed(() => {
  if (
    !partnerReports.value?.data?.data ||
    !['list', 'group_by'].includes(partnerReports.value.data.view_type)
  ) {
    return []
  }

  return partnerReports.value.data.data.map((report) => {
    let mappedRow = {}

    partnerReports.value.data.rows.forEach((fieldname) => {
      mappedRow[fieldname] = report[fieldname]

      if (fieldname === 'reporting_month' && report[fieldname]) {
        mappedRow[fieldname] = {
          label: formatReportingMonth(report[fieldname]),
          value: report[fieldname],
        }
      } else if (fieldname === 'submitted_by' && report[fieldname]) {
        const user = getUser(report[fieldname])
        mappedRow[fieldname] = {
          label: user?.full_name || report[fieldname],
          ...(user || {}),
        }
      } else if (['creation', 'modified'].includes(fieldname) && report[fieldname]) {
        mappedRow[fieldname] = {
          label: formatDate(report[fieldname]),
          timeAgo: __(timeAgo(report[fieldname])),
        }
      }
    })

    return mappedRow
  })
})

const columns = computed(() => {
  let listColumns = partnerReports.value?.data?.columns || []

  if (listColumns.length) {
    listColumns = listColumns.map((column, index) => {
      if (index === listColumns.length - 1) {
        return { ...column, align: 'right' }
      }
      return column
    })
  }

  return listColumns
})

function createNew() {
  selectedReportId.value = 'new'
  showPartnerReportModal.value = true
}

function showReport(name) {
  selectedReportId.value = name
  showPartnerReportModal.value = true
}

function handleSubmitted(name) {
  partnerReports.value?.reload?.()
  selectedReportId.value = name
  setTimeout(() => {
    showPartnerReportModal.value = true
  })
}

function handleSaved() {
  partnerReports.value?.reload?.()
}

function formatReportingMonth(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
  })
}
</script>
