import json
from django.utils import timezone
from django.http import JsonResponse
from api.models import Invoice,InvoicePayment, Commande, Recherche, Pharmacie, WalletPharmacie, WalletPharmacieHistory, Notification
from decimal import Decimal
import requests
from api.utils import send_sms_jetfy
from api.serializers import CommandeSerializer


def get_or_create_wallet_pharmacie(pharmacie_id):
        try:
            pharmacie = Pharmacie.objects.get(pk=pharmacie_id)
        except Pharmacie.DoesNotExist:
            raise ValueError("Pharmacie non trouvée")
            
        wallet, created = WalletPharmacie.objects.get_or_create(
            pharmacie=pharmacie,
            defaults={'balance': 0.00, 'old_balance': 0.00}
        )
        
        if created:
            WalletPharmacieHistory.objects.create(
                wallet=wallet,
                action_type='depot',
                label='Création du wallet',
                amount=0.00,
                new_balance=0.00
            )
            
        return wallet, created



def wehook_function(request):
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
           
            if data.get('typeTransaction') == "collecte":
                if  invoice.status == 'payee':
                    return JsonResponse({'error': 'Commande déja payée'}, status=403)
                # Vérifier le statut du paiement et mettre à jour en conséquence
                if payment_status == 'SUCCESSFULL':
                    invoice.status = 'payee'  # ou un autre statut que vous utilisez pour les paiements
                    invoice.paid_at = timezone.now()

                    # Mettre à jour le statut de la commande
                    commande = invoice.commande
                    if  commande and commande.terminer == False:
                        commande.statut = 'en_attente_livraison'
                        commande.save()

                        # Mettre à jour le statut de la recherche
                        if commande.recherche:
                            recherche = Recherche.objects.get(pk=commande.recherche.pk)
                            recherche.statut = 'termine'
                            recherche.save()

                        # Récupérer la pharmacie
                        pharmacie  = commande.pharmacie_id
                        
                        ####### Mis ajour du wallet  ###########
                        wallet, is_new = get_or_create_wallet_pharmacie(pharmacie.pk)
                        amount = Decimal(str(invoice.total_amount))
                        

                        # Mise à jour du solde
                        wallet.old_balance = wallet.balance
                        wallet.balance += amount
                        wallet.save()
                        
                        # Création de l'historique
                        action_type = 'depot'
                        label = 'Paiement de la commande '+ str(commande.pk)+" par le client"
                        WalletPharmacieHistory.objects.create(
                            wallet=wallet,
                            action_type=action_type,
                            label=label,
                            amount=amount,
                            new_balance=wallet.balance
                        )

                        notification = Notification.objects.create(
                            title = "Nouveau paiement effectué",
                            message = 'Vous avez reçu un nouveau paiement pour la commande '+ str(commande.pk)+' par le client',
                            type = "commande",
                            data_id = commande.pk,
                            metadata = CommandeSerializer(commande, many=False).data,
                            is_read = False,
                            user_type = 'pharmacie',
                            user_id = pharmacie.pk
                        )

                        # SEND SMS
                        if pharmacie.numero_contact_pharmacie:
                            send_sms_jetfy(pharmacie.numero_contact_pharmacie, notification.message)
                            
                else:
                    invoice.status = 'echouee'  # statut en cas d'échec du paiement

                # Mettre à jour la date de dernière modification (si pertinent)
                invoice.save() 
            else:
                if  payment.type_transaction == 'SUCCESSFULL':
                    return JsonResponse({'message': 'Payment deja effectué'}, status=403)          

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


def transfer_mobile_money():
    url = "https://api.digitalpaye.com/v1/transfers/mobile-money"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb21wYW55X2lkIjoiMSIsImlhdCI6MTcxMjYwODUxMywiZXhwIjoxNzEyNjA5MTEzfQ.fui_sVqSoQs_OtCqCm7vkH0pFlcQud5tKsyCZI64NnU"
    }
    payload = {
        "code_country": "CI",
        "currency": "XOF",
        "customer_id": "0546573332",
        "name": "GUEI HELIE",
        "amount": 300,
        "operator": "WAVE_CI",
        "transaction_id": "TICK-0110379110832"
    }

    try:
        # Effectuer la requête POST
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Vérifier si la requête a réussi
        if response.status_code == 200:
            return response.json()  # Retourne la réponse sous forme d'objet JSON
        else:
            return {
                "error": f"Erreur lors du transfert : {response.status_code}",
                "details": response.text
            }
    except requests.exceptions.RequestException as e:
        # Gestion des erreurs réseau
        return {"error": f"Erreur réseau : {str(e)}"}
    

def transfer_mobile_money():
    url = "https://api.digitalpaye.com/v1/transfers/mobile-money"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb21wYW55X2lkIjoiMSIsImlhdCI6MTcxMjYwODUxMywiZXhwIjoxNzEyNjA5MTEzfQ.fui_sVqSoQs_OtCqCm7vkH0pFlcQud5tKsyCZI64NnU"
    }
    payload = {
        "code_country": "CI",
        "currency": "XOF",
        "customer_id": "0546573332",
        "name": "GUEI HELIE",
        "amount": 300,
        "operator": "WAVE_CI",
        "transaction_id": "TICK-0110379110832"
    }

    try:
        # Effectuer la requête POST
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Vérifier si la requête a réussi
        if response.status_code == 200:
            return response.json()  # Retourne la réponse sous forme d'objet JSON
        else:
            return {
                "error": f"Erreur lors du transfert : {response.status_code}",
                "details": response.text
            }
    except requests.exceptions.RequestException as e:
        # Gestion des erreurs réseau
        return {"error": f"Erreur réseau : {str(e)}"}