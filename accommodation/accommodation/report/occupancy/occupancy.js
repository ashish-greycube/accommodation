// Copyright (c) 2016, DBF and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Occupancy"] = {
    onload: function (report) {
        report.page.remove_inner_button("Set Chart");
    },

    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.now_date(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.now_date(),
            "reqd": 1
        },
        {
            "fieldname": "report",
            "label": __("Report"),
            "fieldtype": "Select",
            "options": "Checked In\nToday Check Out\nToday Arrival\nFuture Booking\nCompleted",
            "default": "Checked In",
            "reqd": 1
        },
        {
            "fieldname": "today",
            "label": __("Today"),
            "fieldtype": "Date",
            "default": frappe.datetime.nowdate(),
            "hidden": 1
        },
        {
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		}

    ]
}