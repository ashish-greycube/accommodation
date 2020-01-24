// Copyright (c) 2016, DBF and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Advance Payment"] = {
    onload: function (report) {
        report.page.remove_inner_button("Set Chart");
    },
    "filters": [
        {
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.now_date(), -30),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.now_date(),
            "reqd": 1
        },
    ]
}