from odoo import models, fields, api

class DesktopPlanning(models.Model):
    _name = 'project_planning.desktop_planning'
    _description = 'Desktop Planning Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Planning Title', required=True)
    description = fields.Text(string='Description')
    document_ids = fields.Many2many('ir.attachment', string='Attached Documents')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('reviewed', 'Reviewed'),
        ('completed', 'Completed')
    ], string='Status', default='draft', track_visibility='onchange')

    project_id = fields.Many2one('project.project', string="Related Project")
    planning_approved = fields.Boolean(string="Planning Approved", default=False)
    client_request_id = fields.Many2one('project_planning.client_request', string="Client Request")

    @api.model
    def create(self, vals):
        res = super(DesktopPlanning, self).create(vals)
        res.message_subscribe([res.project_id.user_id.partner_id.id])
        return res

    def action_in_progress(self):
        self.write({'status': 'in_progress'})
        self.message_post(body="Desktop Planning is now in progress.")

    def action_reviewed(self):
        self.write({'status': 'reviewed'})
        self.message_post(body="Desktop Planning has been reviewed.")

    def action_completed(self):
        self.write({'status': 'completed'})
        self.message_post(body=f"{self.name} has been completed.")

        # Update the corresponding milestone status
        if self.project_id:
            milestone = self.env['project.milestone'].search([('name', '=', 'Desktop Planning'), ('project_id', '=', self.project_id.id)])
            if milestone:
                milestone.write({'state': 'done'})
