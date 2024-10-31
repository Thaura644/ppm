{
    'name': 'Project Planning Management',
    'version': '1.0',
    'category': "Project Management",
    'summary': 'Manage client requests, acquisitions, desktop designs, field surveys, and wayleave applications.',
    'author': 'Metro Ict Limited',
    'website': 'https://www.odoo.co.ke',
    'depends': ['project'],
    'data': [


        'security/ir.model.access.csv',
        #'security/security_groups.xml',
        'data/sequence_data.xml',  # Load sequences before views
        #'data/project_stages_data.xml',  # Include the data file for stages
        'views/client_request_views.xml',  # Load views first
        'views/project_views.xml',
        'views/desktop_planning_views.xml',
        'views/acquisition_views.xml',
        'views/desktop_design_views.xml',
        'views/field_survey_views.xml',
        'views/wayleave_application_views.xml',

        # Other files and data rela



        'views/search_views.xml',  # Search views can come after all main views
          # Load actions after the views they reference
        'report/report_action.xml',

        
        'report/client_request_report.xml',
        'report/report_field_survey.xml',
        'views/report_views.xml',
        'views/action_views.xml',
        'views/menu_views.xml'  # Load menus last, after actions are defined
    ],
    'installable': True,
    'application': True,
}
