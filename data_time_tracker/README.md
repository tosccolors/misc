Data Time Tracker
================

This is a generic module which can be used on any Model for tracking values changes.

* Tracking is done for selected Model with selected Fields.
* And have different "Data Time Tracking > Tracking Configuration" with different Models (res.partner / account.account / product.template / etc).

Notes:
- Tracking can't be done for past date.
- Tracking is enabled only when configured field's value changes.
- Last tracking always consider as infinity.


Configuration
=============

* After the installation of this module, you need to add some entries in "Settings > Technical > Data Time Tracking > Tracking Configuration".
* Create a record in "Data Time Tracking > Tracking Configuration" by selecting Model (Ex: fleet.vehicle) and it's Field (Ex: driver_id.). Note: Only Many2one type field are allowed.

Usage (for user)
================

* Go to related Model (Ex: fleet.vehicle) and update values of any field specified in "Data Time Tracking > Tracking Configuration".
* You can find the changes tracked in configured model and relational model form view .


Usage (for module dev)
======================

* Add this data_time_tracker as a dependency in __manifest__.py

Below is example with Model (res.partner):

* Inherit data.track.thread:

.. code:: python

        For model:
            class FleetVehicle(models.Model):
                _name = 'fleet.vehicle'
                _inherit = ['fleet.vehicle', 'data.track.thread']

        For Co-model of Many2one field:
            class Partner(models.Model):
                _name = 'res.partner'
                _inherit = ['res.partner', 'data.track.thread']

        #Note: For new Model
        _inherit = 'data.track.thread'


.. Form view::xml


         # Add new tab for tracking changes
         For Model:
            <page name="time_faced" string="Time Data Tracker">
                <field name="model_track_ids" readonly="1" context="{'active_model':'fleet.vehicle', 'relation_ref':True}"/>
            </page>
            Note: For model 'relation_ref' should be False & 'active_model' must be model name.

         For Co-model of Many2one field:
            <page name="time_faced" string="Time Data Tracker">
                <field name="relation_track_ids" readonly="1" context="{'active_model':'res.partner', 'relation_ref':False}"/>
            </page>
            Note: For co-model of Many2one 'relation_ref' should be True & 'active_model' must be Co-model name.
