from odoo import models, fields, api, http
from odoo.exceptions import UserError
import base64
import io
import xlsxwriter
import csv

class Report(models.Model):
    _name = 'project_planning.report'
    _description = 'Project Planning Report'

    name = fields.Char(string='Report Name', required=True)
    report_type = fields.Selection([
        ('acquisition', 'Acquisition'),
        ('client_request', 'Client Request'),
        ('field_survey', 'Field Survey'),
        ('desktop_planning', 'Desktop Planning'),
        ('wayleave_application', 'Wayleave Application'),
        ('reporting', 'Reporting')
    ], string='Report Type', required=True)
    model_id = fields.Many2one('ir.model', string='Related Model', required=True, ondelete='cascade')
    report_data = fields.Text(string='Report Data')
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now)
    report_file = fields.Binary(string="Report File", readonly=True, attachment=True)
    report_filename = fields.Char(string="Report Filename")

    def action_preview_pdf_report(self):
        """Generate a PDF report for preview purposes."""
        return self._generate_report(file_format='pdf', preview=True)

    def generate_report(self, file_format='pdf'):
        """Generate a report in the specified format (PDF, XLSX, CSV)."""
        if file_format == 'pdf':
            return self._generate_report(file_format='pdf')
        elif file_format == 'xlsx':
            return self._generate_report(file_format='xlsx')
        elif file_format == 'csv':
            return self._generate_report(file_format='csv')
        else:
            raise UserError("Unsupported file format")

    def _generate_report(self, file_format='pdf', preview=False):
        # Logic for report generation by file format
        if file_format == 'pdf':
            action = self.env.ref('project_planning_management.client_request_report_action').report_action(self)
            return action if not preview else {'type': 'ir.actions.act_url', 'url': f'/web/content/{self.id}/report_file/{self.report_filename}', 'target': 'new'}
        elif file_format == 'xlsx':
            self._generate_excel_report()
        elif file_format == 'csv':
            self._generate_csv_report()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self.id}/report_file/{self.report_filename}?download=true',
            'target': 'self',
        }

    def _generate_excel_report(self):
        """Generate an Excel report."""
        file_data = io.BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        worksheet = workbook.add_worksheet()

        headers = ['Request Reference', 'Client', 'Company', 'Email', 'Request Date', 'Description', 'Status']
        worksheet.write_row(0, 0, headers)

        row = 1
        for rec in self:
            worksheet.write_row(row, 0, [
                rec.name, 
                rec.client_id.name if rec.client_id else '',
                rec.company_id.name if rec.company_id else '',
                rec.email_from or '',
                rec.request_date or '',
                rec.description or '',
                rec.state or '',
            ])
            row += 1

        workbook.close()
        file_data.seek(0)
        self.write({
            'report_file': base64.b64encode(file_data.read()),
            'report_filename': f'{self.name}.xlsx'
        })

    def _generate_csv_report(self):
        """Generate a CSV report."""
        file_data = io.StringIO()
        writer = csv.writer(file_data)

        headers = ['Request Reference', 'Client', 'Company', 'Email', 'Request Date', 'Description', 'Status']
        writer.writerow(headers)

        for rec in self:
            writer.writerow([
                rec.name,
                rec.client_id.name if rec.client_id else '',
                rec.company_id.name if rec.company_id else '',
                rec.email_from or '',
                rec.request_date or '',
                rec.description or '',
                rec.state or '',
            ])

        file_data.seek(0)
        self.write({
            'report_file': base64.b64encode(file_data.getvalue().encode()),
            'report_filename': f'{self.name}.csv'
        })

