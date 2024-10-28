from odoo import models, fields, api, http
import base64, io, csv
from io import BytesIO

class Report(models.Model):
    _name = 'project_planning.report'
    _description = 'Project Planning Report'
    
    name = fields.Char(string='Report Name', required=True)
    report_type = fields.Selection([
        ('acquisition', 'Acquisition Report'),
        ('client_request', 'Client Request Report'),
        ('field_survey', 'Field Survey Report'),
    ], string='Report Type', required=True)
    report_data = fields.Text(string='Report Data')
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now)
    model_id = fields.Many2one('ir.model', string='Related Model')

    # File field to store the generated report for download
    report_file = fields.Binary(string="Report File", readonly=True, attachment=True)
    report_filename = fields.Char(string="Report Filename")

    
    def action_preview_pdf_report(self):
        """ Generate PDF report and prepare it for preview """
        # Ensure the report is generated
        file_data, filename = self._generate_pdf_report()

        # Update report fields to make it available for preview
        self.report_file = file_data
        self.report_filename = filename

        # Return the action to open the report preview in a new tab
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model={self._name}&id={self.id}&field=report_file&download=false&filename={filename}',
            'target': 'new',
        }
    
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

    def _generate_excel_report(self):
        # Initialize workbook
        file_data = io.BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        worksheet = workbook.add_worksheet()

        # Define columns and populate data
        headers = ['Request Reference', 'Client', 'Company', 'Email', 'Request Date', 'Description', 'Status']
        worksheet.write_row(0, 0, headers)
        
        row = 1
        for rec in self:
            worksheet.write_row(row, 0, [rec.name, rec.client_id.name, rec.company_id.name,
                                         rec.email_from, rec.request_date, rec.description, rec.state])
            row += 1
        
        workbook.close()
        file_data.seek(0)

        # Save as an attachment and return
        self.report_file = base64.b64encode(file_data.read())
        self.report_filename = 'Client_Request_Report.xlsx'
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self.id}/report_file/{self.report_filename}?download=true',
            'target': 'self',
        }

    def _generate_csv_report(self):
        file_data = io.StringIO()
        writer = csv.writer(file_data)

        # Define columns and populate data
        headers = ['Request Reference', 'Client', 'Company', 'Email', 'Request Date', 'Description', 'Status']
        writer.writerow(headers)

        for rec in self:
            writer.writerow([rec.name, rec.client_id.name, rec.company_id.name,
                             rec.email_from, rec.request_date, rec.description, rec.state])

        file_data.seek(0)
        self.report_file = base64.b64encode(file_data.getvalue().encode())
        self.report_filename = 'Client_Request_Report.csv'
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self.id}/report_file/{self.report_filename}?download=true',
            'target': 'self',
        }

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
