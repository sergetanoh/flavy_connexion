import json
from django.utils import timezone
from django.http import JsonResponse
from api.models import Invoice

def notification(request):
    if request.method == 'POST' or request.method == 'GET':
        try:
            # Charger les données JSON de la requête
            data = json.loads(request.body)

            # Extraire le transaction_id et le status
            transaction_id = data.get('transaction_id')
            payment_status = data.get('status')

            # Récupérer la facture en fonction du transaction_id
            invoice = Invoice.objects.get(reference=transaction_id)

            # Vérifier le statut du paiement et mettre à jour en conséquence
            if payment_status == 'SUCCESSFULL':
                invoice.status = 'payee'  # ou un autre statut que vous utilisez pour les paiements
                invoice.paid_at = timezone.now()
            else:
                invoice.status = 'echouee'  # statut en cas d'échec du paiement

            # Mettre à jour la date de dernière modification (si pertinent)
            invoice.save()

            # Réponse de succès
            return JsonResponse({'message': 'Status updated successfully'}, status=200)

        except Invoice.DoesNotExist:
            return JsonResponse({'error': 'Invoice not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
