from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class PackInformatique(models.Model):
    _name = 'parckotech.pack.informatique'
    _description = 'Pack Informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Nom du pack', required=True, tracking=True)
    ref = fields.Char('Référence', readonly=True, copy=False)
    client_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True,
                                domain=[('is_company', '=', True), ('is_it_client', '=', True)])
    site_id = fields.Many2one('parckotech.site.client', string='Site', required=True, tracking=True,
                             domain="[('client_id', '=', client_id)]")
    date_mise_service = fields.Date('Date de mise en service', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('maintenance', 'En maintenance'),
        ('suspended', 'Suspendu'),
        ('terminated', 'Résilié')
    ], string='Statut', default='draft', tracking=True)
    
    materiel_ids = fields.One2many('parckotech.materiel', 'pack_id', string='Matériels')
    logiciel_ids = fields.One2many('parckotech.logiciel', 'pack_id', string='Logiciels')
    contrat_ids = fields.One2many('parckotech.contrat.service', 'pack_id', string='Contrats de service')
    
    materiel_count = fields.Integer(compute='_compute_materiel_count', string='Nombre de matériels')
    logiciel_count = fields.Integer(compute='_compute_logiciel_count', string='Nombre de logiciels')
    contrat_count = fields.Integer(compute='_compute_contrat_count', string='Nombre de contrats')
    
    description = fields.Text('Description')
    notes = fields.Text('Notes')
    active = fields.Boolean(default=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('ref'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('parckotech.pack.informatique')
        return super().create(vals_list)
    
    @api.depends('materiel_ids')
    def _compute_materiel_count(self):
        for pack in self:
            pack.materiel_count = len(pack.materiel_ids)
    
    @api.depends('logiciel_ids')
    def _compute_logiciel_count(self):
        for pack in self:
            pack.logiciel_count = len(pack.logiciel_ids)
    
    @api.depends('contrat_ids')
    def _compute_contrat_count(self):
        for pack in self:
            pack.contrat_count = len(pack.contrat_ids)
    
    def action_active(self):
        self.write({'state': 'active'})
    
    def action_maintenance(self):
        self.write({'state': 'maintenance'})
    
    def action_suspend(self):
        self.write({'state': 'suspended'})
    
    def action_terminate(self):
        self.write({'state': 'terminated'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.constrains('client_id', 'site_id')
    def _check_site_client(self):
        for record in self:
            if record.site_id.client_id != record.client_id:
                raise ValidationError(_("Le site doit appartenir au client sélectionné."))

