import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from .models.rag_messsage_model import SfRagMessage, SfTicket
from .LLM.chat_bot import SfChatBot
from .LLM.llama_constant import LLamaConstant

def default_view(request):
    # Récupérer les messages pour les statistiques
    messages = request.session.get('messages', [])
    context = {'messages': messages}
    return render(request, 'MainWebApp/default.html', context)

def chat_ticket_view(request):
    tickets = SfTicket.objects.all()
    selected_ticket = None

    if request.method == 'POST':
        selected_ticket_id = request.POST.get('ticket')
        if selected_ticket_id:
            selected_ticket = SfTicket.objects.get(id=selected_ticket_id)
            request.session['selected_ticket_id'] = selected_ticket_id

    return render(request, 'MainWebApp/chat_page.html', {
        'tickets': tickets,
        'selected_ticket': selected_ticket
    })

def chat_view(request):
    # Récupérer ou créer l'historique des messages (utiliser la session)
    if 'messages' not in request.session:
        request.session['messages'] = []  

    ticket_id = request.session.get('selected_ticket_id', 1)
    selected_ticket = SfTicket.objects.get(id=ticket_id)
    ticket_staff_id = selected_ticket.staff_id
    assistant_id = 2
    
    rag_messages = SfRagMessage.objects.filter(ticket_id=1).order_by('date_message')
    rag_messages = list(rag_messages)

    user_bot_history = []
    for rag_message in rag_messages :

        if rag_message.staff_id == ticket_staff_id :
            history_user = LLamaConstant.USER.value
        elif rag_message.staff_id == 2 :
            history_user = LLamaConstant.ASSISTANT.value
        else :
            raise Exception("En cours de développement")
                
        user_bot_history.append({
            LLamaConstant.ROLE.value: history_user, 
            LLamaConstant.CONTENT.value: rag_message.message_text
        })
                  
    if len(request.session['messages'])==0:
        for rag_message in rag_messages :
            match rag_message.staff_id :
                case 1 :
                    session_message = {}
                    session_message['user_message'] = rag_message.message_text            
                case 2 : 
                    session_message['bot_response'] = rag_message.message_text
                    request.session['messages'].append(session_message)
                case _ : 
                    raise Exception("En cours de développement")
    
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:

            # Enregistrer dans la BDD
            new_question = SfRagMessage.objects.create(
                message_text = user_message,
                staff_id = 1, 
                ticket_id = 1  
            )

            chat_bot = SfChatBot()
            chat_bot.set_history(user_bot_history)

            bot_message = None
            try :
                # Obtenir la réponse du chatbot 
                bot_response = chat_bot.execute(user_message)
                bot_role = bot_response['role']
                bot_message = bot_response['content']

            except Exception as exc:
                raise exc
            
            if bot_message :
                # Enregistrer dans la BDD
                new_answer = SfRagMessage.objects.create(
                    message_text = bot_message,
                    staff_id = 2, 
                    ticket_id=1  
                )
            
            # Ajouter à la session
            request.session['messages'].append({
                'user_message': user_message,
                'bot_response': bot_message
            })
            request.session.modified = True
            
            # Rediriger pour éviter la resoumission du formulaire
            return redirect('chat')
    
    context = {
        'messages': request.session.get('messages', [])
    }
    return render(request, 'MainWebApp/chat_page.html', context)



