from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import qrcode
import base64
from io import BytesIO

class Materiel(models.Model):
    _name = 'parckotech.materiel'
    _description = 'Matériel Informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    company_id = fields.Many2one(
       'res.company',
        string='Société',
        default=lambda self: self.env.company,
        index=True,       
        tracking=True,
  )
    
    name = fields.Char('Nom', required=True, tracking=True)
    ref = fields.Char('Référence', readonly=True, copy=False)
    type_id = fields.Many2one('parckotech.materiel.type', string='Type', required=True, tracking=True)
    marque = fields.Char('Marque', tracking=True)
    modele = fields.Char('Modèle', tracking=True)
    numero_serie = fields.Char('Numéro de série', tracking=True)
    date_achat = fields.Date('Date d\'achat', tracking=True)
    
    duree_garantie = fields.Integer('Durée garantie (mois)', default=12, tracking=True)
    date_fin_garantie = fields.Date('Date fin garantie', compute='_compute_date_fin_garantie', store=True, tracking=True)
    
    etat = fields.Selection([
        ('new', 'Neuf'),
        ('good', 'Bon état'),
        ('average', 'État moyen'),
        ('bad', 'Mauvais état'),
        ('out_of_order', 'Hors service')
    ], string='État', default='new', tracking=True)
    
    employee_id = fields.Many2one('hr.employee', string='Utilisateur', tracking=True)
    pack_id = fields.Many2one('parckotech.pack.informatique', string='Pack', required=True, tracking=True)
    client_id = fields.Many2one('res.partner', related='pack_id.client_id', store=True, string='Client')
    site_id = fields.Many2one('parckotech.site.client', related='pack_id.site_id', store=True, string='Site')
    
    description = fields.Text('Description')
    notes = fields.Text('Notes')
    active = fields.Boolean(default=True)
    
    # Amortissement
    valeur_achat = fields.Float('Valeur d\'achat', tracking=True)
    duree_amortissement = fields.Integer('Durée amortissement (mois)', default=36, tracking=True)
    valeur_residuelle = fields.Float('Valeur résiduelle', compute='_compute_valeur_residuelle')
    
    # QR Code
    qr_code = fields.Binary('QR Code', compute='_compute_qr_code')
    
    # Relations
    incident_ids = fields.One2many('parckotech.incident', 'materiel_id', string='Incidents')
    incident_count = fields.Integer(compute='_compute_incident_count', string='Nombre d\'incidents')
    
    intervention_ids = fields.One2many('parckotech.intervention', 'materiel_id', string='Interventions')
    intervention_count = fields.Integer(compute='_compute_intervention_count', string='Nombre d\'interventions')
    
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')
    maintenance_plan_ids = fields.One2many('parckotech.maintenance.plan', 'materiel_id', string='Plans de maintenance')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('ref'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('parckotech.materiel')
        return super().create(vals_list)
    
    @api.depends('date_achat', 'duree_garantie')
    def _compute_date_fin_garantie(self):
        for materiel in self:
            if materiel.date_achat and materiel.duree_garantie:
                materiel.date_fin_garantie = fields.Date.add_months(materiel.date_achat, materiel.duree_garantie)
            else:
                materiel.date_fin_garantie = False
    
    @api.depends('valeur_achat', 'duree_amortissement', 'date_achat')
    def _compute_valeur_residuelle(self):
        today = fields.Date.today()
        for materiel in self:
            if not materiel.date_achat or not materiel.valeur_achat or not materiel.duree_amortissement:
                materiel.valeur_residuelle = 0.0
                continue
                
            # Si date achat est dans le futur
            if materiel.date_achat > today:
                materiel.valeur_residuelle = materiel.valeur_achat
                continue
                
            # Calculer mois écoulés depuis l'achat
            months_diff = (today.year - materiel.date_achat.year) * 12 + today.month - materiel.date_achat.month
            
            # Si la durée d'amortissement est dépassée
            if months_diff >= materiel.duree_amortissement:
                materiel.valeur_residuelle = 0.0
            else:
                # Amortissement linéaire
                taux_amortissement_mensuel = materiel.valeur_achat / materiel.duree_amortissement
                materiel.valeur_residuelle = materiel.valeur_achat - (taux_amortissement_mensuel * months_diff)
    
    def _compute_qr_code(self):
        for record in self:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr_data = f"Matériel: {record.name}\nRéférence: {record.ref}\nNuméro série: {record.numero_serie}\nClient: {record.client_id.name}\nSite: {record.site_id.name}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            record.qr_code = base64.b64encode(buffered.getvalue())
    
    @api.depends('incident_ids')
    def _compute_incident_count(self):
        for record in self:
            record.incident_count = len(record.incident_ids)
            
    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for record in self:
            record.intervention_count = len(record.intervention_ids)
            

class MaterielType(models.Model):
    _name = 'parckotech.materiel.type'
    _description = 'Type de Matériel'
    
    name = fields.Char('Nom', required=True)
    description = fields.Text('Description')
    category = fields.Selection([
        ('computer', 'Ordinateur'),
        ('printer', 'Imprimante'),
        ('network', 'Équipement réseau'),
        ('server', 'Serveur'),
        ('storage', 'Stockage'),
        ('peripheral', 'Périphérique'),
        ('other', 'Autre')
    ], string='Catégorie', default='other', required=True)
    active = fields.Boolean(default=True)