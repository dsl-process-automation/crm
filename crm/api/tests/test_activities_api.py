# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from crm.api.activities import (
	get_contact_activities,
	get_linked_notes,
	get_linked_tasks,
	get_organization_activities,
)
from crm.fcrm.doctype.crm_deal.test_crm_deal import create_test_contact


class TestActivitiesAPI(IntegrationTestCase):
	def tearDown(self) -> None:
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_get_contact_activities_permission_denied(self):
		contact = create_test_contact(first_name="Denied")

		with patch("crm.api.activities.frappe.has_permission", return_value=False):
			with self.assertRaises(frappe.PermissionError):
				get_contact_activities(contact.name)

	def test_get_contact_activities_returns_creation_event(self):
		contact = create_test_contact(first_name="Activity", last_name="Contact")

		activities, calls, notes, tasks, attachments = get_contact_activities(contact.name)

		self.assertEqual(calls, [])
		self.assertEqual(notes, [])
		self.assertEqual(tasks, [])
		self.assertTrue(any(item["activity_type"] == "creation" for item in activities))
		self.assertTrue(any(item["data"] == "created this contact" for item in activities))
		self.assertEqual(attachments, [])

	def test_get_contact_activities_includes_comments(self):
		contact = create_test_contact(first_name="Commented")
		frappe.get_doc(
			{
				"doctype": "Comment",
				"comment_type": "Comment",
				"reference_doctype": "Contact",
				"reference_name": contact.name,
				"content": "Contact activity comment",
			}
		).insert(ignore_permissions=True)

		activities, *_ = get_contact_activities(contact.name)

		self.assertTrue(
			any(
				item["activity_type"] == "comment" and item.get("content") == "Contact activity comment"
				for item in activities
			)
		)

	def test_get_organization_activities_permission_denied(self):
		organization = create_test_organization()

		with patch("crm.api.activities.frappe.has_permission", return_value=False):
			with self.assertRaises(frappe.PermissionError):
				get_organization_activities(organization.name)

	def test_get_organization_activities_returns_creation_event(self):
		organization = create_test_organization()

		activities, calls, notes, tasks, attachments = get_organization_activities(organization.name)

		self.assertEqual(calls, [])
		self.assertEqual(notes, [])
		self.assertEqual(tasks, [])
		self.assertTrue(any(item["activity_type"] == "creation" for item in activities))
		self.assertTrue(any(item["data"] == "created this organization" for item in activities))
		self.assertEqual(attachments, [])

	def test_get_organization_activities_includes_comments(self):
		organization = create_test_organization()
		frappe.get_doc(
			{
				"doctype": "Comment",
				"comment_type": "Comment",
				"reference_doctype": "CRM Organization",
				"reference_name": organization.name,
				"content": "Organization activity comment",
			}
		).insert(ignore_permissions=True)

		activities, *_ = get_organization_activities(organization.name)

		self.assertTrue(
			any(
				item["activity_type"] == "comment"
				and item.get("content") == "Organization activity comment"
				for item in activities
			)
		)

	def test_get_linked_notes_with_reference_doctype(self):
		contact = create_test_contact(first_name="Shared", last_name="Name")
		create_test_organization(organization_name=contact.name)

		contact_note = frappe.get_doc(
			{
				"doctype": "FCRM Note",
				"title": "Contact Note",
				"reference_doctype": "Contact",
				"reference_docname": contact.name,
				"content": "Only contact note",
			}
		).insert()
		frappe.get_doc(
			{
				"doctype": "FCRM Note",
				"title": "Organization Note",
				"reference_doctype": "CRM Organization",
				"reference_docname": contact.name,
				"content": "Only organization note",
			}
		).insert()

		result = get_linked_notes(contact.name, "Contact")

		self.assertEqual([row["name"] for row in result], [contact_note.name])

	def test_get_linked_tasks_with_reference_doctype(self):
		contact = create_test_contact(first_name="Shared", last_name="Task")
		create_test_organization(organization_name=contact.name)

		contact_task = frappe.get_doc(
			{
				"doctype": "CRM Task",
				"title": "Contact Task",
				"reference_doctype": "Contact",
				"reference_docname": contact.name,
			}
		).insert()
		frappe.get_doc(
			{
				"doctype": "CRM Task",
				"title": "Organization Task",
				"reference_doctype": "CRM Organization",
				"reference_docname": contact.name,
			}
		).insert()

		result = get_linked_tasks(contact.name, "Contact")

		self.assertEqual([row["name"] for row in result], [contact_task.name])


def create_test_organization(**kwargs):
	data = {
		"doctype": "CRM Organization",
		"organization_name": f"CRM Organization {frappe.generate_hash(length=6)}",
	}
	data.update(kwargs)
	return frappe.get_doc(data).insert()