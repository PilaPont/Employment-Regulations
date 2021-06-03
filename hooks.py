from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    last_number = env['hr.employee'].search([], limit=1, order="employee_number desc").employee_number
    env.ref("hr_employee_iran_rules.employee_number_sequence").number_next = int(last_number) + 1



def pre_init_hook(cr):
    cr.execute(""" 
        ALTER TABLE hr_employee ADD COLUMN IF NOT EXISTS employee_number VARCHAR;
    """)
    cr.execute(
        """
        UPDATE hr_employee SET employee_number="id"  WHERE employee_number IS null OR employee_number='/';
    """)
