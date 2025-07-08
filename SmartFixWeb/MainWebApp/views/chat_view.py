import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from ..models.rag_messsage_model import SfRagMessage, SfTicket
from ..LLM.chat_bot import SfChatBot
from ..LLM.llama_constant import LLamaConstant

def show_chat_view(request):
    sf_tickets = SfTicket.objects.all()
    sf_tickets = list(sf_tickets)

    selected_ticket_id = request.session.get('new_ticket_id')
    if request.method == 'POST':
        if not selected_ticket_id : # cas d'un post "changement de ticket" 
            selected_ticket_id = request.POST.get('ticket')
        
        if not selected_ticket_id : # cas d'un post "nouveau message" 
            selected_ticket_id = request.POST.get('embedded_ticket_id')
        
    if not selected_ticket_id :# default
        selected_ticket_id = 1 # 2 is the id of first user for instance ( 2 would be better)

    current_ticket = SfTicket.objects.get(id=selected_ticket_id)
    user_staff_id = current_ticket.staff_id
    assistant_id = 2 # 2 is the id of the bot, for instance ( 1 would be better)
    
    sf_rag_messages = SfRagMessage.objects.filter(ticket_id=current_ticket.id).order_by('date_message')
    sf_rag_messages = list(sf_rag_messages)

    rag_messages_for_view = []
    user_bot_history = []
    for rag_message in sf_rag_messages :

        if rag_message.staff_id == user_staff_id :
            history_user = LLamaConstant.USER.value
            rag_message.is_from_user = True
        elif rag_message.staff_id == assistant_id :
            history_user = LLamaConstant.ASSISTANT.value
            rag_message.is_from_user = False
        else :
            raise Exception("En cours de développement")
        
        rag_messages_for_view.append(rag_message)     
        user_bot_history.append({
            LLamaConstant.ROLE.value: history_user, 
            LLamaConstant.CONTENT.value: rag_message.message_text
        })
                  
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:

            # Enregistrer dans la BDD
            new_question = SfRagMessage.objects.create(
                message_text = user_message,
                staff_id = user_staff_id, 
                ticket_id = current_ticket.id
            )
            new_question.is_from_user = True   
            rag_messages_for_view.append(new_question)
      
            chat_bot = SfChatBot()
            chat_bot.set_history(user_bot_history)

            bot_message = None
            try :
                # Obtenir la réponse du chatbot 
                bot_response = chat_bot.execute(user_message)
                bot_role = bot_response[LLamaConstant.ROLE.value]
                bot_message = bot_response[LLamaConstant.CONTENT.value]

            except Exception as exc:
                raise exc
            
            if bot_message :
                # Enregistrer dans la BDD
                new_answer = SfRagMessage.objects.create(
                    message_text = bot_message,
                    staff_id = assistant_id, 
                    ticket_id= current_ticket.id  
                )
                new_answer.is_from_user = False   
                rag_messages_for_view.append(new_answer)
                
                
    context = {
        'tickets' : sf_tickets,
        'selected_ticket' : current_ticket,
        'rag_messages': rag_messages_for_view
    }
    return render(request, 'MainWebApp/chat_page.html', context)


def new_ticket(request):
    previous_ticket_id = request.GET.get('previous_ticket_id')
    if previous_ticket_id:
        previous_ticket = SfTicket.objects.get(id=previous_ticket_id)

    if not previous_ticket :
        previous_ticket_id = 1 # 2 is the id of first user for instance ( 2 would be better)
        previous_ticket = SfTicket.objects.get(id=previous_ticket_id)
       
    number = SfTicket.objects.count() +1
    title = f"ticket n°{number}"

    new_ticket = SfTicket.objects.create(
        titre = title,
        description = title,
        staff = previous_ticket.staff,
        client = previous_ticket.client,
        workflow = None
    )   
    request.session['new_ticket_id']  = new_ticket.id
    return redirect('chat')

    return render(request, 'MainWebApp/chat_page.html')
