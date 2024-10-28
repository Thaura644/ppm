from odoo import models, fields, api

class DesktopDesign(models.Model):
    _name = 'project_planning.desktop_design'
    _description = 'Desktop Design Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Design Title', required=True)
    description = fields.Text(string='Description')
    document_ids = fields.Many2many('ir.attachment', string='Attached Documents')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('completed', 'Completed')
    ], string='Status', default='draft', track_visibility='onchange')
    project_id = fields.Many2one('project.project', string="Related Project")
    design_approved = fields.Boolean(related='project_id.design_approved', string="Design Approved", readonly=False)
    client_request_id = fields.Many2one('project_planning.client_request', string="Client Request")

    @api.model
    def create(self, vals):
        res = super(DesktopDesign, self).create(vals)
        res.message_subscribe([res.project_id.user_id.partner_id.id])
        return res

    def _update_milestone(self, milestone_name):
        if self.project_id:
            milestone = self.env['project.milestone'].search([('name', '=', milestone_name), ('project_id', '=', self.project_id.id)])
            if milestone:
                milestone.write({'state': 'done'})

    def action_reviewed(self):
        self.write({'status': 'reviewed'})
        self.message_post(body=f"{self.name} has been reviewed.")
        self._update_milestone('Design Reviewed')

    def action_approved(self):
        self.write({'status': 'approved'})
        self.message_post(body=f"{self.name} has been approved.")
        self._update_milestone('Design Approved')

    def action_completed(self):
        self.write({'status': 'completed'})
        self.message_post(body=f"{self.name} has been completed.")
        self._update_milestone('Design Completed')
