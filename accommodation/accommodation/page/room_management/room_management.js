frappe.pages['room-management'].on_page_load = function (wrapper) {
	// frappe.require(ag_grid_assets, () => {
	// 	agGrid.LicenseManager.setLicenseKey(ag_grid_license_key);
	// 	// frappe.accommodation_room_management = new frappe.AccommodationRoomManagement({ parent: wrapper, report_name: "Room Management", title: "Room Management" });
	// });

}

// frappe.AccommodationRoomManagement = class AccommodationRoomManagement extends frappe.CustomReportBase {

// 	onGridReady(params) {
// 		let page = frappe.accommodation_room_management.page;

// 		page.add_inner_button("Set Clean", () => {
// 			frappe.accommodation_room_management.set_cleaned(params.api)
// 		})

// 		page.add_inner_button("Set Clean", () => {
// 			frappe.accommodation_room_management.set_cleaned(params.api)
// 		})
// 	}

// 	set_cleaned(api) {
// 		let rows = api.getSelectedRows();
// 		let rooms = rows.filter(d => d.room_status === 'Dirty').map(d => d.name);
// 		frappe.call({
// 			method: 'accommodation.accommodation.controller.set_cleaned',
// 			args: { rooms: rooms },
// 			callback: function (r) {
// 				frappe.accommodation_room_management.refresh();
// 			}
// 		})
// 	}

// 	run_report(filters, gridOptions) {
// 		gridOptions.rowSelection = 'multiple';
// 		gridOptions.rowMultiSelectWithClick = true;

// 		var me = this;
// 		return new Promise(resolve => {
// 			frappe.call({
// 				method: 'accommodation.accommodation.controller.get_room_management',
// 				args: { filters: filters },
// 				callback: function (r) {
// 					const { columns, data } = r.message;
// 					me._setColumnDefs(columns);
// 					me._setRowData(data);
// 				}
// 			})
// 		});
// 	}

// 	_setColumnDefs() {
// 		let columns = [
// 			{ headerName: "Room Type", field: "room_type", width: 180, filter: 'agTextColumnFilter', },
// 			{ headerName: "Room", field: "name", width: 120, checkboxSelection: true, filter: 'agTextColumnFilter', },
// 			{ headerName: "Status", field: "room_status", width: 120, filter: 'agTextColumnFilter', },
// 		];
// 		this.gridOptions.api.setColumnDefs(columns);
// 	}

// 	_setRowData(data) {
// 		this.gridOptions.api
// 			.setRowData(data);
// 		this.gridOptions.api
// 			.setFilterModel({ room_status: { type: 'startsWith', filter: 'Dirty' } });
// 		this.gridOptions.api.onFilterChanged();
// 	}

// };
