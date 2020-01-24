// Copyright (c) 2019, DBF and contributors
// For license information, please see license.txt

frappe.ui.form.on('Accommodation Guest', {
	refresh: function (frm) {

	},

	sync_icard: function (frm) {
		if (!frm.doc.mahatma_id) {
			frappe.msgprint("Please enter a valid Mahatma ID to sync.");
			return;
		}

		frappe.call({
			method: "accommodation.accommodation.controller.sync_icard",
			args: { doc: frm.doc },
			callback: function (r) {
				frappe.model.sync(r.message);
				frm.refresh();
				frappe.show_alert({ message: __("Guest details synced with ICARD "), indicator: 'green' });
			}
		});
	}


});
