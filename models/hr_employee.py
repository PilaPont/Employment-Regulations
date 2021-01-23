from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied

class HrSSWorkplace(models.Model):
    _name = 'hr.ss.workplace'

    name = fields.Char(string='Code')
    display_name = fields.Char(compute="_compute_display_name")
    partner_id = fields.Many2one('res.partner', string='Address')

    @api.depends('name', 'partner_id')
    def _compute_display_name(self):
        for workplace in self:
            workplace.display_name = '{} ({})'.format(workplace.partner_id.name, workplace.name)

    def unlink(self):
        for workplace in self:
            employees = self.env['hr.employee'].search([('insurance_workplace_id','=',workplace.id)])
            if employees:
                raise AccessDenied(_('You cannot remove this workplace because some employees are members of it.'))
            else:
                return super(HrSSWorkplace, self).unlink()

class HrEmployeeDependants(models.Model):
    _name = 'hr.employee.dependants'

    first_name = fields.Char()
    last_name = fields.Char()
    national_number = fields.Char()
    relation = fields.Selection(
        [('spouse', 'Spouse'), ('child', 'Child'), ('father', 'Father'), ('mother', 'Mother'), ('other', 'Other')],
        required=True, default='spouse')
    student = fields.Boolean()
    employee = fields.Many2one('hr.employee')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    first_name = fields.Char()
    last_name = fields.Char()
    nick_name = fields.Char()
    father_name = fields.Char()
    birth_certificate_number = fields.Char()
    place_of_issue_birth_certificate_id = fields.Many2one('res.city')
    insurance_code = fields.Char()
    insurance_workplace_id = fields.Many2one('hr.ss.workplace')
    dependant_person_ids = fields.One2many('hr.employee.dependants', 'employee')
    children = fields.Integer(compute="_compute_child_count")
    departure_reason = fields.Selection([
        ('fired', 'Fired'),
        ('resigned', 'Resigned'),
        ('retired', 'Retired'),
        ('end_of_contract', 'End of contract'),
    ], string="Departure Reason", groups="hr.group_hr_user", copy=False, tracking=True)
    start_work_date = fields.Datetime()

    @api.depends('dependant_person_ids')
    def _compute_child_count(self):
        for employee in self:
            employee.children = len(employee.dependant_person_ids.filtered(lambda x: x.relation == 'child'))

