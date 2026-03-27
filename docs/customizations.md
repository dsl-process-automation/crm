# DSL CRM Customizations

Branch: `dsl/customizations` (fork: `dsl-process-automation/crm`)

---

## 1. Notes removed from sidebar navigation

**Files changed:**
- `frontend/src/components/Layouts/AppSidebar.vue`
- `frontend/src/components/Mobile/MobileSidebar.vue`

**What:** Removed the standalone "Notes" nav item from both desktop and mobile sidebars.  
**Why:** Notes are now accessible directly from the Contact and Organization detail pages (see below), making the top-level nav entry redundant.

---

## 2. Activity tabs added to Contact page

**Files changed:**
- `frontend/src/pages/Contact.vue`

**What:** The Contact detail page previously only showed a "Deals" tab. We added a full activity panel with the following tabs:

| Tab | Content |
|-----|---------|
| Deals | Linked deals list (unchanged) |
| Activity | Field change history, comments, attachment logs |
| Emails | Inbound/outbound email communications |
| Comments | User comments |
| Notes | Linked FCRM Notes |
| Tasks | Linked CRM Tasks |
| Attachments | Uploaded files |

**How:**
- Imported `Activities.vue` and tab icon components
- Converted `tabs` from a static array to a `computed()` so tab counts stay reactive
- Replaced the old `#tab-panel="{ tab }"` slot with a named `#tab-panel` that conditionally renders `DealsListView` or `<Activities>` based on `tabs[tabIndex].name`
- Used `useActiveTabManager(tabs, 'lastContactTab')` to persist the last-selected tab per user in localStorage
- `v-if="tab.count != null"` added to the badge so tabs without counts don't show a `0` badge

---

## 3. Activity tabs added to Organization page

**Files changed:**
- `frontend/src/pages/Organization.vue`

**What:** Same as Contact above, but for organizations. The Organization page previously had "Deals" and "Contacts" tabs. We added:

| Tab | Content |
|-----|---------|
| Deals | Linked deals list (unchanged) |
| Contacts | Linked contacts list (unchanged) |
| Activity | Field change history, comments, attachment logs |
| Emails | Email communications |
| Comments | Comments |
| Notes | Linked FCRM Notes |
| Tasks | Linked CRM Tasks |
| Attachments | Uploaded files |

**How:** Same pattern as Contact — `Activities` component, `computed()` tabs, `useActiveTabManager(tabs, 'lastOrganizationTab')`.

---

## 4. Activities component — doctype prop forwarded to backend

**Files changed:**
- `frontend/src/components/Activities/Activities.vue`

**What:** The `get_activities` API call now passes `doctype` alongside `name`.  
**Why:** The backend dispatcher needs to know whether to fetch Contact or CRM Organization activities (see backend section below).

**Change:**
```js
// before
params: { name: props.docname }
// after
params: { name: props.docname, doctype: props.doctype }
```

---

## 5. Backend: activities API extended for Contact and CRM Organization

**Files changed:**
- `crm/api/activities.py`

### `get_activities()` dispatcher
Added `doctype` parameter. Routing order:
1. `doctype == "Contact"` → `get_contact_activities(name)`
2. `doctype == "CRM Organization"` → `get_organization_activities(name)`
3. Otherwise fall through to existing Deal/Lead logic

### `get_contact_activities(name)`
New function. Fetches and merges:
- Creation event
- Field change versions (from `frappe.get_doc_info` / `docinfo.versions`)
- Comments
- Email communications (inbound + automated)
- Attachment logs
- Linked notes (`FCRM Note` filtered by `reference_doctype = "Contact"`)
- Linked tasks (`CRM Task` filtered by `reference_doctype = "Contact"`)
- Linked attachments

Permission check via `frappe.has_permission("Contact", "read", name)`.

### `get_organization_activities(name)`
Identical pattern to `get_contact_activities`, but for `CRM Organization` doctype.

### `get_linked_notes()` / `get_linked_tasks()`
Both functions gained an optional `reference_doctype` parameter so queries are scoped correctly when called for Contact or Organization (previously they only filtered by `reference_docname`, which could return cross-doctype collisions).

---

## 6. DSL Theme

**Files changed:**
- `frontend/src/composables/useDSLTheme.ts` *(new)*
- `frontend/src/App.vue`
- `frontend/src/components/Settings/ThemeSwitcher.vue`
- `frontend/src/index.css`

**What:** Added a fourth "DSL" theme option alongside Light / Dark / System.  
**Appearance:** Identical to Dark theme but with a teal gradient background:
```
linear-gradient(180deg, #0D2326 0%, #1F4042 20%)
```

**How:**
- `useDSLTheme.ts` wraps frappe-ui's `useTheme`. Stores the user's choice (including `'dsl'`) in `localStorage` under `dsl_theme`. When `'dsl'` is selected it sets frappe-ui to `'dark'` (so all CSS variables stay correct) and adds `data-dsl-theme="true"` on `<html>`.
- `index.css` applies the gradient to `html` and `body` when `data-dsl-theme="true"` is present.
- `ThemeSwitcher.vue` renders a 4th card for the DSL theme.
- `App.vue` now calls `initializeDSLTheme()` from `useDSLTheme` instead of frappe-ui's `initializeTheme`.
