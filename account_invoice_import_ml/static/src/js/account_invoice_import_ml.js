// Copyright 2021 Hunki Enterprises BV
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
odoo.define('account_invoice_import_ml', function(require) {
    var common = require('web.form_common');
    var core = require('web.core');

    var FieldImportMlResult = common.AbstractField.extend(common.ReinitializeFieldMixin, {
        template: 'import_ml_result',
        start: function() {
            this.field_manager.on('load_record', this, this._import_ml_result_update_labels);
            this._import_ml_result_update_labels();
            return this._super.apply(this, arguments);
        },
        render_value: function() {
            this.renderElement();
        },
        _import_ml_result_update_labels: function() {
            var self = this,
                value = this.get_value();
            this.field_manager.$('.confidence-high').removeClass('confidence-high');
            this.field_manager.$('.confidence-medium').removeClass('confidence-medium');
            this.field_manager.$('.confidence-low').removeClass('confidence-low');
            _.each(
                this._import_ml_result_get_fields(), function(key) {
                    if(!self.field_manager.fields[key]) {
                        return;
                    }
                    var field = self.field_manager.fields[key],
                        confidence = value[key + '_confidence'],
                        $els = field.$el.add(field.$label);
                    $els.toggleClass('confidence-high', confidence >= .8);
                    $els.toggleClass('confidence-medium', confidence >= .4 && confidence < .8);
                    $els.toggleClass('confidence-low', confidence < .4);
                }
            );
        },
        _import_ml_result_get_fields: function() {
            return _.filter(
                _.keys(this.get_value()),
                function(key) { return !key.endsWith('_confidence') }
            );
        }
    })

    core.form_widget_registry.add('import_ml_result', FieldImportMlResult);
    return FieldImportMlResult;
});
