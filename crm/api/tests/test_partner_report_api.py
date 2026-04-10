# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import json
from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from crm.api.doc import get_data, get_filterable_fields, get_query_filters
from crm.api.partner_report import (
	create_partner_report,
	get_partner_report_analytics,
	get_partner_report_countries,
	get_partner_report,
	get_partner_report_permissions,
	get_partner_reports,
	get_partners_for_user,
	update_partner_report,
)
from crm.fcrm.doctype.crm_partner_report.test_crm_partner_report import (
	create_test_territory,
	create_test_partner_report,
	get_test_partner_report_data,
)


class TestPartnerReportAPI(IntegrationTestCase):
	def tearDown(self) -> None:
		frappe.set_user("Administrator")
		frappe.db.rollback()

	@patch("crm.api.partner_report.frappe.db.commit")
	def test_create_partner_report_with_dict(self, _commit):
		report_name = create_partner_report(get_test_partner_report_data())

		report = frappe.get_doc("CRM Partner Report", report_name)
		self.assertEqual(report.partner_satisfaction, "Satisfied, no complaints but no praise either")

	@patch("crm.api.partner_report.frappe.db.commit")
	def test_create_partner_report_with_json_string(self, _commit):
		report_name = create_partner_report(json.dumps(get_test_partner_report_data()))

		self.assertTrue(frappe.db.exists("CRM Partner Report", report_name))

	def test_create_partner_report_invalid_json(self):
		with self.assertRaises(json.JSONDecodeError):
			create_partner_report("{")

	def test_get_partner_report_success(self):
		report = create_test_partner_report()

		result = get_partner_report(report.name)

		self.assertEqual(result["name"], report.name)
		self.assertEqual(result["partner"], report.partner)

	@patch("crm.api.partner_report.frappe.db.commit")
	def test_update_partner_report_success(self, _commit):
		report = create_test_partner_report()

		result = update_partner_report(
			report.name,
			{"partner_satisfaction": "Happy, often praising DreamSave/DSL"},
		)

		report.reload()
		self.assertEqual(result, report.name)
		self.assertEqual(report.partner_satisfaction, "Happy, often praising DreamSave/DSL")

	def test_get_partner_reports_pagination(self):
		create_test_partner_report(reporting_month="2026-01-01")
		create_test_partner_report(reporting_month="2026-02-01")
		create_test_partner_report(reporting_month="2026-03-01")

		result = get_partner_reports(page=1, page_length=2)

		self.assertEqual(result["total"], 3)
		self.assertEqual(len(result["reports"]), 2)

	def test_get_partner_reports_filtering(self):
		partner_one = frappe.get_doc(
			{
				"doctype": "CRM Organization",
				"organization_name": f"Partner Report API Org {frappe.generate_hash(length=6)}",
			}
		).insert()
		partner_two = frappe.get_doc(
			{
				"doctype": "CRM Organization",
				"organization_name": f"Partner Report API Org {frappe.generate_hash(length=6)}",
			}
		).insert()

		create_test_partner_report(partner=partner_one.name)
		create_test_partner_report(partner=partner_two.name)

		result = get_partner_reports(filters=[["partner", "=", partner_one.name]])

		self.assertEqual(result["total"], 1)
		self.assertEqual(len(result["reports"]), 1)
		self.assertEqual(result["reports"][0]["partner"], partner_one.name)

	def test_get_data_filters_partner_reports_by_country(self):
		india_report = create_test_partner_report(country="India")
		us_report = create_test_partner_report(country="United States")

		result = get_data(
			doctype="CRM Partner Report",
			filters={"country": "India"},
			order_by="reporting_month desc, creation desc",
			view={"view_type": "list"},
		)

		report_names = {row["name"] for row in result["data"]}
		self.assertIn(india_report.name, report_names)
		self.assertNotIn(us_report.name, report_names)

	def test_get_data_without_region_filter_returns_partner_reports(self):
		region = create_test_territory()
		report = create_test_partner_report(region=region.name)

		result = get_data(
			doctype="CRM Partner Report",
			filters={},
			order_by="reporting_month desc, creation desc",
			page_length=5000,
			view={"view_type": "list"},
		)

		report_names = {row["name"] for row in result["data"]}
		self.assertIn(report.name, report_names)

	def test_get_query_filters_without_region_leaves_partner_reports_unscoped(self):
		self.assertEqual(get_query_filters("CRM Partner Report", {}), {})

	def test_get_partner_report_countries_reads_report_country_values(self):
		create_test_partner_report(country="Ghana")
		create_test_partner_report(country="Uganda")

		result = get_partner_report_countries()

		self.assertEqual([item["value"] for item in result], ["Ghana", "Uganda"])

	def test_get_filterable_fields_includes_partner_report_country(self):
		fieldnames = {field["fieldname"] for field in get_filterable_fields("CRM Partner Report")}

		self.assertIn("country", fieldnames)

	def test_get_partner_report_analytics_all_time_uses_full_report_history(self):
		create_test_partner_report(
			reporting_month="2024-01-01",
			num_of_groups_on_insights=12,
			num_of_registered_groups=8,
		)
		create_test_partner_report(
			reporting_month="2024-03-01",
			num_of_groups_on_insights=9,
			num_of_registered_groups=6,
		)

		result = get_partner_report_analytics(metric_group="group", all_time=1)

		self.assertEqual(result["months"], ["JAN 2024", "FEB 2024", "MAR 2024"])
		self.assertEqual(result["report_count"], 2)
		self.assertEqual(result["data"][0]["JAN 2024"], 12)
		self.assertEqual(result["data"][0]["FEB 2024"], 0)
		self.assertEqual(result["data"][0]["MAR 2024"], 9)

	def test_get_partner_report_analytics_filters_by_report_country(self):
		create_test_partner_report(
			reporting_month="2026-03-01",
			country="Ghana",
			percentage_of_two_plus_not_backed_up_groups=66.7,
		)
		create_test_partner_report(
			reporting_month="2026-03-01",
			country="Uganda",
			percentage_of_two_plus_not_backed_up_groups=40.0,
		)

		result = get_partner_report_analytics(
			metric_group="backup",
			all_time=1,
			countries=["Ghana"],
		)

		self.assertEqual(result["months"], ["MAR 2026"])
		self.assertEqual(result["report_count"], 1)
		self.assertEqual(result["data"][0]["MAR 2026"], 66.7)

	def test_get_partner_report_permissions_without_name(self):
		with patch(
			"crm.api.partner_report.frappe.has_permission",
			side_effect=[True, True, False, False],
		):
			result = get_partner_report_permissions()

		self.assertEqual(
			result,
			{"permissions": {"create": True, "read": True, "write": False, "delete": False}},
		)

	def test_get_partner_report_permissions_with_name(self):
		report = create_test_partner_report()

		with patch(
			"crm.api.partner_report.frappe.has_permission",
			side_effect=[True, True, True, False],
		) as mock_has_permission:
			result = get_partner_report_permissions(report.name)

		self.assertEqual(result["permissions"]["create"], True)
		self.assertEqual(result["permissions"]["read"], True)
		self.assertEqual(result["permissions"]["write"], True)
		self.assertEqual(result["permissions"]["delete"], False)
		self.assertEqual(mock_has_permission.call_args_list[1].kwargs["doc"], report.name)
		self.assertEqual(mock_has_permission.call_args_list[2].kwargs["doc"], report.name)
		self.assertEqual(mock_has_permission.call_args_list[3].kwargs["doc"], report.name)

	def test_get_partners_for_user_with_territories(self):
		managed_territory = create_test_territory(territory_manager="Administrator")
		other_territory = create_test_territory()

		included_active = create_test_organization(territory=managed_territory.name, contract_status="Active")
		included_expired = create_test_organization(
			territory=managed_territory.name,
			contract_status="Expired",
		)
		excluded_other_territory = create_test_organization(
			territory=other_territory.name,
			contract_status="Active",
		)
		excluded_prospect = create_test_organization(
			territory=managed_territory.name,
			contract_status="Prospect",
		)

		result = get_partners_for_user()
		result_names = {row["name"] for row in result}

		self.assertIn(included_active.name, result_names)
		self.assertIn(included_expired.name, result_names)
		self.assertNotIn(excluded_other_territory.name, result_names)
		self.assertNotIn(excluded_prospect.name, result_names)

	def test_get_partners_for_user_without_territories(self):
		territory_one = create_test_territory(territory_manager="crm.user1@example.com")
		territory_two = create_test_territory(territory_manager="crm.user2@example.com")

		included_active = create_test_organization(territory=territory_one.name, contract_status="Active")
		included_expired = create_test_organization(territory=territory_two.name, contract_status="Expired")
		excluded_terminated = create_test_organization(
			territory=territory_one.name,
			contract_status="Terminated",
		)

		result = get_partners_for_user()
		result_names = {row["name"] for row in result}

		self.assertIn(included_active.name, result_names)
		self.assertIn(included_expired.name, result_names)
		self.assertNotIn(excluded_terminated.name, result_names)


def create_test_organization(**kwargs):
	data = {
		"doctype": "CRM Organization",
		"organization_name": f"CRM Organization {frappe.generate_hash(length=6)}",
	}
	data.update(kwargs)
	return frappe.get_doc(data).insert()


def create_test_address(country):
	return frappe.get_doc(
		{
			"doctype": "Address",
			"address_title": f"Partner Report Address {frappe.generate_hash(length=6)}",
			"address_type": "Billing",
			"address_line1": "123 Test Street",
			"city": "Test City",
			"country": country,
		}
	).insert()