<template>
  <div class="flex h-full min-h-0 flex-col">
    <!-- Header -->
    <div v-if="!inDialog" class="flex items-center gap-3 border-b px-5 py-3">
      <Button variant="ghost" icon="arrow-left" @click="router.push({ name: 'Partner Reports' })" />
      <h1 class="text-xl font-semibold text-ink-gray-9">
        {{ isNew ? __('New Partner Report') : showForm ? __('Edit Partner Report') : __('Partner Report') }}
      </h1>
      <Badge v-if="!isNew" :label="reportId" variant="subtle" />
    </div>

    <!-- Step indicator -->
    <div v-if="showForm" class="flex items-center gap-0 border-b bg-surface-gray-1 px-6 py-3">
      <template v-for="(step, idx) in steps" :key="step.key">
        <div
          class="flex items-center gap-2 cursor-pointer"
          @click="goToStep(idx)"
        >
          <div
            class="flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold"
            :class="
              idx < currentStep
                ? 'bg-surface-green-3 text-neutral-white'
                : idx === currentStep
                ? 'bg-ink-gray-9 text-neutral-white'
                : 'bg-surface-gray-3 text-ink-gray-5'
            "
          >
            <span v-if="idx < currentStep">✓</span>
            <span v-else>{{ idx + 1 }}</span>
          </div>
          <span
            class="text-sm font-medium"
            :class="idx === currentStep ? 'text-ink-gray-9' : 'text-ink-gray-5'"
          >
            {{ __(step.label) }}
          </span>
        </div>
        <div
          v-if="idx < steps.length - 1"
          class="mx-4 h-px flex-1 bg-outline-gray-1"
          style="min-width: 2rem"
        />
      </template>
    </div>

    <!-- Loading existing report -->
    <div v-if="loading" class="flex min-h-0 flex-1 items-center justify-center">
      <LoadingIndicator class="h-6 w-6 text-ink-gray-4" />
    </div>

    <div v-else class="flex min-h-0 flex-1 flex-col overflow-hidden">
      <!-- Step content -->
      <div v-if="showForm" class="min-h-0 flex-1 overflow-y-auto px-6 py-6">

        <!-- ── STEP 1: Partner ── -->
        <div v-if="currentStep === 0" class="mx-auto w-full max-w-5xl space-y-6">
          <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium text-ink-gray-7">
                {{ __('Reporting Month') }} <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.reporting_month"
                type="month"
                class="form-input w-full"
                :class="{ 'border-red-400': errors.reporting_month }"
              />
              <p v-if="errors.reporting_month" class="mt-1 text-xs text-red-500">
                {{ errors.reporting_month }}
              </p>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-ink-gray-7">
                {{ __('Partner') }} <span class="text-red-500">*</span>
              </label>
              <div
                class="rounded-md"
                :class="errors.partner ? 'ring-1 ring-red-400' : ''"
              >
                <Autocomplete
                  v-model="form.partner"
                  :options="partnerOptions"
                  :placeholder="__('Select partner…')"
                  variant="outline"
                  size="lg"
                  :disabled="lockPartner"
                />
              </div>
              <p v-if="errors.partner" class="mt-1 text-xs text-red-500">
                {{ errors.partner }}
              </p>
            </div>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-ink-gray-7">
              {{ __('Key Achievements') }} <span class="text-red-500">*</span>
            </label>
            <p class="mb-1 text-xs text-ink-gray-5">
              {{ __('Key achievements with the partner\'s pilot/project(s) this month — e.g. groups trained, staff who installed the app, etc.') }}
            </p>
            <TextEditor
              variant="outline"
              :editor-class="getEditorClass('achievements')"
              :bubbleMenu="true"
              :content="form.achievements"
              :placeholder="__('Indicate key achievements this month…')"
              @change="(val) => (form.achievements = val)"
            />
            <p v-if="errors.achievements" class="mt-1 text-xs text-red-500">
              {{ errors.achievements }}
            </p>
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-ink-gray-7">
              {{ __('How satisfied is this Partner Organization with DreamSave?') }}
              <span class="text-red-500">*</span>
            </label>
            <div class="space-y-2">
              <label
                v-for="opt in partnerSatisfactionOptions"
                :key="opt"
                class="flex cursor-pointer items-start gap-3 rounded-lg border px-3 py-2 transition-colors"
                :class="
                  form.partner_satisfaction === opt
                    ? 'border-ink-gray-9 bg-surface-gray-2'
                    : 'border-outline-gray-2 bg-surface-white hover:bg-surface-gray-1'
                "
              >
                <input
                  v-model="form.partner_satisfaction"
                  type="radio"
                  :value="opt"
                  class="mt-0.5 h-4 w-4 shrink-0 border-outline-gray-3 text-ink-gray-9 focus:ring-2 focus:ring-outline-gray-3"
                />
                <span class="text-sm text-ink-gray-8">{{ opt }}</span>
              </label>
            </div>
            <p v-if="errors.partner_satisfaction" class="mt-1 text-xs text-red-500">
              {{ errors.partner_satisfaction }}
            </p>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-ink-gray-7">
              {{ __('Partner Satisfaction Details') }} <span class="text-red-500">*</span>
            </label>
            <p class="mb-1 text-xs text-ink-gray-5">
              {{ __('E.g. are they excited about new areas? Did a glitch make them nervous? What would make us lose a partner?') }}
            </p>
            <TextEditor
              variant="outline"
              :editor-class="getEditorClass('partner_satisfaction_details')"
              :bubbleMenu="true"
              :content="form.partner_satisfaction_details"
              @change="(val) => (form.partner_satisfaction_details = val)"
            />
            <p v-if="errors.partner_satisfaction_details" class="mt-1 text-xs text-red-500">
              {{ errors.partner_satisfaction_details }}
            </p>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-ink-gray-7">
              {{ __('Insights Issues') }} <span class="text-red-500">*</span>
            </label>
            <p class="mb-1 text-xs text-ink-gray-5">
              {{ __('Any major complaints or issues experienced by the partner with Insights?') }}
            </p>
            <TextEditor
              variant="outline"
              :editor-class="getEditorClass('insights_issues')"
              :bubbleMenu="true"
              :content="form.insights_issues"
              @change="(val) => (form.insights_issues = val)"
            />
            <p v-if="errors.insights_issues" class="mt-1 text-xs text-red-500">
              {{ errors.insights_issues }}
            </p>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-ink-gray-7">
              {{ __('Next Steps and Upcoming Plans with this Partner') }} <span class="text-red-500">*</span>
            </label>
            <TextEditor
              variant="outline"
              :editor-class="getEditorClass('next_steps_with_partner')"
              :bubbleMenu="true"
              :content="form.next_steps_with_partner"
              @change="(val) => (form.next_steps_with_partner = val)"
            />
            <p v-if="errors.next_steps_with_partner" class="mt-1 text-xs text-red-500">
              {{ errors.next_steps_with_partner }}
            </p>
          </div>
        </div>

        <!-- ── STEP 2: Groups ── -->
        <div v-if="currentStep === 1" class="mx-auto w-full max-w-5xl space-y-6">
          <div>
            <label class="mb-2 block text-sm font-medium text-ink-gray-7">
              {{ __('How satisfied are the groups with DreamSave?') }}
              <span class="text-red-500">*</span>
            </label>
            <div class="space-y-2">
              <label
                v-for="opt in groupSatisfactionOptions"
                :key="opt"
                class="flex cursor-pointer items-start gap-3 rounded-lg border px-3 py-2 transition-colors"
                :class="
                  form.group_satisfaction === opt
                    ? 'border-ink-gray-9 bg-surface-gray-2'
                    : 'border-outline-gray-2 bg-surface-white hover:bg-surface-gray-1'
                "
              >
                <input
                  v-model="form.group_satisfaction"
                  type="radio"
                  :value="opt"
                  class="mt-0.5 h-4 w-4 shrink-0 border-outline-gray-3 text-ink-gray-9 focus:ring-2 focus:ring-outline-gray-3"
                />
                <span class="text-sm text-ink-gray-8">{{ opt }}</span>
              </label>
            </div>
            <p v-if="errors.group_satisfaction" class="mt-1 text-xs text-red-500">
              {{ errors.group_satisfaction }}
            </p>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-ink-gray-7">
              {{ __('Group Satisfaction Details') }} <span class="text-red-500">*</span>
            </label>
            <p class="mb-1 text-xs text-ink-gray-5">
              {{ __('E.g. what are the groups loving about the app? What problems are they having?') }}
            </p>
            <TextEditor
              variant="outline"
              :editor-class="getEditorClass('group_satisfaction_details')"
              :bubbleMenu="true"
              :content="form.group_satisfaction_details"
              @change="(val) => (form.group_satisfaction_details = val)"
            />
            <p v-if="errors.group_satisfaction_details" class="mt-1 text-xs text-red-500">
              {{ errors.group_satisfaction_details }}
            </p>
          </div>

          <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium text-ink-gray-7">
                {{ __('Number of Groups on Insights') }} <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="form.num_of_groups_on_insights"
                type="number"
                min="0"
                class="form-input w-full"
                :class="{ 'border-red-400': errors.num_of_groups_on_insights }"
              />
              <p v-if="errors.num_of_groups_on_insights" class="mt-1 text-xs text-red-500">
                {{ errors.num_of_groups_on_insights }}
              </p>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-ink-gray-7">
                {{ __('Number of Registered Groups (Partner Reported)') }} <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="form.num_of_registered_groups"
                type="number"
                min="0"
                class="form-input w-full"
                :class="{ 'border-red-400': errors.num_of_registered_groups }"
              />
              <p v-if="errors.num_of_registered_groups" class="mt-1 text-xs text-red-500">
                {{ errors.num_of_registered_groups }}
              </p>
            </div>
          </div>

          <!-- Conditional: group number difference -->
          <div v-if="groupNumbersDiffer">
            <label class="mb-1 block text-sm font-medium text-ink-gray-7">
              {{ __('Reason for Difference in Group Numbers') }} <span class="text-red-500">*</span>
            </label>
            <p class="mb-1 text-xs text-ink-gray-5">
              {{ __('The numbers on Insights and what the partner reported differ. Please explain and describe steps to resolve.') }}
            </p>
            <TextEditor
              variant="outline"
              :editor-class="getEditorClass('group_number_difference_reason')"
              :bubbleMenu="true"
              :content="form.group_number_difference_reason"
              @change="(val) => (form.group_number_difference_reason = val)"
            />
            <p v-if="errors.group_number_difference_reason" class="mt-1 text-xs text-red-500">
              {{ errors.group_number_difference_reason }}
            </p>
          </div>

          <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium text-ink-gray-7">
                {{ __('% Groups with 2+ Meetings Not Backed Up') }} <span class="text-red-500">*</span>
              </label>
              <p class="mb-1 text-xs text-ink-gray-5">{{ __('Found on DreamSave Insights Sidebar, bottom left') }}</p>
              <input
                v-model.number="form.percentage_of_two_plus_not_backed_up_groups"
                type="number"
                min="0"
                max="100"
                step="0.1"
                class="form-input w-full"
                :class="{ 'border-red-400': errors.percentage_of_two_plus_not_backed_up_groups }"
              />
              <p v-if="errors.percentage_of_two_plus_not_backed_up_groups" class="mt-1 text-xs text-red-500">
                {{ errors.percentage_of_two_plus_not_backed_up_groups }}
              </p>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-ink-gray-7">
                {{ __('% Groups that Have Never Backed Up Meetings') }} <span class="text-red-500">*</span>
              </label>
              <p class="mb-1 text-xs text-ink-gray-5">{{ __('Found on DreamSave Insights Sidebar, bottom left') }}</p>
              <input
                v-model.number="form.percentage_of_never_backed_up_groups"
                type="number"
                min="0"
                max="100"
                step="0.1"
                class="form-input w-full"
                :class="{ 'border-red-400': errors.percentage_of_never_backed_up_groups }"
              />
              <p v-if="errors.percentage_of_never_backed_up_groups" class="mt-1 text-xs text-red-500">
                {{ errors.percentage_of_never_backed_up_groups }}
              </p>
            </div>
          </div>

          <!-- Conditional: backup issues -->
          <template v-if="hasBackupIssues">
            <div>
              <label class="mb-1 block text-sm font-medium text-ink-gray-7">
                {{ __('Reasons for Groups Not Backing Up Meetings') }} <span class="text-red-500">*</span>
              </label>
              <TextEditor
                variant="outline"
                :editor-class="getEditorClass('reasons_for_groups_not_backing_up')"
                :bubbleMenu="true"
                :content="form.reasons_for_groups_not_backing_up"
                @change="(val) => (form.reasons_for_groups_not_backing_up = val)"
              />
              <p v-if="errors.reasons_for_groups_not_backing_up" class="mt-1 text-xs text-red-500">
                {{ errors.reasons_for_groups_not_backing_up }}
              </p>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-ink-gray-7">
                {{ __('Support Plan for Backup Issues') }} <span class="text-red-500">*</span>
              </label>
              <p class="mb-1 text-xs text-ink-gray-5">
                {{ __('What did you do this month to support groups not backing up? If nothing, what plans have you made?') }}
              </p>
              <TextEditor
                variant="outline"
                :editor-class="getEditorClass('support_plan_for_backups')"
                :bubbleMenu="true"
                :content="form.support_plan_for_backups"
                @change="(val) => (form.support_plan_for_backups = val)"
              />
              <p v-if="errors.support_plan_for_backups" class="mt-1 text-xs text-red-500">
                {{ errors.support_plan_for_backups }}
              </p>
            </div>
          </template>
        </div>

        <!-- ── STEP 3: General ── -->
        <div v-if="currentStep === 2" class="mx-auto w-full max-w-5xl space-y-6">
          <div>
            <label class="mb-1 block text-sm font-medium text-ink-gray-7">
              {{ __('Insights Data Concerns') }} <span class="text-red-500">*</span>
            </label>
            <p class="mb-1 text-xs text-ink-gray-5">
              {{ __('What data concerns do you have and what steps have you taken to troubleshoot or fix the data issues?') }}
            </p>
            <TextEditor
              variant="outline"
              :editor-class="getEditorClass('insights_data_concerns')"
              :bubbleMenu="true"
              :content="form.insights_data_concerns"
              :placeholder="__('Describe any data concerns and your troubleshooting steps…')"
              @change="(val) => (form.insights_data_concerns = val)"
            />
            <p v-if="errors.insights_data_concerns" class="mt-1 text-xs text-red-500">
              {{ errors.insights_data_concerns }}
            </p>
          </div>

          <!-- Summary preview -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-gray-1 p-4 text-sm">
            <p class="mb-2 font-medium text-ink-gray-7">{{ __('Summary') }}</p>
            <dl class="space-y-1 text-ink-gray-6">
              <div class="flex gap-2">
                <dt class="w-32 shrink-0 font-medium">{{ __('Partner') }}:</dt>
                <dd>{{ partnerName }}</dd>
              </div>
              <div class="flex gap-2">
                <dt class="w-32 shrink-0 font-medium">{{ __('Month') }}:</dt>
                <dd>{{ formatMonth(form.reporting_month) }}</dd>
              </div>
              <div class="flex gap-2">
                <dt class="w-32 shrink-0 font-medium">{{ __('Partner sat.') }}:</dt>
                <dd class="truncate">{{ form.partner_satisfaction }}</dd>
              </div>
              <div class="flex gap-2">
                <dt class="w-32 shrink-0 font-medium">{{ __('Group sat.') }}:</dt>
                <dd class="truncate">{{ form.group_satisfaction }}</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      <div v-else class="min-h-0 flex-1 overflow-y-auto bg-white">
        <PartnerReportDocument
          :report="form"
          :partner-name="partnerName"
          :partner-territory="partnerTerritory"
          :can-edit="true"
          @edit="startEditing"
        />
      </div>

      <!-- Navigation footer -->
      <div v-if="showForm" class="shrink-0 flex items-center justify-between border-t px-6 py-4">
        <Button
          v-if="currentStep > 0"
          variant="subtle"
          :label="__('Back')"
          icon-left="arrow-left"
          @click="currentStep--"
        />
        <Button
          v-else-if="!isNew"
          variant="subtle"
          :label="__('Cancel')"
          @click="cancelEditing"
        />
        <div v-else />

        <div class="flex items-center gap-3">
          <p v-if="saveError" class="text-xs text-red-500">{{ saveError }}</p>
          <Button
            v-if="currentStep < steps.length - 1"
            variant="solid"
            :label="__('Next')"
            icon-right="arrow-right"
            @click="nextStep"
          />
          <Button
            v-else
            variant="solid"
            :label="isNew ? __('Submit Report') : __('Save Changes')"
            :loading="saving"
            @click="submit"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Autocomplete from '@/components/frappe-ui/Autocomplete.vue'
import PartnerReportDocument from '@/components/PartnerReports/PartnerReportDocument.vue'
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  createResource,
  Button,
  Badge,
  LoadingIndicator,
  TextEditor,
  toast,
} from 'frappe-ui'

const props = defineProps({
  reportId: {
    type: String,
    required: true,
  },
  inDialog: {
    type: Boolean,
    default: false,
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

const emit = defineEmits(['submitted', 'saved'])

const router = useRouter()
const isNew = computed(() => props.reportId === 'new')
const isEditing = ref(isNew.value)
const showForm = computed(() => isNew.value || isEditing.value)

const currentStep = ref(0)
const loading = ref(false)
const saving = ref(false)
const saveError = ref('')
const loadedReport = ref(null)

const steps = [
  { key: 'partner', label: 'Partner' },
  { key: 'groups', label: 'Groups' },
  { key: 'general', label: 'General' },
]

const createReportResource = createResource({
  url: 'crm.api.partner_report.create_partner_report',
})

const updateReportResource = createResource({
  url: 'crm.api.partner_report.update_partner_report',
})

const defaultForm = {
  reporting_month: '',
  partner: '',
  achievements: '',
  partner_satisfaction: '',
  partner_satisfaction_details: '',
  insights_issues: '',
  next_steps_with_partner: '',
  group_satisfaction: '',
  group_satisfaction_details: '',
  num_of_groups_on_insights: null,
  num_of_registered_groups: null,
  group_number_difference_reason: '',
  percentage_of_two_plus_not_backed_up_groups: null,
  percentage_of_never_backed_up_groups: null,
  reasons_for_groups_not_backing_up: '',
  support_plan_for_backups: '',
  insights_data_concerns: '',
}

const form = ref({ ...defaultForm })

const errors = ref({})

const partnerSatisfactionOptions = [
  'This is a new partnership',
  'Disappointed, but we are working on improvements',
  'Satisfied, no complaints but no praise either',
  'Happy, often praising DreamSave/DSL',
  'The Partner is recommending DreamSave/DSL to friends and colleagues',
  'Limited engagement and prioritization of DreamSave',
]

const groupSatisfactionOptions = [
  'Groups have not started using DreamSave yet',
  'Disappointed, but we are working on improvements',
  'Satisfied, no complaints but no praise either',
  'Happy, often praising DreamSave/DSL',
  'Members are recommending DreamSave to friends and colleagues',
]

// Partners list
const partnersResource = createResource({
  url: 'crm.api.partner_report.get_partners_for_user',
  auto: true,
})

function formatPartnerLabel(partner) {
  return `${partner.organization_name}${partner.territory ? ` (${partner.territory})` : ''}`
}

const partners = computed(() => {
  const items = partnersResource.data || []
  const selectedPartner = form.value.partner || props.initialPartner
  const selectedPartnerLabel =
    selectedPartner === props.initialPartner
      ? props.initialPartnerLabel || selectedPartner
      : selectedPartner

  if (
    selectedPartner &&
    !items.some((partner) => partner.name === selectedPartner)
  ) {
    return [
      {
        name: selectedPartner,
        organization_name: selectedPartnerLabel,
        territory: '',
      },
      ...items,
    ]
  }

  return items
})

const partnerOptions = computed(() =>
  partners.value.map((partner) => ({
    label: formatPartnerLabel(partner),
    value: partner.name,
  })),
)

const partnerName = computed(() => {
  const found = partners.value.find((p) => p.name === form.value.partner)
  return found ? formatPartnerLabel(found) : form.value.partner
})

const partnerTerritory = computed(() => {
  const found = partners.value.find((p) => p.name === form.value.partner)
  return found?.territory || ''
})

const richTextFields = new Set([
  'achievements',
  'partner_satisfaction_details',
  'insights_issues',
  'next_steps_with_partner',
  'group_satisfaction_details',
  'group_number_difference_reason',
  'reasons_for_groups_not_backing_up',
  'support_plan_for_backups',
  'insights_data_concerns',
])

const richTextEditorBaseClass =
  '!prose-sm w-full max-w-full overflow-auto min-h-[240px] max-h-[28rem] rounded-md border px-3 py-2 text-ink-gray-8 transition-colors border-[--surface-gray-2] bg-surface-gray-2 placeholder-ink-gray-4 hover:border-outline-gray-modals hover:bg-surface-gray-3 hover:shadow-sm focus:bg-surface-white focus:border-outline-gray-4 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3'

function getEditorClass(field) {
  return `${richTextEditorBaseClass} ${errors.value[field] ? 'border-red-400 focus-visible:ring-red-200' : ''}`
}

function stripRichText(value) {
  return (value || '')
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function isEmptyField(field, value) {
  if (richTextFields.has(field)) {
    return !stripRichText(value)
  }

  return value === null || value === undefined || value === ''
}

// Conditional logic
const groupNumbersDiffer = computed(() => {
  const a = form.value.num_of_groups_on_insights
  const b = form.value.num_of_registered_groups
  return a !== null && b !== null && a !== b
})

const hasBackupIssues = computed(() => {
  return (
    (form.value.percentage_of_never_backed_up_groups ?? 0) > 0 ||
    (form.value.percentage_of_two_plus_not_backed_up_groups ?? 0) > 0
  )
})

// Load existing report
function normalizeReportData(report = {}) {
  return {
    ...defaultForm,
    ...report,
    reporting_month: report.reporting_month?.slice?.(0, 7) || '',
  }
}

function applyFormData(report = {}) {
  form.value = normalizeReportData(report)
}

function startEditing() {
  isEditing.value = true
  errors.value = {}
  saveError.value = ''
}

function cancelEditing() {
  if (isNew.value) return
  applyFormData(loadedReport.value || {})
  isEditing.value = false
  currentStep.value = 0
  errors.value = {}
  saveError.value = ''
}

async function loadReport() {
  currentStep.value = 0
  errors.value = {}
  saveError.value = ''

  if (isNew.value) {
    loadedReport.value = null
    applyFormData({
      partner: props.initialPartner || '',
    })
    isEditing.value = true
    return
  }

  loading.value = true
  try {
    const resource = createResource({
      url: 'crm.api.partner_report.get_partner_report',
      params: { name: props.reportId },
      auto: true,
    })
    await resource.promise
    if (resource.data) {
      loadedReport.value = normalizeReportData(resource.data)
      applyFormData(resource.data)
      isEditing.value = false
    }
  } catch {
    toast({ title: 'Error loading report', icon: 'x', iconClasses: 'text-red-500' })
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.reportId, props.initialPartner, props.initialPartnerLabel],
  () => {
    loadReport()
  },
  { immediate: true },
)

// Validation per step
const stepValidations = {
  0: [
    'reporting_month',
    'partner',
    'achievements',
    'partner_satisfaction',
    'partner_satisfaction_details',
    'insights_issues',
    'next_steps_with_partner',
  ],
  1: [
    'group_satisfaction',
    'group_satisfaction_details',
    'num_of_groups_on_insights',
    'num_of_registered_groups',
    'percentage_of_two_plus_not_backed_up_groups',
    'percentage_of_never_backed_up_groups',
  ],
  2: ['insights_data_concerns'],
}

function validateStep(step) {
  const newErrors = {}
  const fields = stepValidations[step] || []
  for (const field of fields) {
    const val = form.value[field]
    if (isEmptyField(field, val)) {
      newErrors[field] = 'This field is required'
    }
  }

  // Conditional required fields for step 1
  if (step === 1) {
    if (
      groupNumbersDiffer.value &&
      isEmptyField(
        'group_number_difference_reason',
        form.value.group_number_difference_reason,
      )
    ) {
      newErrors.group_number_difference_reason = 'Please explain the difference in group numbers'
    }
    if (hasBackupIssues.value) {
      if (
        isEmptyField(
          'reasons_for_groups_not_backing_up',
          form.value.reasons_for_groups_not_backing_up,
        )
      ) {
        newErrors.reasons_for_groups_not_backing_up = 'This field is required'
      }
      if (
        isEmptyField('support_plan_for_backups', form.value.support_plan_for_backups)
      ) {
        newErrors.support_plan_for_backups = 'This field is required'
      }
    }
  }

  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

function nextStep() {
  if (validateStep(currentStep.value)) {
    currentStep.value++
    errors.value = {}
  }
}

function goToStep(idx) {
  // Only allow going back, or to already-validated steps
  if (idx < currentStep.value) {
    currentStep.value = idx
    errors.value = {}
  }
}

function formatMonth(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + '-01')
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long' })
}

function getErrorMessage(error) {
  return (
    error?.messages?.join?.('\n') ||
    error?.error?.messages?.join?.('\n') ||
    error?.message ||
    __('An error occurred while saving')
  )
}

async function submit() {
  if (!validateStep(currentStep.value)) return

  saving.value = true
  saveError.value = ''

  // Convert reporting_month from YYYY-MM to YYYY-MM-01 for Frappe Date field
  const payload = {
    ...form.value,
    reporting_month: form.value.reporting_month
      ? form.value.reporting_month + '-01'
      : form.value.reporting_month,
  }

  try {
    if (isNew.value) {
      const newName = await createReportResource.submit({ data: payload })
      toast({ title: 'Report submitted successfully', icon: 'check', iconClasses: 'text-green-500' })
      emit('submitted', newName)
      if (!props.inDialog) {
        router.push({ name: 'PartnerReport', params: { reportId: newName } })
      }
    } else {
      await updateReportResource.submit({ name: props.reportId, data: payload })
      loadedReport.value = {
        ...(loadedReport.value || {}),
        ...form.value,
      }
      isEditing.value = false
      currentStep.value = 0
      toast({ title: 'Report saved', icon: 'check', iconClasses: 'text-green-500' })
      emit('saved', props.reportId)
    }
  } catch (e) {
    saveError.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}
</script>
