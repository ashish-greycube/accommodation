// Copyright (c) 2019, DBF and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Accommodation Booking', 'items_add', function (frm) {
// 	console.log('row added');
// });
frappe.ui.form.on('Accommodation Booking', {
	before_load: function (frm) { },

	items_on_form_rendered: function (frm, grid_row) {
	},

	setup: function (frm) {
		frm.add_fetch('customer', 'customer_group', 'customer_group');
	},

	onload: function (frm) {

		frm.set_query("room", "items", function (doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "accommodation.accommodation.controller.get_available_rooms",
				filters: {
					'room_type': row.room_type,
					'check_in': row.check_in,
					'check_out': row.check_out,
					'package': frm.doc.package
				}
			}
		});


	},

	refresh: function (frm) {
		frm.trigger("add_custom_buttons");
		frm.events.set_item_status(frm);
		frm.events.show_payments(frm);

		frm.set_df_property('customer_contact', 'hidden', frm.doc.customer_group !== "Internal");
		frm.set_df_property('package', 'read_only', !frm.doc.__islocal && frm.doc.status !== "Booking");

		if (frm.doc.customer_group == "Internal") {
			frm.events.set_customer_contacts(frm);
		}
		if (frm.doc.invoice || frm.doc.status == 'Cancelled') {
			frm.set_read_only();
			frm.refresh_fields();
		}
	},

	check_in: function (frm, item) {
		if (item.item_status != 'Reserved') {
			frappe.msgprint("Please select a reserved room to check in.")
			return;
		}
		frappe.model.set_value(item.doctype, item.name, "check_in", frappe.datetime.get_today())
		frappe.model.set_value(item.doctype, item.name, "item_status", "Checked In")
	},

	check_out: function (frm, item) {
		if (item.item_status != 'Checked In') {
			frappe.msgprint("Please select a checked in room to check out.")
			return;
		}
		frappe.model.set_value(item.doctype, item.name, "check_out", frappe.datetime.get_today())
		frappe.model.set_value(item.doctype, item.name, "item_status", "Checked Out")
	},

	make_invoice: function (frm) {
		return frappe.call({
			method: "make_sales_invoice",
			doc: frm.doc,
			freeze: true,
			args: { submit_invoice: 0 },
			callback: function (r) {
				frm.reload_doc();
			}
		})
	},

	submit_invoice: function (frm) {
		return frappe.call({
			method: "submit_sales_invoice",
			doc: frm.doc,
			callback: function (r) {
				frm.reload_doc();
			}
		})
	},

	submit_invoice: function (frm) {
		return frappe.call({
			method: "submit_sales_invoice",
			doc: frm.doc,
			callback: function (r) {
				frm.reload_doc();
			}
		})
	},

	cancel_invoice: function (frm) {
		return frappe.call({
			method: "cancel_sales_invoice",
			doc: frm.doc,
			callback: function (r) {
				frm.reload_doc();
			}
		})
	},

	show_payments: function (frm) {
		frm.fields_dict.payments_html.$wrapper.empty();
		frm.fields_dict.payments_section.collapse(false);
		return frappe.call({
			method: "accommodation.accommodation.controller.get_payments_for_booking",
			args: { booking: frm.doc.name },
			callback: function (r) {
				let payments = r.message || [];

				if (!payments.length)
					return;

				function total_payment(total, d) {
					return total + (d.is_refund ? 0 - d.total_amount : d.total_amount);
				}
				let total_amount = payments.reduce(total_payment, 0);
				payments.push({ total_amount: total_amount, total_amount_currency: 'INR', pay_to_recd_from: 'Total Paid' })

				let html = frappe.render_template('payments', { payments: payments })
				frm.fields_dict.payments_html.$wrapper.html(html);
				frm.fields_dict.payments_html.$wrapper.on('click', '.receipt-print-link', function () {
					let name = $(this).attr('data-name');
					frappe.custom.print_doc("Journal Entry", name, true);
				});
			}
		})
	},


	add_custom_buttons: function (frm) {
		frm.page.clear_icons();

		frm.page.add_menu_item(__("Cancel Booking"), function () {
			frappe.confirm(
				__('Are you sure you want to cancel this booking?'),
				function () {
					frappe.call({
						method:
							"accommodation.accommodation.controller.cancel_booking",
						args: { name: frm.doc.name },
						callback: function (r) {
							if (!r.exc) {
								frm.reload_doc();
							}
						}
					});
				}
			);
		})

		frm.page.add_action_icon('fa fa-print', () => {
			if (!cur_frm.doc.invoice)
				frappe.throw(__("Please make invoice for Booking."));
			frappe.custom.print_doc("Sales Invoice", cur_frm.doc.invoice, true);
		});

		if (!frm.doc.__islocal && !frm.doc.invoice && frm.doc.status != 'Cancelled') {

			frm.add_custom_button(__('Make Invoice'), function () {
				frm.events.make_invoice(frm);
			});
		}

		if (frm.doc.invoice) {
			if (frm.doc.invoice_status == 'Draft') {
				frm.add_custom_button(__("Submit Invoice"), function () {
					frm.events.submit_invoice(frm);
				}).addClass("btn-primary");
			}
			else if (frm.doc.invoice_status != 'Cancelled') {
				frm.add_custom_button(__("Cancel Invoice"), function () {
					frm.events.cancel_invoice(frm);
				}).addClass("btn-danger");
			}

		}

		if (!frm.doc.__islocal && frm.doc.customer_group && frm.doc.customer_group !== "Internal") {
			frm.add_custom_button(__("Make Payment"), function () {
				frm.events.make_payment(frm);
			});
		}

		frappe.custom.add_grid_custom_button(frm.fields_dict["items"].grid, "Check Out", () => {
			let selected = frm.fields_dict["items"].grid.get_selected_children();

			if (!selected.length) {
				frappe.msgprint({
					message: __('Please select rooms to Check Out'),
					indicator: 'orange',
					title: "Select Items"
				});
				return;
			}

			selected.forEach(r => {
				frm.events.check_out(frm, r);
			});
			frm.refresh_field("items");
			frm.trigger("calculate_totals");
		});

		frappe.custom.add_grid_custom_button(frm.fields_dict["items"].grid, "Check In", () => {
			let selected = frm.fields_dict["items"].grid.get_selected_children();
			if (!selected.length) {
				frappe.msgprint({
					message: __('Please select rooms to Check In'),
					indicator: 'orange',
					title: "Select Items"
				});
				return;
			}
			selected.forEach(r => {
				frm.events.check_in(frm, r);
			});
			frm.refresh_field("items");
			frm.trigger("calculate_totals");
		});

	},

	set_item_status: function (frm) {
		frm.fields_dict["items"].grid.grid_rows.forEach(function (row) {
			row.wrapper.find('.row-index')
				.removeClass((i, classes) => {
					var matches = classes.match(/\bitem-\S+/ig);
					return (matches) ? matches.join(' ') : '';
				})
				.addClass(frappe.model.scrub('item-' + row.doc.item_status));
		});
	},

	calculate_totals: function (frm) {
		frappe.call({
			method: "accommodation.accommodation.controller.set_item_rates",
			args: { booking: frm.doc },
			callback: function (r) {
				for (var i = 0; i < r.message.items.length; i++) {
					let d = r.message.items[i];
					Object.assign(frm.doc.items[i], {
						room_rate: d.room_rate,
						bed_rate: d.bed_rate,
						amount: d.amount,
					});
				}
				frm.set_value("total_amount", r.message.total_amount);
			}
		});
	},

	make_payment: function (frm) {
		accommodation.booking.make_payment_dialog(frm);
	},

	validate: function (frm) {
		$.each(frm.doc.items, (idx, d) => {
			if (d.__islocal && d.room && d.item_status === "Reserved" && d.check_in === frappe.datetime.get_today())
				// auto checkin for today 
				d.item_status = "Checked In";
		});
	},

	set_customer_contacts: function (frm) {
		frappe.call({
			method: 'accommodation.accommodation.controller.get_customer_contacts',
			args: { 'customer': frm.doc.customer },
			callback: function (r) {
				frm.fields_dict.customer_contact.df.options = [""].concat(r.message);
				frm.fields_dict.customer_contact.refresh();
			}
		});
	},

	customer: function (frm) {
		frm.set_df_property('customer_contact', 'hidden', frm.doc.customer_group !== "Internal");
		frm.refresh_field('customer_contact');
		if (frm.doc.customer_group !== "Internal") {
			frm.doc.customer_contact = null;
		}
		else {
			frm.events.set_customer_contacts(frm);
		}
	},

	update_beds: function (frm, cdt, cdn, arr_beds) {
		let item = locals[cdt][cdn]
		let days = Math.max(frappe.datetime.get_diff(item.checkout, item.check_in), 1);
		item.extra_bed_count = arr_beds.length;
		item.total_extra_bed_count = arr_beds.length * days;
		item.alloted_beds = arr_beds.join(",");
		frm.refresh_field("items")
	}

});

frappe.ui.form.on("Accommodation Booking Item", {
	"form_render": function (frm, cdt, cdn) {
		var d = locals[cdt][cdn],
			$wrapper = frm.fields_dict[d.parentfield].grid.grid_rows_by_docname[cdn].grid_form.fields_dict["beds_html"].$wrapper;
		$('<div id="bed-list"></div>').appendTo($wrapper);
		return frappe.call({
			method: "accommodation.accommodation.controller.get_beds",
			args: { room: d.room, booking: frm.doc.name },
			callback: function (r) {
				createTable('#bed-list', r.message || [], frm, cdt, cdn)
			}
		})

	},

	"select_all_beds": function (frm, cdt, cdn) {
		debugger;
		let $tbl = $('#bed-list'),
			data = $tbl.jexcel('getData'),
			_beds = [];
		$.each(data[0], (idx, val) => {
			if (val != "O") {
				data[0][idx] = "X";
				_beds.push(idx + 1);
			}
		});
		$('#bed-list').jexcel('setData', data);
		frappe.model.set_value(cdt, cdn, "alloted_beds", _beds.join(","));
	},

	"clear_all_beds": function (frm, cdt, cdn) {
		let $tbl = $('#bed-list'),
			data = $tbl.jexcel('getData');
		$.each(data[0], (idx, val) => {
			if (val != "O") {
				data[0][idx] = "";
			}
		});
		$('#bed-list').jexcel('setData', data);
		frappe.model.set_value(cdt, cdn, "alloted_beds", "");
	},

	"items_add": function (frm, cdt, cdn) {
		let today = frappe.datetime.get_today();
		frappe.model.set_value(cdt, cdn, "check_in", today)
		frappe.model.set_value(cdt, cdn, "check_out", frappe.datetime.add_days(today, 1));
		frappe.model.set_value(cdt, cdn, "item_status", 'Reserved');
	},

	// "before_items_remove": function (frm, cdt, cdn) {
	// 	let line = locals[cdt][cdn]
	// 	if (!line.__islocal)
	// 		frappe.throw(__("You cannot delete this row"));
	// },

	"items_remove": function (frm, cdt, cdn) {
		frm.trigger("calculate_totals");
	},

	"check_in": function (frm, cdt, cdn) {
		frm.trigger("calculate_totals");
	},

	"check_out": function (frm, cdt, cdn) {
		frm.trigger("calculate_totals");
	},

	"package": function (frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "room", null);
		frm.trigger("calculate_totals");
	},

	"extra_bed_count": function (frm, cdt, cdn) {
		let item = frappe.get_doc(cdt, cdn);
		let days = frappe.datetime.get_diff(item.checkout, item.check_in) - 1;
		days = days < 1 ? 1 : days;
		frappe.model.set_value(cdt, cdn, "total_extra_bed_count", item.extra_bed_count * days);
		frm.trigger("calculate_totals");
	},

	"total_extra_bed_count": function (frm, cdt, cdn) {
		frm.trigger("calculate_totals");
	},

	"room_count": function (frm, cdt, cdn) {
		frm.trigger("calculate_totals");
	},

	"room": function (frm, cdt, cdn) {
		frm.trigger("calculate_totals");
	},

});


frappe.provide('accommodation.booking');

const bed_legend = { "O": "#f7430c", "X": "#935eff", "": "#ffffff" }

function sync_beds(item, data) {
	let item_beds = item.alloted_beds ? item.alloted_beds.split(",") : [],
		selected_beds = $('#bed-list').jexcel('getSelectedCells'),
		_beds = [];
	$.each(item_beds, (idx, val) => {
		data[0][parseInt(val) - 1] = "X";
	});

	$.each(selected_beds || [], (idx, val) => {
		const index = val.cellIndex - 1;
		if (data[0][index] != "O")
			data[0][index] = data[0][index] == "" ? "X" : "";
	});

	$.each(data[0], (idx, val) => {
		if (data[0][idx] == "X")
			_beds.push(idx + 1);
	});
	console.log(_beds);
	return _beds.join(",");
}

function createTable(container, data, frm, cdt, cdn) {
	let item = locals[cdt][cdn],
		item_beds = sync_beds(item, data);

	$(container).jexcel({
		data: data,
		colHeaders: Array.from(new Array(data[0].length), (val, index) => index + 1),
		editable: false,
		defaultColWidth: 45,
		onload: function (a) {
			$(container).jexcel('updateSettings',
				{
					table: (instance, cell, col, row, val, id) => {
						$(cell).css('background-color', bed_legend[val]);
						$(cell).css('font-weight', 'bold');
					}
				});
		},
		onselection: function (obj, cell, val) {
			let data = $('#bed-list').jexcel('getData');
			item_beds = sync_beds(item, data);
			console.log(item_beds);
			$('#bed-list').jexcel('setData', data);
			frappe.model.set_value(cdt, cdn, "alloted_beds", item_beds);
		},

	});
}

function log() { }

accommodation.booking.make_payment_dialog = function (frm) {
	var d = new frappe.ui.Dialog({
		title: __('Make Payment'),
		fields: get_dialog_fields(frm),
		primary_action: function () {
			d.hide();
			var data = d.get_values();
			if (data.amount <= 0) {
				frappe.msgprint(`Invalid payment amount ${data.amount}`);
				return;
			}
			if (data.mode_of_payment == "Cheque") {
				if (!data.cheque_no || !data.cheque_date) {
					frappe.throw(__('Please set Cheque No and Cheque Date'));
					return;
				}
			}

			data.booking = frm.doc.name;
			data.submit = 1;
			data.is_refund = data.is_refund ? 1 : 0;
			frappe.call({
				method: "accommodation.accommodation.controller.make_payment",
				args: data,
				callback: function (r) {
					frm.reload_doc();
					if (frm.doc.invoice) {
						frappe.show_alert(
							{
								message: __('Paid {0} against Invoice {1}',
									[data.amount, `<a href="#Form/Sales Invoice/${frm.doc.invoice}">${frm.doc.invoice}</a>`]),
								indicator: 'green'
							});
					} else {
						frappe.show_alert(
							{
								message: __('Paid {0} against Booking {1}',
									[data.amount, frm.doc.name]),
								indicator: 'green'
							});
					}
				}
			});
		},
		primary_action_label: __('Submit')
	});
	d.show();

}

const payment_options = ["Cash", "Bank", "Card"];

function get_dialog_fields(frm) {
	var fields = [
		{
			"label": "Is Refund",
			"fieldname": "is_refund",
			"fieldtype": "Check",
			"default": (frm.doc.invoice_amount > 0) && (frm.doc.outstanding_amount < 0)
		},
		{
			"label": "Posting Date",
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"label": "Amount",
			"fieldname": "amount",
			"fieldtype": "Currency",
			"reqd": 1,
			"default": Math.abs(frm.doc.outstanding_amount)
		},
		{
			"label": "Mode of payment",
			"fieldname": "mode_of_payment",
			"fieldtype": "Select",
			"options": payment_options,
			"default": payment_options[0],
			"reqd": 1
		},
		{
			"label": "Cheque No",
			"fieldname": "cheque_no",
			"fieldtype": "Data",
		},
		{
			"label": "Cheque Date",
			"fieldname": "cheque_date",
			"fieldtype": "Date",
		},
	];
	return fields;
}