from odoo import models, fields
class HomeVisit(models.Model):
    _name = 'home.visit'
    _description = 'Visit'
    _inherit = ['mail.thread']
    _order = 'visit_date desc'


    request_id = fields.Many2one('home.request', string='Request',required=True, ondelete='cascade')
    property_id = fields.Many2one(
        'home.property',related='request_id.property_id', store=True,)
    technician_id = fields.Many2one('res.users', string='Technician',
                                   required=True, tracking=True)
    visit_date = fields.Datetime(string='Visit Date', required=True, tracking=True)
    slot_id = fields.Many2one('home.slot', string='Appointment Slot',
                              copy=False, ondelete='restrict', tracking=True,
                              domain="[('state', '=', 'free')]")
    duration = fields.Float(string='Duration (hours)', default=1.0)
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('planned', 'Planned'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='planned', required=True, tracking=True)

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


