<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <div class="flex items-center gap-3 border-b px-5 py-3">
      <Button variant="ghost" icon="arrow-left" @click="router.push({ name: 'PartnerReports' })" />
      <h1 class="text-xl font-semibold text-ink-gray-9">
        {{ isNew ? __('New Partner Report') : __('Partner Report') }}
      </h1>
      <Badge v-if="!isNew" :label="reportId" variant="subtle" />
    </div>

    <!-- Step indicator -->
    <div class="flex items-center gap-0 border-b bg-surface-gray-1 px-6 py-3">
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
    <div v-if="loading" class="flex flex-1 items-center justify-center">
      <LoadingIndicator class="h-6 w-6 text-ink-gray-4" />
    </div>

    <div v-else class="flex flex-1 flex-col overflow-hidden">
      <!-- Step content -->
      <div class="flex-1 overflow-y-auto px-6 py-6">

        <!-- ── STEP 1: Partner ── -->
        <div v-if="currentStep === 0" class="mx-auto max-w-2xl space-y-6">
          <div class="grid grid-cols-2 gap-4">
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
              <select
                v-model="form.partner"
                class="form-select w-full"
                :class="{ 'border-red-400': errors.partner }"
              >
                <option value="">{{ __('Select partner…') }}</option>
                <option
                  v-for="org in partners"
                  :key="org.name"
                  :value="org.name"
                >
                  {{ org.organization_name }}
                  <template v-if="org.territory"> ({{ org.territory }})</template>
                </option>
              </select>
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
            <textarea
              v-model="form.achievements"
              rows="4"
              class="form-textarea w-full"
              :class="{ 'border-red-400': errors.achievements }"
              :placeholder="__('Indicate key achievements this month…')"
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
                class="flex cursor-pointer items-center gap-2 rounded p-2 hover:bg-surface-gray-1"
              >
                <input
                  type="radio"
                  :value="opt"
                  v-model="form.partner_satisfaction"
                  class="form-checkbox"
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
            <textarea
              v-model="form.partner_satisfaction_details"
              rows="4"
              class="form-textarea w-full"
              :class="{ 'border-red-400': errors.partner_satisfaction_details }"
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
            <textarea
              v-model="form.insights_issues"
              rows="4"
              class="form-textarea w-full"
              :class="{ 'border-red-400': errors.insights_issues }"
            />
            <p v-if="errors.insights_issues" class="mt-1 text-xs text-red-500">
              {{ errors.insights_issues }}
            </p>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-ink-gray-7">
              {{ __('Next Steps and Upcoming Plans with this Partner') }} <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="form.next_steps_with_partner"
              rows="4"
              class="form-textarea w-full"
              :class="{ 'border-red-400': errors.next_steps_with_partner }"
            />
            <p v-if="errors.next_steps_with_partner" class="mt-1 text-xs text-red-500">
              {{ errors.next_steps_with_partner }}
            </p>
          </div>
        </div>

        <!-- ── STEP 2: Groups ── -->
        <div v-if="currentStep === 1" class="mx-auto max-w-2xl space-y-6">
          <div>
            <label class="mb-2 block text-sm font-medium text-ink-gray-7">
              {{ __('How satisfied are the groups with DreamSave?') }}
              <span class="text-red-500">*</span>
            </label>
            <div class="space-y-2">
              <label
                v-for="opt in groupSatisfactionOptions"
                :key="opt"
                class="flex cursor-pointer items-center gap-2 rounded p-2 hover:bg-surface-gray-1"
              >
                <input
                  type="radio"
                  :value="opt"
                  v-model="form.group_satisfaction"
                  class="form-checkbox"
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
            <textarea
              v-model="form.group_satisfaction_details"
              rows="4"
              class="form-textarea w-full"
              :class="{ 'border-red-400': errors.group_satisfaction_details }"
            />
            <p v-if="errors.group_satisfaction_details" class="mt-1 text-xs text-red-500">
              {{ errors.group_satisfaction_details }}
            </p>
          </div>

          <div class="grid grid-cols-2 gap-4">
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
            <textarea
              v-model="form.group_number_difference_reason"
              rows="4"
              class="form-textarea w-full"
              :class="{ 'border-red-400': errors.group_number_difference_reason }"
            />
            <p v-if="errors.group_number_difference_reason" class="mt-1 text-xs text-red-500">
              {{ errors.group_number_difference_reason }}
            </p>
          </div>

          <div class="grid grid-cols-2 gap-4">
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
              <textarea
                v-model="form.reasons_for_groups_not_backing_up"
                rows="4"
                class="form-textarea w-full"
                :class="{ 'border-red-400': errors.reasons_for_groups_not_backing_up }"
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
              <textarea
                v-model="form.support_plan_for_backups"
                rows="4"
                class="form-textarea w-full"
                :class="{ 'border-red-400': errors.support_plan_for_backups }"
              />
              <p v-if="errors.support_plan_for_backups" class="mt-1 text-xs text-red-500">
                {{ errors.support_plan_for_backups }}
              </p>
            </div>
          </template>
        </div>

        <!-- ── STEP 3: General ── -->
        <div v-if="currentStep === 2" class="mx-auto max-w-2xl space-y-6">
          <div>
            <label class="mb-1 block text-sm font-medium text-ink-gray-7">
              {{ __('Insights Data Concerns') }} <span class="text-red-500">*</span>
            </label>
            <p class="mb-1 text-xs text-ink-gray-5">
              {{ __('What data concerns do you have and what steps have you taken to troubleshoot or fix the data issues?') }}
            </p>
            <textarea
              v-model="form.insights_data_concerns"
              rows="6"
              class="form-textarea w-full"
              :class="{ 'border-red-400': errors.insights_data_concerns }"
              :placeholder="__('Describe any data concerns and your troubleshooting steps…')"
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

      <!-- Navigation footer -->
      <div class="flex items-center justify-between border-t px-6 py-4">
        <Button
          v-if="currentStep > 0"
          variant="subtle"
          :label="__('Back')"
          icon-left="arrow-left"
          @click="currentStep--"
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, Button, Badge, LoadingIndicator, toast } from 'frappe-ui'

const props = defineProps({
  reportId: {
    type: String,
    required: true,
  },
})

const router = useRouter()
const isNew = computed(() => props.reportId === 'new')

const currentStep = ref(0)
const loading = ref(false)
const saving = ref(false)
const saveError = ref('')

const steps = [
  { key: 'partner', label: 'Partner' },
  { key: 'groups', label: 'Groups' },
  { key: 'general', label: 'General' },
]

const form = ref({
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
})

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
const partners = computed(() => partnersResource.data || [])
const partnerName = computed(() => {
  const found = partners.value.find((p) => p.name === form.value.partner)
  return found ? found.organization_name : form.value.partner
})

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
onMounted(async () => {
  if (!isNew.value) {
    loading.value = true
    try {
      const resource = createResource({
        url: 'crm.api.partner_report.get_partner_report',
        params: { name: props.reportId },
        auto: true,
      })
      await resource.promise
      if (resource.data) {
        Object.assign(form.value, resource.data)
      }
    } catch (e) {
      toast({ title: 'Error loading report', icon: 'x', iconClasses: 'text-red-500' })
    } finally {
      loading.value = false
    }
  }
})

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
    if (val === null || val === undefined || val === '') {
      newErrors[field] = 'This field is required'
    }
  }

  // Conditional required fields for step 1
  if (step === 1) {
    if (groupNumbersDiffer.value && !form.value.group_number_difference_reason?.trim()) {
      newErrors.group_number_difference_reason = 'Please explain the difference in group numbers'
    }
    if (hasBackupIssues.value) {
      if (!form.value.reasons_for_groups_not_backing_up?.trim()) {
        newErrors.reasons_for_groups_not_backing_up = 'This field is required'
      }
      if (!form.value.support_plan_for_backups?.trim()) {
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
      const resource = createResource({
        url: 'crm.api.partner_report.create_partner_report',
        params: { data: payload },
      })
      await resource.submit()
      const newName = resource.data
      toast({ title: 'Report submitted successfully', icon: 'check', iconClasses: 'text-green-500' })
      router.push({ name: 'PartnerReport', params: { reportId: newName } })
    } else {
      const resource = createResource({
        url: 'crm.api.partner_report.update_partner_report',
        params: { name: props.reportId, data: payload },
      })
      await resource.submit()
      toast({ title: 'Report saved', icon: 'check', iconClasses: 'text-green-500' })
    }
  } catch (e) {
    saveError.value = e.message || 'An error occurred while saving'
  } finally {
    saving.value = false
  }
}
</script>
