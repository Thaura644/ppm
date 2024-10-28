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

    def generate_report(self, file_format='pdf'):
        if file_format == 'pdf':
            return self._generate_pdf_report()
        elif file_format == 'xlsx':
            return self._generate_excel_report()
        elif file_format == 'csv':
            return self._generate_csv_report()
        else:
            raise UserError(_("Unsupported file format"))
        
    def generate_pdf_report(self):
        return self._generate_pdf_report()

    def generate_xlsx_report(self):
        return self._generate_excel_report()

    def generate_csv_report(self):
        return self._generate_csv_report()

    def _generate_pdf_report(self):
        return self.env.ref('project_planning_management.client_request_report_action').report_action(self)

    @http.route('/web/content/report', type='http', auth='public', website=True)
    def download_report(self, report_id):
        """Download the report file"""
        report = self.browse(int(report_id))
        if not report.report_file:
            return http.local_redirect('/web#id={}&model=project_planning.report'.format(report_id))

        # Prepare the response for file download
        response = http.request.make_response(
            base64.b64decode(report.report_file),
            headers={
                'Content-Type': 'application/octet-stream',
                'Content-Disposition': f'attachment; filename="{report.report_filename}"'
            }
        )
        return response
    
    def action_download_report(self):
        """Redirect to the report download route"""
        report_id = self.id  # Use self.id to get the current record's ID
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/report?report_id={report_id}',
            'target': 'self',  # Open in the same tab
        }

    def _generate_report_data(self):
        # Logic to gather data for the report
        return "Sample report data based on the acquisition model."
    
    
