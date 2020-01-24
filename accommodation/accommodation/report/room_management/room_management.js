// Copyright (c) 2016, DBF and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Room Management"] = {
    "filters": [
        {
            "fieldname": "room_type",
            "label": __("Room Type"),
            "fieldtype": "Select",
            "options": ["==", "AC", "NAC", "Suite"],
            "default": "=="
        },
        {
            "fieldname": "room_status",
            "label": __("Room Status"),
            "fieldtype": "Select",
            "options": ["==", "Occupied", "Dirty", "Maintenance"],
            "default": "Dirty"
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Select",
            "options": [frappe.user_defaults.company],
            "default": frappe.user_defaults.company,
            "hidden": 1

        }
    ],
    get_datatable_options(options) {
        return Object.assign(options, {
            checkboxColumn: true,
        });
    },
    onload: function (report) {
        setTimeout(() => {
            report.page.remove_inner_button("Set Chart")
        }, 500);


        report.page.add_inner_button(__('Set Cleaned'), function () {
            const selected = get_selected('room');
            if (!selected.length) {
                frappe.show_alert({
                    message: __('No Dirty rows selected.'),
                    indicator: 'orange'
                })
                return;
            }

            return frappe.call({
                method: "accommodation.accommodation.controller.set_cleaned",
                args: { rooms: selected },
                callback: function (r) {
                    frappe.query_report.refresh();
                }
            });
        });

    }
}


function get_selected() {
    const report = frappe.query_report;
    const indices = report.datatable.rowmanager.getCheckedRows();
    return indices
        .map(i => report.datatable.datamanager.getData(i))
        .filter(i => i["Status"] == 'Dirty')
        .map(i => i["Room"]);
}
