from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FactureContrat(models.Model):
    _name = 'parckotech.facture.contrat'
    _description = 'Facture Contrat'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_facture desc'
    
    name = fields.Char('Numéro', compute='_compute_name', store=True)
    
    contrat_id = fields.Many2one('parckotech.contrat.service', string='Contrat', required=True, tracking=True)
    client_id = fields.Many2one('res.partner', related='contrat_id.client_id', store=True, string='Client')
    pack_id = fields.Many2one('parckotech.pack.informatique', related='contrat_id.pack_id', store=True, string='Pack')
    
    date_facture = fields.Date('Date de facture', default=fields.Date.today, tracking=True)
    date_echeance = fields.Date('Date d\'échéance', compute='_compute_date_echeance', store=True, tracking=True)
    
    montant_ht = fields.Float('Montant HT', required=True, tracking=True)
    tva = fields.Float('TVA (%)', default=20.0, tracking=True)
    montant_tva = fields.Float('Montant TVA', compute='_compute_montants', store=True)
    montant_ttc = fields.Float('Montant TTC', compute='_compute_montants', store=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
        ('paid', 'Payée'),
        ('cancelled', 'Annulée')
    ], string='État', default='draft', tracking=True)
    
    periode_debut = fields.Date('Début de période', tracking=True)
    periode_fin = fields.Date('Fin de période', tracking=True)
    
    paiement_effectue = fields.Boolean('Paiement effectué', default=False, tracking=True)
    date_paiement = fields.Date('Date de paiement', tracking=True)
    method_paiement = fields.Char('Méthode de paiement', tracking=True)
    
    invoice_id = fields.Many2one('account.move', string='Facture Odoo', tracking=True)
    
    notes = fields.Text('Notes', tracking=True)
    
    @api.depends('contrat_id', 'date_facture')
    def _compute_name(self):
        for facture in self:
            if facture.contrat_id and facture.date_facture:
                date_str = fields.Date.to_string(facture.date_facture)
                facture.name = f"FACT/{facture.contrat_id.ref or ''}/{date_str}"
            else:
                facture.name = "Nouvelle facture"
    
    @api.depends('date_facture')
    def _compute_date_echeance(self):
        for facture in self:
            if facture.date_facture:
                facture.date_echeance = fields.Date.add(facture.date_facture, days=30)
    
    @api.depends('montant_ht', 'tva')
    def _compute_montants(self):
        for facture in self:
            facture.montant_tva = facture.montant_ht * (facture.tva / 100)
            facture.montant_ttc = facture.montant_ht + facture.montant_tva
    
    def action_send(self):
        self.write({'state': 'sent'})
        # Ici, on pourrait créer automatiquement une tâche pour envoyer par mail
    
    def action_mark_paid(self):
        self.write({
            'state': 'paid',
            'paiement_effectue': True,
            'date_paiement': fields.Date.today()
        })
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    def action_create_invoice(self):
        # Cette méthode créerait une facture dans le module account
        Invoice = self.env['account.move']
        for record in self:
            if record.invoice_id:
                raise ValidationError(_("Une facture Odoo existe déjà pour cette facture de contrat."))
            
            invoice_vals = {
                'partner_id': record.client_id.id,
                'invoice_date': fields.Date.today(),
                'move_type': 'out_invoice',
                'ref': record.name,
                'invoice_line_ids': [(0, 0, {
                    'name': f"Services pour {record.contrat_id.name}",
                    'quantity': 1,
                    'price_unit': record.montant_ht,
                })]
            }
            
            invoice = Invoice.create(invoice_vals)
            record.invoice_id = invoice.id
            
            return {
                'type': 'ir.actions.act_window',
                'name': _('Facture'),
                'res_model': 'account.move',
                'res_id': invoice.id,
                'view_mode': 'form',
                'target': 'current',
            }