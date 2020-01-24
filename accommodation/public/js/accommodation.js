frappe.provide('frappe.custom');

$.extend(frappe.custom, {
    add_grid_custom_button: function (grid, label, click) {
        if (!grid.header_buttons) {
            grid.header_buttons = $(`
        <div class="small form-clickable-section" style="border:0 solid #ffffff; border-bottom:1px solid #d1d8dd;">
            <div class="row">
                <div class="grid-header-buttons"></div>
            </div>
        </div>
        `).insertBefore(grid.wrapper.find(".grid-heading-row"));
        }


        var btn = grid.custom_buttons[label];
        if (!btn) {
            btn = $('<button class="btn btn-default btn-xs btn-custom pull-right">' + label + '</button>')
                .css('margin-right', '4px')
                .appendTo(grid.wrapper.find(".grid-header-buttons"))
                .on('click', click);
            grid.custom_buttons[label] = btn;
        } else {
            btn.removeClass('hidden');
        }
    }
});

$.extend(frappe.custom, {
    print_doc: function (doctype, docname, printit) {
        var me = this;
        var w = window.open(frappe.urllib.get_full_url("/printview?"
            + "doctype=" + encodeURIComponent(doctype)
            + "&name=" + encodeURIComponent(docname)
            + (printit ? "&trigger_print=1" : "")
            // + "&format=" + me.selected_format()
            // + "&no_letterhead=" + (me.with_letterhead() ? "0" : "1")
            // + (me.lang_code ? ("&_lang=" + me.lang_code) : "")
        ));
        if (!w) {
            frappe.msgprint(__("Please enable pop-ups")); return;
        }
    },

    // frm.add_custom_button(__('Print'), function () {
    //     let url = "/api/method/frappe.utils.print_format.download_pdf?doctype=Sales Invoice&name=SINV-00052&format=Sales Invoice SNS&no_letterhead=0&_lang=en";
    //     frappe.custom.download(url, {});
    // });
    
    download: function (url, data) {
        var formData = new FormData();
        $.each(data, (d) => {
            formData.append(d, data[d]);
        });
        var xhr = new XMLHttpRequest();
        xhr.open("POST", url);
        xhr.setRequestHeader("X-Frappe-CSRF-Token", frappe.csrf_token);
        xhr.responseType = "arraybuffer";

        xhr.onload = function (success) {
            if (this.status === 200) {
                var blob = new Blob([success.currentTarget.response], { type: "application/pdf" });
                var objectUrl = URL.createObjectURL(blob);

                //Open report in a new window
                window.open(objectUrl);
            }
        };
        xhr.send(formData);
    }
});


