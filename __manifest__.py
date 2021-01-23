{
    'name': 'HR Employee Iran Rules',
    'version': '14.0.0.1.0.0+210125',
    'summary': 'Extra Information for employees based on Iran Rules.',
    'description': """
    Adding some data to Employee model based on Iran Rules.
    """,
    'author': "Kenevist Developers, Mostafa Abdi",
    'website': "www.kenevist.ir",  # add /url/to/module_info if exist
    'license': 'OPL-1',  # for free addons use 'LGPL-3'
    'category': 'Human Resources',
    'depends': ['hr',
                'l10n_ir_partner',
                ],
    'data': ['views/hr_employee_views.xml',
             'views/hr_ss_workplace_views.xml',
             'security/ir.model.access.csv',],
    'auto_install': True,
    'application': False,
    'installable': True,
}