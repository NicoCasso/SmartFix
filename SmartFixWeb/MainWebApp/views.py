import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect

def default_view(request):
    return render(request, 'MainWebApp/default.html')

def chat_request(request):
    # Récupérer ou créer l'historique des messages (vous pouvez utiliser la session)
    if 'messages' not in request.session:
        request.session['messages'] = []
    
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            # Traiter le message avec votre logique de chatbot
            bot_response = process_message(user_message)  # Votre fonction de traitement
            
            # Ajouter à l'historique
            request.session['messages'].append({
                'user_message': user_message,
                'bot_response': bot_response
            })
            request.session.modified = True
            
            # Rediriger pour éviter la resoumission du formulaire
            return redirect('chat')
    
    context = {
        'messages': request.session.get('messages', [])
    }
    return render(request, 'MainWebApp/default.html', context)

def process_message(message):
    # Votre logique de chatbot ici
    # Remplacez 'YOUR_API_KEY' par votre clé API réelle et 'API_ENDPOINT' par l'URL de l'API
    api_key = 'YOUR_API_KEY'
    api_endpoint = 'API_ENDPOINT'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'prompt': message,
        'max_tokens': 150  # Ajustez selon vos besoins
    }

    response = requests.post(api_endpoint, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        response_message = response_data.get('choices', [{}])[0].get('text', 'Désolé, je n\'ai pas pu générer de réponse.')
    else:
        response_message = "Désolé, je n'ai pas pu obtenir de réponse."

    return response_message


