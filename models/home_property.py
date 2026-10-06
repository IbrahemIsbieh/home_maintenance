from odoo import models, fields, api
class HomeProperty(models.Model):
    _name = 'home.property'
    _description = 'Property'
    _inherit = ['mail.thread']

    name = fields.Char(string='Home Property Name', required=True,tracking=True)
    partner_id = fields.Many2one('res.partner', string='Owner', required=True, tracking=True)
    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('office', 'Office'),

    ],string='Property Type',required=True, default='apartment')
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    area = fields.Float(string='Area')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    request_ids = fields.One2many('home.request', 'property_id', string='Requests')
    request_count = fields.Integer(string='Requests Count', compute='_compute_request_count')

    @api.depends('request_ids')
    def _compute_request_count(self):
        for rec in self:
            rec.request_count = len(rec.request_ids)

    def action_view_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Requests',
            'res_model': 'home.request',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }