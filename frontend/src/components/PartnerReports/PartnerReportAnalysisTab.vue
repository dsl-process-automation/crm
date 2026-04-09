<template>
	<div class="flex h-full min-h-0 flex-col">
		<div class="border-b px-5 py-4">
			<div class="flex flex-wrap items-center gap-2">
				<div class="text-lg font-medium text-ink-gray-8">
					{{ __('Reporting Dashboard') }}
				</div>

				<div class="ml-auto flex flex-wrap items-center gap-2">
					<Popover placement="bottom-start">
						<template #target="{ togglePopover }">
							<Button
								variant="outline"
								icon-left="filter"
								:label="getFilterButtonLabel(__('Regions'), selectedRegions.length)"
								:disabled="!regionOptions.length"
								@click="togglePopover()"
							/>
						</template>
						<template #body="{ togglePopover }">
							<div class="mt-1 w-80 rounded-lg bg-surface-white p-3 shadow-2xl">
								<div class="flex items-center gap-2">
									<div class="flex-1 text-base font-medium text-ink-gray-8">
										{{ __('Regions') }}
									</div>
									<Button variant="ghost" icon="x" @click="togglePopover()" />
								</div>
								<input
									v-model="queries.regions"
									class="form-input mt-3 w-full"
									type="text"
									:placeholder="__('Search')"
								/>
								<div class="mt-2 flex items-center justify-between text-sm text-ink-gray-5">
									<span>{{ __('{0} selected', [selectedRegions.length]) }}</span>
									<Button
										variant="ghost"
										size="sm"
										:label="__('Clear all')"
										:disabled="!selectedRegions.length"
										@click="clearRegions"
									/>
								</div>
								<div class="mt-2 max-h-72 overflow-y-auto rounded-md border">
									<div
										v-if="regionsResource.loading"
										class="px-3 py-5 text-sm text-ink-gray-5"
									>
										{{ __('Loading...') }}
									</div>
									<label
										v-for="option in filteredRegions"
										v-else
										:key="option.value"
										class="flex cursor-pointer items-center gap-3 border-b px-3 py-2 last:border-b-0 hover:bg-surface-gray-2"
									>
										<FormControl
											type="checkbox"
											:modelValue="selectedRegions.includes(option.value)"
											@update:modelValue="(value) => toggleRegion(option.value, value)"
										/>
										<div class="truncate text-base text-ink-gray-8">
											{{ option.label }}
										</div>
									</label>
									<div
										v-if="!regionsResource.loading && !filteredRegions.length"
										class="px-3 py-5 text-sm text-ink-gray-5"
									>
										{{ __('No matches') }}
									</div>
								</div>
							</div>
						</template>
					</Popover>

					<Popover placement="bottom-start">
						<template #target="{ togglePopover }">
							<Button
								variant="outline"
								icon-left="filter"
								:label="getFilterButtonLabel(__('Countries'), selectedCountries.length)"
								:disabled="!countryOptions.length"
								@click="togglePopover()"
							/>
						</template>
						<template #body="{ togglePopover }">
							<div class="mt-1 w-80 rounded-lg bg-surface-white p-3 shadow-2xl">
								<div class="flex items-center gap-2">
									<div class="flex-1 text-base font-medium text-ink-gray-8">
										{{ __('Countries') }}
									</div>
									<Button variant="ghost" icon="x" @click="togglePopover()" />
								</div>
								<input
									v-model="queries.countries"
									class="form-input mt-3 w-full"
									type="text"
									:placeholder="__('Search')"
								/>
								<div class="mt-2 flex items-center justify-between text-sm text-ink-gray-5">
									<span>{{ __('{0} selected', [selectedCountries.length]) }}</span>
									<Button
										variant="ghost"
										size="sm"
										:label="__('Clear all')"
										:disabled="!selectedCountries.length"
										@click="clearCountries"
									/>
								</div>
								<div class="mt-2 max-h-72 overflow-y-auto rounded-md border">
									<div
										v-if="countriesResource.loading"
										class="px-3 py-5 text-sm text-ink-gray-5"
									>
										{{ __('Loading...') }}
									</div>
									<label
										v-for="option in filteredCountries"
										v-else
										:key="option.value"
										class="flex cursor-pointer items-center gap-3 border-b px-3 py-2 last:border-b-0 hover:bg-surface-gray-2"
									>
										<FormControl
											type="checkbox"
											:modelValue="selectedCountries.includes(option.value)"
											@update:modelValue="(value) => toggleCountry(option.value, value)"
										/>
										<div class="truncate text-base text-ink-gray-8">
											{{ option.label }}
										</div>
									</label>
									<div
										v-if="!countriesResource.loading && !filteredCountries.length"
										class="px-3 py-5 text-sm text-ink-gray-5"
									>
										{{ __('No matches') }}
									</div>
								</div>
							</div>
						</template>
					</Popover>

					<Popover placement="bottom-start">
						<template #target="{ togglePopover }">
							<Button
								variant="outline"
								icon-left="filter"
								:label="getFilterButtonLabel(__('Partners'), selectedPartners.length)"
								:disabled="!partnerOptions.length"
								@click="togglePopover()"
							/>
						</template>
						<template #body="{ togglePopover }">
							<div class="mt-1 w-80 rounded-lg bg-surface-white p-3 shadow-2xl">
								<div class="flex items-center gap-2">
									<div class="flex-1 text-base font-medium text-ink-gray-8">
										{{ __('Partners') }}
									</div>
									<Button variant="ghost" icon="x" @click="togglePopover()" />
								</div>
								<input
									v-model="queries.partners"
									class="form-input mt-3 w-full"
									type="text"
									:placeholder="__('Search')"
								/>
								<div class="mt-2 flex items-center justify-between text-sm text-ink-gray-5">
									<span>{{ __('{0} selected', [selectedPartners.length]) }}</span>
									<Button
										variant="ghost"
										size="sm"
										:label="__('Clear all')"
										:disabled="!selectedPartners.length"
										@click="clearPartners"
									/>
								</div>
								<div class="mt-2 max-h-72 overflow-y-auto rounded-md border">
									<div
										v-if="partnersResource.loading"
										class="px-3 py-5 text-sm text-ink-gray-5"
									>
										{{ __('Loading...') }}
									</div>
									<label
										v-for="option in filteredPartners"
										v-else
										:key="option.value"
										class="flex cursor-pointer items-center gap-3 border-b px-3 py-2 last:border-b-0 hover:bg-surface-gray-2"
									>
										<FormControl
											type="checkbox"
											:modelValue="selectedPartners.includes(option.value)"
											@update:modelValue="(value) => togglePartner(option.value, value)"
										/>
										<div class="truncate text-base text-ink-gray-8">
											{{ option.label }}
										</div>
									</label>
									<div
										v-if="!partnersResource.loading && !filteredPartners.length"
										class="px-3 py-5 text-sm text-ink-gray-5"
									>
										{{ __('No matches') }}
									</div>
								</div>
							</div>
						</template>
					</Popover>

					<Button
						variant="outline"
						icon-left="filter"
						:label="__('Date range: {0}', [monthRangeLabel])"
						@click="openDateDialog"
					/>

					<Button
						variant="solid"
						icon-left="download"
						:label="__('Export')"
						@click="openExportDialog"
					/>
				</div>
			</div>

			<div v-if="filtersLoading" class="mt-2 text-sm text-ink-gray-5">
				{{ __('Loading filters...') }}
			</div>
		</div>

		<div class="min-h-0 flex-1 overflow-auto px-5 py-4">
			<div v-if="analytics.loading" class="space-y-3">
				<div class="h-10 animate-pulse rounded bg-surface-gray-2" />
				<div
					v-for="index in 4"
					:key="index"
					class="h-16 animate-pulse rounded bg-surface-gray-2"
				/>
			</div>

			<div v-else class="space-y-3">
				<div class="overflow-x-auto rounded-lg border">
				<table class="min-w-full border-collapse text-left text-sm">
					<thead class="bg-surface-gray-2">
						<tr>
							<th
								class="sticky left-0 z-10 min-w-72 border-b border-r bg-surface-gray-2 px-4 py-3 text-sm font-semibold text-ink-gray-8"
							>
								{{ __('Metric') }}
							</th>
							<th
								v-for="month in displayMonths"
								:key="month"
								class="min-w-32 border-b px-4 py-3 text-sm font-semibold text-ink-gray-8"
							>
								{{ month }}
							</th>
						</tr>
					</thead>
					<tbody>
						<tr
							v-for="row in displayAnalyticsRows"
							:key="row.metric"
							class="odd:bg-surface-white even:bg-surface-gray-1"
						>
							<td class="sticky left-0 border-b border-r bg-inherit px-4 py-3 font-medium text-ink-gray-8">
								{{ row.metric }}
							</td>
							<td
								v-for="month in displayMonths"
								:key="`${row.metric}-${month}`"
								class="border-b px-4 py-3 text-ink-gray-7"
							>
								{{ formatMetricValue(row[month]) }}
							</td>
						</tr>
					</tbody>
				</table>
			</div>

				<div
					v-if="showNoDataMessage"
					class="rounded-lg border border-dashed px-4 py-3 text-sm text-ink-gray-5"
				>
					{{ __('No analysis data available for the selected filters.') }}
				</div>
			</div>
		</div>

		<Dialog v-model="showDateDialog" :options="{ title: __('Select date range') }">
			<template #body-content>
				<div class="flex flex-col gap-4">
					<div class="flex gap-2">
						<Button
							:variant="dateMode === 'quick' ? 'solid' : 'outline'"
							:label="__('Quick range')"
							@click="dateMode = 'quick'"
						/>
						<Button
							:variant="dateMode === 'custom' ? 'solid' : 'outline'"
							:label="__('Custom range')"
							@click="dateMode = 'custom'"
						/>
					</div>

					<div v-if="dateMode === 'quick'" class="flex flex-wrap gap-2">
						<Button
							v-for="value in [3, 6, 9, 12]"
							:key="value"
							:variant="draftMonthFilter.quickMonths === value ? 'solid' : 'outline'"
							:label="__('Last {0} months', [value])"
							@click="handleQuickRangeSelect(value)"
						/>
					</div>

					<div v-else class="grid gap-3 sm:grid-cols-2">
						<FormControl
							v-model="draftMonthFilter.startMonth"
							type="select"
							:label="__('Start month')"
							:options="monthOptions"
						/>
						<FormControl
							v-model="draftMonthFilter.startYear"
							type="select"
							:label="__('Start year')"
							:options="yearOptions"
						/>
						<FormControl
							v-model="draftMonthFilter.endMonth"
							type="select"
							:label="__('End month')"
							:options="monthOptions"
						/>
						<FormControl
							v-model="draftMonthFilter.endYear"
							type="select"
							:label="__('End year')"
							:options="yearOptions"
						/>
					</div>

					<div v-if="invalidCustomRange" class="text-sm text-red-500">
						{{ __('Start month must be before or equal to end month.') }}
					</div>
				</div>
			</template>

			<template #actions>
				<div class="flex items-center justify-end gap-2">
					<Button variant="ghost" :label="__('Clear date')" @click="clearDateFilter" />
					<Button variant="outline" :label="__('Cancel')" @click="showDateDialog = false" />
					<Button
						variant="solid"
						:label="__('Apply')"
						:disabled="invalidCustomRange"
						@click="applyDateFilter"
					/>
				</div>
			</template>
		</Dialog>

		<Dialog v-model="showExportDialog" :options="{ title: exportDialogTitle }">
			<template #body-content>
				<div class="grid gap-3 sm:grid-cols-2">
					<FormControl
						v-model="exportRange.startMonth"
						type="select"
						:label="__('Start month')"
						:options="monthOptions"
					/>
					<FormControl
						v-model="exportRange.startYear"
						type="select"
						:label="__('Start year')"
						:options="exportYearOptions"
					/>
					<FormControl
						v-model="exportRange.endMonth"
						type="select"
						:label="__('End month')"
						:options="monthOptions"
					/>
					<FormControl
						v-model="exportRange.endYear"
						type="select"
						:label="__('End year')"
						:options="exportYearOptions"
					/>
				</div>

				<div v-if="invalidExportRange" class="mt-3 text-sm text-red-500">
					{{ __('Start month must be before or equal to end month.') }}
				</div>
			</template>

			<template #actions>
				<div class="flex items-center justify-end gap-2">
					<Button variant="outline" :label="__('Cancel')" @click="showExportDialog = false" />
					<Button
						variant="solid"
						:label="__('Export')"
						:disabled="invalidExportRange"
						@click="exportAnalytics"
					/>
				</div>
			</template>
		</Dialog>
	</div>
</template>

<script setup>
import { Button, Dialog, FormControl, Popover, createResource } from 'frappe-ui'
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
	metricGroup: {
		type: String,
		required: true,
	},
	filters: {
		type: Object,
		default: () => ({}),
	},
})

const emit = defineEmits(['update:filters'])

const queries = reactive({
	regions: '',
	countries: '',
	partners: '',
})

const showDateDialog = ref(false)
const showExportDialog = ref(false)
const dateMode = ref('quick')

const monthOptions = [
	'January',
	'February',
	'March',
	'April',
	'May',
	'June',
	'July',
	'August',
	'September',
	'October',
	'November',
	'December',
].map((label, value) => ({ label: __(label), value }))

const currentDate = new Date()
const currentYear = currentDate.getFullYear()
const currentMonth = currentDate.getMonth()
const monthAbbreviations = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
const defaultMetricLabels = {
	group: [
		__('Number of Groups on Insights'),
		__('Number of Registered Groups'),
	],
	backup: [
		__('% Groups 2+ Meetings Not Backed Up'),
		__('% Groups Never Backed Up'),
	],
}
const yearOptions = Array.from({ length: 8 }, (_, index) => currentYear - 3 + index).map((value) => ({
	label: `${value}`,
	value,
}))

const normalizedFilters = computed(() => normalizeFilters(props.filters))
const selectedRegions = computed({
	get: () => normalizedFilters.value.regions,
	set: (value) => updateFilters({ regions: value }),
})
const selectedCountries = computed({
	get: () => normalizedFilters.value.countries,
	set: (value) => updateFilters({ countries: value }),
})
const selectedPartners = computed({
	get: () => normalizedFilters.value.partners,
	set: (value) => updateFilters({ partners: value }),
})
const monthFilter = computed({
	get: () => normalizedFilters.value.monthFilter,
	set: (value) => updateFilters({ monthFilter: value }),
})

const draftMonthFilter = reactive(createDefaultDraftMonthFilter())
const exportRange = reactive(createDefaultExportRange())

const regionsResource = createResource({
	url: 'crm.api.partner_report.get_partner_report_regions',
	auto: true,
	initialData: [],
})

const countriesResource = createResource({
	url: 'crm.api.partner_report.get_partner_report_countries',
	auto: true,
	initialData: [],
	makeParams() {
		return {
			regions: selectedRegions.value,
		}
	},
})

const partnersResource = createResource({
	url: 'crm.api.partner_report.get_partner_report_partners',
	auto: true,
	initialData: [],
	makeParams() {
		return {
			regions: selectedRegions.value,
			countries: selectedCountries.value,
		}
	},
})

const analytics = createResource({
	url: 'crm.api.partner_report.get_partner_report_analytics',
	auto: true,
	initialData: { months: [], data: [], report_count: 0 },
	makeParams() {
		const window = resolveMonthWindow(monthFilter.value)

		return {
			metric_group: props.metricGroup,
			all_time: window ? 0 : 1,
			...(window
				? {
						year: window.startYear,
						month: window.startMonth,
						month_count: window.monthCount,
					}
				: {}),
			regions: selectedRegions.value,
			countries: selectedCountries.value,
			partners: selectedPartners.value,
		}
	},
})

watch(selectedRegions, () => {
	countriesResource.reload()
	partnersResource.reload()
	analytics.reload()
}, { deep: true })

watch(selectedCountries, () => {
	partnersResource.reload()
	analytics.reload()
}, { deep: true })

watch([selectedPartners, monthFilter, () => props.metricGroup], () => {
	analytics.reload()
}, { deep: true })

const regionOptions = computed(() => regionsResource.data || [])
const countryOptions = computed(() => countriesResource.data || [])
const partnerOptions = computed(() => {
	return (partnersResource.data || []).map((partner) => ({
		label: formatPartnerLabel(partner),
		value: partner.name,
	}))
})

const filteredRegions = computed(() => filterOptions(regionOptions.value, queries.regions))
const filteredCountries = computed(() => filterOptions(countryOptions.value, queries.countries))
const filteredPartners = computed(() => filterOptions(partnerOptions.value, queries.partners))

const months = computed(() => analytics.data?.months || [])
const analyticsRows = computed(() => analytics.data?.data || [])
const analyticsReportCount = computed(() => Number(analytics.data?.report_count || 0))
const fallbackMonths = computed(() => buildFallbackMonths())
const displayMonths = computed(() => months.value.length ? months.value : fallbackMonths.value)
const displayAnalyticsRows = computed(() => {
	if (analyticsRows.value.length) {
		return analyticsRows.value
	}

	return (defaultMetricLabels[props.metricGroup] || []).map((metric) => {
		const row = { metric }
		for (const month of displayMonths.value) {
			row[month] = 0
		}
		return row
	})
})
const showNoDataMessage = computed(() => analyticsReportCount.value === 0)

const filtersLoading = computed(() => {
	return Boolean(regionsResource.loading || countriesResource.loading || partnersResource.loading)
})

const monthRangeLabel = computed(() => {
	if (!monthFilter.value) {
		return __('All time')
	}

	if (monthFilter.value.mode === 'custom') {
		return __('{0} {1} - {2} {3}', [
			monthOptions[monthFilter.value.startMonth]?.label,
			monthFilter.value.startYear,
			monthOptions[monthFilter.value.endMonth]?.label,
			monthFilter.value.endYear,
		])
	}

	return __('Last {0} months', [monthFilter.value.quickMonths || 3])
})

const invalidCustomRange = computed(() => {
	if (dateMode.value !== 'custom') {
		return false
	}

	const startValue = draftMonthFilter.startYear * 12 + draftMonthFilter.startMonth
	const endValue = draftMonthFilter.endYear * 12 + draftMonthFilter.endMonth
	return startValue > endValue
})

const invalidExportRange = computed(() => {
	const startValue = Number(exportRange.startYear) * 12 + Number(exportRange.startMonth)
	const endValue = Number(exportRange.endYear) * 12 + Number(exportRange.endMonth)
	return startValue > endValue
})

const exportYearOptions = computed(() => {
	const years = [currentYear]
	for (const value of [exportRange.startYear, exportRange.endYear]) {
		if (!years.includes(Number(value))) {
			years.push(Number(value))
		}
	}

	const minYear = Math.min(...years) - 2
	const maxYear = Math.max(...years) + 1
	return Array.from({ length: maxYear - minYear + 1 }, (_, index) => ({
		label: `${minYear + index}`,
		value: minYear + index,
	}))
})

const exportDialogTitle = computed(() => {
	return props.metricGroup === 'group'
		? __('Export Group Number Analysis')
		: __('Export Back Up Rate Analysis')
})

function createDefaultDraftMonthFilter() {
	return {
		mode: 'quick',
		quickMonths: 3,
		startYear: currentYear,
		startMonth: currentMonth,
		endYear: currentYear,
		endMonth: currentMonth,
	}
}

function createDefaultExportRange() {
	const defaultWindow = resolveMonthWindow(monthFilter.value) || resolveMonthWindow({ mode: 'quick', quickMonths: 6 })
	return {
		startYear: defaultWindow.startYear,
		startMonth: defaultWindow.startMonth,
		endYear: defaultWindow.endYear,
		endMonth: defaultWindow.endMonth,
	}
}

function buildFallbackMonths() {
	const window = resolveMonthWindow(monthFilter.value) || resolveMonthWindow({ mode: 'quick', quickMonths: 12 })
	if (!window) {
		return []
	}

	const labels = []
	const cursor = new Date(window.startYear, window.startMonth, 1)

	for (let index = 0; index < window.monthCount; index++) {
		labels.push(formatMonthLabel(cursor.getFullYear(), cursor.getMonth()))
		cursor.setMonth(cursor.getMonth() + 1)
	}

	return labels
}

function formatMonthLabel(year, monthIndex) {
	return `${monthAbbreviations[monthIndex]} ${year}`
}

function resolveMonthWindow(filter) {
	if (!filter) {
		return null
	}

	if (filter.mode === 'custom') {
		const startYear = Number(filter.startYear)
		const startMonth = Number(filter.startMonth)
		const endYear = Number(filter.endYear)
		const endMonth = Number(filter.endMonth)
		const monthCount = Math.max(0, (endYear - startYear) * 12 + (endMonth - startMonth)) + 1

		return {
			startYear,
			startMonth,
			endYear,
			endMonth,
			monthCount,
		}
	}

	const endYear = currentYear
	const endMonth = currentMonth
	const monthCount = Math.max(1, Number(filter.quickMonths) || 3)
	const startDate = new Date(endYear, endMonth, 1)
	startDate.setMonth(startDate.getMonth() - (monthCount - 1))

	return {
		startYear: startDate.getFullYear(),
		startMonth: startDate.getMonth(),
		endYear,
		endMonth,
		monthCount,
	}
}

function filterOptions(options, query) {
	const normalizedQuery = query.trim().toLowerCase()
	if (!normalizedQuery) {
		return options
	}

	return options.filter((option) => {
		const label = String(option.label || '').toLowerCase()
		const value = String(option.value || '').toLowerCase()
		return label.includes(normalizedQuery) || value.includes(normalizedQuery)
	})
}

function formatPartnerLabel(partner) {
	return `${partner.organization_name}${partner.territory ? ` (${partner.territory})` : ''}`
}

function getFilterButtonLabel(baseLabel, count) {
	return count ? `${baseLabel} (${count})` : baseLabel
}

function toggleRegion(value, checked) {
	updateFilters({
		regions: toggleSelection(selectedRegions.value, value, checked),
		countries: [],
		partners: [],
	})
	queries.countries = ''
	queries.partners = ''
}

function toggleCountry(value, checked) {
	updateFilters({
		countries: toggleSelection(selectedCountries.value, value, checked),
		partners: [],
	})
	queries.partners = ''
}

function togglePartner(value, checked) {
	selectedPartners.value = toggleSelection(selectedPartners.value, value, checked)
}

function toggleSelection(values, value, checked) {
	const next = new Set(values)
	if (checked) {
		next.add(value)
	} else {
		next.delete(value)
	}
	return Array.from(next)
}

function clearRegions() {
	updateFilters({
		regions: [],
		countries: [],
		partners: [],
	})
	queries.regions = ''
	queries.countries = ''
	queries.partners = ''
}

function clearCountries() {
	updateFilters({
		countries: [],
		partners: [],
	})
	queries.countries = ''
	queries.partners = ''
}

function clearPartners() {
	selectedPartners.value = []
	queries.partners = ''
}

function openDateDialog() {
	const nextFilter = monthFilter.value || createDefaultDraftMonthFilter()
	draftMonthFilter.mode = nextFilter.mode
	draftMonthFilter.quickMonths = nextFilter.quickMonths
	draftMonthFilter.startYear = nextFilter.startYear
	draftMonthFilter.startMonth = nextFilter.startMonth
	draftMonthFilter.endYear = nextFilter.endYear
	draftMonthFilter.endMonth = nextFilter.endMonth
	dateMode.value = nextFilter.mode === 'custom' ? 'custom' : 'quick'
	showDateDialog.value = true
}

function handleQuickRangeSelect(value) {
	draftMonthFilter.mode = 'quick'
	draftMonthFilter.quickMonths = value
}

function applyDateFilter() {
	if (invalidCustomRange.value) {
		return
	}

	monthFilter.value = {
		mode: dateMode.value,
		quickMonths: draftMonthFilter.quickMonths,
		startYear: Number(draftMonthFilter.startYear),
		startMonth: Number(draftMonthFilter.startMonth),
		endYear: Number(draftMonthFilter.endYear),
		endMonth: Number(draftMonthFilter.endMonth),
	}
	showDateDialog.value = false
}

function clearDateFilter() {
	monthFilter.value = null
	showDateDialog.value = false
}

function openExportDialog() {
	const range = createDefaultExportRange()
	exportRange.startYear = range.startYear
	exportRange.startMonth = range.startMonth
	exportRange.endYear = range.endYear
	exportRange.endMonth = range.endMonth
	showExportDialog.value = true
}

function formatMetricValue(value) {
	const numericValue = Number(value || 0)

	if (props.metricGroup === 'backup') {
		return `${numericValue.toFixed(2)}%`
	}

	return Number.isInteger(numericValue) ? `${numericValue}` : numericValue.toFixed(2)
}

function exportAnalytics() {
	if (invalidExportRange.value) {
		return
	}

	const monthCount =
		Math.max(
			0,
			(Number(exportRange.endYear) - Number(exportRange.startYear)) * 12 +
				(Number(exportRange.endMonth) - Number(exportRange.startMonth)),
		) + 1

	const params = new URLSearchParams({
		metric_group: props.metricGroup,
		year: String(exportRange.startYear),
		month: String(exportRange.startMonth),
		month_count: String(monthCount),
	})

	if (selectedRegions.value.length) {
		params.set('regions', selectedRegions.value.join(','))
	}
	if (selectedCountries.value.length) {
		params.set('countries', selectedCountries.value.join(','))
	}
	if (selectedPartners.value.length) {
		params.set('partners', selectedPartners.value.join(','))
	}

	const link = document.createElement('a')
	link.href = `/api/method/crm.api.partner_report.export_partner_report_analytics?${params.toString()}`
	link.click()
	showExportDialog.value = false
}

function normalizeFilters(filters) {
	const value = filters && typeof filters === 'object' ? filters : {}
	return {
		regions: normalizeStringArray(value.regions),
		countries: normalizeStringArray(value.countries),
		partners: normalizeStringArray(value.partners),
		monthFilter: normalizeMonthFilter(value.monthFilter),
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

function updateFilters(patch) {
	const nextFilters = {
		...normalizedFilters.value,
		...patch,
	}

	emit('update:filters', {
		regions: normalizeStringArray(nextFilters.regions),
		countries: normalizeStringArray(nextFilters.countries),
		partners: normalizeStringArray(nextFilters.partners),
		monthFilter: normalizeMonthFilter(nextFilters.monthFilter),
	})
}
</script>
