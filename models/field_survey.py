from odoo import models, fields, api, http, _
import io
import logging
from odoo.exceptions import UserError
import base64

_logger = logging.getLogger(__name__)

class FieldSurvey(models.Model):
    _name = 'project_planning.field_survey'
    _description = 'Field Survey Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Existing fields
    name = fields.Char(string='Survey Title', required=True)
    survey_date = fields.Date(string='Survey Date', required=True, default=fields.Date.today)
    description = fields.Text(string='Description')
    document_ids = fields.Many2many('ir.attachment', string='Attached Documents')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='pending', tracking=True)

    project_id = fields.Many2one('project.project', string="Related Project")
    surveyor_assigned = fields.Boolean(related='project_id.surveyor_assigned', string="Surveyor Assigned", readonly=False)
    client_request_id = fields.Many2one('project_planning.client_request', string="Client Request")

    # New fields from the Survey Report Form
    done_by = fields.Many2one('res.users', string='Done By')
    site_name = fields.Char(string='Site Name')
    location = fields.Char(string='Site Location')
    street = fields.Char(string='Street/Road/Avenue')
    building_floor_room = fields.Char(string='Building/Floor/Room')

    # Survey Details
    space_in_rack = fields.Selection([
        ('available', 'Available'),
        ('not_available', 'Not Available'),
    ], string='Space in Existing Rack')
    rack_required = fields.Boolean(string='Rack Required')
    rack_size = fields.Char(string='Rack Size (If required)')
    cabinet_288_fiber = fields.Integer(string='288 Fiber Cabinet Quantity')
    cabinet_144_fiber = fields.Integer(string='144 Fiber Cabinet Quantity')
    cabinet_576_fiber = fields.Integer(string='576 Fiber Cabinet Quantity')

    type_of_connection = fields.Selection([
        ('internet', 'Internet'),
        ('p2p', 'P2P'),
        ('gpon', 'GPON'),
    ], string='Type of Connection')
    existing_equipment = fields.Text(string='Existing Equipment')
    equipment_atb_2_port = fields.Integer(string='2 Port ATB Quantity')
    onus = fields.Integer(string='ONUs Quantity')
    fats_48_port = fields.Integer(string='FATS 48 Port Quantity')
    fats_24_port = fields.Integer(string='FATS 24 Port Quantity')
    fats_12_port = fields.Integer(string='FATS 12 Port Quantity')
    splitter = fields.Integer(string='Splitter (1:64) Quantity')
    trunking = fields.Integer(string='Trunking Quantity')
    
    # Report fields
    report_file = fields.Binary(string='Report File')  
    report_filename = fields.Char(string='Report Filename')  

    # Underground Materials
    fiber_optic_144_core = fields.Integer(string='Fiber Optic Cable (144 Core) Qty')
    fiber_optic_96_core = fields.Integer(string='Fiber Optic Cable (96 Core) Qty')
    fiber_optic_48_core = fields.Integer(string='Fiber Optic Cable (48 Core) Qty')
    fiber_optic_24_core = fields.Integer(string='Fiber Optic Cable (24 Core) Qty')
    fiber_optic_12_core = fields.Integer(string='Fiber Optic Cable (12 Core) Qty')
    fiber_optic_2_core_drop = fields.Integer(string='2 Core Drop Cable Qty')
    manholes_masonry = fields.Integer(string='Manholes (Masonry) Qty')
    manholes_precast = fields.Integer(string='Manholes (Precast) Qty')
    hdpe_32mm = fields.Integer(string='HDPE 32 mm Qty')
    hdpe_microduct = fields.Integer(string='HDPE Micro Duct Qty')
    warning_tape = fields.Integer(string='Warning Tape Qty')
    pvc_110mm = fields.Integer(string='PVC (110 mm) Qty')

    # Overhead Materials
    adss_foc_144_core = fields.Integer(string='ADSS FOC (144 Core) Qty')
    adss_foc_96_core = fields.Integer(string='ADSS FOC (96 Core) Qty')
    adss_foc_48_core = fields.Integer(string='ADSS FOC (48 Core) Qty')
    adss_foc_24_core = fields.Integer(string='ADSS FOC (24 Core) Qty')
    adss_foc_12_core = fields.Integer(string='ADSS FOC (12 Core) Qty')
    adss_foc_2_core_drop = fields.Integer(string='ADSS FOC 2 Core Drop Cable Qty')
    closures_144_port = fields.Integer(string='Closures (144 Port) Qty')
    closures_96_port = fields.Integer(string='Closures (96 Port) Qty')
    closures_48_port = fields.Integer(string='Closures (48 Port) Qty')
    closures_24_port = fields.Integer(string='Closures (24 Port) Qty')
    closures_12_port = fields.Integer(string='Closures (12 Port) Qty')

    # Civil Works
    road_crossing = fields.Char(string='Road Crossing')
    trenching = fields.Char(string='Trenching')
    tarmac_slabs = fields.Char(string='Tarmac Slabs')
    cabro = fields.Char(string='Cabro')
    cable_pulling = fields.Char(string='Cable Pulling')
    cabinet_mounting = fields.Char(string='Cabinet Mounting and Powering')
    concrete_cutting = fields.Char(string='Concrete Cutting')
    masonry_manholes = fields.Char(string='Construction of Masonry Manholes')
    laying_hdpes = fields.Char(string='Laying of HDPEs')
    precast_manholes = fields.Char(string='Installation of Precast Manholes')

    # Additional Information
    remarks = fields.Text(string='Remarks')

    @api.model
    def create(self, vals):
        res = super(FieldSurvey, self).create(vals)
        if res.project_id.user_id.partner_id:
            res.message_subscribe([res.project_id.user_id.partner_id.id])
        return res

    def action_in_progress(self):
        self.write({'status': 'in_progress'})
        self.message_post(body="Field Survey is now in progress.")

    def action_completed(self):
        self.write({'status': 'completed'})
        self.message_post(body=f"{self.name} has been completed.")

        if self.project_id:
            milestone = self.env['project.milestone'].search([
                ('name', '=', 'Field Survey'),
                ('project_id', '=', self.project_id.id)
            ])
            if milestone:
                milestone.write({'state': 'done'})

    def generate_pdf_report(self):
        return self._generate_pdf_report()
                
    def _generate_pdf_report(self):
        return self.env.ref('project_planning_management.action_field_survey_report').report_action(self)

    def action_generate_pdf_report(self):
        """Generate PDF report and attach it to the record"""
        report_action = self.env.ref('project_planning_management.action_field_survey_report')
        if not report_action:
            raise UserError(_('Report action not found!'))

    # Generate the report and get the action result
        report_result = report_action.report_action(self)

    # Log the result for debugging
        _logger.debug("Report result: %s", report_result)

    # The report_result is expected to be a dictionary, we need to get the PDF data
        if 'data' in report_result:
            pdf_data = report_result.get('data')
            if isinstance(pdf_data, bytes):
                self.write({
                    'report_file': base64.b64encode(pdf_data).decode(),
                    'report_filename': f"{self.name}_report.pdf"
                })
            else:
                raise UserError(_('Generated report data is not valid. Expected bytes but got: %s', type(pdf_data)))
        else:
            raise UserError(_('No report data returned.'))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Field Survey Report'),
            'res_model': 'project_planning.field_survey',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @http.route('/web/content/report', type='http', auth='public', website=True)
    def action_download_report(self):
        """Downloads the report file"""
        # Get the record by ID (ensure the method is properly authenticated)
        survey_id = self.request.params.get('id')
        survey = self.env['project_planning.field_survey'].browse(int(survey_id))

        if not survey.report_file:
            raise UserError(_('No report has been generated yet!'))

        # Generate the URL for downloading the report
        return http.local_redirect('/web/content/?model=project_planning.field_survey&id=%s&field=report_file&download=true&filename=%s' % (survey.id, survey.report_filename))
