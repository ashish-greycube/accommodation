frappe.provide('accommodation');

const license_key = "Dada_Bhagwan_Foundation_Dada_Bhagwan_Foundation_1Devs28_September_2018__MTUzODA4OTIwMDAwMA==e40c526c93cbe82aaa30b417ac60a42b"

// cell renderer class
function MedalCellRenderer() { }

// init method gets the details of the cell to be rendere
MedalCellRenderer.prototype.init = function (params) {
	if (!params.value)
		return;
	this.eGui = document.createElement('span');
	var text = '';
	if (["room", "room_type"].includes(params.colDef.field))
		text = params.value;
	else {
		let parts = params.value.split("/").slice(1);
		var text = `<a href="#Form/Accommodation Booking/${parts[0]}">${parts[1]}</a>`;
	}
	this.eGui.innerHTML = text;
};

MedalCellRenderer.prototype.getGui = function () {
	return this.eGui;
};


frappe.pages['frontdesk'].on_page_load = function (wrapper) {

	frappe.require(["assets/accommodation/js/lib/ag-grid-enterprise.min.js",], () => {
		agGrid.LicenseManager.setLicenseKey(license_key);
		accommodation.frontdesk = new accommodation.Frontdesk(wrapper);
	});

	// frappe.breadcrumbs.add("Frontdesk");
}


frappe.pages["frontdesk"].refresh = function () {
	accommodation.frontdesk && accommodation.frontdesk.refresh();
};


accommodation.Frontdesk = Class.extend({
	init: function (wrapper) {
		let me = this;
		me.setup(wrapper);
	},

	setup: function (wrapper) {
		let me = this;

		me.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Frontdesk',
			single_column: true
		});


		me.page.add_action_item(__("Refresh"), function () {
			me.refresh();
		});


		me.parent = wrapper;
		$(`<div id="aggrid" class="ag-theme-balham" style="height:500px;width:100%;margin-bottom:25px;"></div>`)
			.appendTo($(me.page.main));

		$(legend_html).appendTo(me.page.main);

		me.make_grid();
		me.set_up_filters();
		me.refresh();
	},


	refresh: function () {
		this.gridOptions.api.purgeInfiniteCache();
	},

	set_up_filters: function () {
		var me = this;
		me.filters = get_filters();
		for (let f of me.filters) {
			me.page.add_field({
				fieldtype: f.fieldtype,
				label: f.label,
				fieldname: f.fieldname,
				default: f.default,
				options: f.options || "",
				onchange: () => {
					accommodation.frontdesk &&
						accommodation.frontdesk.gridOptions.api.purgeInfiniteCache();
				}
			});
		}
	},

	make_grid: function () {
		var me = this;
		var gridDiv = document.querySelector('#aggrid');

		this.gridOptions = {
			enableColResize: true,
			rowModelType: 'infinite',
			// pagination: true,
			// paginationAutoPageSize: true,
			enableRangeSelection: true,
			suppressMultiRangeSelection: true,
			getContextMenuItems: getContextMenuItems,
			// domLayout: 'autoHeight',
			rowSelection: 'single',
			showToolPanel: false,
			defaultColDef: {
			},
			components: {
				'medalCellRenderer': MedalCellRenderer
			}
		};

		this.gridOptions.onCellClicked = function (params) {
			if (params.value && !["room_type", "room_name"].includes(params.colDef.field))
				;// me.show_summary(params.value, params.colDef.field);
		}

		new agGrid.Grid(gridDiv, me.gridOptions);
		this.gridOptions.api.setDatasource(ServerDataSource);
		this.gridOptions.api.addEventListener('rangeSelectionChanged', function (event) {
			// 
		});

	},

	show_summary: (val, field) => {
		frappe.db.get_value('Accommodation Booking', { name: val.split('|').slice(1) },
			"*", (r) => {
				let d = new frappe.ui.Dialog({
					title: __('<a href="desk#Form/Accommodation Booking/{0}">{1}</a>', [r.name, r.guest_name]),
					fields: [{ "fieldtype": "HTML", "fieldname": "summary_html" }]
				});
				let template = `
				<ul class="list-unstyled sidebar-menu">
					<li>Dates: {{ from_date }} to {{ to_date }}</li>
					<li>Room Package: {{ item }} </li>
					<li>Booking Status: {{ status }} </li>
					<li>Room: {{ room }} </li>
					<li>Room Status: {{ room_status }} </li>
				</ul>
				`;
				d.get_field("summary_html").$wrapper.append(frappe.render_template(template, r));
				d.show();
			});
	},
});

function create_booking(params) {

	let api = accommodation.frontdesk.gridOptions.columnApi;
	let range = accommodation.frontdesk.gridOptions.api.getRangeSelections()[0];

	let start_date = null;
	let end_date = null;
	let from_date = accommodation.frontdesk.page.fields_dict.from_date.value;
	let columns = api.getAllColumns();

	let startColId = range.columns[0].colId
	let endColId = (range.columns.slice(-1)[0]).colId

	$.map(columns, (col, idx) => {
		if (col.colId == startColId) {
			start_date = frappe.datetime.add_days(from_date, idx - 2);
		}
		if (col.colId == endColId) {
			end_date = frappe.datetime.add_days(from_date, idx - 2);
		}
	});

	let res = frappe.model.make_new_doc_and_get_name('Accommodation Booking');
	let doc = locals['Accommodation Booking'][res];
	Object.assign(doc, { "status": "Booked", "company": frappe.user_defaults.company });

	accommodation.frontdesk.gridOptions.api.forEachNode(function (rowNode, index) {
		if (index >= range.start.rowIndex && index <= range.end.rowIndex) {
			let item = frappe.model.add_child(doc, "Accommodation Booking Item", "items");
			item["check_in"] = start_date;
			item["check_out"] = end_date;
			item["room_type"] = rowNode.data.room_type;
			item["room"] = rowNode.data.room;
		}
	});

	frappe.set_route('Form', 'Accommodation Booking', res);
}

function createBookingItem(check_in, check_out, room_type, room_name) {

	return
}


function getContextMenuItems(params) {
	var row_data = params.node.data;
	var context = [];
	context.push({
		name: `Create booking`,
		action: function () {
			create_booking(row_data);
		}
	});

	return context;
}

function get_filters() {
	return [
		{
			"fieldname": "from_date",
			"label": __("From"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), 0),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), 7),
			"reqd": 1
		},
		// {
		// 	"fieldname": "view",
		// 	"label": __("View"),
		// 	"fieldtype": "Select",
		// 	"default": "Booking",
		// 	"options": ["Booking", "Checkout", "Cleaning"],
		// 	"reqd": 0
		// },

	]
}



var ServerDataSource = {
	getRows: function (params) {
		var me = accommodation.frontdesk;
		var filters = params.filterModel || {};

		Object.assign(filters, {
			from_date: me.page.fields_dict.from_date.value,
			to_date: me.page.fields_dict.to_date.value,
			// room_status: me.page.fields_dict.room_status.value || "",
		});

		frappe.call({
			method: "accommodation.accommodation.controller.get_frontdesk",
			args: filters,
			callback: r => {
				let data = r.message[1] || [];
				set_columns(r.message[0])
				params.successCallback(data, data.length)
			}
		});

	}
}

function set_columns(columns) {
	var api = accommodation.frontdesk.gridOptions.api;
	columnDefs = [];
	for (col of columns) {
		columnDefs.push({
			headerName: col.toUpperCase().replace("_", " "),
			field: col.replace(" ", "_").toLowerCase(),
			width: 110,
			filter: 'agTextColumnFilter',
			cellRenderer: 'medalCellRenderer',
			cellStyle: function (params) {
				if (!params.value) { return null; }
				else if (params.value.indexOf('check_out') > -1) {
					return { color: 'black', backgroundColor: 'lightblue' };
				} else if (params.value.indexOf('dirty') > -1) {
					return { color: 'white', backgroundColor: 'black' };
				} else if (params.value.indexOf('available') > -1) {
					return { color: 'black', backgroundColor: 'pink' };
				} else if (params.value.indexOf('maintenance') > -1) {
					return { color: 'black', backgroundColor: 'blue' };
				} else if (params.value.indexOf('booked') > -1) {
					return { color: 'black', backgroundColor: 'orange' };
				} else if (params.value.indexOf('checked_in') > -1) {
					return { color: 'white', backgroundColor: 'lightgreen' };
				} else if (params.value.indexOf('reserved') > -1) {
					return { color: 'black', backgroundColor: 'beige' };
				} else {
					return null;
				}
			},
		});
	}
	api.setColumnDefs(columnDefs);
}



const legend_html = `
<div class='my-legend' style='padding-left:30px;'>
<!-- <div class='legend-title'> Room Status Legend</div> -->
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li><span style='background:#008000;'></span>In House</li>
    <li><span style='background:#ffa500;'></span>Reserved</li>
    <li><span style='background:pink;'></span>Available</li>
    <li><span style='background:blue;'></span>Maintenance</li>
    <li><span style='background:lightblue;'></span>Check Out</li>
    <li><span style='background:black;'></span>Dirty</li>
  </ul>
</div>
<div class='legend-source'><a href="#link to source">&nbsp;</a></div> 
</div>

<style type='text/css'>
  .my-legend .legend-title {
	text-align: left;
    margin-bottom: 8px;
    font-weight: bold;
    font-size: 90%;
    }
  .my-legend .legend-scale ul {
    margin: 0;
    padding: 0;
    float: left;
    list-style: none;
    }
  .my-legend .legend-scale ul li {
    display: block;
    float: left;
    width: 75px;
    margin-bottom: 6px;
    text-align: center;
    font-size: 80%;
    list-style: none;
    }
  .my-legend ul.legend-labels li span {
    display: block;
    float: left;
    height: 15px;
    width: 75px;
    }
  .my-legend .legend-source {
    font-size: 70%;
    color: #999;
    clear: both;
    }
  .my-legend a {
    color: #777;
    }
</style>
`