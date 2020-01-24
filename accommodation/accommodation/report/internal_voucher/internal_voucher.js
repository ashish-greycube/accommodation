// Copyright (c) 2016, Amba Tech and contributors
// For license information, please see license.txt
/* eslint-disable */

const months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

frappe.query_reports["Internal Voucher"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "to_date",
			"label": __("To"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "\nJan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
			"default": ""
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nPaid\nUnpaid\nCancelled",
			"default": ""
		}
	],

	get_datatable_options(options) {
		return Object.assign(options, {
			checkboxColumn: true,
		});
	},

	onload: function (report) {
		add_buttons(report);

	}
};


function get_selected_invoices() {
	const report = frappe.query_report;
	const indices = report.datatable.rowmanager.getCheckedRows();
	return indices.map(i => report.datatable.datamanager.getData(i)["Invoice"]);
}


function add_buttons(report) {
	report.page.add_inner_button(__('Email All'), function () {
		const invoice_list = get_selected_invoices();
		if (!invoice_list.length) {
			frappe.show_alert({
				message: __('No invoices selected.'),
				indicator: 'orange'
			})
		}

		return frappe.call({
			method: "accommodation.accommodation.notifications.send_internal_invoice_emails",
			args: { invoices: invoice_list },
			callback: function (r) {
				frappe.show_alert({
					message: __('Internal Voucher emails queued.'),
					indicator: 'green'
				})
				frappe.query_report.refresh();
			}
		});
	});

	report.page.add_inner_button(__('Approve All'), function () {
		const invoice_list = get_selected_invoices();
		if (!invoice_list.length) {
			frappe.show_alert({
				message: __('No invoices selected.'),
				indicator: 'orange'
			})
			return;
		}

		return frappe.call({
			method: "accommodation.accommodation.controller.approve_all_internal_invoices",
			args: { invoice_list: invoice_list, approval_date: frappe.datetime.get_today() },
			callback: function (r) {
				console.log(r);
				frappe.query_report.refresh();
			}
		});
	});
};