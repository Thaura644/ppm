import io, csv
from odoo import models, fields, api, http, _

class ProjectPlanningClientRequest(models.Model):
    _name = 'project_planning.client_request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Client Request for Survey'
    _order = 'request_date desc'

    # General fields for client request
    sequence = fields.Char(string='Sequence', required=True, copy=False, readonly=True, index=True, 
                           default=lambda self: _('New'))
    name = fields.Char(string='Request Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: self.env['ir.sequence'].next_by_code('project_planning.client_request'))
    client_id = fields.Many2one('res.partner', string='Client', required=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    email_from = fields.Char(string='Email', required=True)
    request_date = fields.Datetime(string='Request Date', default=fields.Datetime.now, required=True)
    description = fields.Text(string='Description')
    report_file = fields.Binary(string='Report File')  # This field will hold the report file
    report_filename = fields.Char(string='Report Filename')  # This field will hold the name of the report file
    





    # Fields for controlling button visibility
    #show_assign_planner = fields.Boolean(compute='_compute_button_visibility')
    show_assign_planner = fields.Boolean(default=True)
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



    # Assigned users for specific phases
    planner_id = fields.Many2one('res.users', string='Assigned Planner', track_visibility='onchange')
    acquisition_officer_id = fields.Many2one('res.users', string='Acquisition Officer')
    surveyor_id = fields.Many2one('res.users', string='Surveyor')
    designer_id = fields.Many2one('res.users', string='Designer')
    wayleave_officer_id = fields.Many2one('res.users', string='Wayleave Officer')

    # Related project data and control fields for various phases
    project_id = fields.Many2one('project.project', string="Related Project")
    acquisition_required = fields.Boolean(string="Acquisition Required")
    survey_required = fields.Boolean(string="Survey Required")
    surveyor_assigned = fields.Boolean(string="Surveyor Assigned", default=False)
    designer_assigned = fields.Boolean(string="Designer Assigned", default=False)
    design_completed = fields.Boolean(string='Design Completed', default=False)
    design_approved = fields.Boolean(string="Design Approved")
    wayleave_required = fields.Boolean(string="Wayleave Required")
    wayleave_officer_assigned = fields.Boolean(string="Wayleave Officer Assigned", default=False)
    permit_granted = fields.Boolean(string="Permit Granted")
    crf_approved = fields.Boolean(string="CRF Approved")
    boq_created = fields.Boolean(string='BOQ Created', default=False)
    permit_attachment = fields.Binary(string='Permit Attachment')

    # Status control for the request
    state = fields.Selection([
        ('new', 'New'),
        ('desktop_planning', 'Desktop Planning'),
        ('acquisition', 'Acquisition'),
        ('survey', 'Survey'),
        ('desktop_design', 'Desktop Design'),
        ('wayleave_application', 'Wayleave Application'),
        ('permit_granted', 'Permit Granted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='new', track_visibility='onchange')

    # Related document data and attachments
    documents = fields.Many2many('ir.attachment', string='Attached Documents')

    # Computed fields for counting related records
    acquisition_count = fields.Integer(string="Acquisition Count", compute='_compute_acquisition_count')
    survey_count = fields.Integer(string="Survey Count", compute='_compute_survey_count')
    desktop_design_count = fields.Integer(string="Desktop Design Count", compute='_compute_desktop_design_count')
    desktop_planning_count = fields.Integer(string="Desktop Planning Count", compute='_compute_desktop_planning_count')
    wayleave_count = fields.Integer(string="Wayleave Application Count", compute='_compute_wayleave_count')

    # One2many fields for related phases
    acquisition_ids = fields.One2many('project_planning.acquisition', 'client_request_id', string="Acquisitions")
    field_survey_ids = fields.One2many('project_planning.field_survey', 'client_request_id', string="Field Surveys")
    desktop_design_ids = fields.One2many('project_planning.desktop_design', 'client_request_id', string='Desktop Designs')
    desktop_planning_ids = fields.One2many('project_planning.desktop_planning', 'client_request_id', string='Desktop Plannings')
    wayleave_application_ids = fields.One2many('project_planning.wayleave_application', 'client_request_id', string='Wayleave Applications')






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
    @api.depends('state', 'planner_id', 'acquisition_required', 'acquisition_officer_id', 'surveyor_id',
                'boq_created', 'designer_id', 'design_completed', 'wayleave_required', 'wayleave_officer_id',
                'permit_granted', 'permit_attachment')
    

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
    def _compute_button_visibility(self):
        for record in self:
            if not record.id:  # Handling new records
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
                record.show_start_desktop_planning = (record.state == 'new' and bool(record.planner_id))
                record.show_check_acquisition = (record.state == 'desktop_planning' and bool(record.acquisition_required and record.acquisition_officer_id))
                record.show_start_acquisition = (record.state == 'desktop_planning' and record.acquisition_required and record.acquisition_officer_id)
                record.show_assign_surveyor = (record.state == 'acquisition' and record.survey_required and record.surveyor_id)
                record.show_create_boq = bool(record.boq_created)
                record.show_assign_designer = True  # This seems to always be True based on your logic
                record.show_share_design_quote = (record.state == 'desktop_design' and record.design_completed)
                record.show_assign_wayleave_officer = (record.state == 'desktop_design' and record.wayleave_required and record.wayleave_officer_id)
                record.show_permit_granted = (record.state == 'wayleave_application' and record.permit_granted)
                record.show_notify_rollout_team = (record.state == 'wayleave_application' and record.permit_granted and record.permit_attachment)
                record.show_complete = (record.state == 'completed')
                record.show_cancel = (record.state not in ['completed', 'cancelled'])

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('project_planning.client_request') or _('New')
        return super(ProjectPlanningClientRequest, self).create(vals)

    # ----------------------------------------
    # Computed Methods
    # ----------------------------------------
    def _compute_acquisition_count(self):
        for record in self:
            record.acquisition_count = self.env['project_planning.acquisition'].search_count([('client_request_id', '=', record.id)])

    def _compute_survey_count(self):
        for record in self:
            record.survey_count = self.env['project_planning.field_survey'].search_count([('client_request_id', '=', record.id)])

    def _compute_desktop_design_count(self):
        for record in self:
            record.desktop_design_count = self.env['project_planning.desktop_design'].search_count([('client_request_id', '=', record.id)])

    def _compute_desktop_planning_count(self):
        for record in self:
            record.desktop_planning_count = self.env['project_planning.desktop_planning'].search_count([('client_request_id', '=', record.id)])

    def _compute_wayleave_count(self):
        for record in self:
            record.wayleave_count = self.env['project_planning.wayleave_application'].search_count([('client_request_id', '=', record.id)])

    # ----------------------------------------
    # Button Actions and Workflow Methods
    # ----------------------------------------
    def assign_planner(self):
        self.ensure_one()

        if not self.planner_id:
            raise UserError("Please assign a planner.")

        if not self.project_id:
            project = self.env['project.project'].create({
                'name': f"{self.name} - Project",
                'partner_id': self.client_id.id,
                'company_id': self.company_id.id,
                'acquisition_required': self.acquisition_required,
                'survey_required': self.survey_required,
                'design_approved': self.design_approved,
                'wayleave_required': self.wayleave_required,
                'permit_granted': self.permit_granted,
                'crf_approved': self.crf_approved,
            })
            self.project_id = project.id

        desktop_planning = self.env['project_planning.desktop_planning'].create({
            'name': f"Desktop Planning for {self.name}",
            'client_request_id': self.id,
            'project_id': self.project_id.id,
        })

        self.message_subscribe([self.planner_id.partner_id.id])
        desktop_planning.message_subscribe([self.planner_id.partner_id.id])

        self.message_post(body=f"Planner {self.planner_id.name} assigned. Desktop planning started.")
        desktop_planning.message_post(body=f"Desktop Planning started by {self.planner_id.name}.")

        self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get('project_planning.client_request').id,
            'res_id': self.id,
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': 'Desktop Planning',
            'user_id': self.planner_id.id,
        })

        self.state = 'desktop_planning'
        self.create_milestones_for_project(self.project_id)

















###############################


    def create_milestones_for_project(self, project):
        milestone_obj = self.env['project.milestone']


        # Desktop Planning
        desktop_planning_milestone = milestone_obj.create({
            'name': 'Desktop Planning',
            'project_id': project.id,
            'state': 'draft',
        })
        previous_milestone = desktop_planning_milestone

        # Acquisition
        if project.acquisition_required:
            acquisition_milestone = milestone_obj.create({
                'name': 'Acquisition',
                'project_id': project.id,
                'state': 'draft',
                'previous_milestone_id': previous_milestone.id,
            })
            previous_milestone = acquisition_milestone

        # Survey
        if project.survey_required:
            survey_milestone = milestone_obj.create({
                'name': 'Survey',
                'project_id': project.id,
                'state': 'draft',
                'previous_milestone_id': previous_milestone.id,
            })
            previous_milestone = survey_milestone

        # Detailed Design
        desktop_design_milestone = milestone_obj.create({
            'name': 'Detailed Project Design',
            'project_id': project.id,
            'state': 'draft',
            'previous_milestone_id': previous_milestone.id,
        })
        previous_milestone = desktop_design_milestone

        # Risk Assessment
        risk_assessment_milestone = milestone_obj.create({
            'name': 'Risk Assessment & Mitigation',
            'project_id': project.id,
            'state': 'draft',
            'previous_milestone_id': previous_milestone.id,
        })
        previous_milestone = risk_assessment_milestone

        # Finalize Budget
        budget_finalization_milestone = milestone_obj.create({
            'name': 'Budget Finalization',
            'project_id': project.id,
            'state': 'draft',
            'previous_milestone_id': previous_milestone.id,
        })

        # Team Allocation
        team_allocation_milestone = milestone_obj.create({
            'name': 'Team Allocation',
            'project_id': project.id,
            'state': 'draft',
            'previous_milestone_id': previous_milestone.id,
        })

        # Continue as planned...

##############################################


    @api.model
    def transition_to_next_stage(self, record):
        # Ensure no milestones are left incomplete before moving to the next stage
        incomplete_milestones = self.env['project.milestone'].search([
            ('project_id', '=', record.project_id.id),
            ('state', '!=', 'done')
        ])
        
        if incomplete_milestones:
            raise UserError('All milestones must be completed before moving to the next stage.')

        # Move to the next state
        record.state = 'next_stage'  # Replace with the actual next state

        # Post message for state change
        record.message_post(body=f"Project transitioned to {record.state} stage.")



    def client_signoff_on_milestone(self):
        self.ensure_one()
        if not self.client_id:
            raise UserError("Client information is missing for sign-off.")
        
        # Mark milestone as signed off
        signoff_milestone = self.env['project.milestone'].search([
            ('project_id', '=', self.project_id.id),
            ('name', '=', 'Final Client Sign-off')
        ])
        signoff_milestone.write({'state': 'done'})
        self.message_post(body="Client has signed off on the milestone.")
















    def start_acquisition(self):
        if not self.acquisition_officer_id:
            raise UserError("Please assign an Acquisition Officer.")
        if not self.acquisition_required:
            raise UserError("Acquisition is not required for this request.")

        acquisition = self.env['project_planning.acquisition'].create({
            'name': f"Acquisition for {self.name}",
            'client_request_id': self.id,
            'project_id': self.project_id.id,
        })

        self.message_subscribe([self.acquisition_officer_id.partner_id.id])
        acquisition.message_subscribe([self.acquisition_officer_id.partner_id.id])

        self.message_post(body=f"Acquisition Officer {self.acquisition_officer_id.name} assigned. Acquisition phase started.")
        acquisition.message_post(body=f"Acquisition started by {self.acquisition_officer_id.name}.")

        self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get('project_planning.client_request').id,
            'res_id': self.id,
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': 'Acquisition',
            'user_id': self.acquisition_officer_id.id,
        })

        self.state = 'acquisition'

    def start_survey(self):
        if not self.surveyor_id:
            raise UserError("Please assign a surveyor.")

        survey = self.env['project_planning.field_survey'].create({
            'name': f"Field Survey for {self.name}",
            'client_request_id': self.id,
            'project_id': self.project_id.id,
        })

        self.message_subscribe([self.surveyor_id.partner_id.id])
        survey.message_subscribe([self.surveyor_id.partner_id.id])

        self.message_post(body=f"Surveyor {self.surveyor_id.name} assigned. Survey phase started.")
        survey.message_post(body=f"Survey started by {self.surveyor_id.name}.")

        self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get('project_planning.client_request').id,
            'res_id': self.id,
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': 'Field Survey',
            'user_id': self.surveyor_id.id,
        })

        self.state = 'survey'
        self.surveyor_assigned = True

    def create_boq(self):
        self.ensure_one()
        if self.state != 'survey':
            raise UserError("The request must be in the Survey phase to create BOQ.")

        survey_lines = self.env['project_planning.field_survey.line'].search([('client_request_id', '=', self.id)])
        if not survey_lines:
            raise UserError("No survey items available to create the BOQ.")

        sale_order = self.env['sale.order'].create({
            'partner_id': self.client_id.id,
            'client_request_id': self.id,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.quantity,
                'price_unit': line.price_unit,
            }) for line in survey_lines],
        })

        self.message_post(body=f"BOQ created from Survey and Sales Order {sale_order.name} generated.")
        self.state = 'desktop_design'

    def assign_designer(self):
        self.ensure_one()

        if not self.designer_id:
            raise UserError("Please assign a Designer before proceeding.")

        incomplete_surveys = self.env['project_planning.field_survey'].search([('client_request_id', '=', self.id), 
                                                                              ('status', 'not in', ['completed', 'canceled'])])
        if incomplete_surveys:
            raise UserError("All related surveys must be completed or canceled before proceeding.")

        desktop_design = self.env['project_planning.desktop_design'].create({
            'name': f"Desktop Design for {self.name}",
            'client_request_id': self.id,
            'project_id': self.project_id.id,
        })

        self.message_subscribe([self.designer_id.partner_id.id])
        desktop_design.message_subscribe([self.designer_id.partner_id.id])

        self.message_post(body=f"Designer {self.designer_id.name} assigned. Desktop design phase started.")
        desktop_design.message_post(body=f"Desktop Design started by {self.designer_id.name}.")

        self._send_designer_notification()

        self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get('project_planning.client_request').id,
            'res_id': self.id,
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': 'Desktop Design',
            'user_id': self.designer_id.id,
        })

        self.state = 'desktop_design'
        self.designer_assigned = True

    def _send_designer_notification(self):
        email_from = self.env.user.email or 'noreply@yourcompany.com'
        email_to = self.designer_id.email

        if not email_to:
            raise UserError(f"Assigned designer {self.designer_id.name} does not have an email address.")

        subject = f"New Design Assignment: {self.name}"
        body_html = f"""
            <p>Dear {self.designer_id.name},</p>
            <p>You have been assigned as the designer for the project <b>{self.name}</b>.</p>
            <p>Please proceed with the desktop design phase. You can find more details in the project management system.</p>
            <p>Best Regards,</p>
            <p>{self.env.user.name}</p>
        """

        mail_values = {
            'subject': subject,
            'body_html': body_html,
            'email_from': email_from,
            'email_to': email_to,
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()

    def assign_wayleave_officer(self):
        self.ensure_one()

        if not self.wayleave_required:
            raise UserError("Wayleave is not required for this request.")

        if not self.wayleave_officer_id:
            raise UserError("Please assign a Wayleave Officer before proceeding.")

        incomplete_design_docs = self.desktop_design_ids.filtered(lambda d: d.status not in ['completed', 'canceled'])
        if incomplete_design_docs:
            raise UserError("Ensure all desktop design documents are completed or canceled before assigning a Wayleave Officer.")

        wayleave_application = self.env['project_planning.wayleave_application'].create({
            'name': f"Wayleave Application for {self.name}",
            'client_request_id': self.id,
            'project_id': self.project_id.id,
        })

        self.message_subscribe([self.wayleave_officer_id.partner_id.id])
        wayleave_application.message_subscribe([self.wayleave_officer_id.partner_id.id])

        message_body = f"Wayleave Officer {self.wayleave_officer_id.name} assigned. Wayleave Application phase started."
        self.message_post(body=message_body)
        wayleave_application.message_post(body=message_body)

        self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get('project_planning.client_request').id,
            'res_id': self.id,
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': 'Wayleave Application',
            'user_id': self.wayleave_officer_id.id,
        })

        self.state = 'wayleave_application'
        self.wayleave_officer_assigned = True

        self._send_wayleave_officer_notification()

    def _send_wayleave_officer_notification(self):
        email_from = self.env.user.email or 'noreply@yourcompany.com'
        email_to = self.wayleave_officer_id.email

        if not email_to:
            raise UserError(f"Assigned wayleave officer {self.wayleave_officer_id.name} does not have an email address.")

        subject = f"New Wayleave Assignment: {self.name}"
        body_html = f"""
            <p>Dear {self.wayleave_officer_id.name},</p>
            <p>You have been assigned as the wayleave officer for the project <b>{self.name}</b>.</p>
            <p>Please proceed with the wayleave application phase. You can find more details in the project management system.</p>
            <p>Best Regards,</p>
            <p>{self.env.user.name}</p>
        """

        mail_values = {
            'subject': subject,
            'body_html': body_html,
            'email_from': email_from,
            'email_to': email_to,
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()

    def permit_granted(self):
        self.ensure_one()

        incomplete_wayleave_apps = self.wayleave_application_ids.filtered(lambda w: w.status not in ['completed', 'canceled'])
        if incomplete_wayleave_apps:
            raise UserError("Ensure all Wayleave applications are completed or canceled before granting the permit.")

        if not self.permit_granted:
            raise UserError("Please mark the 'Permit Granted' checkbox before proceeding.")

        required_files = ['Permit', 'LLD']
        attached_files = self.documents.mapped('datas_fname')
        for required in required_files:
            if not any(required in f for f in attached_files):
                raise UserError(f"{required} file must be attached before notifying the Rollout Team.")

        self._notify_rollout_team()
        self.state = 'completed'

        if self.project_id:
            self.project_id.stage_id = self.env.ref('project.project_stage_rollout').id

        self.message_post(body="Permit has been granted and the request is now in the Completed stage. The Rollout Team has been notified.")

    def _notify_rollout_team(self):
        email_from = self.env.user.email or 'noreply@yourcompany.com'
        rollout_team_email = 'rolloutteam@yourcompany.com'

        lld_document = self.documents.filtered(lambda d: 'LLD' in d.datas_fname)
        permit_document = self.documents.filtered(lambda d: 'Permit' in d.datas_fname)

        subject = f"Permit Granted and Rollout Notification for Project: {self.name}"
        body_html = f"""
            <p>Dear Rollout Team,</p>
            <p>The permit has been granted for the project <b>{self.name}</b>.</p>
            <p>Please find attached the Low-Level Design (LLD) and the Permit for your reference.</p>
            <p>Best Regards,</p>
            <p>{self.env.user.name}</p>
        """

        mail_values = {
            'subject': subject,
            'body_html': body_html,
            'email_from': email_from,
            'email_to': rollout_team_email,
            'attachment_ids': [(4, lld_document.id), (4, permit_document.id)],
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()

    # ----------------------------------------
    # Actions to view related records
    # ----------------------------------------
    def action_view_desktop_planning(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Desktop Plannings',
            'view_mode': 'tree,form',
            'res_model': 'project_planning.desktop_planning',
            'domain': [('client_request_id', '=', self.id)],
            'context': dict(self._context),
        }

    def action_view_acquisition(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Acquisitions',
            'view_mode': 'tree,form',
            'res_model': 'project_planning.acquisition',
            'domain': [('client_request_id', '=', self.id)],
            'context': dict(self._context),
        }

    def action_view_survey(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Surveys',
            'view_mode': 'tree,form',
            'res_model': 'project_planning.field_survey',
            'domain': [('client_request_id', '=', self.id)],
            'context': dict(self._context),
        }

    def action_view_desktop_design(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Desktop Designs',
            'view_mode': 'tree,form',
            'res_model': 'project_planning.desktop_design',
            'domain': [('client_request_id', '=', self.id)],
            'context': dict(self._context),
        }

    def action_view_wayleave_application(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Wayleave Applications',
            'view_mode': 'tree,form',
            'res_model': 'project_planning.wayleave_application',
            'domain': [('client_request_id', '=', self.id)],
            'context': dict(self._context),
        }
    
    def action_generate_report(self):
        # Logic to generate the report for client requests
        report_data = self._generate_report_data()
        report_name = f"Report for {self.name}"

        self.env['project_planning.report'].create({
            'name': report_name,
            'report_type': 'client_request',
            'report_data': report_data,
            'model_id': self.env['ir.model'].search([('model', '=', 'project_planning.client_request')], limit=1).id,
        })

    def _generate_report_data(self):
        # Replace with logic specific to client request reports
        return "Sample client request report data."
    
    







