di gitbash
https://github.com/Dswl1/gallery_creative.git
cd gallery_creative
pip install Flask
python3 -m venv .venv

di terminal vscode
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\activate                                                 

migrate db:
py setup.py

Nyalain server:
py main.py
