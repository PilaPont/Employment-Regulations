from odoo import api, fields, models


class ResourceResource(models.Model):
    _name = 'resource.resource'
    _inherit = ['resource.resource', 'editable.sequence.mixin']

    _sequence_field = 'employee_number'
    _sequence_date_field = "create_date"

    employee_number = fields.Char(string="Employee Number", copy=False)

    _sql_constraints = [
        ('unique_employee_number', 'UNIQUE(employee_number)',
         'Unfortunately this employee number is already used, please choose a unique one')
    ]

    @api.model
    def create(self, vals):
        res = super(ResourceResource, self).create(vals)
        if not vals.get('employee_number'):
            res._set_next_sequence()

        return res

    def _get_starting_sequence(self):
        """overwrite to produce 0000 sequence instead of 00000000 one
        """
        self.ensure_one()
        return "0000"

