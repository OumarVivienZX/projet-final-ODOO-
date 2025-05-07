from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_it_client = fields.Boolean('Client IT', help="Indique si ce partenaire est un client IT")
    responsible_id = fields.Many2one('res.partner', string='Responsable', domain=[('is_company', '=', False)])
    technical_contact_id = fields.Many2one('res.partner', string='Contact technique', domain=[('is_company', '=', False)])
    site_count = fields.Integer(string='Nombre de sites', compute='_compute_site_count')
    pack_count = fields.Integer(string='Nombre de packs', compute='_compute_pack_count')
    
    @api.depends('child_ids')
    def _compute_site_count(self):
        for partner in self:
            partner.site_count = self.env['parckotech.site.client'].search_count([('client_id', '=', partner.id)])
    
    @api.depends()
    def _compute_pack_count(self):
        for partner in self:
            partner.pack_count = self.env['parckotech.pack.informatique'].search_count([('client_id', '=', partner.id)])

