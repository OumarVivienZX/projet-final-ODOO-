from odoo import api, fields, models, _
class Incident(models.Model):
    _name = 'parckotech.incident'
    _description = 'Incident'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name              = fields.Char('Titre', required=True, tracking=True)
    ref               = fields.Char('Référence', readonly=True, copy=False)
    description       = fields.Text('Description', tracking=True)
    date_signalement  = fields.Datetime('Date de signalement', default=fields.Datetime.now, tracking=True)
    date_echeance     = fields.Datetime('Date d\'échéance', tracking=True)

    materiel_id       = fields.Many2one('parckotech.materiel', string='Matériel concerné', tracking=True)
    logiciel_id       = fields.Many2one('parckotech.logiciel', string='Logiciel concerné', tracking=True)
    client_id         = fields.Many2one('res.partner', string='Client', required=True, tracking=True,
                                        domain=[('is_company','=',True),('is_it_client','=',True)])
    site_id           = fields.Many2one('parckotech.site.client', string='Site', required=True, tracking=True,
                                        domain="[('client_id','=',client_id)]")
    technicien_id     = fields.Many2one('hr.employee', string='Technicien assigné', tracking=True)

        # Plan de maintenance lié (pour le One2many inverse défini dans MaintenancePlan)
    maintenance_plan_id = fields.Many2one(
        'parckotech.maintenance.plan',
        string='Plan de maintenance',
        help='Plan de maintenance préventive générant cet incident',
        tracking=True,
    )

    state = fields.Selection([
        ('new','Nouveau'),('in_progress','En cours'),('waiting','En attente'),
        ('resolved','Résolu'),('closed','Clôturé'),('cancelled','Annulé')
    ], default='new', tracking=True)
    type = fields.Selection([
        ('curative', 'Curatif'),
        ('preventive', 'Préventif')
    ], string='Type', default='curative', required=True, tracking=True)
    
    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Normale'),
        ('2', 'Haute'),
        ('3', 'Urgente')
    ], string='Priorité', default='1', tracking=True)
    
    intervention_ids = fields.One2many('parckotech.intervention', 'incident_id', string='Interventions')
    intervention_count = fields.Integer(compute='_compute_intervention_count', string='Nombre d\'interventions')
    
    active = fields.Boolean(default=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('ref'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('parckotech.incident')
        return super().create(vals_list)
    
    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for incident in self:
            incident.intervention_count = len(incident.intervention_ids)
            
    def action_in_progress(self):
        self.write({'state': 'in_progress'})
    
    def action_waiting(self):
        self.write({'state': 'waiting'})
    
    def action_resolved(self):
        self.write({'state': 'resolved'})
    
    def action_close(self):
        self.write({'state': 'closed'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_new(self):
        self.write({'state': 'new'})