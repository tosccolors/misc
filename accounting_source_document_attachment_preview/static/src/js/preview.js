odoo.define('accounting_source_document_attachment_preview', function (require) {
"use strict";

    var core = require('web.core');
    var FormView = require('web.FormView');
    var SideBar = require('web.Sidebar');
    var data = require('web.data');
    var session = require('web.session');
    var Model = require('web.Model');

    FormView.include({

        render_buttons: function($node) {

            // GET BUTTON REFERENCE
            this._super($node);
            if (this.$buttons) {
                var attachment_preview_btn = this.$buttons.find('.show_attachment_preview');
            }

            // PERFORM THE ACTION
            attachment_preview_btn.on('click', this.proxy('_onAttachmentPreview'));

        },
    });

    SideBar.include({

        do_attachement_update: function(dataset, model_id, args) {
            var self = this;
            this.dataset = dataset;
            this.model_id = model_id;
            if (args && args[0].error) {
                this.do_warn(_t('Uploading Error'), args[0].error);
            }
            if (!model_id) {
                this.on_attachments_loaded([]);
            }
            else {
                if (dataset.model == 'account.move') {
                    var dom = [['type', 'in', ['binary', 'url']], '|', ['res_model', '=', dataset.model], ['source_res_model', '=', dataset.model], '|', ['source_res_id', '=', model_id], ['res_id', '=', model_id] ];
                }else{
                    var dom = [['res_model', '=', dataset.model], ['res_id', '=', model_id], ['type', 'in', ['binary', 'url']]];

                }
                var ds = new data.DataSetSearch(this, 'ir.attachment', dataset.get_context(), dom);
                ds.read_slice(['name', 'url', 'type', 'create_uid', 'create_date', 'write_uid', 'write_date'], {}).done(this.on_attachments_loaded);
            }
        }

    });

});
