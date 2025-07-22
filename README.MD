# Pour faire fonctionner SmartFixApi
    se positionner dans le dossier SmartFixApi  :
        python -m venv .venv_api
        python source .venv_api/bin/activate
        pip install -r requirements.txt

    mais aussi : installation de Ollama nécessaire :
        page de téléchargement : https://ollama.com/download

    vérifier la présence du modèle sur la machine : 
        ollama --version

    le modèle utilisé sera llama3.2:3b
        ollama pull llama3.2:3b
        
    executer le script :
        test_file.ipynb 
        (changer la valeur force_initialize à True, la première fois pour générer chroma_db.
          Attention le chargement des documents pdf est long)

    lancer l'appli : 
        uvicorn main:app --reload --port 8080


# Pour faire fonctionner SmartFixWeb (ouvrir un second projet)
    se positionner dans le dossier SmartFixWeb
        python -m venv .venv_web
        python source .venv_web/bin/activate
        pip install -r requirements.txt

    initialiser la base de données 
        python manage.py makemigrations
        python manage.py migrate

    créer un admin
        python manage.py createsuperuser
        (adresse : http://127.0.0.1:8000/admin)

    lancer l'appli :
        python manage.py runserver  
        (adresse : http://127.0.0.1:8000)


# (Optionnel) Pour faire fonctionner Workflows_init
    se positionner dans le dossier Workflows_init
        python -m venv .venv_wkf
        python source .venv_wkf/bin/activate
        pip install -r requirements.txt