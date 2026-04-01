<template>
  <LayoutHeader v-if="organization.doc">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <CustomActions
        v-if="organization._actions?.length"
        :actions="organization._actions"
      />
    </template>
  </LayoutHeader>
  <div v-if="organization.doc" ref="parentRef" class="flex h-full">
    <Resizer
      v-if="organization.doc"
      :parent="$refs.parentRef"
      class="flex h-full flex-col overflow-hidden border-r"
    >
      <div class="border-b">
        <FileUploader
          :validateFile="validateIsImageFile"
          @success="changeOrganizationImage"
        >
          <template #default="{ openFileSelector, error }">
            <div class="flex flex-col items-start justify-start gap-4 p-5">
              <div class="flex gap-4 items-center">
                <div class="group relative h-15.5 w-15.5">
                  <Avatar
                    size="3xl"
                    class="h-15.5 w-15.5"
                    :label="organization.doc.organization_name"
                    :image="organization.doc.organization_logo"
                  />
                  <component
                    :is="organization.doc.organization_logo ? Dropdown : 'div'"
                    v-bind="
                      organization.doc.organization_logo
                        ? {
                            options: [
                              {
                                icon: 'upload',
                                label: organization.doc.organization_logo
                                  ? __('Change Image')
                                  : __('Upload Image'),
                                onClick: openFileSelector,
                              },
                              {
                                icon: 'trash-2',
                                label: __('Remove Image'),
                                onClick: () => changeOrganizationImage(''),
                              },
                            ],
                          }
                        : { onClick: openFileSelector }
                    "
                    class="!absolute bottom-0 left-0 right-0"
                  >
                    <div
                      class="z-1 absolute bottom-0 left-0 right-0 flex h-14 cursor-pointer items-center justify-center rounded-b-full bg-black bg-opacity-40 pt-5 opacity-0 duration-300 ease-in-out group-hover:opacity-100"
                      style="
                        -webkit-clip-path: inset(22px 0 0 0);
                        clip-path: inset(22px 0 0 0);
                      "
                    >
                      <CameraIcon class="h-6 w-6 cursor-pointer text-white" />
                    </div>
                  </component>
                </div>
                <div class="flex flex-col gap-2 truncate">
                  <div class="truncate text-2xl font-medium text-ink-gray-9">
                    <span>{{ organization.doc.name }}</span>
                  </div>
                  <div
                    v-if="organization.doc.website"
                    class="flex items-center gap-1.5 text-base text-ink-gray-8"
                  >
                    <WebsiteIcon class="size-4" />
                    <span>{{ website(organization.doc.website) }}</span>
                  </div>
                  <ErrorMessage :message="__(error)" />
                </div>
              </div>
              <div class="flex gap-1.5">
                <Button
                  v-if="canDelete"
                  :label="__('Delete')"
                  theme="red"
                  size="sm"
                  iconLeft="trash-2"
                  @click="deleteOrganization()"
                />
                <Button
                  :tooltip="__('Open Website')"
                  icon="link"
                  @click="openWebsite"
                />
              </div>
            </div>
          </template>
        </FileUploader>
      </div>
      <div
        v-if="sections.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <SidePanelLayout
          :sections="sections.data"
          doctype="CRM Organization"
          :docname="organization.doc.name"
          @reload="sections.reload"
          @beforeFieldChange="beforeFieldChange"
        />
      </div>
    </Resizer>
    <Tabs
      v-model="tabIndex"
      as="div"
      :tabs="tabs"
      class="flex flex-1 overflow-hidden flex-col [&_[role='tablist']]:gap-7.5 [&_[role='tablist']]:px-5 [&_[role='tabpanel']:not([hidden])]:flex [&_[role='tabpanel']:not([hidden])]:grow"
    >
      <template #tab-item="{ tab, selected }">
        <button
          class="group flex items-center gap-2 border-b border-transparent py-2.5 text-base text-ink-gray-5 duration-300 ease-in-out hover:text-ink-gray-9"
          :class="{ 'text-ink-gray-9': selected }"
        >
          <component :is="tab.icon" v-if="tab.icon" class="h-5" />
          {{ __(tab.label) }}
          <Badge
            v-if="tab.count != null"
            class="group-hover:bg-surface-gray-7"
            :class="[selected ? 'bg-surface-gray-7' : 'bg-gray-600']"
            variant="solid"
            theme="gray"
            size="sm"
          >
            {{ tab.count }}
          </Badge>
        </button>
      </template>
      <template #tab-panel>
        <template v-if="tabs[tabIndex]?.name === 'Deals'">
          <DealsListView
            v-if="rows.length"
            class="mt-4"
            :rows="rows"
            :columns="columns"
            :options="{ selectable: false, showTooltip: false }"
          />
          <EmptyState v-else :icon="tabs[tabIndex]?.icon" :name="__('Deals')" />
        </template>
        <template v-else-if="tabs[tabIndex]?.name === 'Contacts'">
          <ContactsListView
            v-if="rows.length"
            class="mt-4"
            :rows="rows"
            :columns="columns"
            :options="{ selectable: false, showTooltip: false }"
          />
          <EmptyState v-else :icon="tabs[tabIndex]?.icon" :name="__('Contacts')" />
        </template>
        <template v-else-if="tabs[tabIndex]?.name === 'Partner Reports'">
          <div class="flex justify-end px-5 pt-4">
            <Button
              v-if="partnerReportPermissions.data?.permissions?.create"
              variant="solid"
              :label="__('New Report')"
              iconLeft="plus"
              @click="createPartnerReport"
            />
          </div>
          <PartnerReportsListView
            v-if="organizationPartnerReportRows.length"
            class="mt-4"
            v-model="organizationPartnerReports.data.page_length_count"
            v-model:list="organizationPartnerReports"
            :rows="organizationPartnerReportRows"
            :columns="organizationPartnerReportColumns"
            :options="{
              selectable: true,
              showTooltip: false,
              rowCount: organizationPartnerReports.data.row_count,
              totalCount: organizationPartnerReports.data.total_count,
              canDelete: partnerReportPermissions.data?.permissions?.delete,
            }"
            @loadMore="loadMoreOrganizationPartnerReports"
            @updatePageCount="updateOrganizationPartnerReportPageCount"
            @showReport="showPartnerReport"
          />
          <EmptyState
            v-else
            :icon="tabs[tabIndex]?.icon"
            :name="__('Partner Reports')"
            :description="__('It appears that there are currently no Partner Reports available. You can create a Partner Report using the New Report button.')"
          />
        </template>
        <Activities
          v-else
          doctype="CRM Organization"
          :docname="organizationId"
          :tabs="tabs"
          v-model:tabIndex="tabIndex"
          v-model:reload="reload"
        />
      </template>
    </Tabs>
  </div>
  <ErrorPage
    v-else-if="errorTitle"
    :errorTitle="errorTitle"
    :errorMessage="errorMessage"
  />
  <DeleteLinkedDocModal
    v-if="showDeleteLinkedDocModal"
    v-model="showDeleteLinkedDocModal"
    :doctype="'CRM Organization'"
    :docname="props.organizationId"
    name="Organizations"
  />
  <PartnerReportModal
    v-if="showPartnerReportModal"
    v-model="showPartnerReportModal"
    :report-id="selectedPartnerReportId"
    :initial-partner="props.organizationId"
    :initial-partner-label="organization.doc?.organization_name || props.organizationId"
    :lock-partner="selectedPartnerReportId === 'new'"
    @submitted="handlePartnerReportSubmitted"
    @saved="handlePartnerReportSaved"
  />
</template>

<script setup>
import ErrorPage from '@/components/ErrorPage.vue'
import Resizer from '@/components/Resizer.vue'
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import Icon from '@/components/Icon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import DealsListView from '@/components/ListViews/DealsListView.vue'
import ContactsListView from '@/components/ListViews/ContactsListView.vue'
import PartnerReportsListView from '@/components/ListViews/PartnerReportsListView.vue'
import WebsiteIcon from '@/components/Icons/WebsiteIcon.vue'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import PartnerReportIcon from '@/components/Icons/PartnerReportIcon.vue'
import Activities from '@/components/Activities/Activities.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import EmptyState from '@/components/ListViews/EmptyState.vue'
import PartnerReportModal from '@/components/Modals/PartnerReportModal.vue'
import { useActiveTabManager } from '@/composables/useActiveTabManager'
import DeleteLinkedDocModal from '@/components/DeleteLinkedDocModal.vue'
import CustomActions from '@/components/CustomActions.vue'
import { showAddressModal, addressProps } from '@/composables/modals'
import { useDocument } from '@/data/document'
import { getSettings } from '@/stores/settings'
import { globalStore } from '@/stores/global'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { getView } from '@/utils/view'
import {
  formatDate,
  timeAgo,
  validateIsImageFile,
  setupCustomizations,
  openWebsite as openExternalWebsite,
} from '@/utils'
import {
  Breadcrumbs,
  Avatar,
  FileUploader,
  Dropdown,
  Tabs,
  createListResource,
  usePageMeta,
  createResource,
  toast,
  call,
} from 'frappe-ui'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  organizationId: { type: String, required: true },
})

const { brand } = getSettings()
const { $dialog, $socket } = globalStore()
const { getUser } = usersStore()
const { getDealStatus } = statusesStore()
const { doctypeMeta } = getMeta('CRM Organization')

const route = useRoute()
const router = useRouter()

const errorTitle = ref('')
const errorMessage = ref('')

const showDeleteLinkedDocModal = ref(false)
const showPartnerReportModal = ref(false)
const selectedPartnerReportId = ref('new')

const {
  document: organization,
  permissions,
  scripts,
} = useDocument('CRM Organization', props.organizationId)

const canDelete = computed(() => permissions.data?.permissions?.delete || false)

const breadcrumbs = computed(() => {
  let items = [{ label: __('Organizations'), route: { name: 'Organizations' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(
      route.query.view,
      route.query.viewType,
      'CRM Organization',
    )
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Organizations',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: title.value,
    route: {
      name: 'Organization',
      params: { organizationId: props.organizationId },
    },
  })
  return items
})

const title = computed(() => {
  let t = doctypeMeta.value?.title_field || 'name'
  return organization.doc?.[t] || props.organizationId
})

usePageMeta(() => {
  return {
    title: title.value,
    icon: brand.favicon,
  }
})

async function deleteOrganization() {
  showDeleteLinkedDocModal.value = true
}

function changeOrganizationImage(file) {
  organization.setValue.submit({
    organization_logo: file?.file_url || null,
  })
}

function beforeFieldChange(data) {
  if (Object.hasOwn(data ?? {}, 'organization_name')) {
    call('frappe.client.rename_doc', {
      doctype: 'CRM Organization',
      old_name: props.organizationId,
      new_name: data.organization_name,
    }).then(() => {
      router.push({
        name: 'Organization',
        params: { organizationId: data.organization_name },
      })
    })
  } else {
    organization.save.submit()
  }
}

function website(url) {
  return url && url.replace(/^(?:https?:\/\/)?(?:www\.)?/i, '')
}

function openWebsite() {
  if (!organization.doc.website) {
    toast.error(__('No Website Found'))
    return
  }

  openExternalWebsite(organization.doc.website)
}

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'CRM Organization'],
  params: { doctype: 'CRM Organization' },
  auto: true,
  transform: (data) => getParsedSections(data),
})

function getParsedSections(_sections) {
  return _sections.map((section) => {
    section.columns = section.columns.map((column) => {
      column.fields = column.fields.map((field) => {
        if (field.fieldname === 'address') {
          return {
            ...field,
            create: (value, close) => {
              openAddressModal()
              close()
            },
            edit: (address) => openAddressModal(address),
          }
        } else {
          return field
        }
      })
      return column
    })
    return section
  })
}

const reload = ref(false)
const tabs = computed(() => [
  {
    name: 'Deals',
    label: __('Deals'),
    icon: DealsIcon,
    count: computed(() => deals.data?.length),
  },
  {
    name: 'Contacts',
    label: __('Contacts'),
    icon: ContactsIcon,
    count: computed(() => contacts.data?.length),
  },
  {
    name: 'Partner Reports',
    label: __('Partner Reports'),
    icon: PartnerReportIcon,
    count: computed(() => organizationPartnerReports.data?.total_count || 0),
  },
  {
    name: 'Activity',
    label: __('Activity'),
    icon: ActivityIcon,
  },
  {
    name: 'Emails',
    label: __('Emails'),
    icon: EmailIcon,
  },
  {
    name: 'Comments',
    label: __('Comments'),
    icon: CommentIcon,
  },
  {
    name: 'Notes',
    label: __('Notes'),
    icon: NoteIcon,
  },
  {
    name: 'Tasks',
    label: __('Tasks'),
    icon: TaskIcon,
  },
  {
    name: 'Attachments',
    label: __('Attachments'),
    icon: AttachmentIcon,
  },
])
const { tabIndex } = useActiveTabManager(tabs, 'lastOrganizationTab')

const deals = createListResource({
  type: 'list',
  doctype: 'CRM Deal',
  cache: ['deals', props.organizationId],
  fields: [
    'name',
    'organization',
    'currency',
    'annual_revenue',
    'status',
    'email',
    'mobile_no',
    'deal_owner',
    'modified',
  ],
  filters: {
    organization: props.organizationId,
  },
  orderBy: 'modified desc',
  pageLength: 20,
  auto: true,
})

const contacts = createListResource({
  type: 'list',
  doctype: 'Contact',
  cache: ['contacts', props.organizationId],
  fields: [
    'name',
    'full_name',
    'image',
    'email_id',
    'mobile_no',
    'company_name',
    'modified',
  ],
  filters: {
    company_name: props.organizationId,
  },
  orderBy: 'modified desc',
  pageLength: 20,
  auto: true,
})

const partnerReportPermissions = createResource({
  url: 'crm.api.partner_report.get_partner_report_permissions',
  auto: true,
  initialData: { permissions: {} },
})

const organizationPartnerReports = createResource({
  url: 'crm.api.doc.get_data',
  cache: ['organizationPartnerReports', props.organizationId],
  params: {
    doctype: 'CRM Partner Report',
    filters: { partner: props.organizationId },
    order_by: 'reporting_month desc, creation desc',
    view: { view_type: 'list' },
    page_length: 20,
    page_length_count: 20,
  },
  auto: true,
})

const rows = computed(() => {
  let list = !tabIndex.value ? deals : contacts

  if (!list.data) return []

  return list.data.map((row) => {
    return !tabIndex.value ? getDealRowObject(row) : getContactRowObject(row)
  })
})

const { getFormattedCurrency } = getMeta('CRM Deal')

const columns = computed(() => {
  return tabIndex.value === 0 ? dealColumns : contactColumns
})

const organizationPartnerReportRows = computed(() => {
  if (!organizationPartnerReports.data?.data) return []

  return organizationPartnerReports.data.data.map((report) => {
    let mappedRow = {}

    organizationPartnerReports.data.rows.forEach((fieldname) => {
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

const organizationPartnerReportColumns = computed(() => {
  let listColumns = organizationPartnerReports.data?.columns || []

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

function getDealRowObject(deal) {
  return {
    name: deal.name,
    organization: {
      label: deal.organization,
      logo: organization.doc?.organization_logo,
    },
    annual_revenue: getFormattedCurrency('annual_revenue', deal),
    status: {
      label: deal.status,
      color: getDealStatus(deal.status)?.color,
    },
    email: deal.email,
    mobile_no: deal.mobile_no,
    deal_owner: {
      label: deal.deal_owner && getUser(deal.deal_owner).full_name,
      ...(deal.deal_owner && getUser(deal.deal_owner)),
    },
    modified: {
      label: formatDate(deal.modified),
      timeAgo: __(timeAgo(deal.modified)),
    },
  }
}

function getContactRowObject(contact) {
  return {
    name: contact.name,
    full_name: {
      label: contact.full_name,
      image_label: contact.full_name,
      image: contact.image,
    },
    email: contact.email_id,
    mobile_no: contact.mobile_no,
    company_name: {
      label: contact.company_name,
      logo: organization.doc?.organization_logo,
    },
    modified: {
      label: formatDate(contact.modified),
      timeAgo: __(timeAgo(contact.modified)),
    },
  }
}

function formatReportingMonth(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
  })
}

function loadMoreOrganizationPartnerReports() {
  if (organizationPartnerReports.loading) return

  organizationPartnerReports.update({
    params: {
      ...organizationPartnerReports.params,
      page_length:
        organizationPartnerReports.params.page_length +
        organizationPartnerReports.params.page_length_count,
    },
  })
  organizationPartnerReports.reload()
}

function updateOrganizationPartnerReportPageCount(count) {
  if (organizationPartnerReports.loading) return

  organizationPartnerReports.update({
    params: {
      ...organizationPartnerReports.params,
      page_length: count,
      page_length_count: count,
    },
  })
  organizationPartnerReports.reload()
}

function createPartnerReport() {
  selectedPartnerReportId.value = 'new'
  showPartnerReportModal.value = true
}

function showPartnerReport(name) {
  selectedPartnerReportId.value = name
  showPartnerReportModal.value = true
}

function handlePartnerReportSubmitted(name) {
  organizationPartnerReports.reload()
  selectedPartnerReportId.value = name
  setTimeout(() => {
    showPartnerReportModal.value = true
  })
}

function handlePartnerReportSaved() {
  organizationPartnerReports.reload()
}

const dealColumns = [
  {
    label: __('Organization'),
    key: 'organization',
    width: '11rem',
  },
  {
    label: __('Amount'),
    key: 'annual_revenue',
    align: 'right',
    width: '9rem',
  },
  {
    label: __('Status'),
    key: 'status',
    width: '10rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '12rem',
  },
  {
    label: __('Mobile No.'),
    key: 'mobile_no',
    width: '11rem',
  },
  {
    label: __('Deal Owner'),
    key: 'deal_owner',
    width: '10rem',
  },
  {
    label: __('Last Modified'),
    key: 'modified',
    width: '8rem',
  },
]

const contactColumns = [
  {
    label: __('Name'),
    key: 'full_name',
    width: '17rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '12rem',
  },
  {
    label: __('Phone'),
    key: 'mobile_no',
    width: '12rem',
  },
  {
    label: __('Organization'),
    key: 'company_name',
    width: '12rem',
  },
  {
    label: __('Last Modified'),
    key: 'modified',
    width: '8rem',
  },
]

function openAddressModal(_address) {
  showAddressModal.value = true
  addressProps.value = {
    doctype: 'Address',
    address: _address,
  }
}

// Setup custom actions from Form Scripts
watch(
  () => organization.doc,
  async (_doc) => {
    if (scripts.data?.length) {
      let s = await setupCustomizations(scripts.data, {
        doc: _doc,
        $dialog,
        $socket,
        router,
        toast,
        updateField: organization.setValue.submit,
        createToast: toast.create,
        deleteDoc: deleteOrganization,
        call,
      })
      organization._actions = s.actions || []
    }
  },
  { once: true },
)
</script>
