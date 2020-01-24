frappe.provide('accommodation.ag_grid');

const ag_grid_license_key = "Dada_Bhagwan_Foundation_Dada_Bhagwan_Foundation_1Devs28_September_2018__MTUzODA4OTIwMDAwMA==e40c526c93cbe82aaa30b417ac60a42b"

const ag_grid_assets = [
    "assets/accommodation/js/lib/ag-grid-enterprise.min.js",
];

frappe.CustomReportBase = Class.extend({
    init: function (opts) {
        this.opts = opts || {};
        this.set_defaults();
        if (opts) {
            this.make();
        }
    },

    set_defaults: function () {
        // this.page_length = 20;
        // this.start = 0;
        // this.data = [];
    },

    make: function (opts) {
        if (opts) {
            this.opts = opts;
        }

        $.extend(this, this.opts);

        frappe.ui.make_app_page({
            parent: this.parent,
            title: this.title,
            single_column: true
        });

        this.report_name = this.report_name;
        this.page = this.parent.page;
        frappe.run_serially([
            () => this.setup_actions(),
            () => this.get_report_settings(),
            () => this.get_report_settings(),
            () => this.setup_filters(),
            () => this.make_grid(),
            () => this.refresh(),
        ]);

    },

    setup_actions: function () {
        var me = this;
        this.page.set_primary_action(__("Refresh"), function () {
            me.refresh();
        });
    },

    make_grid: function () {
        var me = this;
        var $container = $(`
		<div id="custom-grid" class="ag-theme-balham" style="height:450px;margin-bottom:25px;"></div>`)
            .appendTo(this.page.main);

        var gridDiv = document.querySelector('#custom-grid');

        this.gridOptions = {
            enableColResize: true,
            showToolPanel: false,
            toolPanelSuppressSideButtons: true,
            enterMovesDownAfterEdit: true,
            defaultColDef: {
                suppressMenu: true,
            },
            floatingFilter: true,
            // columnDefs: get_columnDefs(),
            // getContextMenuItems: getContextMenuItems,
            // onRowDataChanged: function (params) { },
            components: {
                checkboxRenderer: function (params) {
                    return params.value == 1 ? '<i class="fa fa-check"></i>' : ''
                },
                // customHeader: CustomHeader
            },
            rowClassRules: {},
            onGridReady: this.onGridReady
        };
        new agGrid.Grid(gridDiv, this.gridOptions);
    },

    refresh() {

        this.toggle_message(true);
        let filters = this.get_filter_values(true);
        filters = Object.assign(filters || {}, frappe.utils.get_query_params());

        // only one refresh at a time
        if (this.last_ajax) {
            this.last_ajax.abort();
        }

        return this.run_report(filters, this.gridOptions).then(r => {
            // console.log(r);

        });
    },

    clear_filters() {
        // this.page.clear_fields();
    },


    get_report_settings() {
        if (frappe.query_reports[this.report_name]) {
            this.report_settings = frappe.query_reports[this.report_name];
            return this._load_script;
        }

        this._load_script = (new Promise(resolve => frappe.call({
            method: 'frappe.desk.query_report.get_script',
            args: { report_name: this.report_name },
            callback: resolve
        }))).then(r => {
            frappe.dom.eval(r.message.script || '');
            return r;
        }).then(r => {
            return frappe.after_ajax(() => {
                this.report_settings = frappe.query_reports[this.report_name];
                this.report_settings.html_format = r.message.html_format;
            });
        });

        return this._load_script;
    },

    onGridReady(params) { console.log(params); },

    toggle_message(flag, message) { },

    get_filter_values(raise) {
        const mandatory = this.filters.filter(f => f.df.reqd);
        const missing_mandatory = mandatory.filter(f => !f.get_value());
        if (raise && missing_mandatory.length > 0) {
            let message = __('Please set filters');
            this.toggle_message(raise, message);
            throw "Filter missing";
        }

        const filters = this.filters
            .filter(f => f.get_value())
            .map(f => {
                var v = f.get_value();
                // hidden fields dont have $input
                if (f.df.hidden) v = f.value;
                if (v === '%') v = null;
                return {
                    [f.df.fieldname]: v
                };
            })
            .reduce((acc, f) => {
                Object.assign(acc, f);
                return acc;
            }, {});
        return filters;
    },

    setup_filters() {
        if (this.filters)
            this.clear_filters();

        const { filters = [] } = this.report_settings;

        this.filters = filters.map(df => {
            if (df.fieldtype === 'Break') return;

            let f = this.page.add_field(df);

            if (df.default) {
                f.set_input(df.default);
            }

            if (df.get_query) f.get_query = df.get_query;
            if (df.on_change) f.on_change = df.on_change;

            df.onchange = () => {
                if (this.previous_filters
                    && (JSON.stringify(this.previous_filters) == JSON.stringify(this.get_filter_values()))) {
                    // filter values have not changed
                    return;
                }
                this.previous_filters = this.get_filter_values();

                // clear previous_filters after 3 seconds, to allow refresh for new data
                setTimeout(() => this.previous_filters = null, 10000);

                if (f.on_change) {
                    f.on_change(this);
                } else {
                    if (this.prepared_report) {
                        this.reset_report_view();
                    }
                    else if (!this._no_refresh) {
                        this.refresh();
                    }
                }
            };

            f = Object.assign(f, df);

            return f;

        }).filter(Boolean);

        if (this.filters.length === 0) {
            // hide page form if no filters
            this.page.hide_form();
        } else {
            this.page.show_form();
        }
    },

});


// frappe.pages['payroll-loans'].on_page_load = function (wrapper) {
//     const assets = [
//         "assets/hr_payroll/js/ag-grid-enterprise.min.js",
//     ];

//     frappe.require(assets, () => {
//         agGrid.LicenseManager.setLicenseKey(license_key);
//         frappe.payroll_loans = new frappe.PayrollLoans({ parent: wrapper, report_name: "Payroll Loans", title: "Payroll Loans" });
//     });

// }

// frappe.PayrollLoans = class PayrollLoans extends frappe.CustomReportBase {
// 	run_report(filters) {
// 		return new Promise(resolve => {
// 			console.log(filters);
// 		});
// 	}
// };
