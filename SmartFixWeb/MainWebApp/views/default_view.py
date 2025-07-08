from django.shortcuts import render


def show_default_view(request):
    # Récupérer les messages pour les statistiques
    messages = request.session.get('messages', [])
    context = {'messages': messages}
    return render(request, 'MainWebApp/default.html', context)