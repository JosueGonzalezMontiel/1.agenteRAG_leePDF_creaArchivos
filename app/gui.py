import flet as ft
import asyncio
from app.memory import cargar_memoria, guardar_memoria, limitar_historial, resumir_si_necesario
from app.llm import generar_respuesta
from app.agent import procesar_respuesta

def main(page: ft.Page):
    # 1. Page & Font setup
    page.fonts = {
        "Space Grotesk": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap"
    }
    page.title = "A.code AI Agent"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(font_family="Space Grotesk")
    page.window.width = 1100
    page.window.height = 700

    # 2. Colors & Design Tokens
    c_bg_top = "#07070a"
    c_bg_bottom = "#0f1118"
    c_text_main = "#eef1f7"
    c_text_muted = "#b7eef1f7"
    c_accent_1 = "#81c718" # Verde Primario
    c_accent_2 = "#ff8a00" # Naranja 
    
    c_glass_bg = "#d81b202c" # rgba(27, 32, 44, 0.85)
    c_glass_border = "#14ffffff" # Borde sutil
    c_glass_border_hover = "#26ffffff" # Borde activo
    c_shadow = "#59000000" # Sombra profunda

    anim_slow = ft.Animation(700, ft.AnimationCurve.EASE_OUT)
    anim_fast = ft.Animation(250, ft.AnimationCurve.EASE_OUT)

    # 3. Mesh Gradient Background
    mesh_bg = ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(0, -1),   # top_center
            end=ft.Alignment(0, 1),      # bottom_center
            colors=[c_bg_top, c_bg_bottom]
        )
    )

    light_orange = ft.Container(
        width=700, height=700,
        gradient=ft.RadialGradient(colors=["#2dff8a00", ft.Colors.TRANSPARENT]),
        offset=ft.Offset(-0.2, -0.2), # Esquina superior izq
        opacity=0.8
    )
    
    light_green = ft.Container(
        width=600, height=600,
        gradient=ft.RadialGradient(colors=["#2881c718", ft.Colors.TRANSPARENT]),
        offset=ft.Offset(1.0, 0.6), # Borde inferior der
        opacity=0.7
    )

    # 4. Glassmorphism Utilities
    def make_glass_card(content, padding, expand=False, radii=22):
        return ft.Container(
            content=content,
            bgcolor=c_glass_bg,
            border=ft.Border.all(1, c_glass_border),
            border_radius=radii,
            padding=padding,
            expand=expand,
            blur=ft.Blur(15, 15, ft.BlurTileMode.MIRROR),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=50, color=c_shadow, offset=ft.Offset(0, 18)),
            animate=anim_fast,
            animate_scale=anim_fast,
            on_hover=lambda e: hover_card(e)
        )
        
    def hover_card(e):
        e.control.scale = 1.01 if e.data == "true" else 1.0
        e.control.border = ft.Border.all(1, c_glass_border_hover if e.data == "true" else c_glass_border)
        e.control.update()
        
    def hover_btn(e):
        e.control.scale = 1.05 if e.data == "true" else 1.0
        e.control.update()

    # 5. UI Elements
    messages_column = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
    
    txt_input = ft.TextField(
        hint_text="Comunícate con tu agente aquí...",
        hint_style=ft.TextStyle(color=c_text_muted, size=15),
        expand=True,
        border=ft.InputBorder.NONE,
        color=c_text_main,
        cursor_color=c_accent_1,
        content_padding=ft.Padding.symmetric(horizontal=15, vertical=12),
        on_submit=lambda e: send_message()
    )
    
    btn_send = ft.Container(
        content=ft.Icon(ft.Icons.ARROW_UPWARD_ROUNDED, color=c_bg_top, size=24),
        bgcolor=c_accent_1,
        width=45, height=45,
        alignment=ft.Alignment(0, 0),
        border_radius=50,
        on_click=lambda e: send_message(),
        animate_scale=anim_fast,
        on_hover=hover_btn
    )

    # Input Pill
    input_card = ft.Container(
        content=ft.Row([txt_input, btn_send], spacing=0, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=c_glass_bg,
        border=ft.Border.all(1, c_glass_border),
        border_radius=50,
        padding=ft.Padding(10, 6, 6, 6),
        blur=ft.Blur(15, 15, ft.BlurTileMode.MIRROR),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=20, color=c_shadow, offset=ft.Offset(0, 8)),
    )
    
    chat_area = ft.Column([
        make_glass_card(messages_column, padding=30, expand=True),
        input_card
    ], expand=True, spacing=25)

    # Sidebar
    logo_text = ft.Text(
        spans=[
            ft.TextSpan("A.", style=ft.TextStyle(color=c_text_main)),
            ft.TextSpan("code", style=ft.TextStyle(color=c_accent_2))
        ],
        size=36, weight=ft.FontWeight.BOLD
    )

    btn_new = ft.Container(
        content=ft.Text("Nuevo chat", color=c_bg_top, weight=ft.FontWeight.BOLD, size=15),
        bgcolor=c_accent_1, 
        alignment=ft.Alignment(0, 0),    # center
        height=50,
        border_radius=50,
        on_click=lambda e: new_chat(),
        animate_scale=anim_fast,
        on_hover=hover_btn
    )
    
    btn_exit = ft.Container(
        content=ft.Text("Salir", color=c_text_main, weight=ft.FontWeight.BOLD, size=15),
        bgcolor="#05ffffff",
        border=ft.Border.all(1, c_glass_border),
        alignment=ft.Alignment(0, 0),    # center
        height=50,
        border_radius=50,
        on_click=lambda e: page.window.close(),
        animate_scale=anim_fast,
        on_hover=hover_btn
    )

    sidebar_col = ft.Column([
        logo_text,
        ft.Divider(height=40, color=c_glass_border),
        btn_new,
        btn_exit
    ], spacing=15)
    
    sidebar = ft.Container(
        content=sidebar_col,
        width=260,
        bgcolor=c_glass_bg,
        border=ft.Border.all(1, c_glass_border),
        border_radius=28,
        padding=30,
        blur=ft.Blur(15, 15, ft.BlurTileMode.MIRROR),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=50, color=c_shadow, offset=ft.Offset(0, 18)),
    )

    main_layout = ft.Row([
        sidebar,
        chat_area
    ], expand=True, spacing=30)
    
    base_content = ft.Container(
        content=main_layout,
        padding=30,
        expand=True
    )

    main_stack = ft.Stack([
        mesh_bg,
        light_orange,
        light_green,
        base_content
    ], expand=True)
    page.add(main_stack)


    # 6. Message Bubble Logic
    def add_message_bubble(role: str, content: str, animate_entrance: bool = True):
        is_user = role == "user"
        bubble_bg = c_accent_1 if is_user else "#181d29"
        bubble_color = c_bg_top if is_user else c_text_main
        border_col = ft.Colors.TRANSPARENT if is_user else c_glass_border
        
        bubble = ft.Container(
            content=ft.Text(content, color=bubble_color, size=15),
            bgcolor=bubble_bg,
            border=ft.Border.all(1, border_col),
            border_radius=ft.BorderRadius(
                top_left=22, top_right=22,
                bottom_left=4 if not is_user else 22,
                bottom_right=22 if not is_user else 4
            ),
            padding=ft.Padding.symmetric(horizontal=22, vertical=16),
            shadow=ft.BoxShadow(blur_radius=15, color=c_shadow, offset=ft.Offset(0, 5)) if not is_user else None,
            animate_offset=anim_slow,
            animate_opacity=anim_slow
        )
        
        wrapper = ft.Row([bubble], alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START)
        
        if animate_entrance:
            bubble.opacity = 0.0
            bubble.offset = ft.Offset(0, 0.4)
            messages_column.controls.append(wrapper)
            page.update()
            
            # Animate in next frame
            bubble.opacity = 1.0
            bubble.offset = ft.Offset(0, 0)
            page.update()
        else:
            messages_column.controls.append(wrapper)
            page.update()

    def new_chat():
        from app.config import MEMORY_FILE
        import os, json
        if os.path.exists(MEMORY_FILE):
             with open(MEMORY_FILE, 'w') as f: json.dump([], f)
        messages_column.controls.clear()
        page.update()

    def send_message():
        text = txt_input.value.strip()
        if not text: return
        txt_input.value = ""
        page.update()
        
        add_message_bubble("user", text)
        
        loader = ft.Container(
            content=ft.ProgressRing(width=20, height=20, stroke_width=2, color=c_accent_2),
            padding=ft.Padding.symmetric(horizontal=10, vertical=10)
        )
        loader_wrapper = ft.Row([loader], alignment=ft.MainAxisAlignment.START)
        messages_column.controls.append(loader_wrapper)
        page.update()
        
        async def process():
            msgs = cargar_memoria()
            
            SYSTEM_PROMPT = """
            Eres un asistente que habla español y es concreto.

            Tienes acceso a las siguientes herramientas:
            1. Listar archivos
            2. Leer archivos
            3. Editar o crear archivos
            4. Consultar información de documentos PDF (RAG)

            REGLAS:
            - Si el usuario pide ver archivos, listar directorios, leer código, editar/crear archivos, o buscar información en PDFs, SIEMPRE debes usar la herramienta correspondiente.
            - NO respondas con texto normal en esos casos.
            - SOLO responde en JSON válido EXACTAMENTE en estos formatos, según lo que necesites hacer:

            Para listar archivos:
            {"tool": "list_files", "directory": "ruta"}

            Para leer un archivo:
            {"tool": "read_file", "file_path": "ruta"}

            Para editar o crear un archivo:
            {"tool": "edit_file", "file_path": "ruta", "prev_text": "texto viejo a reemplazar (o null si es nuevo)", "new_text": "texto nuevo"}

            Para leer información de PDFs:
            {"tool": "ask_pdf", "question": "pregunta clara y especifica sobre la informacion que buscas"}

            - IMPORTANTE: Cuando uses "ask_pdf", yo te devolveré un resultado con el contexto de "Fuente principal" y "Fragmento usado". En tu Siguiente Turno, DEBES TRANSCRIBIR EXACTAMENTE el resultado junto a sus fuentes si es la información que el usuario pidió, sin cortarlo ni resumirlo.
            - NO agregues texto adicional ni Markdown extra fuera del JSON cuando llames herramientas.
            - Escribe el código dentro de prev_text y new_text de forma natural.

            Para cualquier otra cosa, responde normal.
            """
            
            has_system = any(m.get("role") == "system" for m in msgs)
            if has_system:
                for m in msgs:
                    if m.get("role") == "system":
                        m["content"] = SYSTEM_PROMPT
                        break
            else:
                msgs.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
                
            msgs.append({"role": "user", "content": text})
            
            # Bucle React para herramientas
            while True:
                msgs = resumir_si_necesario(msgs)
                msgs = limitar_historial(msgs)
                
                completion = generar_respuesta(msgs, stream=False)
                raw = completion.choices[0].message.content
                tiene_tools, respuesta_final = procesar_respuesta(raw, msgs)
                
                if tiene_tools:
                    # Guardamos intención JSON
                    msgs.append({"role": "assistant", "content": raw})
                    
                    # Le pasamos el resultado a la siguiente vuelta
                    msgs.append({
                        "role": "user", 
                        "content": f"Resultado de herramientas:\n{respuesta_final}\n\nCon base en esto, ¿cuál es tu siguiente paso? (escribe JSON si usas otra herramienta; si no, responde al usuario incluyendo las fuentes copiadas exactamente igual si usaste ask_pdf)"
                    })
                else:
                    if loader_wrapper in messages_column.controls:
                        messages_column.controls.remove(loader_wrapper)
                    
                    add_message_bubble("assistant", respuesta_final)
                    msgs.append({"role": "assistant", "content": respuesta_final})
                    guardar_memoria(msgs)
                    break
        
        asyncio.create_task(process())


    # 7. Splash Screen Logic
    splash = ft.Container(
        expand=True,
        bgcolor="#eb07070a", # 92% dark overlay
        blur=ft.Blur(12, 12, ft.BlurTileMode.MIRROR),
        content=ft.Column([
            ft.Text(
                spans=[
                    ft.TextSpan("A.", style=ft.TextStyle(color=c_text_main)),
                    ft.TextSpan("code", style=ft.TextStyle(color=c_accent_2))
                ],
                size=64, weight=ft.FontWeight.BOLD
            ),
            ft.Container(height=30),
            ft.ProgressRing(color=c_accent_1, stroke_width=4, width=50, height=50)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        animate_opacity=anim_slow,
        alignment=ft.Alignment(0, 0)     # center
    )
    
    main_stack.controls.append(splash)
    page.update()

    async def init_app():
        msgs = cargar_memoria()
        for msg in msgs:
            if msg.get("role") in ["user", "assistant"]:
                add_message_bubble(msg["role"], msg["content"], animate_entrance=False)
        
        await asyncio.sleep(1.2) # Show off the splash screen
        splash.opacity = 0.0
        page.update()
        await asyncio.sleep(0.7)
        main_stack.controls.remove(splash)
        page.update()

    asyncio.create_task(init_app())

if __name__ == "__main__":
    ft.run(main)
