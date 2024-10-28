from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    acquisition_required = fields.Boolean(string="Acquisition Required", default=False)
    survey_required = fields.Boolean(string="Survey Required")
    surveyor_assigned = fields.Boolean(string="Surveyor Assigned", default=False)
    design_approved = fields.Boolean(string="Design Approved", default=False)
    wayleave_required = fields.Boolean(string="Wayleave Required", default=False)
    permit_granted = fields.Boolean(string="Permit Granted", default=False)
    crf_approved = fields.Boolean(string="CRF Approved", default=False)

    @api.model
    def create(self, vals):
        project = super(ProjectProject, self).create(vals)

        # Automatically create milestones based on project requirements
        milestone_obj = self.env['project.milestone']
        if project.acquisition_required:
            milestone_obj.create({
                'name': 'Acquisition',
                'project_id': project.id,
                'state': 'draft',
            })
        if project.survey_required:
            milestone_obj.create({
                'name': 'Survey',
                'project_id': project.id,
                'state': 'draft',
            })
        if project.wayleave_required:
            milestone_obj.create({
                'name': 'Wayleave',
                'project_id': project.id,
                'state': 'draft',
            })
        if project.design_approved:
            milestone_obj.create({
                'name': 'Design Approval',
                'project_id': project.id,
                'state': 'draft',
            })

        return project


class ProjectTask(models.Model):
    _inherit = 'project.task'

    milestone_id = fields.Many2one('project.milestone', string="Milestone")

    # Adding user_id field if it doesn't exist
    user_id = fields.Many2one('res.users', string="Assigned to")
