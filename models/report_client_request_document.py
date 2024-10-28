from odoo import models

class ClientRequestReport(models.AbstractModel):
    _name = 'report.project_planning_management.client_request_report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['project_planning.client_request'].browse(docids)
        return {
            'docs': docs,
        }
