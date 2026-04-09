# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from crm.api.contact import create_new, get_linked_deals, search_emails, set_as_primary, validate
from crm.fcrm.doctype.crm_deal.test_crm_deal import create_test_contact, create_test_deal


class TestContactAPI(IntegrationTestCase):
	def tearDown(self) -> None:
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_validate_updates_deal_email_mobile_no(self):
		contact = create_test_contact(
			first_name="Contact",
			last_name="Owner",
			email="contact.owner@example.com",
			mobile_no="+1111111111",
		)
		deal = create_test_deal(organization=f"Deal Org {frappe.generate_hash(length=6)}")
		deal.append("contacts", {"contact": contact.name, "is_primary": 1})
		deal.save()

		contact.email_id = "updated.owner@example.com"
		contact.mobile_no = "+2222222222"
		validate(contact, None)

		values = frappe.db.get_value("CRM Deal", deal.name, ["email", "mobile_no"], as_dict=True)
		self.assertEqual(values.email, "updated.owner@example.com")
		self.assertEqual(values.mobile_no, "+2222222222")

	def test_validate_skips_non_primary_contact(self):
		contact = create_test_contact(first_name="Secondary", email="secondary@example.com")
		deal = create_test_deal(organization=f"Deal Org {frappe.generate_hash(length=6)}")
		deal.append("contacts", {"contact": contact.name, "is_primary": 0})
		deal.save()

		contact.email_id = "updated.secondary@example.com"
		validate(contact, None)

		values = frappe.db.get_value("CRM Deal", deal.name, ["email", "mobile_no"], as_dict=True)
		self.assertFalse(values.email)
		self.assertFalse(values.mobile_no)

	def test_create_new_email(self):
		contact = create_test_contact(first_name="Email Only")

		self.assertTrue(create_new(contact.name, "email", "new.email@example.com"))

		contact.reload()
		self.assertEqual(contact.email_ids[-1].email_id, "new.email@example.com")

	def test_create_new_email_sets_primary_if_first(self):
		contact = create_test_contact(first_name="Primary Email")

		create_new(contact.name, "email", "primary.email@example.com")

		contact.reload()
		self.assertEqual(contact.email_ids[0].is_primary, 1)

	def test_create_new_phone(self):
		contact = create_test_contact(first_name="Phone Only")

		self.assertTrue(create_new(contact.name, "mobile_no", "+3333333333"))

		contact.reload()
		self.assertEqual(contact.phone_nos[-1].phone, "+3333333333")
		self.assertEqual(contact.phone_nos[-1].is_primary_mobile_no, 1)

	def test_create_new_invalid_field_throws(self):
		contact = create_test_contact(first_name="Invalid Field")

		with self.assertRaises(frappe.exceptions.ValidationError):
			create_new(contact.name, "invalid", "value")

	def test_set_as_primary_email(self):
		contact = create_test_contact(first_name="Primary Switch", email="old@example.com")
		create_new(contact.name, "email", "new@example.com")

		set_as_primary(contact.name, "email", "new@example.com")

		contact.reload()
		primary_emails = [email.email_id for email in contact.email_ids if email.is_primary]
		self.assertEqual(primary_emails, ["new@example.com"])

	def test_set_as_primary_mobile_no(self):
		contact = create_test_contact(first_name="Primary Mobile", mobile_no="+1111111111")
		create_new(contact.name, "mobile_no", "+4444444444")

		set_as_primary(contact.name, "mobile_no", "+4444444444")

		contact.reload()
		primary_numbers = [phone.phone for phone in contact.phone_nos if phone.is_primary_mobile_no]
		self.assertEqual(primary_numbers, ["+4444444444"])

	def test_get_linked_deals(self):
		contact = create_test_contact(first_name="Linked", email="linked@example.com")
		deal = create_test_deal(organization=f"Deal Org {frappe.generate_hash(length=6)}")
		deal.append("contacts", {"contact": contact.name, "is_primary": 1})
		deal.save()

		result = get_linked_deals(contact.name)

		self.assertEqual(len(result), 1)
		self.assertEqual(result[0]["name"], deal.name)

	def test_get_linked_deals_permission_denied(self):
		contact = create_test_contact(first_name="No Permission")

		with patch("crm.api.contact.frappe.has_permission", return_value=False):
			with self.assertRaises(frappe.PermissionError):
				get_linked_deals(contact.name)

	def test_search_emails(self):
		contact = create_test_contact(
			first_name="Search",
			last_name="Target",
			email="search.target@example.com",
		)

		result = search_emails("search.target")

		self.assertTrue(any(row[1] == "search.target@example.com" and row[2] == contact.name for row in result))