// Copyright (c) 2016, DBF and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Hotel Analytics"] = {
	"filters": [
		{
			"fieldname":"date_range",
			"label": __("Date Range"),
			"fieldtype": "DateRange",
			"default": [frappe.datetime.add_months(frappe.datetime.get_today(),-1), frappe.datetime.get_today()],
			"reqd": 1
		},
		{
			"fieldname":"room_type",
			"label": __("Room Type"),
			"fieldtype": "Check",
			"default": 1,
			"reqd": 0
		},
		{
			"fieldname":"room",
			"label": __("Room"),
			"fieldtype": "Check",
			"default": 0,
			"reqd": 0
		},
		// {
		// 	"fieldname":"company",
		// 	"label": __("Company"),
		// 	"fieldtype": "Link",
		// 	"options": "Company",
		// 	"default": frappe.defaults.get_user_default("Company")
		// }

	]
}
