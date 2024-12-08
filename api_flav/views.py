import json
from django.utils import timezone
from django.http import JsonResponse
from api.models import Invoice,InvoicePayment, Commande, Recherche

def notification(request):
    if request.method == 'POST' or request.method == 'GET':
        try:
            # Charger les données JSON de la requête
            data = json.loads(request.body)

            # Extraire le transaction_id et le status
            transaction_id = data.get('transactionId')
            payment_status = data.get('status')

            # Récupérer la facture en fonction du transaction_id
            payment = InvoicePayment.objects.get(reference=transaction_id)
            invoice = Invoice.objects.get(pk=payment.invoice.pk)
           
            # Vérifier le statut du paiement et mettre à jour en conséquence
            if payment_status == 'SUCCESSFULL':
                invoice.status = 'payee'  # ou un autre statut que vous utilisez pour les paiements
                invoice.paid_at = timezone.now()

                # Mettre à jour le statut de la commande
                commande = Commande.objects.get(pk=invoice.commande.pk)
                if  commande and commande.terminer == False:
                    commande.statut = 'en_attente_livraison'
                    commande.save()

                    # Mettre à jour le statut de la recherche
                    if commande.recherche:
                        recherche = Recherche.objects.get(pk=commande.recherche.pk)
                        recherche.statut = 'termine'
                        recherche.save()

            else:
                invoice.status = 'echouee'  # statut en cas d'échec du paiement

            # Mettre à jour la date de dernière modification (si pertinent)
            invoice.save()

            # Update payment info
            payment.phone = data.get('phone')
            payment.customer = data.get('customer')
            payment.currency = data.get('currency')
            payment.fees = data.get('fees')
            payment.amount_receive = data.get('amountReceive')
            payment.amount_total = data.get('amountTotal')
            payment.status = data.get('status')
            payment.type_transaction = data.get('typeTransaction')
            payment.type_payment = data.get('operator')
            payment.date = data.get('date')
            payment.save()

            # Réponse de succès
            return JsonResponse({'message': 'Status updated successfully'}, status=200)

        except InvoicePayment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)
        except Invoice.DoesNotExist:
            return JsonResponse({'error': 'Invoice not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
