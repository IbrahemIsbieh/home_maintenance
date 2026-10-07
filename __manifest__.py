{
    'name': 'Home maintenance',
    'version': '19.0.1.0.0',
    'summary': ' Manage Home maintenance requests,visits and contracts',
    'category': 'services',
    'author': 'Ibrahem Issa',
    'license': 'LGPL-3',
    'depends': ['base','mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'data/home_request_sequence.xml',
        'data/mail_template.xml',
        'wizard/home_request_cancel_wizard_views.xml',
        'wizard/home_request_schedule_wizard_views.xml',
        'views/home_property_views.xml',
        'views/home_request_views.xml',
        'views/home_visit_views.xml',
        'views/home_slot_views.xml',
        'views/base_menu.xml',
        'views/dashboard_views.xml',
        'report/home_request_report.xml',


    ],
    'assets': {
        'web.assets_backend': [
            'home_maintenance/static/src/dashboard/dashboard.js',
            'home_maintenance/static/src/dashboard/dashboard.xml',
        ],
    },
    'application': True,
    'installable': True,
}