"""
PIER TUI — Interface Textual para a API REST do backend.
Paleta: #FF4FA3 (rosa) / #000000 (preto)
"""

import os
import json
from pathlib import Path

try:
    from drone.network_routes import create_api_session, get_api_source_ip
except ModuleNotFoundError:
    from drone.network_routes import create_api_session, get_api_source_ip

from textual import on, work
from textual.app import App, ComposeResult
from textual.message import Message
from textual.containers import Container, Vertical, Horizontal, Center, VerticalScroll
from textual.widgets import (
    Header, Footer, Input, Button, Label, Static, Rule,
    TabbedContent, TabPane
)
from textual.screen import Screen, ModalScreen

# ─────────────────────────────────────────────────────────────────────────────
# Configurações / helpers de sessão
# ─────────────────────────────────────────────────────────────────────────────

BASE_URL = os.getenv("PIER_API_URL", "http://localhost:5000")
SESSION_FILE = Path.home() / ".pier_session"
API_SESSION = create_api_session()
API_SOURCE_IP = get_api_source_ip()

def save_session(token: str) -> None:
    SESSION_FILE.write_text(json.dumps({"token": token}))

def load_session() -> str | None:
    if SESSION_FILE.exists():
        try:
            return json.loads(SESSION_FILE.read_text()).get("token")
        except json.JSONDecodeError:
            return None
    return None

def clear_session() -> None:
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()

def api_request(method: str, endpoint: str, data: dict | None = None, require_auth: bool = True):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if require_auth:
        token = load_session()
        if token:
            headers["Authorization"] = f"Bearer {token}"
    try:
        response = API_SESSION.request(method, url, headers=headers, json=data, timeout=10)
        try:
            res_json = response.json()
        except Exception:
            res_json = {"message": response.text}
            
        if not response.ok:
            msg = "Erro desconhecido"
            if isinstance(res_json, dict):
                msg = res_json.get("message", res_json.get("msg", "Erro na requisição"))
            return {
                "error": True,
                "status": response.status_code,
                "message": msg,
            }
        return res_json
    except Exception as e:
        message = str(e)
        if API_SOURCE_IP:
            message = f"{message} (PIER_API_SOURCE_IP={API_SOURCE_IP})"
        return {"error": True, "message": message}

# ─────────────────────────────────────────────────────────────────────────────
# Componentes Reutilizáveis
# ─────────────────────────────────────────────────────────────────────────────

class ActionButton(Button):
    """Botão de ação padronizado com estilo rosa e preto."""
    DEFAULT_CSS = """
    ActionButton {
        background: #000000;
        color: #FF4FA3;
        border: solid #FF4FA3;
        margin-right: 1;
        height: 3;
        min-width: 15;
    }
    ActionButton:hover {
        background: #FF4FA3;
        color: #000000;
        text-style: bold;
    }
    """

class SectionToolbar(Horizontal):
    """Barra horizontal para conter os ActionButtons de uma aba."""
    DEFAULT_CSS = """
    SectionToolbar {
        height: auto;
        padding: 1;
        background: #0a0a0a;
        border-bottom: solid #FF4FA3 30%;
    }
    """

class DataCard(Static):
    """Cartão premium para exibir dados da API com cores e bordas estilizadas."""
    DEFAULT_CSS = """
    DataCard {
        background: #111111;
        border: solid #FF4FA3 30%;
        padding: 1 2;
        margin: 1;
        height: auto;
    }
    DataCard:focus, DataCard:hover {
        border: solid #FF4FA3;
        background: #1a0010;
    }
    .card-title {
        color: #FF4FA3;
        text-style: bold;
        border-bottom: solid #FF4FA3 50%;
        margin-bottom: 1;
        width: 100%;
    }
    .card-content {
        color: #cccccc;
    }
    """

    def __init__(self, title: str, data: dict, **kwargs):
        super().__init__(**kwargs)
        self.card_title = title
        self.data = data

    def compose(self) -> ComposeResult:
        yield Static(f" {self.card_title} ", classes="card-title")
        content = ""
        for k, v in self.data.items():
            content += f"[b]{k}:[/b] {v}\n"
        yield Static(content.strip(), classes="card-content")

# ─────────────────────────────────────────────────────────────────────────────

class ValidationCard(Static):
    """Card de scan pendente com botões de Aprovar e Rejeitar inline."""
    DEFAULT_CSS = """
    ValidationCard {
        background: #0d0008;
        border: solid #FF4FA3 60%;
        padding: 1 2;
        margin: 1;
        height: auto;
    }
    ValidationCard:hover {
        border: solid #FF4FA3;
    }
    .vc-title {
        color: #FF4FA3;
        text-style: bold;
        border-bottom: solid #FF4FA3 50%;
        margin-bottom: 1;
        width: 100%;
    }
    .vc-body {
        color: #cccccc;
        margin-bottom: 1;
    }
    .vc-warning {
        color: #ffcc00;
        text-style: bold;
        margin-bottom: 1;
    }
    .vc-actions {
        height: auto;
        align: left middle;
    }
    .btn-aprovar {
        background: #003300;
        color: #00ff88;
        border: solid #00ff88;
        margin-right: 1;
        height: 3;
        min-width: 12;
    }
    .btn-aprovar:hover {
        background: #00ff88;
        color: #000000;
        text-style: bold;
    }
    .btn-rejeitar {
        background: #330000;
        color: #ff4444;
        border: solid #ff4444;
        height: 3;
        min-width: 12;
    }
    .btn-rejeitar:hover {
        background: #ff4444;
        color: #000000;
        text-style: bold;
    }
    """

    class Aprovar(Message):
        def __init__(self, scan_id: str):
            super().__init__()
            self.scan_id = scan_id

    class Rejeitar(Message):
        def __init__(self, scan_id: str):
            super().__init__()
            self.scan_id = scan_id

    def __init__(self, scan: dict, **kwargs):
        super().__init__(**kwargs)
        self.scan = scan

    def compose(self) -> ComposeResult:
        s = self.scan
        sid = str(s.get("id", ""))
        placa = s.get("placa", "N/A")
        match_val = s.get("match", False)
        horario   = str(s.get("horario_scan", ""))
        drone_id  = str(s.get("id_drone", ""))
        imagem    = s.get("imagem_url") or "Sem imagem"
        lat       = s.get("latitude", "—")
        lon       = s.get("longitude", "—")

        yield Static(f" 🔍  Verificar Leitura OCR — Placa Detectada: {placa} ", classes="vc-title")
        body = (
            f"[b]Scan ID:[/b] {sid}\n"
            f"[b]Drone:[/b]   {drone_id}\n"
            f"[b]Horário:[/b] {horario}\n"
            f"[b]Local:[/b]   lat {lat}  lon {lon}\n"
            f"[b]Imagem:[/b]  {imagem}"
        )
        yield Static(body, classes="vc-body")
        with Horizontal(classes="vc-actions"):
            yield Button("✔ OCR Correto",   id=f"aprovar-{sid}",   classes="btn-aprovar")
            yield Button("✘ OCR Errado",    id=f"rejeitar-{sid}",  classes="btn-rejeitar")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid.startswith("aprovar-"):
            self.post_message(self.Aprovar(bid.removeprefix("aprovar-")))
        elif bid.startswith("rejeitar-"):
            self.post_message(self.Rejeitar(bid.removeprefix("rejeitar-")))

# ─────────────────────────────────────────────────────────────────────────────

# Telas Modais (Login e Forms)
# ─────────────────────────────────────────────────────────────────────────────

class LoginScreen(ModalScreen):
    """Modal de autenticação."""
    CSS = """
    LoginScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.90);
    }
    #login-box {
        width: 56;
        height: auto;
        border: heavy #FF4FA3;
        padding: 2 4;
        background: #111111;
    }
    #login-title {
        text-align: center;
        color: #FF4FA3;
        text-style: bold;
        margin-bottom: 1;
    }
    Input {
        margin-bottom: 1;
        border: solid #FF4FA3 40%;
    }
    Input:focus {
        border: solid #FF4FA3;
    }
    #btn-login {
        width: 100%;
        margin-top: 1;
        background: #FF4FA3;
        color: black;
        text-style: bold;
    }
    #login-error {
        color: #FF4FA3;
        text-align: center;
        margin-top: 1;
        display: none;
    }
    #login-error.visible {
        display: block;
    }
    """

    BINDINGS = [("ctrl+s", "screenshot", "Screenshot")]

    def action_screenshot(self) -> None:
        path = self.app.save_screenshot()
        self.app.notify(f"Screenshot salvo: {path}", title="Screenshot")

    def compose(self) -> ComposeResult:
        with Vertical(id="login-box"):
            yield Static("🛩  PIER LOGIN", id="login-title")
            yield Input(placeholder="E-mail", id="input-email")
            yield Input(placeholder="Senha", password=True, id="input-password")
            yield Button("Entrar", id="btn-login")
            yield Label("", id="login-error")

    @on(Button.Pressed, "#btn-login")
    def handle_login(self) -> None:
        email = self.query_one("#input-email", Input).value.strip()
        password = self.query_one("#input-password", Input).value
        res = api_request("POST", "/api/auth/login", {"email": email, "password": password}, require_auth=False)
        if isinstance(res, dict) and res.get("error"):
            lbl = self.query_one("#login-error", Label)
            lbl.update(f"⚠  {res.get('message', 'Falha ao autenticar.')}")
            lbl.add_class("visible")
            return
        token = res.get("token") or res.get("access_token")
        if token:
            save_session(token)
            self.dismiss(True)


class InputModal(ModalScreen[dict | None]):
    """Modal genérico para formulários pequenos."""
    CSS = """
    InputModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.90);
    }
    #form-box {
        width: 60;
        height: auto;
        border: heavy #FF4FA3;
        padding: 2;
        background: #111111;
    }
    .form-title {
        color: #FF4FA3;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    .form-input {
        margin-bottom: 1;
        border: solid #FF4FA3 50%;
    }
    .form-input:focus {
        border: solid #FF4FA3;
    }
    .form-btn-container {
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    .form-btn {
        margin: 0 1;
        background: #FF4FA3;
        color: black;
        text-style: bold;
    }
    .form-btn-cancel {
        background: #333333;
        color: white;
    }
    """

    def __init__(self, title: str, fields: list[dict]):
        super().__init__()
        self.form_title = title
        self.fields = fields  # list of dicts: {"id": "field_id", "label": "Placeholder"}

    def compose(self) -> ComposeResult:
        with Vertical(id="form-box"):
            yield Static(self.form_title, classes="form-title")
            for field in self.fields:
                yield Input(placeholder=field["label"], id=field["id"], classes="form-input")
            with Horizontal(classes="form-btn-container"):
                yield Button("Cancelar", id="btn-cancel", classes="form-btn form-btn-cancel")
                yield Button("Salvar", id="btn-save", classes="form-btn")

    @on(Button.Pressed, "#btn-cancel")
    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-save")
    def action_save(self) -> None:
        result = {}
        for field in self.fields:
            result[field["id"]] = self.query_one(f"#{field['id']}", Input).value.strip()
        self.dismiss(result)


# ─────────────────────────────────────────────────────────────────────────────
# Tela Principal
# ─────────────────────────────────────────────────────────────────────────────

class MainScreen(Screen):
    CSS = """
    MainScreen {
        background: #000000;
    }
    Header {
        background: #0a0a0a;
        color: #FF4FA3;
    }
    Footer {
        background: #0a0a0a;
        color: #FF4FA3 60%;
    }
    TabbedContent {
        height: 100%;
    }
    TabPane {
        padding: 0;
        background: #000000;
    }
    .data-container {
        height: 1fr;
        padding: 1;
        overflow-y: auto;
    }
    .empty-msg {
        color: #FF4FA3;
        text-align: center;
        padding: 2;
        text-style: italic;
    }
    """

    BINDINGS = [
        ("q", "app.quit", "Sair"),
        ("l", "logout", "Logout"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent():
            # Aba: VEÍCULOS
            with TabPane("Veiculos", id="tab-veiculos"):
                with SectionToolbar():
                    yield ActionButton("Listar Veiculos",   id="btn-veiculos-list")
                    yield ActionButton("Roubados",           id="btn-veiculos-roubados")
                    yield ActionButton("Buscar por Placa",   id="btn-veiculos-placa")
                    yield ActionButton("Registrar Veiculo",  id="btn-veiculos-create")
                    yield ActionButton("Deletar Veiculo",    id="btn-veiculos-delete")
                yield VerticalScroll(id="dt-veiculos", classes="data-container")

            # Aba: OPERAÇÕES
            with TabPane("Operacoes", id="tab-operacoes"):
                with SectionToolbar():
                    yield ActionButton("Listar Operacoes",   id="btn-operacoes-list")
                    yield ActionButton("Nova Operacao",       id="btn-operacoes-create")
                    yield ActionButton("Mudar Status",        id="btn-operacoes-status")
                    yield ActionButton("Deletar Operacao",    id="btn-operacoes-delete")
                yield VerticalScroll(id="dt-operacoes", classes="data-container")

            # Aba: DRONES
            with TabPane("Drones", id="tab-drones"):
                with SectionToolbar():
                    yield ActionButton("Listar Drones",      id="btn-drones-list")
                    yield ActionButton("Em Voo",              id="btn-drones-inflight")
                    yield ActionButton("Registrar Drone",    id="btn-drones-create")
                    yield ActionButton("Atualizar Local",    id="btn-drones-location")
                    yield ActionButton("Deletar Drone",      id="btn-drones-delete")
                yield VerticalScroll(id="dt-drones", classes="data-container")

            # Aba: SCANS
            with TabPane("Scans", id="tab-scans"):
                with SectionToolbar():
                    yield ActionButton("Listar Scans",       id="btn-scans-list")
                    yield ActionButton("Pendentes",           id="btn-scans-pending")
                    yield ActionButton("Com Match",           id="btn-scans-matches")
                    yield ActionButton("Criar Scan",          id="btn-scans-create")
                    yield ActionButton("Validar Scan",        id="btn-scans-validate")
                    yield ActionButton("Vincular Veiculo",    id="btn-scans-bind")
                    yield ActionButton("Historico Usuario",   id="btn-scans-history")
                    yield ActionButton("Deletar Scan",        id="btn-scans-delete")
                yield VerticalScroll(id="dt-scans", classes="data-container")

            # Aba: USUÁRIOS
            with TabPane("Usuarios", id="tab-usuarios"):
                with SectionToolbar():
                    yield ActionButton("Listar Usuarios",    id="btn-usuarios-list")
                    yield ActionButton("Meu Perfil",          id="btn-usuarios-me")
                    yield ActionButton("Buscar por Nome",     id="btn-usuarios-search")
                    yield ActionButton("Criar Usuario",       id="btn-usuarios-create")
                    yield ActionButton("Alterar Senha",       id="btn-usuarios-password")
                    yield ActionButton("Deletar Usuario",     id="btn-usuarios-delete")
                yield VerticalScroll(id="dt-usuarios", classes="data-container")

        yield Footer()

    def action_logout(self) -> None:
        clear_session()
        self.app.push_screen(LoginScreen(), self._after_login)

    def _after_login(self, logged_in) -> None:
        pass

    # ── Helpers Container ────────────────────────────────────────────────────

    def _prepare_container(self, dt_id: str) -> VerticalScroll:
        container = self.query_one(f"#{dt_id}", VerticalScroll)
        # Remove todos os DataCards anteriores
        for child in container.children:
            child.remove()
        return container

    def _show_message(self, msg: str) -> None:
        self.notify(msg)

    # ── Handlers dos Botões ──────────────────────────────────────────────────

    @on(Button.Pressed)
    def handle_button_press(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        
        # Veículos
        if btn_id == "btn-veiculos-list":
            self.load_veiculos()
        elif btn_id == "btn-veiculos-roubados":
            self.load_veiculos(roubado=True)
        elif btn_id == "btn-veiculos-placa":
            self.app.push_screen(
                InputModal("Buscar por Placa", [{"id": "placa", "label": "Placa exata do veiculo"}]),
                self._buscar_veiculo_placa,
            )
        elif btn_id == "btn-veiculos-create":
            self.app.push_screen(
                InputModal("Registrar Veiculo", [
                    {"id": "placa",      "label": "Placa (ex: ABC1D23)"},
                    {"id": "modelo",     "label": "Modelo (ex: Fiat Uno)"},
                    {"id": "cor",        "label": "Cor (ex: Branco)"},
                    {"id": "roubado",    "label": "Roubado? (true / false)"},
                    {"id": "data_roubo", "label": "Data do roubo (ex: 2024-03-15T10:30:00)"},
                ]),
                self.create_veiculo,
            )
        elif btn_id == "btn-veiculos-delete":
            self.app.push_screen(
                InputModal("Deletar Veiculo", [{"id": "vid", "label": "ID (UUID) do veiculo"}]),
                self._delete_veiculo,
            )

        # Operações
        elif btn_id == "btn-operacoes-list":
            self.load_operacoes()
        elif btn_id == "btn-operacoes-create":
            self.app.push_screen(
                InputModal("Nova Operacao", [
                    {"id": "name",        "label": "Nome da Operacao"},
                    {"id": "status",      "label": "Status: ativa | pausada | encerrada"},
                    {"id": "localizacao", "label": "Localizacao (ex: Av. Paulista, SP)"},
                ]),
                self.create_operacao,
            )
        elif btn_id == "btn-operacoes-status":
            self.app.push_screen(
                InputModal("Mudar Status da Operacao", [
                    {"id": "oid",    "label": "ID (UUID) da operacao"},
                    {"id": "status", "label": "Novo status: ativa | pausada | encerrada"},
                ]),
                self._mudar_status_operacao,
            )
        elif btn_id == "btn-operacoes-delete":
            self.app.push_screen(
                InputModal("Deletar Operacao", [{"id": "oid", "label": "ID (UUID) da operacao"}]),
                self._delete_operacao,
            )

        # Drones
        elif btn_id == "btn-drones-list":
            self.load_drones()
        elif btn_id == "btn-drones-inflight":
            self.load_drones_inflight()
        elif btn_id == "btn-drones-create":
            self.app.push_screen(
                InputModal("Registrar Drone", [
                    {"id": "operacao_id",  "label": "ID da Operacao (UUID)"},
                    {"id": "nome",         "label": "Nome do drone (ex: Drone Alpha)"},
                    {"id": "status_voo",   "label": "Status: pousado | em_voo | offline | manutencao"},
                    {"id": "bateria",      "label": "Bateria % (ex: 100) - opcional"},
                    {"id": "conectividade","label": "Conectividade (ex: 4G) - opcional"},
                ]),
                self.create_drone,
            )
        elif btn_id == "btn-drones-location":
            self.app.push_screen(
                InputModal("Atualizar Localizacao do Drone", [
                    {"id": "did",       "label": "ID (UUID) do drone"},
                    {"id": "latitude",  "label": "Latitude (ex: -23.5505)"},
                    {"id": "longitude", "label": "Longitude (ex: -46.6333)"},
                    {"id": "bateria",   "label": "Bateria % - opcional"},
                ]),
                self._update_drone_location,
            )
        elif btn_id == "btn-drones-delete":
            self.app.push_screen(
                InputModal("Deletar Drone", [{"id": "did", "label": "ID (UUID) do drone"}]),
                self._delete_drone,
            )

        # Scans
        elif btn_id == "btn-scans-list":
            self.load_scans()
        elif btn_id == "btn-scans-pending":
            self.load_scans_pending()
        elif btn_id == "btn-scans-matches":
            self.load_scans_matches()
        elif btn_id == "btn-scans-create":
            self.app.push_screen(
                InputModal("Criar Scan", [
                    {"id": "id_drone",   "label": "ID do drone (UUID)"},
                    {"id": "placa",      "label": "Placa lida (ex: ABC1D23)"},
                    {"id": "match",      "label": "Match? (true / false)"},
                    {"id": "imagem_url", "label": "URL da imagem - opcional"},
                    {"id": "latitude",   "label": "Latitude - opcional"},
                    {"id": "longitude",  "label": "Longitude - opcional"},
                ]),
                self.create_scan,
            )
        elif btn_id == "btn-scans-validate":
            self.app.push_screen(
                InputModal("Validar Scan", [
                    {"id": "sid",              "label": "ID do scan (UUID)"},
                    {"id": "status_validacao",  "label": "Status: aprovado | rejeitado | limpo"},
                ]),
                self._validate_scan,
            )
        elif btn_id == "btn-scans-bind":
            self.app.push_screen(
                InputModal("Vincular Veiculo ao Scan", [
                    {"id": "sid",        "label": "ID do scan (UUID)"},
                    {"id": "veiculo_id", "label": "ID do veiculo (UUID)"},
                ]),
                self._bind_veiculo_scan,
            )
        elif btn_id == "btn-scans-history":
            self.app.push_screen(
                InputModal("Historico de Usuario", [{"id": "uid", "label": "ID do usuario (UUID)"}]),
                self._load_historico,
            )
        elif btn_id == "btn-scans-delete":
            self.app.push_screen(
                InputModal("Deletar Scan", [{"id": "sid", "label": "ID do scan (UUID)"}]),
                self._delete_scan,
            )

        # Usuarios
        elif btn_id == "btn-usuarios-list":
            self.load_usuarios()
        elif btn_id == "btn-usuarios-me":
            self.load_me()
        elif btn_id == "btn-usuarios-search":
            self.app.push_screen(
                InputModal("Buscar Usuario por Nome", [{"id": "q", "label": "Nome (parcial)"}]),
                self._search_usuario,
            )
        elif btn_id == "btn-usuarios-create":
            self.app.push_screen(
                InputModal("Criar Usuario", [
                    {"id": "name",     "label": "Nome completo"},
                    {"id": "email",    "label": "E-mail"},
                    {"id": "password", "label": "Senha"},
                    {"id": "role",     "label": "Role: gestor_local | gestor_remoto"},
                ]),
                self._create_usuario,
            )
        elif btn_id == "btn-usuarios-password":
            self.app.push_screen(
                InputModal("Alterar Minha Senha", [
                    {"id": "old_password", "label": "Senha atual"},
                    {"id": "new_password", "label": "Nova senha"},
                ]),
                self._change_password,
            )
        elif btn_id == "btn-usuarios-delete":
            self.app.push_screen(
                InputModal("Deletar Usuario", [{"id": "user_id", "label": "ID do usuario (UUID)"}]),
                self._delete_usuario,
            )

    # ── Callbacks de Criação ─────────────────────────────────────────────────

    def create_veiculo(self, data: dict | None) -> None:
        if not data:
            return
        # Converte o campo 'roubado' de texto para bool
        roubado_raw = data.get("roubado", "false").strip().lower()
        data["roubado"] = roubado_raw in ("true", "1", "sim", "s")
        # data_roubo pode ser vazio se não roubado
        if not data.get("data_roubo"):
            data["data_roubo"] = None
        required = ["placa", "modelo", "cor"]
        if not all(data.get(k) for k in required):
            self._show_message(f"Preencha os campos: {', '.join(required)}")
            return
        res = api_request("POST", "/api/veiculos/", data)
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}")
        else:
            self._show_message("Veículo criado com sucesso! ✔")
            self.load_veiculos()

    def create_operacao(self, data: dict | None) -> None:
        if not data:
            return
        required = ["name", "status", "localizacao"]
        if not all(data.get(k) for k in required):
            self._show_message(f"Preencha os campos obrigatórios: {', '.join(required)}")
            return
        res = api_request("POST", "/api/operacoes/", data)
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}")
        else:
            self._show_message("Operação criada com sucesso! ✔")
            self.load_operacoes()

    def create_drone(self, data: dict | None) -> None:
        if not data:
            return
        required = ["operacao_id", "nome", "status_voo"]
        if not all(data.get(k) for k in required):
            self._show_message(f"Preencha os campos obrigatórios: {', '.join(required)}")
            return
        payload = {
            "operacao_id": data["operacao_id"],
            "nome":        data["nome"],
            "status_voo":  data["status_voo"],
        }
        # campos opcionais
        if data.get("bateria"):
            try:
                payload["bateria"] = int(data["bateria"])
            except ValueError:
                pass
        if data.get("conectividade"):
            payload["conectividade"] = data["conectividade"]
        res = api_request("POST", "/api/drones/", payload)
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}")
        else:
            self._show_message("Drone criado com sucesso! ✔")
            self.load_drones()

    # ── Loaders ──────────────────────────────────────────────────────────────

    def load_operacoes(self) -> None:
        container = self._prepare_container("dt-operacoes")
        res = api_request("GET", "/api/operacoes/")
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}"); return
        data = res if isinstance(res, list) else res.get("operacoes", [])
        if not data:
            container.mount(Static("Nenhuma operação encontrada.", classes="empty-msg"))
            return
        for op in data:
            card_data = {
                "ID": str(op.get("id", "")),
                "Status": str(op.get("status", "")),
                "Localizacao": str(op.get("localizacao", "")),
                "Criado Em": str(op.get("created_at", ""))
            }
            container.mount(DataCard(f"Operacao: {op.get('name', 'N/A')}", card_data))

    def load_drones(self) -> None:
        container = self._prepare_container("dt-drones")
        res = api_request("GET", "/api/drones/")
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}"); return
        data = res if isinstance(res, list) else res.get("drones", [])
        if not data:
            container.mount(Static("Nenhum drone encontrado.", classes="empty-msg"))
            return
        for d in data:
            card_data = {
                "ID": str(d.get("id", "")),
                "Status Voo": str(d.get("status_voo", "")),
                "Bateria": f"{d.get('bateria', 'N/A')}%",
                "Conectividade": str(d.get("conectividade", "")),
                "Operacao ID": str(d.get("operacao_id", ""))
            }
            container.mount(DataCard(f"Drone: {d.get('nome', 'N/A')}", card_data))

    def load_drones_inflight(self) -> None:
        container = self._prepare_container("dt-drones")
        res = api_request("GET", "/api/drones/em-voo")
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}"); return
        data = res if isinstance(res, list) else res.get("drones", [])
        if not data:
            container.mount(Static("Nenhum drone em voo.", classes="empty-msg"))
            return
        for d in data:
            card_data = {
                "ID": str(d.get("id", "")),
                "Status Voo": str(d.get("status_voo", "")),
                "Latitude": str(d.get("latitude", "")),
                "Longitude": str(d.get("longitude", "")),
                "Bateria": f"{d.get('bateria', 'N/A')}%"
            }
            container.mount(DataCard(f"Drone: {d.get('nome', 'N/A')}", card_data))

    def load_scans(self) -> None:
        container = self._prepare_container("dt-scans")
        res = api_request("GET", "/api/scans/")
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}"); return
        data = res if isinstance(res, list) else res.get("scans", [])
        if not data:
            container.mount(Static("Nenhum scan encontrado.", classes="empty-msg"))
            return
        for s in data:
            card_data = {
                "ID": str(s.get("id", "")),
                "Drone ID": str(s.get("id_drone", "")),
                "Status": str(s.get("status_validacao", "")),
                "Placa": str(s.get("placa", "")),
                "Criado Em": str(s.get("created_at", ""))
            }
            container.mount(DataCard(f"Scan (Placa: {s.get('placa', 'N/A')})", card_data))

    def load_scans_pending(self) -> None:
        container = self._prepare_container("dt-scans")
        res = api_request("GET", "/api/scans/pendentes")
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}"); return
        data = res if isinstance(res, list) else res.get("scans", [])
        if not data:
            container.mount(Static("Nenhum scan pendente para validação.", classes="empty-msg"))
            return
        container.mount(Static(
            f"[b]🔍 {len(data)} scan(s) aguardando verificação de OCR[/b] — confirme se o YOLO leu a placa corretamente:",
            classes="empty-msg"
        ))
        for s in data:
            container.mount(ValidationCard(s))

    def load_scans_matches(self) -> None:
        container = self._prepare_container("dt-scans")
        res = api_request("GET", "/api/scans/matches")
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}"); return
        
        # A API retorna {"scans": [...], "total": X}
        data = res if isinstance(res, list) else res.get("scans", [])
        
        if not data:
            container.mount(Static("Nenhum match encontrado.", classes="empty-msg"))
            return
            
        container.mount(Static(
            f"[b]🚨 {len(data)} veículo(s) com alerta de roubo identificado(s)[/b]:",
            classes="empty-msg"
        ))
        
        for m in data:
            card_data = {
                "Placa": str(m.get("placa", "N/A")),
                "Modelo": str(m.get("veiculo_modelo", "Não informado")),
                "Cor": str(m.get("veiculo_cor", "Não informada")),
                "Data Roubo": str(m.get("veiculo_data_roubo", "Desconhecida")),
                "Coordenadas": f"lat {m.get('latitude', '—')} / lon {m.get('longitude', '—')}",
                "Horário Identificado": str(m.get("horario_scan", "")),
                "Scan ID": str(m.get("id", "")),
                "Veículo ID": str(m.get("veiculo_id", "N/A")),
                "Drone Originador": str(m.get("id_drone", ""))
            }
            container.mount(DataCard("🚨 MATCH CONFIRMADO (Dados para Despacho) 🚨", card_data))


    def load_usuarios(self) -> None:
        container = self._prepare_container("dt-usuarios")
        res = api_request("GET", "/api/users/")
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}"); return
        # A API retorna {'users': [...], 'total': N}
        data = res if isinstance(res, list) else res.get("users", res.get("usuarios", []))
        if not data:
            container.mount(Static("Nenhum usuário encontrado.", classes="empty-msg"))
            return
        for u in data:
            card_data = {
                "ID": str(u.get("id", "")),
                "Email": str(u.get("email", "")),
                "Role": str(u.get("role", ""))
            }
            container.mount(DataCard(f"Usuario: {u.get('name', 'N/A')}", card_data))

    def load_me(self) -> None:
        container = self._prepare_container("dt-usuarios")
        res = api_request("GET", "/api/users/me")
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}"); return
        card_data = {str(k): str(v) for k, v in res.items()}
        container.mount(DataCard("Meu Perfil", card_data))

    # ── Novos callbacks e loaders ─────────────────────────────────────────────

    # -- Veículos --
    def load_veiculos(self, roubado: bool | None = None) -> None:
        container = self._prepare_container("dt-veiculos")
        url = "/api/veiculos/" + ("?roubado=true" if roubado else "")
        res = api_request("GET", url)
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}"); return
        data = res if isinstance(res, list) else res.get("veiculos", [])
        if not data:
            container.mount(Static("Nenhum veículo encontrado.", classes="empty-msg"))
            return
        for v in data:
            roubado_str = "[!] Sim" if v.get("roubado") else "[ok] Nao"
            card_data = {
                "ID": str(v.get("id", "")),
                "Modelo": str(v.get("modelo", "")),
                "Cor": str(v.get("cor", "")),
                "Roubado": roubado_str
            }
            container.mount(DataCard(f"Veiculo: {v.get('placa', 'N/A')}", card_data))

    def _buscar_veiculo_placa(self, data: dict | None) -> None:
        if not data or not data.get("placa"):
            return
        res = api_request("GET", f"/api/veiculos/placa/{data['placa'].strip()}")
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}"); return
        container = self._prepare_container("dt-veiculos")
        roubado_str = "[!] Sim" if res.get("roubado") else "[ok] Nao"
        card_data = {
            "ID": str(res.get("id", "")),
            "Modelo": str(res.get("modelo", "")),
            "Cor": str(res.get("cor", "")),
            "Roubado": roubado_str
        }
        container.mount(DataCard(f"Veiculo: {res.get('placa', 'N/A')}", card_data))

    def _delete_veiculo(self, data: dict | None) -> None:
        if not data or not data.get("vid"):
            return
        res = api_request("DELETE", f"/api/veiculos/{data['vid'].strip()}")
        msg = res.get("message", "Removido") if isinstance(res, dict) else "Feito"
        self._show_message(msg)
        self.load_veiculos()

    # -- Operações --
    def _mudar_status_operacao(self, data: dict | None) -> None:
        if not data or not data.get("oid") or not data.get("status"):
            return
        res = api_request("PATCH", f"/api/operacoes/{data['oid'].strip()}/status",
                          {"status": data["status"].strip()})
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}")
        else:
            self._show_message("Status atualizado!")
            self.load_operacoes()

    def _delete_operacao(self, data: dict | None) -> None:
        if not data or not data.get("oid"):
            return
        res = api_request("DELETE", f"/api/operacoes/{data['oid'].strip()}")
        msg = res.get("message", "Removido") if isinstance(res, dict) else "Feito"
        self._show_message(msg)
        self.load_operacoes()

    # -- Drones --
    def _update_drone_location(self, data: dict | None) -> None:
        if not data or not data.get("did"):
            return
        payload: dict = {}
        try:
            payload["latitude"]  = float(data["latitude"])
            payload["longitude"] = float(data["longitude"])
        except (ValueError, KeyError):
            self._show_message("Latitude e longitude sao obrigatorios e devem ser numeros"); return
        if data.get("bateria"):
            try:
                payload["bateria"] = int(data["bateria"])
            except ValueError:
                pass
        res = api_request("PATCH", f"/api/drones/{data['did'].strip()}/localizacao", payload)
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}")
        else:
            self._show_message("Localizacao atualizada!")

    def _delete_drone(self, data: dict | None) -> None:
        if not data or not data.get("did"):
            return
        res = api_request("DELETE", f"/api/drones/{data['did'].strip()}")
        msg = res.get("message", "Removido") if isinstance(res, dict) else "Feito"
        self._show_message(msg)
        self.load_drones()

    # -- Scans --
    def create_scan(self, data: dict | None) -> None:
        if not data:
            return
        required = ["id_drone", "placa", "match"]
        if not all(data.get(k) for k in required):
            self._show_message(f"Preencha: {', '.join(required)}"); return
        match_raw = data["match"].strip().lower()
        payload: dict = {
            "id_drone": data["id_drone"].strip(),
            "placa":    data["placa"].strip().upper(),
            "match":    match_raw in ("true", "1", "sim"),
        }
        for opt in ("imagem_url", "latitude", "longitude"):
            if data.get(opt):
                try:
                    payload[opt] = float(data[opt]) if opt in ("latitude", "longitude") else data[opt]
                except ValueError:
                    pass
        res = api_request("POST", "/api/scans/", payload)
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}")
        else:
            self._show_message("Scan criado!")
            self.load_scans()

    def _validate_scan(self, data: dict | None) -> None:
        if not data or not data.get("sid") or not data.get("status_validacao"):
            return
        res = api_request("PATCH", f"/api/scans/{data['sid'].strip()}/validar",
                          {"status_validacao": data["status_validacao"].strip()})
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}")
        else:
            self._show_message("Scan validado!")
            self.load_scans()

    def on_validation_card_aprovar(self, event: ValidationCard.Aprovar) -> None:
        """Chamado quando o botão Aprovar de um ValidationCard é pressionado."""
        res = api_request("PATCH", f"/api/scans/{event.scan_id}/validar",
                          {"status_validacao": "aprovado"})
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}")
        else:
            self._show_message("✔ OCR confirmado! Leitura da placa registrada como correta.")
            self.load_scans_pending()

    def on_validation_card_rejeitar(self, event: ValidationCard.Rejeitar) -> None:
        """Chamado quando o botão Rejeitar de um ValidationCard é pressionado."""
        res = api_request("PATCH", f"/api/scans/{event.scan_id}/validar",
                          {"status_validacao": "rejeitado"})
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}")
        else:
            self._show_message("✘ OCR marcado como errado. Scan descartado.")
            self.load_scans_pending()

    def _bind_veiculo_scan(self, data: dict | None) -> None:
        if not data or not data.get("sid") or not data.get("veiculo_id"):
            return
        res = api_request("POST", f"/api/scans/{data['sid'].strip()}/vincular-veiculo",
                          {"veiculo_id": data["veiculo_id"].strip()})
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}")
        else:
            self._show_message("Veiculo vinculado ao scan!")

    def _load_historico(self, data: dict | None) -> None:
        if not data or not data.get("uid"):
            return
        res = api_request("GET", f"/api/scans/historico/usuario/{data['uid'].strip()}")
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}"); return
        container = self._prepare_container("dt-scans")
        historico = res.get("historico", []) if isinstance(res, dict) else []
        if not historico:
            container.mount(Static("Nenhum historico encontrado.", classes="empty-msg"))
            return
        for h in historico:
            card_data = {
                "Scan ID": str(h.get("scan_id", "")),
                "Acao": str(h.get("acao", "")),
                "Data": str(h.get("created_at", ""))
            }
            container.mount(DataCard("Registro de Historico", card_data))

    def _delete_scan(self, data: dict | None) -> None:
        if not data or not data.get("sid"):
            return
        res = api_request("DELETE", f"/api/scans/{data['sid'].strip()}")
        msg = res.get("message", "Removido") if isinstance(res, dict) else "Feito"
        self._show_message(msg)
        self.load_scans()

    # -- Usuários --
    def _search_usuario(self, data: dict | None) -> None:
        if not data or not data.get("q"):
            return
        res = api_request("GET", f"/api/users/search?q={data['q'].strip()}")
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}"); return
        container = self._prepare_container("dt-usuarios")
        resultados = res.get("resultados", []) if isinstance(res, dict) else []
        if not resultados:
            container.mount(Static("Nenhum usuario encontrado.", classes="empty-msg"))
            return
        for u in resultados:
            card_data = {
                "ID": str(u.get("id", "")),
                "Email": str(u.get("email", "")),
                "Role": str(u.get("role", ""))
            }
            container.mount(DataCard(f"Usuario: {u.get('name', 'N/A')}", card_data))

    def _create_usuario(self, data: dict | None) -> None:
        if not data:
            return
        required = ["name", "email", "password"]
        if not all(data.get(k) for k in required):
            self._show_message(f"Preencha: {', '.join(required)}"); return
        res = api_request("POST", "/api/auth/register", data)
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}")
        else:
            self._show_message("Usuario criado!")
            self.load_usuarios()

    def _change_password(self, data: dict | None) -> None:
        if not data or not data.get("old_password") or not data.get("new_password"):
            return
        res = api_request("PATCH", "/api/users/me/password", data)
        if isinstance(res, dict) and res.get("error"):
            self._show_message(f"Erro: {res.get('message')}")
        else:
            self._show_message("Senha alterada com sucesso!")

    def _delete_usuario(self, data: dict | None) -> None:
        if not data or not data.get("user_id"):
            return
        res = api_request("DELETE", f"/api/users/{data['user_id'].strip()}")
        msg = res.get("message", "Removido") if isinstance(res, dict) else "Feito"
        self._show_message(msg)
        self.load_usuarios()

# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────

class PierApp(App):
    TITLE = "PIER — Terminal UI"
    ENABLE_COMMAND_PALETTE = True

    BINDINGS = [
        ("ctrl+s", "screenshot", "Screenshot"),
    ]

    def on_mount(self) -> None:
        self.push_screen(MainScreen())
        if not load_session():
            self.push_screen(LoginScreen(), self._after_login)

    def _after_login(self, logged_in) -> None:
        pass

    def action_screenshot(self) -> None:
        path = self.save_screenshot()
        self.notify(f"Screenshot salvo: {path}", title="Screenshot")


if __name__ == "__main__":
    PierApp().run()
