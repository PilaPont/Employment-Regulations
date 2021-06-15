from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    employee_without_first_last_name = env['hr.employee'].search(
        [('first_name', '=', False), ('last_name', '=', False)])
    for employee in employee_without_first_last_name:
        if employee.name:
            employee['first_name'], employee['last_name'] = employee.split_name(employee.name)


def pre_init_hook(cr):
    cr.execute(""" 
        ALTER TABLE resource_resource ADD COLUMN IF NOT EXISTS employee_number VARCHAR, ADD COLUMN IF NOT EXISTS sequence_number VARCHAR;
    """)
    cr.execute(
        """
        UPDATE resource_resource SET employee_number= LPAD(CAST (id AS text), 4, '0') , sequence_number=LPAD(CAST (id AS text), 4, '0') WHERE employee_number IS null OR employee_number='/';
    """)
