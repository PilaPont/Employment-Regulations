from odoo import api, fields, models


class ResourceCalendar(models.Model):
    _inherit = 'resource.resource'

    employee_number = fields.Char(string="Employee Number", default='/', copy=False)

    _sql_constraints = [
        ('unique_employee_number', 'UNIQUE(employee_number)',
         'Unfortunately this employee number is already used, please choose a unique one')
    ]