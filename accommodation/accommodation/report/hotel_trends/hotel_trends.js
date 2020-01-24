// Copyright (c) 2016, DBF and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Hotel Trends"] = {
	"filters": [
		{
			"fieldname": "report",
			"label": __("Report"),
			"fieldtype": "Select",
			"options": ["Room Type Occupancy", "Room Occupancy"].join('\n'),
			"default": "Room Occupancy",
			"reqd": 1
		},
		{
			"fieldname": "check_in",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.now_date(), -7),
			"reqd": 1
		},
		{
			"fieldname": "check_out",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.now_date(),
			"reqd": 1
		},
	],
	
	"formatter": function(value, row, column, data, default_formatter) {

		if (["room_type","room"].indexOf(column.fieldname) < 0) {
			if (value != 0) {
				value = $(`<span>${value}</span>`);
				var $value = $(value).css({
					"margin": "0px",
					"padding-left":"5px",
					"padding-right":"2px",
					"background-color": "#ffcf99",
					"font-weight":"bold",
					"color": "red",
					"width": "auto",
					"display": "block"
				});
			} else {
				value = $(`<span>${value}</span>`);
				var $value = $(value).css({
					"margin": "0px",
					"padding-left":"5px",
					"padding-right":"2px",
					"font-weight":"bold",
					"color": "green",
					"width": "auto",
					"display": "block"
				});
			}
			// "background-color": "#ffcf99",

			value = $value.wrap("<p></p>").parent().html();
		}
		return value;
	}
}
