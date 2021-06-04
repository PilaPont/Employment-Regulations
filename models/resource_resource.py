from odoo import api, fields, models


class ResourceResource(models.Model):
    _name = 'resource.resource'
    _inherit = ['resource.resource', 'sequence.mixin']

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
        import logging
        if 'employee_number' not in vals:
            logging.critical(res._set_next_sequence())

        return res

    def _get_starting_sequence(self):
        """Get a default sequence number.

        This function should be overriden by models heriting from this mixin
        This number will be incremented so you probably want to start the sequence at 0.

        :return: string to use as the default sequence to increment
        """
        self.ensure_one()
        return "0000"