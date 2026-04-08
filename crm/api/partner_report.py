import calendar
import json
from datetime import date

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, nowdate


PARTNER_REPORT_REGION_FIELD = "region"
USER_REGION_FIELD = "region"

ANALYTICS_METRICS = {
	"group": [
		{
			"key": "num_of_groups_on_insights",
			"label": _("Number of Groups on Insights"),
			"aggregation": "sum",
		},
		{
			"key": "num_of_registered_groups",
			"label": _("Number of Registered Groups"),
			"aggregation": "sum",
		},
	],
	"backup": [
		{
			"key": "percentage_of_two_plus_not_backed_up_groups",
			"label": _("% Groups 2+ Meetings Not Backed Up"),
			"aggregation": "average",
		},
		{
			"key": "percentage_of_never_backed_up_groups",
			"label": _("% Groups Never Backed Up"),
			"aggregation": "average",
		},
	],
}


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
def get_partner_report_analytics(
	metric_group: str,
	month_count: int = 12,
	year: int | None = None,
	month: int | None = None,
	countries: list[str] | str | None = None,
	regions: list[str] | str | None = None,
	partners: list[str] | str | None = None,
):
	"""Return monthly partner report analytics for group or backup metrics."""
	if not frappe.has_permission("CRM Partner Report", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	metrics = ANALYTICS_METRICS.get(metric_group)
	if not metrics:
		frappe.throw(_("Invalid metric group"))

	month_count = max(cint(month_count), 1)
	month_starts = _get_month_starts(month_count, year=year, month=month)
	month_labels = [_format_month_label(month_start.year, month_start.month) for month_start in month_starts]
	month_buckets, report_count = _get_month_buckets_for_filters(
		metrics=metrics,
		month_starts=month_starts,
		countries=countries,
		regions=regions,
		partners=partners,
	)

	return _build_analytics_response(month_starts, month_labels, metrics, month_buckets, report_count)


@frappe.whitelist()
def export_partner_report_analytics(
	metric_group: str,
	year: int,
	month: int,
	month_count: int = 1,
	countries: list[str] | str | None = None,
	regions: list[str] | str | None = None,
	partners: list[str] | str | None = None,
):
	"""Return a server-generated analytics export as an Excel-compatible TSV file."""
	if not frappe.has_permission("CRM Partner Report", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	metrics = ANALYTICS_METRICS.get(metric_group)
	if not metrics:
		frappe.throw(_("Invalid metric group"))

	month_count = max(cint(month_count), 1)
	month_starts = _get_month_starts(month_count, year=year, month=month)
	month_labels = [_format_month_label(month_start.year, month_start.month) for month_start in month_starts]
	month_buckets, report_count = _get_month_buckets_for_filters(
		metrics=metrics,
		month_starts=month_starts,
		countries=countries,
		regions=regions,
		partners=partners,
	)
	payload = _build_analytics_response(month_starts, month_labels, metrics, month_buckets, report_count)
	content = _build_export_content(
		payload=payload,
		metric_group=metric_group,
		start_month=month_starts[0],
		end_month=month_starts[-1],
		regions=regions,
		countries=countries,
		partners=partners,
	)
	filename = _build_export_filename(metric_group, month_starts[0], month_starts[-1])

	frappe.response["filename"] = filename
	frappe.response["filecontent"] = content
	frappe.response["type"] = "download"
	frappe.response["content_type"] = "application/vnd.ms-excel"
	frappe.response["display_content_as"] = "attachment"


@frappe.whitelist()
def get_partner_report_regions() -> list[dict]:
	"""Return all top-level CRM territories for the regions filter."""
	if not frappe.has_permission("CRM Partner Report", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	return _get_territory_options(_get_region_territory_names())


@frappe.whitelist()
def get_partner_report_countries(regions: list[str] | str | None = None) -> list[dict]:
	"""Return organization address countries, optionally narrowed by region."""
	if not frappe.has_permission("CRM Partner Report", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	return _get_string_options(_get_country_names_for_filters(regions=regions))


@frappe.whitelist()
def get_partner_report_partners(
	countries: list[str] | str | None = None,
	regions: list[str] | str | None = None,
) -> list[dict]:
	"""Return organizations for the selected geography filters."""
	if not frappe.has_permission("CRM Partner Report", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	partner_names = _get_partner_names_for_filters(regions=regions, countries=countries)
	if not partner_names:
		return []

	return frappe.get_list(
		"CRM Organization",
		filters=[["name", "in", partner_names]],
		fields=["name", "organization_name", "territory", "contract_status"],
		order_by="organization_name asc",
		page_length=500,
	)


@frappe.whitelist()
def get_partner_report(name: str):
	"""Return a single CRM Partner Report."""
	report = frappe.get_doc("CRM Partner Report", name)
	report.check_permission("read")
	return report.as_dict()


@frappe.whitelist()
def get_partner_report_permissions(name: str | None = None):
	"""Return current user's doctype or document permissions for Partner Reports."""
	permissions = {
		"create": bool(frappe.has_permission("CRM Partner Report", "create")),
		"read": bool(frappe.has_permission("CRM Partner Report", "read", doc=name)),
		"write": bool(frappe.has_permission("CRM Partner Report", "write", doc=name)),
		"delete": bool(frappe.has_permission("CRM Partner Report", "delete", doc=name)),
	}
	return {"permissions": permissions}


@frappe.whitelist()
def create_partner_report(data: dict | str):
	"""Create a new CRM Partner Report."""
	if isinstance(data, str):
		data = json.loads(data)
	data = _normalize_partner_report_payload(data)

	doc = frappe.get_doc({"doctype": "CRM Partner Report", **data})
	doc.insert()
	frappe.db.commit()
	return doc.name


@frappe.whitelist()
def update_partner_report(name: str, data: dict | str):
	"""Update an existing CRM Partner Report."""
	if isinstance(data, str):
		data = json.loads(data)
	data = _normalize_partner_report_payload(data)

	doc = frappe.get_doc("CRM Partner Report", name)
	doc.check_permission("write")
	doc.update(data)
	doc.save()
	frappe.db.commit()
	return doc.name


def _normalize_partner_report_payload(data: dict) -> dict:
	normalized = dict(data or {})
	for fieldname in ("partner", "submitted_by", PARTNER_REPORT_REGION_FIELD):
		if fieldname in normalized:
			normalized[fieldname] = _coerce_link_value(normalized.get(fieldname))
	return normalized


def _coerce_link_value(value):
	if isinstance(value, dict):
		return value.get("value") or value.get("name") or value.get("label") or ""
	return value


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


def _get_month_buckets_for_filters(
	metrics: list[dict],
	month_starts: list[date],
	countries: list[str] | str | None = None,
	regions: list[str] | str | None = None,
	partners: list[str] | str | None = None,
) -> tuple[dict, int]:
	month_buckets = _build_month_buckets(month_starts, metrics)
	filters = _build_report_filters(
		month_starts=month_starts,
		regions=regions,
		countries=countries,
		partners=partners,
	)
	if filters is None:
		return month_buckets, 0

	reports = frappe.get_all(
		"CRM Partner Report",
		fields=["reporting_month", "partner", *[metric["key"] for metric in metrics]],
		filters=filters,
		order_by="reporting_month asc",
		page_length=0,
	)
	report_count = len(reports)

	for report in reports:
		report_date = getdate(report.get("reporting_month"))
		if not report_date:
			continue
		month_key = _format_month_key(report_date.year, report_date.month)
		bucket = month_buckets.get(month_key)
		if not bucket:
			continue

		for metric in metrics:
			value = report.get(metric["key"])
			if value in (None, ""):
				continue
			numeric_value = flt(value)
			if metric["aggregation"] == "sum":
				bucket[metric["key"]]["value"] += numeric_value
			else:
				bucket[metric["key"]]["value"] += numeric_value
				bucket[metric["key"]]["count"] += 1

	return month_buckets, report_count


def _build_report_filters(
	month_starts: list[date],
	regions: list[str] | str | None = None,
	countries: list[str] | str | None = None,
	partners: list[str] | str | None = None,
) -> dict | None:
	start_date = month_starts[0]
	end_date = _get_month_end(month_starts[-1])
	filters: dict[str, object] = {
		"reporting_month": ["between", [start_date.isoformat(), end_date.isoformat()]],
	}

	selected_regions = _coerce_string_list(regions)
	selected_countries = _coerce_string_list(countries)
	selected_partners = _coerce_string_list(partners)

	if selected_regions or selected_countries or selected_partners:
		partner_names = _get_partner_names_for_filters(
			regions=selected_regions,
			countries=selected_countries,
			partners=selected_partners,
			include_missing_country=bool(selected_partners),
		)
		if not partner_names:
			return None
		filters["partner"] = ["in", partner_names]

	return filters


def _get_partner_names_for_filters(
	regions: list[str] | str | None = None,
	countries: list[str] | str | None = None,
	partners: list[str] | str | None = None,
	include_missing_country: bool = False,
) -> list[str]:
	selected_regions = _coerce_string_list(regions)
	selected_countries = _coerce_string_list(countries)
	selected_partners = _coerce_string_list(partners)

	organization_filters = []
	if selected_regions:
		region_scope = _get_descendant_territory_names(selected_regions, include_self=True)
		if not region_scope:
			return []
		organization_filters.append(["territory", "in", region_scope])

	if selected_partners:
		organization_filters.append(["name", "in", selected_partners])

	partner_names = frappe.get_all(
		"CRM Organization",
		filters=organization_filters,
		pluck="name",
		order_by="organization_name asc",
		page_length=500,
	)
	partner_names = [name for name in partner_names if name]

	if selected_countries:
		allowed_countries = set(selected_countries)
		address_country_map = _get_address_country_map(partner_names)
		partner_names = [
			name
			for name in partner_names
			if address_country_map.get(name) in allowed_countries
			or (include_missing_country and not address_country_map.get(name))
		]

	return partner_names


def _get_region_territory_names() -> list[str]:
	return [
		territory["name"]
		for territory in _get_territory_records()
		if not territory.get("parent_crm_territory")
	]


def _get_country_names_for_filters(regions: list[str] | str | None = None) -> list[str]:
	selected_regions = _coerce_string_list(regions)
	organization_filters = [["address", "is", "set"]]
	if selected_regions:
		region_scope = _get_descendant_territory_names(selected_regions, include_self=True)
		if not region_scope:
			return []
		organization_filters.append(["territory", "in", region_scope])

	organization_names = frappe.get_all(
		"CRM Organization",
		filters=organization_filters,
		pluck="name",
		distinct=True,
		order_by="name asc",
		page_length=0,
	)
	if not organization_names:
		return []

	address_country_map = _get_address_country_map(organization_names)
	return sorted({country for country in address_country_map.values() if country})


def _get_address_country_map(organization_names: list[str] | None = None) -> dict[str, str]:
	organization_filters = [["address", "is", "set"]]
	if organization_names:
		organization_filters.append(["name", "in", organization_names])

	organizations = frappe.get_all(
		"CRM Organization",
		filters=organization_filters,
		fields=["name", "address"],
		page_length=0,
	)
	if not organizations:
		return {}

	address_names = sorted(
		{organization.get("address") for organization in organizations if organization.get("address")}
	)
	if not address_names:
		return {}

	addresses = frappe.get_all(
		"Address",
		filters=[["name", "in", address_names]],
		fields=["name", "country"],
		page_length=0,
	)
	address_map = {
		address["name"]: address.get("country")
		for address in addresses
		if address.get("name")
	}

	return {
		organization["name"]: address_map.get(organization.get("address"), "")
		for organization in organizations
		if organization.get("name")
	}


def _get_descendant_territory_names(
	territory_names: list[str] | str | None,
	include_self: bool = True,
) -> list[str]:
	selected_names = set(_coerce_string_list(territory_names))
	if not selected_names:
		return []

	territories = _get_territory_records()
	territory_names_set = {territory["name"] for territory in territories if territory.get("name")}
	children_by_parent: dict[str | None, list[str]] = {}
	for territory in territories:
		name = territory.get("name")
		if not name:
			continue
		parent = territory.get("parent_crm_territory")
		children_by_parent.setdefault(parent, []).append(name)

	descendants: list[str] = []
	seen: set[str] = set()
	stack = [name for name in selected_names if name in territory_names_set]

	while stack:
		name = stack.pop()
		if name in seen:
			continue
		seen.add(name)
		if include_self or name not in selected_names:
			descendants.append(name)
		stack.extend(children_by_parent.get(name, []))

	return descendants


def _get_territory_records(territory_names: list[str] | None = None) -> list[dict]:
	filters = {}
	if territory_names:
		filters = [["name", "in", territory_names]]

	return frappe.get_all(
		"CRM Territory",
		filters=filters,
		fields=["name", "territory_name", "parent_crm_territory", "lft", "rgt"],
		page_length=0,
	)


def _get_territory_options(territory_names: list[str]) -> list[dict]:
	territory_names = [name for name in territory_names if name]
	if not territory_names:
		return []

	territories = frappe.get_all(
		"CRM Territory",
		filters=[["name", "in", territory_names]],
		fields=["name", "territory_name"],
		page_length=0,
	)
	territory_map = {
		territory["name"]: territory.get("territory_name") or territory["name"]
		for territory in territories
	}

	return [
		{
			"label": territory_map.get(name, name),
			"value": name,
		}
		for name in sorted(set(territory_names), key=lambda value: territory_map.get(value, value))
	]


def _get_string_options(values: list[str] | None = None) -> list[dict]:
	if not values:
		return []

	return [{"label": value, "value": value} for value in values if value]


def _coerce_string_list(values: list[str] | str | None) -> list[str]:
	if not values:
		return []

	if isinstance(values, str):
		try:
			parsed = json.loads(values)
		except json.JSONDecodeError:
			parsed = [value.strip() for value in values.split(",") if value.strip()]
		else:
			if isinstance(parsed, list):
				return [str(value) for value in parsed if value]
			return [str(parsed)] if parsed else []
		return parsed

	return [str(value) for value in values if value]


def _get_month_starts(month_count: int, year: int | None = None, month: int | None = None) -> list[date]:
	if year is not None and month is not None:
		normalized_month = cint(month)
		if 0 <= normalized_month <= 11:
			normalized_month += 1
		if normalized_month < 1 or normalized_month > 12:
			frappe.throw(_("Invalid month"))
		end_month = date(cint(year), normalized_month, 1)
	else:
		today = getdate(nowdate())
		end_month = date(today.year, today.month, 1)

	month_starts = []
	current_year = end_month.year
	current_month = end_month.month - month_count + 1
	while current_month <= 0:
		current_month += 12
		current_year -= 1

	for _ in range(month_count):
		month_starts.append(date(current_year, current_month, 1))
		current_month += 1
		if current_month > 12:
			current_month = 1
			current_year += 1

	return month_starts


def _build_month_buckets(month_starts: list[date], metrics: list[dict]) -> dict[str, dict[str, dict[str, float | int]]]:
	buckets = {}
	for month_start in month_starts:
		month_key = _format_month_key(month_start.year, month_start.month)
		buckets[month_key] = {
			metric["key"]: {"value": 0, "count": 0}
			for metric in metrics
		}
	return buckets


def _get_month_end(month_start: date) -> date:
	last_day = calendar.monthrange(month_start.year, month_start.month)[1]
	return date(month_start.year, month_start.month, last_day)


def _format_month_key(year: int, month: int) -> str:
	return f"{year:04d}-{month:02d}"


def _format_month_label(year: int, month: int) -> str:
	return f"{calendar.month_abbr[month].upper()} {year}"


def _build_analytics_response(
	month_starts: list[date],
	months: list[str],
	metrics: list[dict],
	month_buckets: dict,
	report_count: int,
) -> dict:
	data = []
	for metric in metrics:
		row = {"metric": metric["label"]}
		for month_start, month_label in zip(month_starts, months):
			month_key = _format_month_key(month_start.year, month_start.month)
			month_metric = month_buckets[month_key][metric["key"]]
			if metric["aggregation"] == "average":
				count = month_metric["count"]
				row[month_label] = round(month_metric["value"] / count, 2) if count else 0
			else:
				row[month_label] = month_metric["value"]
		data.append(row)

	return {"months": months, "data": data, "report_count": report_count}


def _build_export_content(
	payload: dict,
	metric_group: str,
	start_month: date,
	end_month: date,
	regions: list[str] | str | None = None,
	countries: list[str] | str | None = None,
	partners: list[str] | str | None = None,
) -> str:
	selected_regions = _coerce_string_list(regions)
	selected_countries = _coerce_string_list(countries)
	selected_partners = _coerce_string_list(partners)
	territory_labels = {
		item["value"]: item["label"]
		for item in _get_territory_options(selected_regions + selected_countries)
	}
	selected_partner_labels = _get_partner_label_map(selected_partners)

	title = {
		"group": _("Group Number Analysis"),
		"backup": _("Back Up Rate Analysis"),
	}.get(metric_group, _("Partner Report Analysis"))

	rows = [
		[title],
		[_("Period"), f"{_format_month_label(start_month.year, start_month.month)} - {_format_month_label(end_month.year, end_month.month)}"],
		[_("Regions"), ", ".join(territory_labels.get(region, region) for region in selected_regions) if selected_regions else _("All")],
		[_("Countries"), ", ".join(selected_countries) if selected_countries else _("All")],
		[_("Partners"), ", ".join(selected_partner_labels.get(partner, partner) for partner in selected_partners) if selected_partners else _("All")],
		[],
		[_("Metric"), *payload.get("months", [])],
	]

	for item in payload.get("data", []):
		rows.append([item.get("metric", ""), *[item.get(month, "") for month in payload.get("months", [])]])

	return "\n".join(["\t".join(_escape_tsv_value(value) for value in row) for row in rows])


def _get_partner_label_map(partner_names: list[str]) -> dict[str, str]:
	if not partner_names:
		return {}

	partners = frappe.get_all(
		"CRM Organization",
		filters=[["name", "in", partner_names]],
		fields=["name", "organization_name"],
		page_length=500,
	)
	return {
		partner["name"]: partner.get("organization_name") or partner["name"]
		for partner in partners
	}


def _build_export_filename(metric_group: str, start_month: date, end_month: date) -> str:
	prefix = {
		"group": "group-number-analysis",
		"backup": "back-up-rate-analysis",
	}.get(metric_group, "partner-report-analysis")
	return f"{prefix}-{start_month.year}-{start_month.month:02d}-to-{end_month.year}-{end_month.month:02d}.xls"


def _escape_tsv_value(value) -> str:
	normalized = str(value or "")
	return normalized.replace("\t", " ").replace("\r", " ").replace("\n", " ")
