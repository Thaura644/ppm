class AsbuiltDocumentation(models.Model):
    _name = 'project_planning.asbuilt_documentation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    project_id = fields.Many2one('project.project', string="Related Project")
    crf_approved = fields.Boolean(related='project_id.crf_approved', string="CRF Approved", readonly=False)

    client_request_id = fields.Many2one('project_planning.client_request', string="Client Request")
    
