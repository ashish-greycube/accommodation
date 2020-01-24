// Copyright (c) 2016, DBF and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["CheckOut"] = {
	"filters": [
        {
			"fieldname": "checkout_date",
			"label": __("Check Out"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},

	]
}
