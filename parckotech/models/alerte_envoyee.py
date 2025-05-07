from odoo import api, fields, models

class AlerteEnvoyee(models.Model):
    _name = 'parckotech.alerte.envoyee'
    _description = 'Alerte Envoyée'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_envoi desc'
    
    name = fields.Char('Nom', compute='_compute_name', store=True)
    
    type = fields.Selection([
        ('garantie', 'Garantie'),
        ('licence', 'Licence'),
        ('maintenance', 'Maintenance'),
        ('contrat', 'Contrat')
    ], string='Type', required=True)
    
    date_envoi = fields.Datetime('Date d\'envoi', default=fields.Datetime.now)
    
    materiel_id = fields.Many2one('parckotech.materiel', string='Matériel concerné')
    licence_id = fields.Many2one('parckotech.licence.logicielle', string='Licence concernée')
    contrat_id = fields.Many2one('parckotech.contrat.service', string='Contrat concerné')
    maintenance_plan_id = fields.Many2one('parckotech.maintenance.plan', string='Plan de maintenance concerné')
    
    user_id = fields.Many2one('res.users', string='Utilisateur notifié')
    client_id = fields.Many2one('res.partner', string='Client', required=True)
    
    etat_traitement = fields.Selection([
        ('new', 'Nouvelle'),
        ('in_progress', 'En traitement'),
        ('done', 'Traitée'),
        ('ignored', 'Ignorée')
    ], string='État de traitement', default='new', tracking=True)
    
    message = fields.Text('Message')
    repetition_count = fields.Integer('Nombre de répétitions', default=1)
    
    parametres_id = fields.Many2one('parckotech.parametre.alerte', string='Paramètre d\'alerte')
    
    @api.depends('type', 'materiel_id', 'licence_id', 'contrat_id', 'maintenance_plan_id')
    def _compute_name(self):
        for alerte in self:
            if alerte.type == 'garantie' and alerte.materiel_id:
                alerte.name = f"Garantie: {alerte.materiel_id.name}"
            elif alerte.type == 'licence' and alerte.licence_id:
                alerte.name = f"Licence: {alerte.licence_id.name}"
            elif alerte.type == 'contrat' and alerte.contrat_id:
                alerte.name = f"Contrat: {alerte.contrat_id.name}"
            elif alerte.type == 'maintenance' and alerte.maintenance_plan_id:
                alerte.name = f"Maintenance: {alerte.maintenance_plan_id.name}"
            else:
                alerte.name = f"Alerte {alerte.type}"
    
    def action_in_progress(self):
        self.write({'etat_traitement': 'in_progress'})
    
    def action_done(self):
        self.write({'etat_traitement': 'done'})
    
    def action_ignore(self):
        self.write({'etat_traitement': 'ignored'})