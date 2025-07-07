import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .models.rag_messsage_model import SfRagMessage
from .LLM.chat_bot import SfChatBot

def default_view(request):
    # Récupérer les messages pour les statistiques
    messages = request.session.get('messages', [])
    context = {'messages': messages}
    return render(request, 'MainWebApp/default.html', context)

def chat_view(request):
    # Récupérer ou créer l'historique des messages (utiliser la session)
    if 'messages' not in request.session:
        request.session['messages'] = []  

    if len(request.session['messages'])==0:
        ticket_id = 1
        user_id = 1
        assistant_id = 2
        rag_messages = SfRagMessage.objects.filter(ticket_id=1).order_by('date_message')
        rag_messages = list(rag_messages)
        user_bot_history = []
        for rag_message in rag_messages :
            match rag_message.staff_id :
                case 1 :
                    session_message = {}
                    session_message['user_message'] = rag_message.message_text
                    user_bot_history.append({"role": "user", "content": rag_message.message_text})
                case 2 : 
                    session_message['bot_response'] = rag_message.message_text
                    request.session['messages'].append(session_message)
                    user_bot_history.append({"role": "assistant", "content": rag_message.message_text})
                case _ : 
                    raise Exception("En cours de développement")
    
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:

            chat_bot = SfChatBot()
            chat_bot.set_history(user_bot_history)

            # Obtenir la réponse du chatbot 
            bot_response = chat_bot.execute(user_message)
            bot_role = bot_response['role']
            bot_message = bot_response['content']

            # Enregistrer dans la BDD
            new_message = SfRagMessage.objects.create(
                message_text = bot_message,
                staff_id = 2, 
                ticket_id=1  
            )
            
            # Ajouter à la session
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
    return render(request, 'MainWebApp/chat_page.html', context)

def process_message(message):
    
    ticket_id = 1
    user_id = 1
    assistant_id = 1

    return "pas de message pour l'instant"


