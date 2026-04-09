# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from crm.fcrm.doctype.crm_partner_report.crm_partner_report import CRMPartnerReport, RICH_TEXT_FIELDS


class TestCRMPartnerReport(IntegrationTestCase):
	def tearDown(self) -> None:
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_insert_sanitizes_rich_text_fields(self):
		report = create_test_partner_report(
			achievements="<p>Safe <strong>content</strong></p><script>alert('x')</script>",
		)

		self.assertIn("<strong>content</strong>", report.achievements)
		self.assertNotIn("<script", report.achievements.lower())

	def test_update_sanitizes_rich_text_fields(self):
		report = create_test_partner_report()

		report.group_satisfaction_details = (
			'<p>Updated</p><a href="javascript:alert(1)">bad</a>'
		)
		report.save()

		self.assertIn("<p>Updated</p>", report.group_satisfaction_details)
		self.assertNotIn("javascript:", report.group_satisfaction_details.lower())

	def test_before_insert_sets_submitted_by(self):
		report = create_test_partner_report(submitted_by=None)

		self.assertEqual(report.submitted_by, "Administrator")

	def test_before_insert_preserves_explicit_submitted_by(self):
		report = create_test_partner_report(submitted_by="crm.user1@example.com")

		self.assertEqual(report.submitted_by, "crm.user1@example.com")

	def test_before_insert_resolves_region_from_report(self):
		territory = create_test_territory()

		report = create_test_partner_report(region=territory.name)

		self.assertEqual(report.region, territory.name)

	def test_before_insert_resolves_region_by_territory_name(self):
		territory = create_test_territory()

		report = create_test_partner_report(region=territory.territory_name)

		self.assertEqual(report.region, territory.name)

	def test_before_insert_resolves_region_from_user(self):
		if not frappe.get_meta("User").has_field("region"):
			self.skipTest("User.region is not available in this test site")

		territory = create_test_territory()
		frappe.db.set_value("User", "Administrator", "region", territory.territory_name)

		report = create_test_partner_report(region=None, submitted_by=None)

		self.assertEqual(report.region, territory.name)

	def test_before_insert_skips_region_if_field_missing(self):
		doc = frappe.get_doc({"doctype": "CRM Partner Report", **get_test_partner_report_data()})
		original_has_field = doc.meta.has_field

		with patch.object(
			doc.meta,
			"has_field",
			side_effect=lambda fieldname: False if fieldname == "region" else original_has_field(fieldname),
		):
			doc.before_insert()

		self.assertFalse(doc.get("region"))

	def test_validate_sets_country_from_partner_name_suffix(self):
		partner = frappe.get_doc(
			{
				"doctype": "CRM Organization",
				"organization_name": f"Partner Report Test Org {frappe.generate_hash(length=4)} - Uganda",
			}
		).insert()

		report = create_test_partner_report(partner=partner.name, country=None)

		self.assertEqual(report.country, "Uganda")

	def test_default_list_data_structure(self):
		data = CRMPartnerReport.default_list_data()

		self.assertEqual(sorted(data.keys()), ["columns", "rows"])
		self.assertEqual([column["key"] for column in data["columns"]], [
			"partner",
			"reporting_month",
			"partner_satisfaction",
			"group_satisfaction",
			"submitted_by",
			"creation",
		])
		self.assertEqual(data["rows"], [
			"name",
			"partner",
			"reporting_month",
			"partner_satisfaction",
			"group_satisfaction",
			"submitted_by",
			"creation",
		])

	def test_sanitize_all_rich_text_fields(self):
		payload = {
			fieldname: f"<p>{fieldname}</p><script>alert('x')</script>"
			for fieldname in RICH_TEXT_FIELDS
		}

		report = create_test_partner_report(**payload)

		for fieldname in RICH_TEXT_FIELDS:
			value = report.get(fieldname)
			self.assertIn(f"<p>{fieldname}</p>", value)
			self.assertNotIn("<script", value.lower())

	def test_sanitize_skips_empty_and_none_fields(self):
		report = create_test_partner_report(
			group_number_difference_reason="",
			reasons_for_groups_not_backing_up=None,
			support_plan_for_backups="",
		)

		self.assertEqual(report.group_number_difference_reason, "")
		self.assertIsNone(report.reasons_for_groups_not_backing_up)
		self.assertEqual(report.support_plan_for_backups, "")


def create_test_territory(**kwargs):
	data = {
		"doctype": "CRM Territory",
		"territory_name": f"Territory {frappe.generate_hash(length=6)}",
	}
	data.update(kwargs)
	return frappe.get_doc(data).insert()


def get_test_partner_report_data(**kwargs):
	partner = kwargs.pop("partner", None)
	if not partner:
		partner = frappe.get_doc(
			{
				"doctype": "CRM Organization",
				"organization_name": f"Partner Report Test Org {frappe.generate_hash(length=6)}",
			}
		).insert().name

	data = {
		"partner": partner,
		"reporting_month": "2026-03-01",
		"achievements": "<p>Achievements</p>",
		"partner_satisfaction": "Satisfied, no complaints but no praise either",
		"partner_satisfaction_details": "<p>Partner satisfaction details</p>",
		"insights_issues": "<p>Insights issues</p>",
		"next_steps_with_partner": "<p>Next steps</p>",
		"group_satisfaction": "Satisfied, no complaints but no praise either",
		"group_satisfaction_details": "<p>Group satisfaction details</p>",
		"num_of_groups_on_insights": 10,
		"num_of_registered_groups": 12,
		"group_number_difference_reason": "<p>Difference reason</p>",
		"percentage_of_two_plus_not_backed_up_groups": 20,
		"percentage_of_never_backed_up_groups": 10,
		"reasons_for_groups_not_backing_up": "<p>Reasons</p>",
		"support_plan_for_backups": "<p>Support plan</p>",
		"insights_data_concerns": "<p>Data concerns</p>",
	}
	data.update(kwargs)
	return data


def create_test_partner_report(**kwargs):
	return frappe.get_doc({"doctype": "CRM Partner Report", **get_test_partner_report_data(**kwargs)}).insert()