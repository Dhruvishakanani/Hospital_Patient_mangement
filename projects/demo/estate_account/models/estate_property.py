from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        # Call the original method from the parent class
        res = super().action_sold()

        # Calculate invoice lines
        selling_price = self.selling_price
        administrative_fees = 100.00
        commission = selling_price * 0.06  # 6% commission

        # Get the default journal for customer invoices
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),  # Sale journal
            ('company_id', '=', self.env.company.id),
        ], limit=1)

        if not journal:
            raise ValueError("No default sale journal found. Please configure one in the Accounting app.")

        try:
            # Create an invoice
            invoice = self.env['account.move'].create({
                'partner_id': self.buyer_id.id,  # Buyer of the property
                'move_type': 'out_invoice',  # Customer Invoice
                'journal_id': journal.id,  # Default sale journal
                'invoice_line_ids': [
                    (0, 0, {  # First invoice line
                        'product_id': False,  # Optional: Set the product_id if required
                        'name': 'Commission (6% of selling price)',
                        'quantity': 1,
                        'price_unit': commission,
                    }),
                    (0, 0, {  # Second invoice line
                        'product_id': False,  # Optional: Set the product_id if required
                        'name': 'Administrative Fees',
                        'quantity': 1,
                        'price_unit': administrative_fees,
                    })
                ]
            })

            print("INVOICE ==========", invoice)

            # Create the invoice lines directly
            self.env['account.move.line'].create({
                'move_id': invoice.id,
                'product_id': False,  # Optional: Set the product_id if required
                'name': 'Commission (6% of selling price)',
                'quantity': 1,
                'price_unit': commission,
            })

            self.env['account.move.line'].create({
                'move_id': invoice.id,
                'product_id': False,  # Optional: Set the product_id if required
                'name': 'Administrative Fees',
                'quantity': 1,
                'price_unit': administrative_fees,
            })

            # Log the created invoice ID
            _logger.info(f"Invoice created: {invoice.id}")

        except Exception as e:
            _logger.error(f"Failed to create invoice: {e}")
            raise ValueError("There was an error while creating the invoice.")

        #Browse invoice record id 54
        invoice_rec = self.env['account.move'].browse(54)
        return res