from odoo import models, fields, api, http

class Acquisition(models.Model):
    _name = 'project_planning.acquisition'
    _description = 'Acquisition Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Acquisition Title', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    land_parcel = fields.Char(string='Land Parcel')
    owner_name = fields.Char(string='Owner Name')
    owner_contact = fields.Char(string='Owner Contact')
    status = fields.Selection([
        ('identification', 'Identification'),
        ('due_diligence', 'Due Diligence'),
        ('negotiation', 'Negotiation'),
        ('documentation', 'Documentation'),
        ('completed', 'Completed')
    ], string='Status', default='identification', track_visibility='onchange')
    document_ids = fields.Many2many('ir.attachment', string='Attached Documents')
    budget = fields.Float(string='Budget')
    expenses = fields.Float(string='Expenses')
    balance = fields.Float(string='Balance', compute='_compute_balance', store=True)
    client_request_id = fields.Many2one('project_planning.client_request', string="Client Request")
    report_file = fields.Binary(string='Report File')  # This field will hold the report file
    report_filename = fields.Char(string='Report Filename')  # This field will hold the name of the report file


    @api.depends('budget', 'expenses')
    def _compute_balance(self):
        for record in self:
            record.balance = record.budget - record.expenses

    @api.model
    def create(self, vals):
        res = super(Acquisition, self).create(vals)
        res.message_subscribe([res.project_id.user_id.partner_id.id])
        return res

    def _update_milestone(self, milestone_name):
        if self.project_id:
            milestone = self.env['project.milestone'].search([('name', '=', milestone_name), ('project_id', '=', self.project_id.id)])
            if milestone:
                milestone.write({'state': 'done'})

    def action_due_diligence(self):
        self.status = 'due_diligence'
        self.message_post(body=f"{self.name} is now in Due Diligence phase.")
        self._update_milestone('Due Diligence')

    def action_negotiation(self):
        self.status = 'negotiation'
        self.message_post(body=f"{self.name} is now in Negotiation phase.")
        self._update_milestone('Negotiation')

    def action_documentation(self):
        self.status = 'documentation'
        self.message_post(body=f"{self.name} is now in Documentation phase.")
        self._update_milestone('Documentation')

    def action_completed(self):
        self.status = 'completed'
        self.message_post(body=f"{self.name} has been completed.")
        self._update_milestone('Acquisition Completed')    
    
