from odoo import api, fields, models

class LicenceLogicielle(models.Model):
    _name = 'parckotech.licence.logicielle'
    _description = 'Licence Logicielle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Nom', required=True, tracking=True)
    ref = fields.Char('Référence', readonly=True, copy=False)
    
    logiciel_id = fields.Many2one('parckotech.logiciel', string='Logiciel', required=True, tracking=True)
    pack_id = fields.Many2one('parckotech.pack.informatique', related='logiciel_id.pack_id', store=True, string='Pack')
    client_id = fields.Many2one('res.partner', related='logiciel_id.client_id', store=True, string='Client')
    site_id = fields.Many2one('parckotech.site.client', related='logiciel_id.site_id', store=True, string='Site')
    
    type_duree = fields.Selection([
        ('perpetual', 'Perpétuelle'),
        ('monthly', 'Mensuelle'),
        ('yearly', 'Annuelle'),
        ('other', 'Autre')
    ], string='Type de durée', default='yearly', required=True, tracking=True)
    
    cout = fields.Float('Coût', tracking=True)
    date_debut = fields.Date('Date de début', tracking=True)
    date_fin = fields.Date('Date de fin', tracking=True)
    
    renouvellement_requis = fields.Boolean('Renouvellement requis', default=True, tracking=True)
    
    etat = fields.Selection([
        ('active', 'Active'),
        ('expiring_soon', 'Expire bientôt'),
        ('expired', 'Expirée'),
        ('renewed', 'Renouvelée')
    ], string='État', compute='_compute_etat', store=True, tracking=True)
    
    description = fields.Text('Description')
    notes = fields.Text('Notes')
    active = fields.Boolean(default=True)
    
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('ref'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('parckotech.licence.logicielle')
        return super().create(vals_list)
    
    @api.depends('date_fin', 'renouvellement_requis')
    def _compute_etat(self):
        today = fields.Date.today()
        for licence in self:
            if not licence.date_fin:
                licence.etat = 'active'
                continue
                
            days_to_expiry = (licence.date_fin - today).days
            
            if licence.date_fin < today:
                licence.etat = 'expired'
            elif days_to_expiry <= 30:
                licence.etat = 'expiring_soon'
            else:
                licence.etat = 'active'