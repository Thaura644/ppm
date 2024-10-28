from odoo import models, fields, api

class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], default='draft', string="Status", tracking=True)

    previous_milestone_id = fields.Many2one('project.milestone', string='Previous Milestone', help='The milestone that this milestone depends on.')
    
    @api.model
    def create(self, vals):
        # Avoid creating duplicate milestones
        existing_milestone = self.env['project.milestone'].search([
            ('name', '=', vals.get('name')),
            ('project_id', '=', vals.get('project_id'))
        ])
        if existing_milestone:
            return existing_milestone

        # Create the milestone
        milestone = super(ProjectMilestone, self).create(vals)

        # Automatically create associated tasks for the milestone
        milestone.create_tasks_for_milestone()

        return milestone















    def create_tasks_for_milestone(self):
        """Create tasks associated with each milestone based on the milestone's name."""
        task_obj = self.env['project.task']

        if self.name == 'Desktop Planning':
            tasks = [
                ('Initial Site Analysis', None),
                ('Network Design Draft', 'Initial Site Analysis'),
                ('Resource Allocation Planning', 'Network Design Draft'),
                ('Stakeholder Consultation', 'Resource Allocation Planning'),
                ('Final Desktop Planning Report', 'Stakeholder Consultation'),
            ]
        elif self.name == 'Acquisition':
            tasks = [
                ('Identify Land Parcels', None),
                ('Due Diligence', 'Identify Land Parcels'),
                ('Negotiation with Owners', 'Due Diligence'),
                ('Documentation Preparation', 'Negotiation with Owners'),
                ('Finalize Acquisition', 'Documentation Preparation'),
            ]
        elif self.name == 'Survey':
            tasks = [
                ('Prepare Survey Equipment', None),
                ('Conduct Field Survey', 'Prepare Survey Equipment'),
                ('Data Collection', 'Conduct Field Survey'),
                ('Data Analysis', 'Data Collection'),
                ('Survey Report Compilation', 'Data Analysis'),
            ]
        elif self.name == 'Detailed Project Design':
            tasks = [
                ('Develop Detailed Designs', None),
                ('Design Review Meeting', 'Develop Detailed Designs'),
                ('Incorporate Feedback', 'Design Review Meeting'),
                ('Finalize Designs', 'Incorporate Feedback'),
                ('Design Approval', 'Finalize Designs'),
            ]
        else:
            # Default tasks if milestone name doesn't match
            tasks = [
                ('General Task 1', None),
                ('General Task 2', 'General Task 1'),
            ]

        previous_task = None
        for task_name, dependency in tasks:
            task_vals = {
                'name': task_name,
                'project_id': self.project_id.id,
                'milestone_id': self.id,
                'user_id': self.project_id.user_id.id,
            }

            # Set dependencies within the tasks of the same milestone
            if dependency and previous_task:
                task_vals['dependent_ids'] = [(4, previous_task.id)]

            # Create the task
            task = task_obj.create(task_vals)
            previous_task = task


















    def create_monitoring_milestones(self, project):
        milestone_obj = self.env['project.milestone']

        # Final Quality Audit
        quality_audit_milestone = milestone_obj.create({
            'name': 'Final Quality Audits',
            'project_id': project.id,
            'state': 'draft',
        })
        
        # Final Client Sign-off
        client_signoff_milestone = milestone_obj.create({
            'name': 'Final Client Sign-off',
            'project_id': project.id,
            'state': 'draft',
            'previous_milestone_id': quality_audit_milestone.id,
        })

        # As-Built Documentation
        asbuilt_documentation_milestone = milestone_obj.create({
            'name': 'As-Built Documentation Submission',
            'project_id': project.id,
            'state': 'draft',
            'previous_milestone_id': client_signoff_milestone.id,
        })

        # Project Handover to Support
        handover_milestone = milestone_obj.create({
            'name': 'Project Handover to Support',
            'project_id': project.id,
            'state': 'draft',
            'previous_milestone_id': client_signoff_milestone.id,
        })

