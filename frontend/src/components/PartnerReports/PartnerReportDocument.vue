<template>
  <div class="flex min-h-full w-full flex-col bg-white">
    <div class="border-b-2 border-[#FFA500] px-6 py-5 sm:px-8 sm:py-6">
      <div class="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-[#2196F3]">
            {{ __('Partner Report') }}
          </p>
          <h2 class="mt-2 text-[28px] font-semibold leading-tight text-ink-gray-9">
            {{ partnerName }} - {{ reportingMonthLabel }}
          </h2>
        </div>
        <div class="flex items-start gap-3 sm:items-center">
          <div class="text-right">
            <div class="text-2xl font-semibold leading-none text-[#2196F3]">DreamSave</div>
            <div class="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-[#FFA500]">
              {{ __('Partner Updates') }}
            </div>
          </div>
          <Button
            v-if="canEdit"
            :label="__('Edit')"
            icon-left="edit-2"
            variant="solid"
            @click="$emit('edit')"
          />
        </div>
      </div>
    </div>

    <div class="px-6 py-6 text-[14px] leading-6 text-ink-gray-8 sm:px-8 sm:py-8">
      <section class="document-section">
        <p>
          <strong>
            {{ __('Partner Report for') }} {{ partnerName }} - {{ reportingMonthLabel }}
          </strong>
        </p>
      </section>

      <section class="document-section">
        <p>
          {{ introText }}
        </p>
      </section>

      <section class="document-section space-y-1">
        <p>
          <strong>{{ __('Date Submitted:') }}</strong>
          {{ submittedAtLabel }}
        </p>
        <p v-if="report.submitted_by">
          <strong>{{ __('Submitted by:') }}</strong>
          {{ report.submitted_by }}
        </p>
        <p v-if="showModifiedAt">
          <strong>{{ __('Last updated:') }}</strong>
          {{ modifiedAtLabel }}
        </p>
      </section>

      <section
        v-for="section in sections"
        :key="section.key"
        class="document-section"
      >
        <h4 class="document-heading">{{ section.title.toUpperCase() }} {{ __('Updates').toUpperCase() }}</h4>
        <ol class="space-y-4 pl-5">
          <li
            v-for="item in section.items"
            :key="item.key"
            class="page-break"
          >
            <div>
              <strong>{{ item.question }}</strong>
              <span v-if="item.type === 'number'"> {{ item.answerText }}</span>
            </div>
            <template v-if="item.type !== 'number'">
              <div
                v-if="item.answerText"
                class="document-primary-answer"
                :class="{ 'document-primary-answer--highlight': item.highlightAnswer }"
              >
                <cite v-if="item.highlightAnswer">{{ item.answerText }}</cite>
                <template v-else>{{ item.answerText }}</template>
              </div>
              <div
                v-if="item.answerHtml"
                class="prose-f mt-2 max-w-none text-[14px] leading-6"
                v-html="item.answerHtml"
              />
              <div
                v-for="(subAnswer, idx) in item.subAnswers"
                :key="`${item.key}-sub-${idx}`"
                class="prose-f mt-2 max-w-none text-[14px] leading-6"
                v-html="subAnswer"
              />
            </template>
          </li>
        </ol>
      </section>
    </div>
  </div>
</template>

<script setup>
import { Button } from 'frappe-ui'
import { computed } from 'vue'

const props = defineProps({
  report: {
    type: Object,
    required: true,
  },
  partnerName: {
    type: String,
    default: '',
  },
  partnerTerritory: {
    type: String,
    default: '',
  },
  canEdit: {
    type: Boolean,
    default: true,
  },
})

defineEmits(['edit'])

function stripRichText(value) {
  return (value || '')
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function hasText(value) {
  return !!stripRichText(value)
}

function formatMonth(value) {
  if (!value) return __('Unknown month')
  const date = new Date(`${value}-01`)
  return date.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })
}

function formatDateTime(value) {
  if (!value) return __('Unknown')
  const date = new Date(value)
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatNumber(value, suffix = '') {
  if (value === null || value === undefined || value === '') {
    return __('Not provided')
  }
  return `${value}${suffix}`
}

function textItem(key, question, answerHtml, options = {}) {
  return {
    key,
    question,
    type: 'text',
    answerHtml,
    answerText: options.answerText || '',
    highlightAnswer: !!options.highlightAnswer,
    subAnswers: options.subAnswers || [],
  }
}

function numberItem(key, question, answerText) {
  return {
    key,
    question,
    type: 'number',
    answerText,
  }
}

const reportingMonthLabel = computed(() => formatMonth(props.report.reporting_month))
const submittedAtLabel = computed(() => formatDateTime(props.report.creation))
const modifiedAtLabel = computed(() => formatDateTime(props.report.modified))
const showModifiedAt = computed(
  () => props.report.modified && props.report.modified !== props.report.creation,
)

const introText = computed(() => {
  const territoryText = props.partnerTerritory ? ` in ${props.partnerTerritory}` : ''
  return __(
    `This is a snapshot of the current DreamSave uptake by the groups under our partner ${props.partnerName}${territoryText} as reported in the month of ${reportingMonthLabel.value}.`,
  )
})

const sections = computed(() => {
  const sectionGroups = [
    {
      key: 'partner',
      title: 'Partner',
      items: [
        textItem(
          'achievements',
          __('Key Achievements'),
          props.report.achievements,
        ),
        textItem(
          'partner_satisfaction',
          __('How satisfied is this Partner Organization with DreamSave?'),
          '',
          {
            answerText: props.report.partner_satisfaction,
            highlightAnswer: true,
            subAnswers: hasText(props.report.partner_satisfaction_details)
              ? [props.report.partner_satisfaction_details]
              : [],
          },
        ),
        textItem(
          'insights_issues',
          __('Any major complaints or issues experienced by the partner with Insights?'),
          props.report.insights_issues,
        ),
        textItem(
          'next_steps_with_partner',
          __('Next Steps and Upcoming Plans with this Partner'),
          props.report.next_steps_with_partner,
        ),
      ],
    },
    {
      key: 'groups',
      title: 'Groups',
      items: [
        textItem(
          'group_satisfaction',
          __('How satisfied are the groups with DreamSave?'),
          '',
          {
            answerText: props.report.group_satisfaction,
            highlightAnswer: true,
            subAnswers: hasText(props.report.group_satisfaction_details)
              ? [props.report.group_satisfaction_details]
              : [],
          },
        ),
        numberItem(
          'num_of_groups_on_insights',
          __('Number of Groups on Insights'),
          formatNumber(props.report.num_of_groups_on_insights),
        ),
        numberItem(
          'num_of_registered_groups',
          __('Number of Registered Groups (Partner Reported)'),
          formatNumber(props.report.num_of_registered_groups),
        ),
        textItem(
          'group_number_difference_reason',
          __('Reason for Difference in Group Numbers'),
          props.report.group_number_difference_reason,
        ),
        numberItem(
          'percentage_of_two_plus_not_backed_up_groups',
          __('% Groups with 2+ Meetings Not Backed Up'),
          formatNumber(props.report.percentage_of_two_plus_not_backed_up_groups, '%'),
        ),
        numberItem(
          'percentage_of_never_backed_up_groups',
          __('% Groups that Have Never Backed Up Meetings'),
          formatNumber(props.report.percentage_of_never_backed_up_groups, '%'),
        ),
        textItem(
          'reasons_for_groups_not_backing_up',
          __('Reasons for Groups Not Backing Up Meetings'),
          props.report.reasons_for_groups_not_backing_up,
        ),
        textItem(
          'support_plan_for_backups',
          __('Support Plan for Backup Issues'),
          props.report.support_plan_for_backups,
        ),
      ],
    },
    {
      key: 'general',
      title: 'General',
      items: [
        textItem(
          'insights_data_concerns',
          __('Insights Data Concerns'),
          props.report.insights_data_concerns,
        ),
      ],
    },
  ]

  return sectionGroups.map((section) => ({
    ...section,
    items: section.items.filter((item) => {
      if (item.type === 'number') {
        return item.answerText !== __('Not provided')
      }

      return item.answerText || item.answerHtml || item.subAnswers?.length
    }),
  }))
})
</script>

<style scoped>
.document-section + .document-section {
  margin-top: 20px;
}

.document-heading {
  margin-bottom: 16px;
  color: #2196f3;
  font-size: 16px;
  font-weight: 700;
}

.document-primary-answer {
  margin-top: 8px;
}

.document-primary-answer--highlight {
  color: #0070c0;
  font-style: italic;
  font-weight: 700;
}

.page-break {
  break-inside: avoid;
}
</style>