import frappe
from frappe.model.document import Document
from frappe.utils.html_utils import sanitize_html


RICH_TEXT_FIELDS = (
	"achievements",
	"partner_satisfaction_details",
	"insights_issues",
	"next_steps_with_partner",
	"group_satisfaction_details",
	"group_number_difference_reason",
	"reasons_for_groups_not_backing_up",
	"support_plan_for_backups",
	"insights_data_concerns",
)


class CRMPartnerReport(Document):
	def validate(self):
		self._sanitize_rich_text_fields()
		self._set_country()

	def before_insert(self):
		self.submitted_by = self.submitted_by or frappe.session.user

		# Tolerate sites that have code updated before DocType metadata is migrated.
		if not self.meta.has_field("region"):
			return

		region = _resolve_region_link_value(self.get("region"))
		if not region and self.submitted_by and frappe.get_meta("User").has_field("region"):
			region = _resolve_region_link_value(
				frappe.db.get_value("User", self.submitted_by, "region")
			)

		if region:
			self.set("region", region)

	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Partner",
				"type": "Link",
				"key": "partner",
				"options": "CRM Organization",
				"width": "16rem",
			},
			{
				"label": "Reporting Month",
				"type": "Date",
				"key": "reporting_month",
				"width": "11rem",
			},
			{
				"label": "Partner Satisfaction",
				"type": "Select",
				"key": "partner_satisfaction",
				"width": "18rem",
			},
			{
				"label": "Group Satisfaction",
				"type": "Select",
				"key": "group_satisfaction",
				"width": "18rem",
			},
			{
				"label": "Submitted By",
				"type": "Link",
				"key": "submitted_by",
				"options": "User",
				"width": "12rem",
			},
			{
				"label": "Submitted On",
				"type": "Datetime",
				"key": "creation",
				"width": "9rem",
			},
		]
		rows = [
			"name",
			"partner",
			"reporting_month",
			"partner_satisfaction",
			"group_satisfaction",
			"submitted_by",
			"creation",
		]
		return {"columns": columns, "rows": rows}

	def _sanitize_rich_text_fields(self):
		for fieldname in RICH_TEXT_FIELDS:
			value = self.get(fieldname)
			if not isinstance(value, str) or not value:
				continue

			self.set(fieldname, sanitize_html(value, always_sanitize=True))

	def _set_country(self):
		if not self.meta.has_field("country"):
			return

		country = _resolve_country_link_value(self.get("country"))
		if not country:
			country = get_partner_country(self.get("partner"))

		if country:
			self.set("country", country)


def _resolve_region_link_value(value: str | None) -> str | None:
	if not value:
		return None

	region = str(value).strip()
	if not region:
		return None

	if frappe.db.exists("CRM Territory", region):
		return region

	return frappe.db.get_value("CRM Territory", {"territory_name": region}, "name")


def get_partner_country(value: str | None) -> str | None:
	partner = _resolve_link_value(value)
	if not partner:
		return None

	organization = frappe.db.get_value(
		"CRM Organization",
		partner,
		["organization_name", "address"],
		as_dict=True,
	)
	if not organization:
		return _extract_country_from_label(partner)

	address = organization.get("address")
	if address:
		country = _resolve_country_link_value(frappe.db.get_value("Address", address, "country"))
		if country:
			return country

	return _extract_country_from_label(organization.get("organization_name") or partner)


def _resolve_country_link_value(value: str | None) -> str | None:
	if not value:
		return None

	country = str(value).strip()
	if not country:
		return None

	if frappe.db.exists("Country", country):
		return country

	return None


def _resolve_link_value(value):
	if isinstance(value, dict):
		return value.get("value") or value.get("name") or value.get("label") or None
	return value


def _extract_country_from_label(label: str | None) -> str | None:
	if not label:
		return None

	normalized_label = str(label).strip()
	if not normalized_label:
		return None

	candidates = []
	if " - " in normalized_label:
		candidates.append(normalized_label.rsplit(" - ", 1)[-1].strip())
	if normalized_label.endswith(")") and "(" in normalized_label:
		candidates.append(normalized_label.rsplit("(", 1)[-1].rstrip(")").strip())

	for candidate in candidates:
		country = _resolve_country_link_value(candidate)
		if country:
			return country

	return None
