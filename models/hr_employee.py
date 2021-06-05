from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied


class HRDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    departure_reason = fields.Selection(selection_add=[
        ('contraction_finished', 'Contraction finished'),
    ], string="Departure Reason", copy=False, tracking=True)


class HRSSWorkplace(models.Model):
    _name = 'hr.ss.workplace'
    _description = 'This model stores the workplaces of insurance.'

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
                return super(HRSSWorkplace, self).unlink()

    def action_show_workplace_employees(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.employee",
            "view_mode": "tree,form",
            "domain": [("workplace_id", "=", self.ids)],
            "name": "Employees in Workplace",
            "view_id": False,
            "search_view_id": self.env.ref("hr.view_employee_filter").id
        }

    def name_get(self):
        res = []
        for workplace in self:
            res.append((workplace.id, '{} ({})'.format(workplace.partner_id.name, workplace.name)))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain_name = ['|', ('name', operator, name), ('partner_id.name', operator, name)]
        recs = self.search(domain_name + args, limit=limit)
        return recs.name_get()


class HREmployeeDependants(models.Model):
    _name = 'hr.employee.dependants'
    _description = 'This model stores the employees dependants.'

    first_name = fields.Char()
    last_name = fields.Char()
    national_id_num = fields.Char()
    relation = fields.Selection(
        selection=[('spouse', 'Spouse'), ('child', 'Child'), ('father', 'Father'), ('mother', 'Mother'),
                   ('other', 'Other')],
        required=True, default='spouse')
    is_student = fields.Boolean()
    employee_id = fields.Many2one('hr.employee')


class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    employee_number = fields.Char(related='resource_id.employee_number', store=True)
    first_name = fields.Char(groups="hr.group_hr_user")
    last_name = fields.Char(groups="hr.group_hr_user")
    nick_name = fields.Char(groups="hr.group_hr_user")
    father_name = fields.Char(groups="hr.group_hr_user")
    national_id_card_image = fields.Binary(groups="hr.group_hr_user")
    identity_certificate_image = fields.Binary(groups="hr.group_hr_user")
    passport_image = fields.Binary(groups="hr.group_hr_user")
    educational_documents = fields.Binary(groups="hr.group_hr_user")
    identity_certificate_number = fields.Char(groups="hr.group_hr_user")
    identity_certificate_place_of_issue_id = fields.Many2one(comodel_name='res.city', groups="hr.group_hr_user")
    ssn = fields.Char(groups="hr.group_hr_user")
    workplace_id = fields.Many2one(comodel_name='hr.ss.workplace', groups="hr.group_hr_user")
    dependant_ids = fields.One2many(comodel_name='hr.employee.dependants', inverse_name='employee_id',
                                    groups="hr.group_hr_user")
    number_of_children = fields.Integer(compute="_compute_child_count", groups="hr.group_hr_user")
    departure_reason = fields.Selection(selection_add=[
        ('contraction_finished', 'Contraction finished'),
    ], tracking=True, groups="hr.group_hr_user")
    employment_date = fields.Date(groups="hr.group_hr_user")

    _sql_constraints = [
        ('uniq_employee_number', 'UNIQUE(employee_number)', 'This employee number is already taken.'),
    ]

    @api.depends('dependant_ids')
    def _compute_child_count(self):
        for employee in self:
            employee.number_of_children = len(employee.dependant_ids.filtered(lambda x: x.relation == 'child'))

    @api.model
    def create(self, vals):
        if 'first_name' and 'last_name' in vals:
            vals['name'] = vals.get('first_name') + ' ' + vals.get('last_name')
        elif 'name' in vals:
            name_split = vals['name'].split()
            if len(name_split) > 1:
                vals['first_name'] = name_split[0]
                vals['last_name'] = ' '.join(name_split[1:])
            else:
                vals['last_name'] = vals.get('name')

        res = super(HrEmployeePrivate, self).create(vals)
        for dependant in res.dependant_ids:
            self.env['res.partner'].check_personal_nid(dependant.national_id_num)
        return res

    def write(self, vals):
        for employee in self:
            if 'first_name' or 'last_name' in vals:
                vals['name'] = vals.get('first_name', employee.first_name or '') + ' ' + vals.get('last_name',
                                                                                            employee.last_name or '')
            elif 'name' in vals:
                name_split = vals['name'].split()
                if len(name_split) > 1:
                    vals['first_name'] = name_split[0]
                    vals['last_name'] = ' '.join(name_split[1:])
                else:
                    vals['last_name'] = vals.get('name')

        res = super(HrEmployeePrivate, self).write(vals)
        for employee in self:
            for person in employee.dependant_ids:
                self.env['res.partner'].check_personal_nid(person.national_id_num)
        return res

    @api.model
    def default_get(self, field_list):
        vals = super().default_get(field_list)
        if 'first_name' or 'last_name' in vals:
            vals['name'] = vals.get('first_name', '') + ' ' + vals.get('last_name', '')
        elif 'name' in vals:
            name_split = vals['name'].split()
            if len(name_split) > 1:
                vals['first_name'] = name_split[0]
                vals['last_name'] = ' '.join(name_split[1:])
            else:
                vals['last_name'] = vals.get('name')
        return vals


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    employee_number = fields.Char(readonly=True)
