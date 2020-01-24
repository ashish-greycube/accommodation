const license_key = "Dada_Bhagwan_Foundation_Dada_Bhagwan_Foundation_1Devs28_September_2018__MTUzODA4OTIwMDAwMA==e40c526c93cbe82aaa30b417ac60a42b"

frappe.pages['mahatma-search'].on_page_load = function (wrapper) {
	const assets = [
		"assets/accommodation/js/lib/ag-grid-enterprise.min.js",
	];

	frappe.require(assets, () => {
		agGrid.LicenseManager.setLicenseKey(license_key);
		frappe.mahatma_search = new frappe.MahatmaSearch(wrapper);
	});

}


frappe.MahatmaSearch = Class.extend({

	init: function (parent) {
		frappe.ui.make_app_page({
			parent: parent,
			title: 'Mahatma Search',
			single_column: true
		});

		this.parent = parent;
		this.page = this.parent.page;

		this.add_buttons();
		this.make();
		this.make_grid();
		this.load_data();
	},

	make: function () {
		var me = this;
		var $container = $(`
		<div id="aggrid" class="ag-theme-balham" style="height:450px;margin-bottom:25px;"></div>`)
			.appendTo(this.page.main);
	},

	add_buttons: function () {
		var me = this;
		this.page.set_primary_action(__("Clear Filters"), function () {
			me.gridOptions.api.setFilterModel(null);
		});

	},

	load_data: function () {
		let me = this,
			api = this.gridOptions.api,
			model = api.getFilterModel();
		let args = {};
		for (let d of Object.keys(model)) {
			args[d] = model[d]['filter'];
		}
		frappe.call({
			method: "accommodation.accommodation.api.get_mahatma",
			args: args,
			callback: function (r) {
				if (!r.exc) {
					me.data = r.message;
					me.gridOptions.api.setRowData(me.data);
				}
			}
		});
	},

	cellDoubleClicked: function (params) {
		let data = params.data;
		let doc_name = frappe.model.make_new_doc_and_get_name('Accommodation Guest');
		let doc = locals['Accommodation Guest'][doc_name];
		Object.assign(doc, {
			"first_name": data.fname,
			"middle_name": data.mname,
			"last_name": data.lname,
			"mobile_no": data.mobile,
			"email": data.EMAIL,
			"dob": data.DOB,
			"mahatma_id": data.person_id,
			"address_1": data.ADDRESS1,
			"address_2": data.ADDRESS2,
			"city": data.CityName,
			"state": data.StateName,
			"country": data.CountryName,
		});
		frappe.set_route('Form', 'Accommodation Guest', doc_name);
	},

	make_grid: function () {
		var me = this;
		var gridDiv = document.querySelector('#aggrid');

		this.gridOptions = {
			enableColResize: true,
			showToolPanel: false,
			toolPanelSuppressSideButtons: true,
			enterMovesDownAfterEdit: true,
			onFilterChanged: function () {
				me.load_data();
			},
			defaultColDef: {
				suppressMenu: true,
				filterParams: { newRowsAction: 'keep' },
				floatingFilterComponentParams: {
					suppressFilterButton: true,
					debounceMs: 500
				}
			},
			floatingFilter: true,
			columnDefs: get_columnDefs(),
			// getContextMenuItems: getContextMenuItems,
			onRowDataChanged: function (params) { },
			components: {
				checkboxRenderer: function (params) {
					return params.value == 1 ? '<i class="fa fa-check"></i>' : ''
				},
				// customHeader: CustomHeader
			},
			onCellDoubleClicked: me.cellDoubleClicked,
			rowClassRules: {

			},
			onGridReady: function (params) {
			}
		};
		new agGrid.Grid(gridDiv, this.gridOptions);
		window.api = this.gridOptions.api;
	},

});

function getContextMenuItems(params) {
	let result = [{
		// custom item
		name: 'Mark Present',
		shortcut: 'Ctrl + P',
		action: function () {

		},
		// icon: '<img src="../images/skills/mac.png"/>'
	}];
	return result

}

function get_columnDefs() {
	columns = [
		{ headerName: "ICard", field: "person_id", width: 100, filter: 'agTextColumnFilter', },
		{ headerName: "FName", field: "fname", width: 180, filter: 'agTextColumnFilter', },
		{ headerName: "MName", field: "mname", width: 180, filter: 'agTextColumnFilter' },
		{ headerName: "LName", field: "lname", width: 180, filter: 'agTextColumnFilter' },
		{ headerName: "M/F", field: "gender", width: 65, filter: 'agTextColumnFilter' },
		{ headerName: "Age", field: "age", width: 65, filter: 'agTextColumnFilter' },
		{ headerName: "Mobile", field: "mobile", width: 180, filter: 'agTextColumnFilter' },
		{ headerName: "Addr 1", field: "ADDRESS1", width: 180, filter: 'agTextColumnFilter' },
		{ headerName: "Addr 2", field: "ADDRESS2", width: 180, filter: 'agTextColumnFilter' },
		{ headerName: "Addr 3", field: "ADDRESS3", width: 180, filter: 'agTextColumnFilter' },
		{ headerName: "Center", field: "CenterName", width: 110, filter: 'agTextColumnFilter' },
		{ headerName: "SubCenter", field: "SubCenterName", width: 110, filter: 'agTextColumnFilter' },
		{ headerName: "City", field: "CityName", width: 110, filter: 'agTextColumnFilter' },
	]
	return columns

	// {
	// 	headerName: "Loan Details",
	// 	children: [
	// 		{
	// 			headerName: "Posting Date",
	// 			field: "posting_date",
	// 			width: 90,
	// 			cellRenderer: function (params) {
	// 				return `<a href='#Form/Loan/${params.data.loan}'>${params.value}</a>`;
	// 			},
	// 		},
	// 		{ headerName: "Start Date", field: "repayment_start_date", width: 90, },
	// 		{ headerName: "Type", field: "loan_type", width: 90, },
	// 		{ headerName: "Amount", field: "loan_amount", width: 90, },
	// 		{ headerName: "Paid", field: "total_amount_paid", width: 90, },
	// 		{ headerName: "Balance", field: "balance_amount", width: 90, },
	// 		{ headerName: "Repayment", field: "repayment_method", width: 90, },

	// 	]
	// },
	// {
	// 	headerName: "Deduction", field: "deduction", width: 90,
	// 	editable: true,
	// 	cellEditor: 'agTextCellEditor',
	// 	cellStyle: { 'background-color': 'paleturquoise' },
	// 	onCellValueChanged: function (params) {

	// 	},
	// },

}
