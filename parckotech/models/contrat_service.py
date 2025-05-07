from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ContratService(models.Model):
    _name = 'parckotech.contrat.service'
    _description = 'Contrat de Service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Nom', required=True, tracking=True)
    ref = fields.Char('Référence', readonly=True, copy=False)
    
    client_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True,
                              domain=[('is_company', '=', True), ('is_it_client', '=', True)])
    pack_id = fields.Many2one('parckotech.pack.informatique', string='Pack', required=True, tracking=True,
                             domain="[('client_id', '=', client_id)]")
    
    date_debut = fields.Date('Date de début', required=True, tracking=True)
    date_fin = fields.Date('Date de fin', tracking=True)
    
    frequence_facturation = fields.Selection([
        ('monthly', 'Mensuelle'),
        ('quarterly', 'Trimestrielle'),
        ('semi_annual', 'Semestrielle'),
        ('annual', 'Annuelle'),
        ('other', 'Autre')
    ], string='Fréquence de facturation', default='monthly', required=True, tracking=True)
    
    tarif = fields.Float('Tarif', required=True, tracking=True)
    
    type_tarif = fields.Selection([
        ('subscription', 'Abonnement'),
        ('fixed', 'Forfait'),
        ('time_material', 'Temps & Matériel')
    ], string='Type de tarification', default='subscription', required=True, tracking=True)
    
    sla_temps_reponse = fields.Integer('SLA - Temps de réponse (heures)', default=24, tracking=True)
    sla_temps_resolution = fields.Integer('SLA - Temps de résolution (heures)', default=48, tracking=True)
    
    renouvellement_auto = fields.Boolean('Renouvellement automatique', default=True, tracking=True)
    duree_engagement = fields.Integer('Durée d\'engagement (mois)', default=12, tracking=True)
    
    conditions = fields.Text('Conditions spécifiques', tracking=True)
    notes = fields.Text('Notes internes')
    active = fields.Boolean(default=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
        ('renewed', 'Renouvelé')
    ], string='État', default='draft', tracking=True)
    
    facture_ids = fields.One2many('parckotech.facture.contrat', 'contrat_id', string='Factures')
    facture_count = fields.Integer(compute='_compute_facture_count', string='Nombre de factures')
    
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('ref'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('parckotech.contrat.service')
        return super().create(vals_list)
    
    @api.depends('facture_ids')
    def _compute_facture_count(self):
        for contrat in self:
            contrat.facture_count = len(contrat.facture_ids)
    
    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for contrat in self:
            if contrat.date_fin and contrat.date_debut > contrat.date_fin:
                raise ValidationError(_("La date de fin doit être postérieure à la date de début."))
    
    def action_active(self):
        self.write({'state': 'active'})
    
    def action_expire(self):
        self.write({'state': 'expired'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_renew(self):
        for contrat in self:
            if contrat.date_fin:
                # Créer un nouveau contrat basé sur celui-ci
                new_contrat = contrat.copy({
                    'date_debut': fields.Date.add(contrat.date_fin, days=1),
                    'date_fin': fields.Date.add(contrat.date_fin, months=contrat.duree_engagement),
                    'state': 'draft',
                })
                
                # Marquer l'ancien contrat comme renouvelé
                contrat.write({'state': 'renewed'})
                
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Contrat renouvelé'),
                    'res_model': 'parckotech.contrat.service',
                    'res_id': new_contrat.id,
                    'view_mode': 'form',
                    'target': 'current',
                }