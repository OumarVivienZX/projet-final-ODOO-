var = {
    'name': 'parckotech',
    'version': '1.0',
    'summary': 'Gestion de parc informatique pour prestataire IT',
    'description': """
        Module de gestion de parc informatique avec facturation récurrente intégrée.
        Permet de gérer :
        - Parc matériel et logiciel
        - Incidents et interventions
        - Alertes automatiques
        - Contrats et facturation récurrente
        - Multi-sites
    """,
    'category': 'Services/IT Management',
    'author': 'Konan Oumar Vivien',
    'website': 'https://www.exemple.com',
    'depends': [
        'base',
        'mail',
        'stock',
        'purchase',
        'account',
        'hr',
        'calendar',
        'sale_subscription',
        'website',
    ],
    'data': [
        'security/parckotech_security.xml',
        'security/ir.model.access.csv',
        'data/parckotech_sequence.xml',
        'data/parckotech_data.xml',
        # VUES
        'views/pack_informatique_views.xml',
        'views/materiel_views.xml',
        'views/logiciel_views.xml',
        'views/licence_logicielle_views.xml',
        'views/incident_views.xml',
        'views/intervention_views.xml',
        'views/alerte_views.xml',
        'views/contrat_views.xml',
        'views/facture_views.xml',
        'views/site_client_views.xml',
        'views/menus.xml',
        'views/dashboards.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            # 'parckotech/static/src/js/dashboard.js',
            # Uncomment when needed
        ],
    },
}
