from odoo import models, fields, api

class ClientRequestLogic(models.AbstractModel):
    _name = 'project_planning.client_request.logic'
    _description = 'Client Request Logic'

    @api.model
    def compute_button_visibility(self, record):
        """
        Compute button visibility based on the state of the client request and related fields.
        """

        # Visibility logic for "Assign Planner" button
        record.show_assign_planner = (record.state == 'new' and record.planner_id)

        # Visibility logic for "Start Desktop Planning" button (after assigning planner)
        record.show_start_desktop_planning = (record.state == 'new' and record.planner_id)

        # Visibility logic for "Check Acquisition" button
        record.show_check_acquisition = (record.state == 'desktop_planning' and record.acquisition_required)

        # Visibility logic for "Start Acquisition" button (when acquisition is required and we're in the acquisition state)
        record.show_start_acquisition = (record.state == 'desktop_planning' and record.acquisition_required and record.acquisition_officer_id)###

        # Visibility logic for "Assign Surveyor" button
        record.show_assign_surveyor = (record.state == 'acquisition' and record.survey_required and record.surveyor_id)

        # Visibility logic for "Create BOQ" button (visible after survey completion)
        record.show_create_boq = True#(record.state == 'field_survey')# and record.boq_created)

        # Visibility logic for "Assign Designer" button
        #record.show_assign_designer = (record.state == 'field_survey' and record.boq_created and record.designer_id)
        record.show_assign_designer = True#(record.state == 'field_survey' and record.designer_id)




        # Visibility logic for "Share Design and Quote" button (visible after design phase)
        #record.show_share_design_quote = (record.state == 'desktop_design' record.design_completed)
        record.show_share_design_quote = (record.state == 'desktop_design' and record.design_completed)


        # Visibility logic for "Assign Wayleave Officer" button
        record.show_assign_wayleave_officer = (record.state == 'desktop_design' and record.wayleave_required and record.wayleave_officer_id)

        # Visibility logic for "Permit Granted" button (visible when permit is approved)
        record.show_permit_granted = (record.state == 'wayleave_application' and record.permit_granted)

        # Visibility logic for "Notify Rollout Team" button (after permit granted)
        record.show_notify_rollout_team = (record.state == 'wayleave_application' and record.permit_granted and record.permit_attachment)

        # Visibility logic for "Complete" button (visible when all steps are completed)
        record.show_complete = (record.state == 'completed')

        # Visibility logic for "Cancel" button (visible in all states except completed or cancelled)
        record.show_cancel = (record.state not in ['completed', 'cancelled'])


class ProjectPlanningClientRequest(models.Model):
    _inherit = 'project_planning.client_request'

    # Fields for controlling button visibility
    show_assign_planner = fields.Boolean(compute='_compute_button_visibility')
    show_start_desktop_planning = fields.Boolean(compute='_compute_button_visibility')
    show_check_acquisition = fields.Boolean(compute='_compute_button_visibility')
    show_start_acquisition = fields.Boolean(compute='_compute_button_visibility')
    show_assign_surveyor = fields.Boolean(compute='_compute_button_visibility')
    show_create_boq = fields.Boolean(compute='_compute_button_visibility')
    show_assign_designer = fields.Boolean(compute='_compute_button_visibility')
    show_share_design_quote = fields.Boolean(compute='_compute_button_visibility')
    show_assign_wayleave_officer = fields.Boolean(compute='_compute_button_visibility')
    show_permit_granted = fields.Boolean(compute='_compute_button_visibility')
    show_notify_rollout_team = fields.Boolean(compute='_compute_button_visibility')
    show_complete = fields.Boolean(compute='_compute_button_visibility')
    show_cancel = fields.Boolean(compute='_compute_button_visibility')

    # Additional Fields used for status tracking
    planner_id = fields.Many2one('res.users', string='Planner')
    acquisition_officer_id = fields.Many2one('res.users', string='Acquisition Officer')
    surveyor_id = fields.Many2one('res.users', string='Surveyor')
    boq_created = fields.Boolean(string='BOQ Created', default=False)
    designer_id = fields.Many2one('res.users', string='Designer')
    design_completed = fields.Boolean(string='Design Completed', default=False)
    wayleave_officer_id = fields.Many2one('res.users', string='Wayleave Officer')
    permit_granted = fields.Boolean(string='Permit Granted', default=False)
    permit_attachment = fields.Binary(string='Permit Attachment')
    wayleave_required = fields.Boolean(string='Wayleave Required', default=False)
    acquisition_required = fields.Boolean(string='Acquisition Required', default=False)
    survey_required = fields.Boolean(string='Survey Required', default=False)




#    @api.depends('state', 'planner_id', 'acquisition_required', 'acquisition_officer_id', 'surveyor_id',
#                 'boq_created', 'designer_id', 'design_completed', 'wayleave_required', 'wayleave_officer_id',
#                 'permit_granted', 'permit_attachment')
#    def _compute_button_visibility(self):
#        """
#        Compute the visibility of buttons based on the current state and other conditions.
#        """
#        for record in self:
#            # Call the logic from the abstract model to compute button visibility
#            self.env['project_planning.client_request.logic'].compute_button_visibility(record)



#####

    @api.depends('state', 'planner_id', 'acquisition_required', 'acquisition_officer_id', 'surveyor_id',
                 'boq_created', 'designer_id', 'design_completed', 'wayleave_required', 'wayleave_officer_id',
                 'permit_granted', 'permit_attachment')
    def _compute_button_visibility(self):
        for record in self:
            if not record.id:  # Handling new records
                record.show_assign_planner = False
                record.show_start_desktop_planning = False
                record.show_check_acquisition = False
                record.show_start_acquisition = False
                record.show_assign_surveyor = False
                record.show_create_boq = False
                record.show_assign_designer = False
                record.show_share_design_quote = False
                record.show_assign_wayleave_officer = False
                record.show_permit_granted = False
                record.show_notify_rollout_team = False
                record.show_complete = False
                record.show_cancel = False
            else:
                # Existing logic for setting button visibility
                record.show_assign_planner = (record.state == 'new' and bool(record.planner_id))
                record.show_start_desktop_planning = (record.state == 'new' and bool(record.planner_id))
                record.show_check_acquisition = (record.state == 'desktop_planning' and bool(record.acquisition_required))
                record.show_start_acquisition = (record.state == 'desktop_planning' and record.acquisition_required and bool(record.acquisition_officer_id))
                record.show_assign_surveyor = (record.state == 'acquisition' and record.survey_required and bool(record.surveyor_id))
                record.show_create_boq = True
                record.show_assign_designer = True
                record.show_share_design_quote = (record.state == 'desktop_design' and record.design_completed)
                record.show_assign_wayleave_officer = (record.state == 'desktop_design' and record.wayleave_required and bool(record.wayleave_officer_id))
                record.show_permit_granted = (record.state == 'wayleave_application' and record.permit_granted)
                record.show_notify_rollout_team = (record.state == 'wayleave_application' and record.permit_granted and record.permit_attachment)
                record.show_complete = (record.state == 'completed')
                record.show_cancel = (record.state not in ['completed', 'cancelled'])

