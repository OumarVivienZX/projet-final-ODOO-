from odoo import api, fields, models

class MaintenancePlan(models.Model):
    _name = 'parckotech.maintenance.plan'
    _description = 'Plan de Maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Nom', required=True, tracking=True)
    
    materiel_id = fields.Many2one('parckotech.materiel', string='Matériel', required=True, tracking=True)
    client_id = fields.Many2one('res.partner', related='materiel_id.client_id', store=True, string='Client')
    site_id = fields.Many2one('parckotech.site.client', related='materiel_id.site_id', store=True, string='Site')
    
    type = fields.Selection([
        ('preventive', 'Préventive'),
        ('corrective', 'Corrective'),
        ('predictive', 'Prédictive')
    ], string='Type', default='preventive', required=True, tracking=True)
    
    frequence_unite = fields.Selection([
        ('day', 'Jour'),
        ('week', 'Semaine'),
        ('month', 'Mois'),
        ('year', 'Année')
    ], string='Unité de fréquence', default='month', required=True, tracking=True)
    
    frequence_valeur = fields.Integer('Valeur de fréquence', default=1, required=True, tracking=True)
    prochaine_date = fields.Date('Prochaine date', required=True, tracking=True)
    derniere_execution = fields.Date('Dernière exécution', tracking=True)
    
    description = fields.Text('Description', tracking=True)
    instructions = fields.Text('Instructions', tracking=True)
    
    active = fields.Boolean(default=True)
    auto_create_incident = fields.Boolean('Créer incident automatiquement', default=True, 
                                          help="Si activé, un incident sera créé automatiquement à la date prévue")
    
    incident_ids = fields.One2many('parckotech.incident', 'maintenance_plan_id', string='Incidents générés')
    incident_count = fields.Integer(compute='_compute_incident_count', string='Nombre d\'incidents')
    
    @api.depends('incident_ids')
    def _compute_incident_count(self):
        for plan in self:
            plan.incident_count = len(plan.incident_ids)
    
    def action_execute_now(self):
        self.ensure_one()
        
        if self.auto_create_incident:
            # Créer un incident préventif
            incident = self.env['parckotech.incident'].create({
                'name': f"Maintenance préventive: {self.name}",
                'description': f"Maintenance planifiée pour le matériel {self.materiel_id.name}\n\n{self.instructions or ''}",
                'materiel_id': self.materiel_id.id,
                'client_id': self.client_id.id,
                'site_id': self.site_id.id,
                'type': 'preventive',
                'priority': '1',
                'maintenance_plan_id': self.id,
            })
        
        # Mettre à jour la prochaine date
        if self.frequence_unite == 'day':
            next_date = fields.Date.add(fields.Date.today(), days=self.frequence_valeur)
        elif self.frequence_unite == 'week':
            next_date = fields.Date.add(fields.Date.today(), weeks=self.frequence_valeur)
        elif self.frequence_unite == 'month':
            next_date = fields.Date.add(fields.Date.today(), months=self.frequence_valeur)
        else:  # year
            next_date = fields.Date.add(fields.Date.today(), years=self.frequence_valeur)
        
        self.write({
            'derniere_execution': fields.Date.today(),
            'prochaine_date': next_date,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f"Plan de maintenance exécuté. Prochaine date: {next_date}",
                'type': 'success',
                'sticky': False,
            }
        }