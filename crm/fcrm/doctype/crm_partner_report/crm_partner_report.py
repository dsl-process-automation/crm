import frappe
from frappe.model.document import Document


class CRMPartnerReport(Document):
	def before_insert(self):
		self.submitted_by = frappe.session.user

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
