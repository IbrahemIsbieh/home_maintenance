from odoo import models, fields, api
from odoo.exceptions import ValidationError
class HomeRequest(models.Model):
    _name = 'home.request'
    _description = 'Maintenance Request'
    _inherit = ['mail.thread']
    _order = 'priority desc,id desc'

    name = fields.Char(string='Request Name', required=True, readonly=True, default='New',copy=False)
    title = fields.Char(string='Request Title',required=True)
    property_id = fields.Many2one('home.property', string='Property',required=True)
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 related='property_id.partner_id', store=True)


    technician_id  = fields.Many2one('res.users', string='Technical')

    description = fields.Char(string='Description')
    priority = fields.Selection([
        ('0','Low'),
        ('1','Normal'),
        ('2','High'),
        ('3','Urgent'), ], string='Priority',default='1')
    state = fields.Selection([
        ('new', 'New'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'), ], string='Status',default='new',readonly=True,tracking=True)
    cancel_reason = fields.Text(string='Cancellation Reason', readonly=True, copy=False)
    visit_ids = fields.One2many('home.visit', 'request_id', string='Visits')
    slot_id = fields.Many2one('home.slot', string='Appointment Slot',
                              copy=False, ondelete='restrict', tracking=True,
                              domain="[('state', '=', 'free')]")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('home.request') or 'New'
        return super().create(vals_list)

    def action_schedule(self):
        self.write({'state': 'scheduled'})

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset(self):
        self.write({'state': 'new','cancel_reason': False})

    @api.constrains('slot_id', 'state')
    def _check_slot_free(self):
        for rec in self:
            if rec.slot_id and rec.state != 'cancelled':
                others = self.sudo().search_count([
                    ('slot_id', '=', rec.slot_id.id),
                    ('id', '!=', rec.id),
                    ('state', '!=', 'cancelled'),
                ])
                if others:
                    raise ValidationError("This slot is already booked.")