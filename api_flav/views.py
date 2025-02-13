import json
from django.utils import timezone
from django.http import JsonResponse
from api.models import Invoice,InvoicePayment, Commande, Recherche, Pharmacie, WalletPharmacie, WalletPharmacieHistory, Notification, Transaction
from decimal import Decimal
import requests
from api.utils import send_sms_jetfy, generate_reference
from api.serializers import CommandeSerializer, InvoiceSerializer
import base64


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
    try:
        if request.method == 'POST' or request.method == 'GET':
            # try:

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

                        # Faire un versement de la pharmacie        
                        return transfer_money(pharmacie, invoice)

                            
                else:
                    invoice.status = 'echouee'  # statut en cas d'échec du paiement

                # Mettre à jour la date de dernière modification (si pertinent)
                invoice.save() 
            else:
                if  payment.status == 'SUCCESSFULL':
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

            # except InvoicePayment.DoesNotExist:
            #     return JsonResponse({'error': 'Payment not found'}, status=404)
            # except Invoice.DoesNotExist:
            #     return JsonResponse({'error': 'Invoice not found'}, status=404)
            # except Exception as e:
            #     return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def transfer_money(pharmacie, invoice):

    url = 'https://api.digitalpaye.com/v1/transfers/mobile-money'
    headers = {
        'Content-Type': 'application/json',
    }

    token = generateToken()
    # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55SWQiOiI4MWU1OGEyOC0wMWExLTQ3YTMtOTAzYy0yNTdkNDE4ZmNlNzEiLCJpYXQiOjE3Mzk0Nzg1MTIsImV4cCI6MTczOTQ3OTExMn0.N3zv3XoUYVc1hNkIexWxKPP6gujwuHZ17n40kgoSqUc"
    if token == "":
        return JsonResponse({'error': 'Token not generated'}, status=500)
    
    print("token : ",token)

    # Obtenir le token d'accès
    headers['Authorization'] = "Bearer " + token

    print("headers : ",headers)

    # Créer le corps de la requête
    transactionId = generate_reference(32, type="transaction")

    # Créer l'objet Transaction
    transaction = Transaction.objects.filter(transaction_id= transactionId).first()

    if not transaction:
        transaction = Transaction()
        transactionId = generate_reference(32, type="transaction")
        transaction.transaction_id= transactionId

    transaction.currency = "XOF"
    transaction.amount = invoice.total_amount
    transaction.fees = 0
    transaction.amount_receive =0
    transaction.amount_total =0
    transaction.phone = pharmacie.numero_contact_pharmacie
    transaction.status = "PENDING"
    transaction.type_transaction = "transfer"
    transaction.operator = None
    transaction.invoice = invoice
    transaction.save()
    print("transaction : ",transaction)

    # Créer le corps de la requête
    payload = {
        "transactionId": transactionId,
        "customer": {
            "lastName": pharmacie.user.username,
            "firstName": pharmacie.nom_pharmacie,
            "phone": pharmacie.numero_contact_pharmacie,
            "address": {
                "countryCode": "CI",
                "city": pharmacie.ville_pharmacie,
                "streetAddress": pharmacie.adresse_pharmacie
            }
        },
        "recipient": pharmacie.numero_contact_pharmacie,
        "amount": str(invoice.total_amount),
        "currency": "XOF",
        "operator": "WAVE_MONEY_CI" #ORANGE_MONEY_CI, MTN_MONEY_CI, WAVE_MONEY_CI
    }

    print("payload : ",payload)

    try:
        response = requests.post(url,  json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

    data = response.json()
    if data['statusCode'] == 200 and data['data']['status'] == "SUCCESSFUL":
        # Créer ou mettre à jour la transaction dans la base de données
        transaction, created = Transaction.objects.get_or_create(
            transaction_id=data['data']['transactionId']
        )
        transaction.ref = data['data']['ref']
        transaction.currency = data['data']['currency']
        transaction.amount = data['data']['amount']
        transaction.fees = data['data']['fees']
        transaction.amount_receive = data['data']['amountReceive']
        transaction.amount_total = data['data']['amountTotal']
        transaction.phone = data['data']['phone']
        transaction.status = data['data']['status']
        transaction.type_transaction = data['data']['typeTransaction']
        transaction.operator = data['data']['operator']
        transaction.invoice = invoice
        transaction.created_at = data['data']['createdAt']
        transaction.save()

        ####### Mis ajour du wallet  ###########
        wallet, is_new = get_or_create_wallet_pharmacie(pharmacie.pk)
        amount = Decimal(str(invoice.total_amount))
        

        # Mise à jour du solde
        wallet.old_balance = wallet.balance
        wallet.balance -= amount
        wallet.save()
        
        # Création de l'historique
        action_type = 'retrait'
        label = 'Versement de la facture numero #'+ str(invoice.pk)
        WalletPharmacieHistory.objects.create(
            wallet=wallet,
            action_type=action_type,
            label=label,
            amount=amount,
            new_balance=wallet.balance
        )

        notification = Notification.objects.create(
            title = "Versement effectué",
            message = 'Flavy a effectué votre versement pour la facture numero #'+ str(invoice.pk),
            type = "payment",
            data_id = invoice.id,
            metadata = InvoiceSerializer(invoice, many=False).data,
            is_read = False,
            user_type = 'pharmacie',
            user_id = pharmacie.user.id
        )

        # SEND SMS
        if pharmacie.numero_contact_pharmacie:
            send_sms_jetfy(pharmacie.numero_contact_pharmacie, notification.message)

        return JsonResponse({'message': 'Transfert réussi'}, status=200)
       
    else:
        transaction, created = Transaction.objects.get_or_create(
            transaction_id=transactionId
        )
        transaction.status = "FAILED"
        transaction.save()
        return JsonResponse({'error': 'Erreur de transfert'}, status=400)
    

# def generateToken():
#     url = 'https://api.digitalpaye.com/v1/auth'
#     payload = ''
#     headers = {
#         'X-Environment': 'Production',
#         'Accept-Language': 'en',
#         'Authorization': 'Basic bGl2ZV9kaWdpdGFscGF5ZTk2NjM4MDo0NDliNjhiZi0xZWU5LTQwN2ItYTRiYS01YjU3ZDdiZGRhOTY='
#     }

#     response = requests.request("POST", url, headers=headers, data=payload, verify=True)
#     response.raise_for_status()
  
#     if response.status_code == 200:
#         data = response.json()
#         token = data['data']['token']
#         return token
#     else:
#         return ""
    

def generateToken():
    url = 'https://api.digitalpaye.com/v1/auth'
    payload = ''
    headers = {
        'X-Environment': 'Production',
        'Accept-Language': 'en',
        'Authorization': 'Basic bGl2ZV9kaWdpdGFscGF5ZTk2NjM4MDo0NDliNjhiZi0xZWU5LTQwN2ItYTRiYS01YjU3ZDdiZGRhOTY=',
        'Content-Type': 'application/json; charset=utf-8',  # ou 'text/plain' si vous n'envoyez pas de JSON
        'Accept': 'application/json; charset=utf-8'  # ou 'text/plain' si vous n'envoyez pas de JSON
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, verify=True)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
        return ""

    if response.status_code == 200:
        data = response.json()
        token = data['data']['token']
        return token
    else:
        return ""