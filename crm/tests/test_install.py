# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from crm.fcrm.doctype.crm_partner_report.test_crm_partner_report import (
	create_test_partner_report,
	create_test_territory,
)
from crm.install import _resolve_region_link_value, backfill_partner_report_regions


class TestInstall(IntegrationTestCase):
	def tearDown(self) -> None:
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_resolve_region_link_value_with_name(self):
		territory = create_test_territory()

		self.assertEqual(_resolve_region_link_value(territory.name), territory.name)

	def test_resolve_region_link_value_with_territory_name(self):
		territory = create_test_territory()

		self.assertEqual(_resolve_region_link_value(territory.territory_name), territory.name)

	def test_resolve_region_link_value_none(self):
		self.assertIsNone(_resolve_region_link_value(None))

	def test_resolve_region_link_value_empty_string(self):
		self.assertIsNone(_resolve_region_link_value("   "))

	def test_resolve_region_link_value_nonexistent(self):
		self.assertIsNone(_resolve_region_link_value("Missing Territory"))

	def test_backfill_partner_report_regions(self):
		if not frappe.get_meta("User").has_field("region"):
			self.skipTest("User.region is not available in this test site")

		territory = create_test_territory()
		frappe.db.set_value("User", "Administrator", "region", territory.territory_name)

		report = create_test_partner_report(submitted_by="Administrator")
		frappe.db.set_value("CRM Partner Report", report.name, "region", None, update_modified=False)

		backfill_partner_report_regions()

		self.assertEqual(
			frappe.db.get_value("CRM Partner Report", report.name, "region"),
			territory.name,
		)

	def test_backfill_skips_reports_with_existing_region(self):
		if not frappe.get_meta("User").has_field("region"):
			self.skipTest("User.region is not available in this test site")

		territory = create_test_territory()
		existing_territory = create_test_territory()
		frappe.db.set_value("User", "Administrator", "region", territory.territory_name)

		report = create_test_partner_report(
			submitted_by="Administrator",
			region=existing_territory.name,
		)

		backfill_partner_report_regions()

		self.assertEqual(
			frappe.db.get_value("CRM Partner Report", report.name, "region"),
			existing_territory.name,
		)

	def test_backfill_idempotent(self):
		if not frappe.get_meta("User").has_field("region"):
			self.skipTest("User.region is not available in this test site")

		territory = create_test_territory()
		frappe.db.set_value("User", "Administrator", "region", territory.territory_name)

		report = create_test_partner_report(submitted_by="Administrator")
		frappe.db.set_value("CRM Partner Report", report.name, "region", None, update_modified=False)

		backfill_partner_report_regions()
		first_value = frappe.db.get_value("CRM Partner Report", report.name, "region")
		backfill_partner_report_regions()
		second_value = frappe.db.get_value("CRM Partner Report", report.name, "region")

		self.assertEqual(first_value, territory.name)
		self.assertEqual(second_value, territory.name)