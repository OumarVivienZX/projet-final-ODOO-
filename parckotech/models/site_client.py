from odoo import api, fields, models

class SiteClient(models.Model):
    _name = 'parckotech.site.client'
    _description = 'Site Client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Nom du site', required=True, tracking=True)
    code = fields.Char('Code', tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True, 
                                domain=[('is_company', '=', True), ('is_it_client', '=', True)])
    parent_id = fields.Many2one('parckotech.site.client', string='Site parent', tracking=True)
    child_ids = fields.One2many('parckotech.site.client', 'parent_id', string='Sites enfants')
    street = fields.Char('Rue')
    street2 = fields.Char('Rue 2')
    zip = fields.Char('Code postal')
    city = fields.Char('Ville')
    state_id = fields.Many2one('res.country.state', string='État/Province')
    country_id = fields.Many2one('res.country', string='Pays')
    contact_name = fields.Char('Nom du contact sur place')
    contact_phone = fields.Char('Téléphone du contact')
    contact_email = fields.Char('Email du contact')
    active = fields.Boolean(default=True)
    type = fields.Selection([
        ('headquarters', 'Siège'),
        ('agency', 'Agence'),
        ('department', 'Département'),
        ('other', 'Autre')
    ], string='Type de site', default='other', required=True)
    
    pack_ids = fields.One2many('parckotech.pack.informatique', 'site_id', string='Packs informatiques')
    pack_count = fields.Integer(compute='_compute_pack_count', string='Nombre de packs')
    
    @api.depends('pack_ids')
    def _compute_pack_count(self):
        for site in self:
            site.pack_count = len(site.pack_ids)