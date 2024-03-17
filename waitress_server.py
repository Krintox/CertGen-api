import main
from waitress import serve
serve(main.app, host='0.0.0.0', port=8080)