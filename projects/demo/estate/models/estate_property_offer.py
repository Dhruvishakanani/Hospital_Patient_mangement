from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from datetime import timedelta
from stdnum.exceptions import ValidationError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'
    _order = 'price desc'

    # name = fields.Char(string="Name")
    status = fields.Selection(
        selection=[('accepted', 'Accepted'),
                   ('refused', 'Refused'),
                   ('new', 'New')],
        default='new'
    )
    property_id = fields.Many2one('estate.property', string="Property", required=True)
    property_type_id = fields.Many2one('estate.property.type', related='property_id.property_type_id', string='Property Type', store=True)
    price = fields.Float(string='Offer Price')
    partner_id = fields.Many2one('res.partner', string="partner", required=True)
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline",store=True)
    create_date = fields.Datetime(string="Create Date", default=fields.Datetime.now)


    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date:
                start_date = fields.Datetime.from_string(offer.create_date).date()
            else:
                start_date = fields.Date.today()
            offer.date_deadline = start_date + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.create_date and offer.date_deadline:
                start_date = fields.Datetime.from_string(offer.create_date).date()
                end_date = offer.date_deadline
                offer.validity = (end_date - start_date).days
            elif offer.date_deadline:
                start_date = fields.Date.today()
                end_date = offer.date_deadline
                offer.validity = (end_date - start_date).days

    def action_accept(self):
        self.ensure_one()
        if self.property_id.state in ['sold', 'canceled']:
            raise ValidationError("Cannot accept an offer for a sold or canceled property.")
        self.status = 'accepted'
        self.property_id.write({
            'selling_price': self.price,
            'buyer_id': self.partner_id.id
        })
        # Refuse all other offers for this property
        other_offers = self.env['estate.property.offer'].search([
            ('property_id', '=', self.property_id.id),
            ('id', '!=', self.id)
        ])
        self.property_id.state = 'offer_accepted'

    def action_refuse(self):
        self.write({'status': 'refused'})

    # In estate_property_offer.py
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'Offer price must be strictly positive.'),
    ]

    @api.model
    def create(self, vals):
        property_id = vals.get('property_id')
        price = vals.get('price', 0)
        if property_id:
            property = self.env['estate.property'].browse(property_id)
            existing_offers = self.search([('property_id', '=', property.id)])
            if existing_offers:
                max_price = max(existing_offers.mapped('price'))
                if price <= max_price:
                    raise ValidationError("Cannot create an offer with a lower price than existing offers.")
        offer = super().create(vals)
        if offer.property_id:
            offer.property_id.state = 'offer_received'
        return offer