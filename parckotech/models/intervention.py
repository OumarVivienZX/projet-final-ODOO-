from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Intervention(models.Model):
    _name = 'parckotech.intervention'
    _description = 'Intervention'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_debut desc'
    
    name = fields.Char('Titre', compute='_compute_name', store=True)
    ref = fields.Char('Référence', readonly=True, copy=False)
    
    incident_id = fields.Many2one('parckotech.incident', string='Incident lié', tracking=True)
    technicien_id = fields.Many2one('hr.employee', string='Technicien', required=True, tracking=True)
    
    date_debut = fields.Datetime('Date de début', default=fields.Datetime.now, tracking=True)
    date_fin = fields.Datetime('Date de fin', tracking=True)
    duree = fields.Float('Durée (heures)', compute='_compute_duree', store=True, tracking=True)
    
    materiel_id = fields.Many2one('parckotech.materiel', related='incident_id.materiel_id', 
                                 store=True, string='Matériel concerné')
    client_id = fields.Many2one('res.partner', related='incident_id.client_id', 
                               store=True, string='Client')
    site_id = fields.Many2one('parckotech.site.client', related='incident_id.site_id', 
                             store=True, string='Site')
    
    compte_rendu = fields.Text('Compte-rendu', tracking=True)
    signature_client = fields.Binary('Signature client')
    signature_date = fields.Datetime('Date de signature')
    
    facturable = fields.Boolean('Facturable', default=True, tracking=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('planned', 'Planifiée'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée'),
        ('cancelled', 'Annulée')
    ], string='État', default='draft', tracking=True)
    
    validation = fields.Selection([
        ('not_validated', 'Non validée'),
        ('validated', 'Validée')
    ], string='Validation', default='not_validated', tracking=True)
    
    piece_ids = fields.Many2many('stock.move', string='Pièces utilisées')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('ref'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('parckotech.intervention')
        return super().create(vals_list)
    
    @api.depends('incident_id', 'date_debut')
    def _compute_name(self):
        for intervention in self:
            if intervention.incident_id:
                intervention.name = f"INT/{intervention.incident_id.ref or ''}"
            else:
                intervention.name = "Nouvelle intervention"
            
            if intervention.date_debut:
                date_str = fields.Datetime.to_string(intervention.date_debut)
                intervention.name += f" ({date_str[:10]})"
    
    @api.depends('date_debut', 'date_fin')
    def _compute_duree(self):
        for intervention in self:
            if intervention.date_debut and intervention.date_fin:
                delta = intervention.date_fin - intervention.date_debut
                intervention.duree = delta.total_seconds() / 3600
            else:
                intervention.duree = 0.0
    
    def action_plan(self):
        self.write({'state': 'planned'})
    
    def action_start(self):
        self.write({
            'state': 'in_progress',
            'date_debut': fields.Datetime.now()
        })
    
    def action_done(self):
        for record in self:
            if not record.date_fin:
                record.date_fin = fields.Datetime.now()
        self.write({'state': 'done'})
        
        # Mettre à jour l'état de l'incident si toutes les interventions sont terminées
        for intervention in self:
            if intervention.incident_id:
                all_done = True
                for interv in intervention.incident_id.intervention_ids:
                    if interv.state != 'done' and interv.state != 'cancelled':
                        all_done = False
                        break
                
                if all_done and intervention.incident_id.state != 'closed':
                    intervention.incident_id.action_resolved()
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_validate(self):
        self.write({'validation': 'validated'})