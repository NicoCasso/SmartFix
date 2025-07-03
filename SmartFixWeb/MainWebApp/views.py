import requests
from django.http import JsonResponse
from django.shortcuts import render

def default_view(request):
    return render(request, 'MainWebApp/default.html')

def chat_request(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')

        # Remplacez 'YOUR_API_KEY' par votre clé API réelle et 'API_ENDPOINT' par l'URL de l'API
        api_key = 'YOUR_API_KEY'
        api_endpoint = 'API_ENDPOINT'

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'prompt': user_message,
            'max_tokens': 150  # Ajustez selon vos besoins
        }

        response = requests.post(api_endpoint, headers=headers, json=data)

        if response.status_code == 200:
            response_data = response.json()
            response_message = response_data.get('choices', [{}])[0].get('text', 'Désolé, je n\'ai pas pu générer de réponse.')
        else:
            response_message = "Désolé, je n'ai pas pu obtenir de réponse."

        return JsonResponse({'message': response_message})

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
