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
          :key="listFiltersKey"
          ref="viewControls"
          v-model="partnerReports"
          v-model:loadMore="loadMore"
          v-model:resizeColumn="triggerResize"
          v-model:updatedPageCount="updatedPageCount"
          doctype="CRM Partner Report"
          :filters="listDefaultFilters"
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
        v-model:filters="sharedFilters"
      />
      <PartnerReportAnalysisTab v-else metric-group="backup" v-model:filters="sharedFilters" />
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
import { computed, ref, watch } from 'vue'

const SHARED_FILTER_STORAGE_KEY = 'crm.partnerReports.sharedFilters'

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
const sharedFilters = ref(loadSharedFilters())

const tabs = [
  { name: 'Partner Reports', label: 'Partner Reports' },
  { name: 'Group Number Analysis', label: 'Group Number Analysis' },
  { name: 'Back Up Rate Analysis', label: 'Back Up Rate Analysis' },
]

const visibleReportIds = computed(() => rows.value.map((report) => report.name).filter(Boolean))
const listDefaultFilters = computed(() => buildListDefaultFilters(sharedFilters.value))
const listFiltersKey = computed(() => JSON.stringify(listDefaultFilters.value))

const permissions = createResource({
  url: 'crm.api.partner_report.get_partner_report_permissions',
  auto: true,
  initialData: { permissions: {} },
})

watch(
  sharedFilters,
  (value) => {
    if (typeof window === 'undefined') {
      return
    }

    window.localStorage.setItem(
      SHARED_FILTER_STORAGE_KEY,
      JSON.stringify(normalizeSharedFilters(value)),
    )
  },
  { deep: true },
)

watch(
  () => partnerReports.value?.params?.filters ?? null,
  (filters) => {
    if (!filters) {
      return
    }

    const nextSharedFilters = buildSharedFiltersFromListFilters(filters)
    if (getSharedFilterSignature(sharedFilters.value) === getSharedFilterSignature(nextSharedFilters)) {
      return
    }

    sharedFilters.value = nextSharedFilters
  },
  { deep: true },
)

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

function createDefaultSharedFilters() {
  return {
    regions: [],
    countries: [],
    partners: [],
    monthFilter: null,
  }
}

function normalizeStringArray(values) {
  if (!Array.isArray(values)) {
    return []
  }

  return Array.from(
    new Set(
      values
        .map((value) => `${value ?? ''}`.trim())
        .filter(Boolean),
    ),
  )
}

function normalizeMonthFilter(filter) {
  if (!filter || typeof filter !== 'object') {
    return null
  }

  if (filter.mode === 'custom') {
    return {
      mode: 'custom',
      quickMonths: Number(filter.quickMonths) || 3,
      startYear: Number(filter.startYear),
      startMonth: Number(filter.startMonth),
      endYear: Number(filter.endYear),
      endMonth: Number(filter.endMonth),
    }
  }

  if (filter.mode === 'quick') {
    return {
      mode: 'quick',
      quickMonths: Math.max(1, Number(filter.quickMonths) || 3),
      startYear: Number(filter.startYear) || 0,
      startMonth: Number(filter.startMonth) || 0,
      endYear: Number(filter.endYear) || 0,
      endMonth: Number(filter.endMonth) || 0,
    }
  }

  return null
}

function normalizeSharedFilters(value) {
  const defaults = createDefaultSharedFilters()
  const nextValue = value && typeof value === 'object' ? value : {}

  return {
    regions: normalizeStringArray(nextValue.regions ?? defaults.regions),
    countries: normalizeStringArray(nextValue.countries ?? defaults.countries),
    partners: normalizeStringArray(nextValue.partners ?? defaults.partners),
    monthFilter: normalizeMonthFilter(nextValue.monthFilter ?? defaults.monthFilter),
  }
}

function buildSharedFiltersFromListFilters(filters) {
  const nextFilters = filters && typeof filters === 'object' ? filters : {}

  return normalizeSharedFilters({
    regions: extractListSelectionValues(nextFilters.region),
    countries: extractListSelectionValues(nextFilters.country),
    partners: extractListSelectionValues(nextFilters.partner),
    monthFilter: extractMonthFilter(nextFilters.reporting_month),
  })
}

function extractListSelectionValues(filterValue) {
  if (filterValue == null || filterValue === '') {
    return []
  }

  if (Array.isArray(filterValue) && filterValue.length === 2 && typeof filterValue[0] === 'string') {
    const operator = filterValue[0].toLowerCase()
    if (['=', 'equals', 'in'].includes(operator)) {
      return splitFilterValues(filterValue[1])
    }
    return []
  }

  return splitFilterValues(filterValue)
}

function splitFilterValues(value) {
  if (Array.isArray(value)) {
    return normalizeStringArray(value)
  }

  if (typeof value === 'string') {
    if (!value.trim()) {
      return []
    }

    if (value.includes(',')) {
      return normalizeStringArray(value.split(','))
    }

    return normalizeStringArray([value])
  }

  if (value == null) {
    return []
  }

  return normalizeStringArray([value])
}

function extractMonthFilter(filterValue) {
  if (filterValue == null || filterValue === '') {
    return null
  }

  if (Array.isArray(filterValue) && filterValue.length === 2 && typeof filterValue[0] === 'string') {
    const operator = filterValue[0].toLowerCase()

    if (operator === 'between') {
      const range = extractDateRange(filterValue[1])
      return range ? buildCustomMonthFilter(range[0], range[1]) : null
    }

    if (['=', 'equals'].includes(operator)) {
      const dateValue = parseMonthDateValue(filterValue[1])
      return dateValue ? buildCustomMonthFilter(dateValue, dateValue) : null
    }

    return null
  }

  const range = extractDateRange(filterValue)
  if (range) {
    return buildCustomMonthFilter(range[0], range[1])
  }

  const dateValue = parseMonthDateValue(filterValue)
  return dateValue ? buildCustomMonthFilter(dateValue, dateValue) : null
}

function extractDateRange(value) {
  if (Array.isArray(value) && value.length >= 2) {
    const startValue = parseMonthDateValue(value[0])
    const endValue = parseMonthDateValue(value[1])

    if (startValue && endValue) {
      return [startValue, endValue]
    }

    return null
  }

  if (typeof value === 'string') {
    const separator = value.includes(' to ') ? ' to ' : value.includes(',') ? ',' : null
    if (!separator) {
      return null
    }

    const [startValue, endValue] = value.split(separator).map((item) => item.trim())
    const startDate = parseMonthDateValue(startValue)
    const endDate = parseMonthDateValue(endValue)

    if (startDate && endDate) {
      return [startDate, endDate]
    }
  }

  return null
}

function parseMonthDateValue(value) {
  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    return {
      year: value.getFullYear(),
      month: value.getMonth(),
    }
  }

  if (typeof value !== 'string') {
    return null
  }

  const trimmedValue = value.trim()
  if (!trimmedValue) {
    return null
  }

  const literalMatch = trimmedValue.match(/^(\d{4})-(\d{2})(?:-(\d{2}))?$/)
  if (literalMatch) {
    return {
      year: Number(literalMatch[1]),
      month: Number(literalMatch[2]) - 1,
    }
  }

  const parsedDate = new Date(trimmedValue)
  if (Number.isNaN(parsedDate.getTime())) {
    return null
  }

  return {
    year: parsedDate.getFullYear(),
    month: parsedDate.getMonth(),
  }
}

function buildCustomMonthFilter(startValue, endValue) {
  if (!startValue || !endValue) {
    return null
  }

  let startYear = Number(startValue.year)
  let startMonth = Number(startValue.month)
  let endYear = Number(endValue.year)
  let endMonth = Number(endValue.month)

  const startDate = new Date(startYear, startMonth, 1)
  const endDate = new Date(endYear, endMonth, 1)
  if (endDate < startDate) {
    ;[startYear, endYear] = [endYear, startYear]
    ;[startMonth, endMonth] = [endMonth, startMonth]
  }

  return {
    mode: 'custom',
    quickMonths: getInclusiveMonthSpan(startYear, startMonth, endYear, endMonth),
    startYear,
    startMonth,
    endYear,
    endMonth,
  }
}

function getInclusiveMonthSpan(startYear, startMonth, endYear, endMonth) {
  return Math.max(1, (endYear - startYear) * 12 + (endMonth - startMonth) + 1)
}

function getSharedFilterSignature(filters) {
  const normalizedFilters = normalizeSharedFilters(filters)

  return JSON.stringify({
    regions: [...normalizedFilters.regions].sort(),
    countries: [...normalizedFilters.countries].sort(),
    partners: [...normalizedFilters.partners].sort(),
    monthWindow: resolveMonthWindow(normalizedFilters.monthFilter),
  })
}

function loadSharedFilters() {
  if (typeof window === 'undefined') {
    return createDefaultSharedFilters()
  }

  try {
    const rawValue = window.localStorage.getItem(SHARED_FILTER_STORAGE_KEY)
    if (!rawValue) {
      return createDefaultSharedFilters()
    }

    return normalizeSharedFilters(JSON.parse(rawValue))
  } catch {
    return createDefaultSharedFilters()
  }
}

function buildListDefaultFilters(filters) {
  const normalizedFilters = normalizeSharedFilters(filters)
  const listFilters = {}

  if (normalizedFilters.regions.length) {
    listFilters.region = ['in', normalizedFilters.regions]
  }

  if (normalizedFilters.countries.length) {
    listFilters.country = ['in', normalizedFilters.countries]
  }

  if (normalizedFilters.partners.length) {
    listFilters.partner = ['in', normalizedFilters.partners]
  }

  const monthWindow = resolveMonthWindow(normalizedFilters.monthFilter)
  if (monthWindow) {
    listFilters.reporting_month = [
      'between',
      [
        formatDateLiteral(monthWindow.startYear, monthWindow.startMonth, 1),
        formatDateLiteral(
          monthWindow.endYear,
          monthWindow.endMonth,
          getLastDayOfMonth(monthWindow.endYear, monthWindow.endMonth),
        ),
      ],
    ]
  }

  return listFilters
}

function resolveMonthWindow(filter) {
  if (!filter) {
    return null
  }

  if (filter.mode === 'custom') {
    return {
      startYear: Number(filter.startYear),
      startMonth: Number(filter.startMonth),
      endYear: Number(filter.endYear),
      endMonth: Number(filter.endMonth),
    }
  }

  const endDate = new Date()
  const endYear = endDate.getFullYear()
  const endMonth = endDate.getMonth()
  const monthCount = Math.max(1, Number(filter.quickMonths) || 3)
  const startDate = new Date(endYear, endMonth, 1)
  startDate.setMonth(startDate.getMonth() - (monthCount - 1))

  return {
    startYear: startDate.getFullYear(),
    startMonth: startDate.getMonth(),
    endYear,
    endMonth,
  }
}

function formatDateLiteral(year, monthIndex, day) {
  return [year, `${monthIndex + 1}`.padStart(2, '0'), `${day}`.padStart(2, '0')].join('-')
}

function getLastDayOfMonth(year, monthIndex) {
  return new Date(year, monthIndex + 1, 0).getDate()
}
</script>
