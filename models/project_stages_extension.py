# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProjectStageExtension(models.Model):
    _inherit = 'project.project'

    # Extend project stages with the four main phases
    stage = fields.Selection([
        ('initiation', 'Initiation'),
        ('planning', 'Planning'),
        ('execution', 'Execution'),
        ('monitoring', 'Monitoring')
    ], string='Project Stage', default='initiation')

    def move_tasks_to_stage(self):
        """
        Automatically assign tasks to relevant stages when the project moves to the next phase.
        """
        for task in self.task_ids:
            if self.stage == 'initiation':
                task.stage_id = self.env.ref('your_module.project_stage_initiation').id
            elif self.stage == 'planning':
                task.stage_id = self.env.ref('your_module.project_stage_planning').id
            elif self.stage == 'execution':
                task.stage_id = self.env.ref('your_module.project_stage_execution').id
            elif self.stage == 'monitoring':
                task.stage_id = self.env.ref('your_module.project_stage_monitoring').id

    @api.onchange('stage')
    def _onchange_stage(self):
        """
        When the project stage changes, trigger the task assignment to the relevant stage.
        """
        self.move_tasks_to_stage()
