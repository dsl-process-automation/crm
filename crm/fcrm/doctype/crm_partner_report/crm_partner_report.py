import frappe
from frappe.model.document import Document


class CRMPartnerReport(Document):
	def before_insert(self):
		self.submitted_by = frappe.session.user
