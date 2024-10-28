from odoo import models, fields, api
from odoo.exceptions import UserError

class WayleaveApplication(models.Model):
    _name = 'project_planning.wayleave_application'
    _description = 'Wayleave Application Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Wayleave Application Title', required=True)
    application_date = fields.Date(string='Application Date', required=True, default=fields.Date.today)
    description = fields.Text(string='Description')
    document_ids = fields.Many2many('ir.attachment', string='Attached Documents')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', track_visibility='onchange')

    project_id = fields.Many2one('project.project', string="Related Project")
    wayleave_required = fields.Boolean(related='project_id.wayleave_required', string="Wayleave Required", readonly=False)
    permit_granted = fields.Boolean(related='project_id.permit_granted', string="Permit Granted", readonly=False)
    client_request_id = fields.Many2one('project_planning.client_request', string="Client Request")

    @api.model
    def create(self, vals):
        res = super(WayleaveApplication, self).create(vals)
        res.message_subscribe([res.project_id.user_id.partner_id.id])
        return res

    def action_submitted(self):
        self.status = 'submitted'
        self.message_post(body=f"Wayleave Application '{self.name}' has been submitted.")
        # Update the corresponding milestone
        if self.project_id:
            milestone = self.env['project.milestone'].search([('name', '=', 'Wayleave Application'), ('project_id', '=', self.project_id.id)])
            if milestone:
                milestone.write({'state': 'progress'})

    def action_approved(self):
        self.status = 'approved'
        self.message_post(body=f"Wayleave Application '{self.name}' has been approved.")
        # Update the corresponding milestone
        if self.project_id:
            milestone = self.env['project.milestone'].search([('name', '=', 'Wayleave Application'), ('project_id', '=', self.project_id.id)])
            if milestone:
                milestone.write({'state': 'done'})

    def action_rejected(self):
        self.status = 'rejected'
        self.message_post(body=f"Wayleave Application '{self.name}' has been rejected.")
        # Optional: You can add logic to handle rejection within milestones if needed
