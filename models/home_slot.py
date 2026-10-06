from odoo import models, fields, api


class HomeSlot(models.Model):
    _name = 'home.slot'
    _description = 'Available Slot'
    _order = 'slot_start'

    technician_id = fields.Many2one('res.users', string='Technician', required=True)
    slot_start = fields.Datetime(string='Start', required=True)
    duration = fields.Float(string='Duration (hours)', default=1.0)
    request_ids = fields.One2many('home.request', 'slot_id', string='Requests')
    state = fields.Selection([
        ('free', 'Free'),
        ('booked', 'Booked'),
    ], string='Status', compute='_compute_state', store=True)

    @api.depends('request_ids.state')
    def _compute_state(self):
        for rec in self:
            active = rec.request_ids.filtered(lambda r: r.state != 'cancelled')
            rec.state = 'booked' if active else 'free'

    @api.depends('technician_id', 'slot_start')
    def _compute_display_name(self):
        for rec in self:
            if rec.slot_start:
                start = fields.Datetime.context_timestamp(rec, rec.slot_start)
                rec.display_name = f"{rec.technician_id.name or ''} - {start.strftime('%Y-%m-%d %H:%M')}"
            else:
                rec.display_name = rec.technician_id.name or ''