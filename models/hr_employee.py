from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied

class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    departure_reason = fields.Selection(selection_add=[
        ('contraction_finished', 'Contraction finished'),
    ], string="Departure Reason", copy=False, tracking=True)

class HrSSWorkplace(models.Model):
    _name = 'hr.ss.workplace'

    name = fields.Integer(string='Code', required=True)
    display_name = fields.Char(compute="_compute_display_name")
    partner_id = fields.Many2one('res.partner', string='Workplace Details', required=True)
    employee_ids = fields.One2many(comodel_name='hr.employee', inverse_name='workplace_id')
    employees_count = fields.Integer(compute="_compute_employees_count")

    @api.depends('employee_ids')
    def _compute_employees_count(self):
        for workplace in self:
            workplace.employees_count = len(workplace.employee_ids)

    @api.depends('name', 'partner_id')
    def _compute_display_name(self):
        for workplace in self:
            workplace.display_name = '{} ({})'.format(workplace.partner_id.name, workplace.name)

    def unlink(self):
        for workplace in self:
            if workplace.employee_ids:
                raise AccessDenied(_('You cannot remove this workplace because some employees are members of it.'))
            else:
                return super(HrSSWorkplace, self).unlink()

    def action_show_workplace_employees(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.employee",
            "view_mode": "tree,form",
            "domain": [("workplace_id", "=", self.ids)],
            "name": "Employees in Workplace",
            "view_id" : False,
            "search_view_id" : self.env.ref("hr.view_employee_filter").id
        }

    def name_get(self):
        res = []
        for workplace in self:
            res.append((workplace.id, '{} ({})'.format(workplace.partner_id.name, workplace.name)))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain_name = ['|', ('name', 'ilike', name), ('partner_id.name', 'ilike', name)]
        recs = self.search(domain_name + args, limit=limit)
        return recs.name_get()


class HrEmployeeDependants(models.Model):
    _name = 'hr.employee.dependants'

    first_name = fields.Char()
    last_name = fields.Char()
    national_number = fields.Char()
    relation = fields.Selection(
        selection=[('spouse', 'Spouse'), ('child', 'Child'), ('father', 'Father'), ('mother', 'Mother'),
                   ('other', 'Other')],
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
    place_of_issue_birth_certificate_id = fields.Many2one(comodel_name='res.city')
    insurance_code = fields.Char()
    workplace_id = fields.Many2one(comodel_name='hr.ss.workplace')
    dependant_person_ids = fields.One2many(comodel_name='hr.employee.dependants', inverse_name='employee')
    children = fields.Integer(compute="_compute_child_count")
    departure_reason = fields.Selection(selection_add=[
        ('contraction_finished', 'Contraction finished'),
    ], string="Departure Reason", copy=False, tracking=True)
    start_work_date = fields.Date()

    @api.depends('dependant_person_ids')
    def _compute_child_count(self):
        for employee in self:
            employee.children = len(employee.dependant_person_ids.filtered(lambda x: x.relation == 'child'))

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        for employee in res:
            for person in employee.dependant_person_ids:
                self.env['res.partner'].check_personal_nid(person.national_number)
        return res

    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        for employee in self:
            for person in employee.dependant_person_ids:
                self.env['res.partner'].check_personal_nid(person.national_number)
        return res
