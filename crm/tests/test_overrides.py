# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

from frappe.tests import UnitTestCase

from crm import hooks
from crm.overrides.contact import CustomContact
from crm.overrides.email_template import CustomEmailTemplate


class TestOverrides(UnitTestCase):
	def test_custom_contact_default_list_data(self):
		data = CustomContact.default_list_data()

		self.assertEqual(sorted(data.keys()), ["columns", "rows"])
		self.assertEqual(
			[column["key"] for column in data["columns"]],
			["full_name", "email_id", "mobile_no", "company_name", "modified"],
		)
		self.assertEqual(
			data["rows"],
			["name", "full_name", "company_name", "email_id", "mobile_no", "modified", "image"],
		)

	def test_custom_email_template_default_list_data(self):
		data = CustomEmailTemplate.default_list_data()

		self.assertEqual(sorted(data.keys()), ["columns", "rows"])
		self.assertEqual(
			[column["key"] for column in data["columns"]],
			["name", "subject", "enabled", "reference_doctype", "modified"],
		)
		self.assertEqual(
			data["rows"],
			[
				"name",
				"enabled",
				"use_html",
				"reference_doctype",
				"subject",
				"response",
				"response_html",
				"modified",
			],
		)

	def test_custom_contact_registered_in_hooks(self):
		self.assertEqual(hooks.override_doctype_class["Contact"], "crm.overrides.contact.CustomContact")

	def test_custom_email_template_registered_in_hooks(self):
		self.assertEqual(
			hooks.override_doctype_class["Email Template"],
			"crm.overrides.email_template.CustomEmailTemplate",
		)