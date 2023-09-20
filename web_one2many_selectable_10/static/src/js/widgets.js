odoo.define('web_one2many_selectable_10.form_widgets', function (require) {
	"use strict";

	var core = require('web.core');
	var form_common = require('web.form_common');
	var _t = core._t;
	var QWeb = core.qweb;
	var Model = require('web.Model');
	var FieldOne2Many = core.form_widget_registry.get('one2many');


	var One2ManySelectable = FieldOne2Many.extend({
		// my custom template for unique char field
		template: 'One2ManySelectable', 

		multi_selection: true,
		//button click
		events: {
			"click .cf_button_confirm": "action_selected_lines",
		},
		start: function() 
	    {
	    	this._super.apply(this, arguments);
			var self=this;			
		   },
		//passing ids to function
		action_selected_lines: function()
		{		
			var self=this;
			var selected_ids = self.get_selected_ids_one2many();
			if (selected_ids.length === 0)
			{
				this.do_warn(_t("You must choose at least one record."));
				return false;
			}
			var model_obj=new Model(this.dataset.model); 
			//you can hardcode model name as: new Model("module.model_name");
			//you can change the function name below
			/* you can use the python function to get the IDS
			      
				def bulk_verify(self):
        				for record in self:
            				print record
			*/
			model_obj.call('bulk_verify',[selected_ids],{context:self.dataset.context})
			.then(function(result){
			});
		},
		//collecting the selected IDS from one2manay list
		get_selected_ids_one2many: function ()
		{
			var ids =[];
			this.$el.find('td.o_list_record_selector input:checked')
					.closest('tr').each(function () {
						
						ids.push(parseInt($(this).context.dataset.id));
						console.log(ids);
			});
			return ids;
		},


	});
	// register unique widget, because Odoo does not know anything about it
	//you can use <field name="One2many_ids" widget="x2many_selectable"> for call this widget
	core.form_widget_registry.add('one2many_selectable', One2ManySelectable);
});
