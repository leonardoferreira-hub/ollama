#!/usr/bin/env python3
"""
Servidor HTTP simples para o Gerenciador de Sugestões de Cláusulas
"""
import http.server
import socketserver
import os
import sys

# Mudar para o diretório dos documentos GOLD
os.chdir('/home/user/webapp/documentos_gold')

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Adicionar headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Log colorido
        sys.stdout.write(f"\033[92m[SERVER]\033[0m {format % args}\n")
        sys.stdout.flush()

def main():
    print("=" * 80)
    print("🚀 SERVIDOR DO GERENCIADOR DE SUGESTÕES - DOCUMENTOS GOLD")
    print("=" * 80)
    print()
    print(f"📁 Diretório: /home/user/webapp/documentos_gold")
    print(f"🌐 Porta: {PORT}")
    print()
    print("✅ Servidor iniciado com sucesso!")
    print()
    print("📝 Para acessar o gerenciador:")
    print(f"   → http://localhost:{PORT}/gerenciar_sugestoes.html")
    print()
    print("⚠️  Pressione Ctrl+C para parar o servidor")
    print("=" * 80)
    print()
    
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Servidor encerrado pelo usuário")
            print("=" * 80)
            sys.exit(0)

if __name__ == '__main__':
    main()
