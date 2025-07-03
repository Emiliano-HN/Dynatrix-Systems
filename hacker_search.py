#!/usr/bin/env python3
import curses
import webbrowser
import urllib.parse
import datetime
import os
import json
import sys
import signal

SEARCH_ENGINES = {
    "1": ("Google", "https://www.google.com/search?q={}"),
    "2": ("DuckDuckGo", "https://duckduckgo.com/?q={}"),
    "3": ("Shodan", "https://www.shodan.io/search?query={}"),
    "4": ("GitHub", "https://github.com/search?q={}"),
}

LOGO = r"""

  ██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗      ██████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗  
██║ ██╔╝██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
  █████╔╝ ███████║██║     █████╔╝ █████╗  ██████╔╝    ╚█████╗ █████╗  ███████║██████╔╝██║     ███████║  
 ██╔═██╗ ██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗     ╚═══██╗██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║ 
 ██║  ██╗██║  ██║╚██████╗██║  ██╗███████╗██║  ██║    ██████╔╝███████╗██║  ██║██║  ██║╚██████╗██║  ██║ 
 ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ 
"""

LOGOS_POR_ENGINE = {
    "1": r""" 
  ██████╗  ██████╗  ██████╗  ██████╗ ██╗     ███████╗
   ██╔════╝ ██╔═══██╗██╔═══██╗██╔════╝ ██║     ██╔════╝  
  ██║  ███╗██║   ██║██║   ██║██║  ███╗██║     █████╗   
   ██║   ██║██║   ██║██║   ██║██║   ██║██║     ██╔══╝    
   ╚██████╔╝╚██████╔╝╚██████╔╝╚██████╔╝███████╗███████╗
    ╚═════╝  ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
 """,  
    "2": r""" 
██████╗ ██╗   ██╗ ██████╗██╗  ██╗██████╗ ██╗   ██╗ ██████╗██╗  ██╗██████╗  ██████╗ 
██╔══██╗██║   ██║██╔════╝██║ ██╔╝██╔══██╗██║   ██║██╔════╝██║ ██╔╝██╔══██╗██╔═══██╗
██║  ██║██║   ██║██║     ████╔╝  ██║  ██║██║   ██║██║     ████╔╝  ██║  ██║██║   ██║
██║  ██║██║   ██║██║     ██╔═██╗ ██║  ██║██║   ██║██║     ██╔═██╗ ██║  ██║██║   ██║
██████╔╝╚██████╔╝╚██████╗██║  ██╗██████╔╝╚██████╔╝╚██████╗██║  ██╗██████╔╝╚██████╔╝
╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ 
 """,
    "3": r""" 
 ██████╗██╗  ██╗ ██████╗ ██████╗  █████╗ ███╗   ██╗
██╔════╝██║  ██║██╔═══██╗██╔══██╗██╔══██╗████╗  ██║
╚█████╗ ███████║██║   ██║██║  ██║███████║██╔██╗ ██║
 ╚═══██╗██╔══██║██║   ██║██║  ██║██╔══██║██║╚██╗██║
██████╔╝██║  ██║╚██████╔╝██████╔╝██║  ██║██║ ╚████║
╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝

 """,
    "4": r""" 
  ██████╗ ██╗████████╗██╗  ██╗██╗   ██╗██████╗ 
 ██╔════╝ ██║╚══██╔══╝██║  ██║██║   ██║██╔══██╗
 ██║  ███╗██║   ██║   ███████║██║   ██║██████╔╝
  ██║   ██║██║   ██║   ██╔══██║██║   ██║██╔═══██╗
 ╚██████╔╝██║   ██║   ██║  ██║╚██████╔╝██████╔╝
    ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝   
 """
}

HISTORY_DIR = os.path.expanduser("~/.hacker_search_history")

class HackerSearch:
    def __init__(self):
        self.stdscr = None
        self.running = True
        
    def signal_handler(self, signum, frame):
        """Maneja la señal de interrupción del teclado"""
        self.running = False
        self.cleanup()
        sys.exit(0)
        
    def cleanup(self):
        """Limpia recursos de curses de forma segura"""
        if self.stdscr:
            try:
                curses.nocbreak()
                self.stdscr.keypad(False)
                curses.echo()
                # Solo llamar endwin() cuando realmente vamos a salir
                curses.endwin()
            except:
                pass
            self.stdscr = None

    def ensure_history_dir(self):
        """Crea el directorio de historial si no existe"""
        try:
            if not os.path.exists(HISTORY_DIR):
                os.makedirs(HISTORY_DIR)
            return True
        except OSError as e:
            self.show_error(f"Error creando directorio de historial: {e}")
            return False

    def history_file(self, engine_key):
        """Retorna la ruta del archivo de historial para un motor específico"""
        return os.path.join(HISTORY_DIR, f"history_{engine_key}.json")

    def load_history(self, engine_key):
        """Carga el historial de búsquedas para un motor específico"""
        try:
            with open(self.history_file(engine_key), "r", encoding='utf-8') as f:
                data = json.load(f)
                # Validar que los datos tienen el formato correcto
                if isinstance(data, list):
                    return [item for item in data if isinstance(item, dict) and 'query' in item and 'date' in item]
                return []
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

    def save_history(self, engine_key, history):
        """Guarda el historial de búsquedas para un motor específico"""
        try:
            with open(self.history_file(engine_key), "w", encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            return True
        except OSError as e:
            self.show_error(f"Error guardando historial: {e}")
            return False

    def add_to_history(self, engine_key, query):
        """Añade una consulta al historial"""
        if not self.ensure_history_dir():
            return False
        
        # Limpiar la consulta
        query = query.strip()
        if not query:
            return False
            
        history = self.load_history(engine_key)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Evitar duplicados (buscar en las últimas 3 entradas)
        recent_queries = [item["query"] for item in history[-3:]]
        if query in recent_queries:
            return True
        
        history.append({"query": query, "date": now})
        
        # Mantener solo las últimas 20 búsquedas
        if len(history) > 20:
            history = history[-20:]
        
        return self.save_history(engine_key, history)

    def draw_safe(self, y, x, text, attr=0):
        """Dibuja texto de forma segura sin errores de curses"""
        if not self.stdscr:
            return
        try:
            h, w = self.stdscr.getmaxyx()
            if y >= h or y < 0 or x < 0:
                return
            # Truncar texto si es necesario
            max_len = max(0, w - x - 1)
            if len(text) > max_len:
                text = text[:max_len]
            if text:
                if attr:
                    self.stdscr.attron(attr)
                self.stdscr.addstr(y, x, text)
                if attr:
                    self.stdscr.attroff(attr)
        except curses.error:
            pass

    def draw_logo(self, start_y=0):
        """Dibuja el logo principal"""
        lines = LOGO.strip('\n').split('\n')
        h, w = self.stdscr.getmaxyx()
        
        for i, line in enumerate(lines):
            if start_y + i >= h:
                break
            x = max((w - len(line)) // 2, 0)
            self.draw_safe(start_y + i, x, line, curses.color_pair(3))

    def draw_menu(self, selected_row_idx, start_y):
        """Dibuja el menú de selección de motores de búsqueda"""
        h, w = self.stdscr.getmaxyx()
        
        if start_y >= h - 1:
            return
        
        self.draw_safe(start_y, 2, "Selecciona motor de búsqueda (usa flechas y Enter):", 
                      curses.color_pair(4) | curses.A_BOLD)
        
        for idx, key in enumerate(SEARCH_ENGINES.keys()):
            engine_name = SEARCH_ENGINES[key][0]
            x = 4
            y = start_y + 2 + idx
            
            if y >= h - 1:
                break
                
            text = f"{key}. {engine_name}"
            attr = curses.color_pair(1) if idx == selected_row_idx else 0
            self.draw_safe(y, x, text, attr)
        
        self.draw_safe(h-2, 2, "Presiona 'q' para salir completamente | ESC para regresar", curses.color_pair(4))

    def draw_query_screen(self, engine_key, engine_name, history, selected_hist_idx, input_str):
        """Dibuja la pantalla de entrada de consulta"""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        # Dibujar logo específico del motor
        logo_height = 0
        if engine_key in LOGOS_POR_ENGINE:
            logo_lines = LOGOS_POR_ENGINE[engine_key].strip('\n').split('\n')
            for i, line in enumerate(logo_lines):
                if i >= h - 1:
                    break
                x = max((w - len(line)) // 2, 0)
                self.draw_safe(i, x, line, curses.color_pair(3))
            logo_height = min(len(logo_lines), h - 10)

        # Header
        header = f"Hacker Search - {engine_name}"
        header_y = logo_height + 1
        if header_y < h - 1:
            x = max(w//2 - len(header)//2, 0)
            self.draw_safe(header_y, x, header, curses.color_pair(2) | curses.A_BOLD)

        # Campo de búsqueda
        prompt = "Buscar ➤ "
        search_y = logo_height + 3
        if search_y < h - 1:
            max_input_len = max(0, w - len(prompt) - 5)
            display_input = input_str[-max_input_len:] if len(input_str) > max_input_len else input_str
            
            if selected_hist_idx == -1:
                self.draw_safe(search_y, 2, prompt, curses.color_pair(1))
                self.draw_safe(search_y, 2 + len(prompt), display_input, curses.color_pair(1))
            else:
                self.draw_safe(search_y, 2, prompt, curses.color_pair(4) | curses.A_BOLD)
                self.draw_safe(search_y, 2 + len(prompt), display_input)

        # Título del historial
        hist_title_y = search_y + 2
        if hist_title_y < h - 1 and history:
            self.draw_safe(hist_title_y, 2, "Historial de búsquedas recientes (flechas ↑↓ y Enter):", 
                          curses.color_pair(4) | curses.A_BOLD)

        # Historial
        if history:
            start_y = hist_title_y + 2
            max_hist = min(10, len(history), h - start_y - 3)
            
            for i in range(max_hist):
                y = start_y + i
                if y >= h - 2:
                    break
                    
                item = history[-(i+1)]
                query_text = item["query"]
                date_text = item["date"]
                line = f"{query_text}  ({date_text})"
                
                max_line_len = w - 10
                if len(line) > max_line_len:
                    line = line[:max_line_len-3] + "..."
                
                if i == selected_hist_idx:
                    self.draw_safe(y, 4, "➤ " + line, curses.color_pair(1))
                else:
                    self.draw_safe(y, 6, line)

        # Instrucciones en la parte inferior
        self.draw_safe(h-1, 2, "Enter: buscar | ESC: volver al menú | Ctrl+C: salir", curses.color_pair(4))
        self.stdscr.refresh()

    def query_input_loop(self, engine_key, engine_name):
        """Loop principal para entrada de consultas"""
        curses.curs_set(1)
        input_str = ""
        selected_hist_idx = -1
        history = self.load_history(engine_key)

        while self.running:
            self.draw_query_screen(engine_key, engine_name, history, selected_hist_idx, input_str)
            
            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                curses.curs_set(0)
                return None

            if key == curses.KEY_UP:
                if len(history) > 0:
                    if selected_hist_idx == -1:
                        selected_hist_idx = 0
                        input_str = history[-1]["query"]
                    elif selected_hist_idx < len(history) - 1:
                        selected_hist_idx += 1
                        input_str = history[-(selected_hist_idx + 1)]["query"]
            elif key == curses.KEY_DOWN:
                if len(history) > 0:
                    if selected_hist_idx > 0:
                        selected_hist_idx -= 1
                        input_str = history[-(selected_hist_idx + 1)]["query"]
                    else:
                        selected_hist_idx = -1
                        input_str = ""
            elif key in (10, 13):  # Enter
                if input_str.strip():
                    curses.curs_set(0)
                    return input_str.strip()
            elif key == 27:  # ESC
                curses.curs_set(0)
                return None
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                selected_hist_idx = -1
                input_str = input_str[:-1]
            elif 32 <= key <= 126:  # Caracteres imprimibles
                selected_hist_idx = -1
                input_str += chr(key)
            elif key == 3:  # Ctrl+C
                curses.curs_set(0)
                return None

        curses.curs_set(0)
        return None

    def init_colors(self):
        """Inicializa los colores de curses"""
        if not curses.has_colors():
            return
            
        curses.start_color()
        curses.use_default_colors()
        
        try:
            # Configurar pares de colores de forma segura
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            curses.init_pair(3, curses.COLOR_CYAN, -1)
            curses.init_pair(4, curses.COLOR_WHITE, -1)
        except curses.error:
            pass

    def show_error(self, message):
        """Muestra un mensaje de error y sale del programa"""
        self.cleanup()
        print(f"Error: {message}")

    def show_error_in_screen(self, message):
        """Muestra un error en pantalla sin salir del programa"""
        if not self.stdscr:
            return
        try:
            h, w = self.stdscr.getmaxyx()
            self.stdscr.clear()
            
            # Centrar mensaje de error
            error_lines = [
                "¡ERROR!",
                "",
                message,
                "",
                "Presiona cualquier tecla para continuar..."
            ]
            
            start_y = max(0, h // 2 - len(error_lines) // 2)
            
            for i, line in enumerate(error_lines):
                x = max(0, (w - len(line)) // 2)
                attr = curses.color_pair(1) | curses.A_BOLD if i == 0 else curses.color_pair(4)
                self.draw_safe(start_y + i, x, line, attr)
            
            self.stdscr.refresh()
            self.stdscr.getch()  # Esperar tecla
        except:
            pass

    def show_search_confirmation(self, engine_name, query):
        """Muestra confirmación de búsqueda abierta"""
        if not self.stdscr:
            return
        try:
            h, w = self.stdscr.getmaxyx()
            self.stdscr.clear()
            
            # Mensaje de confirmación
            success_lines = [
                "✓ ¡BÚSQUEDA ABIERTA!",
                "",
                f"Motor: {engine_name}",
                f"Consulta: {query}",
                "",
                "El navegador debería haberse abierto.",
                "",
                "Presiona cualquier tecla para continuar..."
            ]
            
            start_y = max(0, h // 2 - len(success_lines) // 2)
            
            for i, line in enumerate(success_lines):
                x = max(0, (w - len(line)) // 2)
                if i == 0:
                    attr = curses.color_pair(2) | curses.A_BOLD  # Verde
                elif i in [2, 3]:
                    attr = curses.color_pair(3)  # Cyan
                else:
                    attr = curses.color_pair(4)  # Blanco
                self.draw_safe(start_y + i, x, line, attr)
            
            self.stdscr.refresh()
            self.stdscr.getch()  # Esperar tecla
        except:
            pass

    def open_search(self, engine_key, query):
        """Abre la búsqueda en el navegador"""
        try:
            engine_name, url_template = SEARCH_ENGINES[engine_key]
            url = url_template.format(urllib.parse.quote_plus(query))
            
            # Agregar al historial antes de abrir
            self.add_to_history(engine_key, query)
            
            # Abrir navegador sin cerrar la aplicación
            webbrowser.open(url)
            
            # Mostrar mensaje de confirmación en la pantalla
            self.show_search_confirmation(engine_name, query)
            return True
            
        except Exception as e:
            self.show_error_in_screen(f"Error abriendo navegador: {e}")
            return False

    def main_loop(self, stdscr):
        """Función principal del programa"""
        self.stdscr = stdscr
        
        # Configurar curses
        try:
            curses.cbreak()
            stdscr.keypad(True)
            curses.noecho()
            curses.curs_set(0)
            self.init_colors()
        except curses.error as e:
            raise Exception(f"Error inicializando curses: {e}")

        current_row = 0

        while self.running:
            try:
                self.stdscr.clear()
                self.draw_logo(start_y=0)
                self.draw_menu(current_row, start_y=8)
                self.stdscr.refresh()

                key = self.stdscr.getch()

                if key == curses.KEY_UP and current_row > 0:
                    current_row -= 1
                elif key == curses.KEY_DOWN and current_row < len(SEARCH_ENGINES) - 1:
                    current_row += 1
                elif key in [10, 13]:  # Enter
                    selected_key = list(SEARCH_ENGINES.keys())[current_row]
                    engine_name = SEARCH_ENGINES[selected_key][0]

                    query = self.query_input_loop(selected_key, engine_name)
                    if query:
                        # Abrir búsqueda y continuar (no salir)
                        self.open_search(selected_key, query)
                        # Continuar en el loop para volver al menú principal
                        
                elif key in [ord('q'), ord('Q'), 27]:  # q, Q o ESC
                    break
                elif key == 3:  # Ctrl+C
                    break
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.show_error(f"Error inesperado: {e}")
                return

    def run(self):
        """Ejecuta la aplicación"""
        # Verificar que el terminal soporte curses
        if not os.getenv('TERM'):
            print("Error: Variable de entorno TERM no está configurada.")
            print("Ejecuta: export TERM=xterm-256color")
            return
            
        # Configurar manejador de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        
        try:
            # Verificar dimensiones mínimas del terminal
            try:
                curses.setupterm()
                rows, cols = curses.tigetnum('lines'), curses.tigetnum('cols')
                if rows < 20 or cols < 80:
                    print(f"Terminal muy pequeño ({rows}x{cols}). Mínimo requerido: 20x80")
                    print("Redimensiona tu terminal e intenta de nuevo.")
                    return
            except:
                pass  # Continuar si no se puede verificar
                
            curses.wrapper(self.main_loop)
            
        except KeyboardInterrupt:
            print("\nAplicación interrumpida por el usuario.")
        except Exception as e:
            error_msg = str(e)
            if "endwin" in error_msg:
                print("Error de terminal. Intenta:")
                print("1. export TERM=xterm-256color")
                print("2. Redimensiona tu terminal")
                print("3. Ejecuta en un terminal diferente")
            else:
                print(f"Error ejecutando la aplicación: {error_msg}")
        finally:
            self.cleanup()

def main():
    """Punto de entrada principal"""
    app = HackerSearch()
    app.run()

if __name__ == "__main__":
    main()