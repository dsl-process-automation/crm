import frappe
from frappe import _


@frappe.whitelist()
def get_partner_reports(page: int = 1, page_length: int = 20, filters: list | None = None):
	"""Return paginated list of CRM Partner Reports."""
	page = int(page)
	page_length = int(page_length)
	start = (page - 1) * page_length

	fields = [
		"name",
		"partner",
		"reporting_month",
		"partner_satisfaction",
		"group_satisfaction",
		"submitted_by",
		"creation",
		"modified",
	]

	frappe_filters = filters or []

	reports = frappe.get_list(
		"CRM Partner Report",
		fields=fields,
		filters=frappe_filters,
		order_by="reporting_month desc, creation desc",
		start=start,
		page_length=page_length,
	)

	total = frappe.db.count("CRM Partner Report", filters=frappe_filters)

	return {"reports": reports, "total": total}


@frappe.whitelist()
def get_partner_report(name: str):
	"""Return a single CRM Partner Report."""
	report = frappe.get_doc("CRM Partner Report", name)
	report.check_permission("read")
	return report.as_dict()


@frappe.whitelist()
def create_partner_report(data: dict | str):
	"""Create a new CRM Partner Report."""
	if isinstance(data, str):
		import json
		data = json.loads(data)

	doc = frappe.get_doc({"doctype": "CRM Partner Report", **data})
	doc.insert()
	frappe.db.commit()
	return doc.name


@frappe.whitelist()
def update_partner_report(name: str, data: dict | str):
	"""Update an existing CRM Partner Report."""
	if isinstance(data, str):
		import json
		data = json.loads(data)

	doc = frappe.get_doc("CRM Partner Report", name)
	doc.check_permission("write")
	doc.update(data)
	doc.save()
	frappe.db.commit()
	return doc.name


@frappe.whitelist()
def get_partners_for_user() -> list[dict]:
	"""Return Organizations with contract_status Active, Expired, or unset,
	filtered to the current user's territories if they manage any."""
	user = frappe.session.user

	# Find territories managed by this user
	managed_territories = frappe.db.get_all(
		"CRM Territory",
		filters={"territory_manager": user},
		pluck="name",
	)

	# Include orgs whose contract_status is Active, Expired, or not yet set
	base_filters = [
		["contract_status", "not in", ["Prospect", "Terminated"]],
	]

	if managed_territories:
		base_filters.append(["territory", "in", managed_territories])

	orgs = frappe.get_list(
		"CRM Organization",
		filters=base_filters,
		fields=["name", "organization_name", "territory", "contract_status"],
		order_by="organization_name asc",
		page_length=500,
	)

	return orgs
