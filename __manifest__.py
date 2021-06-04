{
    'name': 'Iranian Employment Regulations',
    'version': '14.0.0.1.0.0+210125',
    'summary': 'Extra Information for employees based on Iran Rules.',
    'description': """
    Adding some data to Employee model based on Iran Rules.
    """,
    'author': "Kenevist Developers, Mostafa Abdi, Maryam Kia",
    'website': "www.kenevist.ir",
    'license': 'OPL-1',
    'category': 'Human Resources',
    'depends': ['hr',
                'l10n_ir_partner',
                'base_core'
                ],
    'data': ['data/employee_number_data.xml',
             'views/hr_employee_views.xml',
             'views/hr_ss_workplace_views.xml',
             'security/ir.model.access.csv', ],
    'auto_install': True,
    'application': False,
    'installable': True,
    'pre_init_hook': 'pre_init_hook',
}
