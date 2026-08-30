import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.markdown import Markdown

load_dotenv()

from core.bridge_ai import IllustratorBridge
from core.bridge_ps import PhotoshopBridge
from core.inspector import DocumentInspector
from core.llm_engine import LLMEngine
from core.gemini_oauth import GeminiOAuthManager

console = Console()


def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║   🎨 Adobe AI Co-Pilot (Photoshop & Illustrator CLI)         ║
    ║   자연어 지시 & 스마트 양방향 디자인 자동화 시스템           ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")


def show_help():
    table = Table(title="[bold yellow]명령어 안내[/bold yellow]", show_header=True, header_style="bold magenta")
    table.add_column("명령어", style="cyan", width=18)
    table.add_column("설명", style="white")
    
    table.add_row("/login", "Google 계정 로그인 (OAuth 토큰 발급/갱신)")
    table.add_row("/status, /info", "현재 연결된 프로그램 및 문서 상태 확인")
    table.add_row("/inspect", "현재 문서의 레이어 및 텍스트 상세 구조 조회")
    table.add_row("/new", "새 캔버스/아트보드 문서 생성")
    table.add_row("/reset, /clear", "이전 대화 및 디자인 맥락 초기화")
    table.add_row("/target [ai|ps]", "작업 대상 프로그램 전환 (Illustrator / Photoshop)")
    table.add_row("/help", "도움말 표시")
    table.add_row("/exit, /quit", "프로그램 종료")
    table.add_row("<자연어 지시>", "예: '여름 이벤트 배너 만들어줘', '텍스트 글자 크기 30pt로 키워줘'")
    
    console.print(table)


def main():
    print_banner()
    
    ai_bridge = IllustratorBridge()
    ps_bridge = PhotoshopBridge()
    llm = LLMEngine()
    oauth_mgr = GeminiOAuthManager()
    
    # Check connections
    ai_ok = False
    ps_ok = False
    
    with console.status("[bold green]Adobe 소프트웨어 및 LLM 연결 확인 중...[/bold green]"):
        try:
            ai_ok = ai_bridge.connect()
        except Exception:
            ai_ok = False

        try:
            ps_ok = ps_bridge.connect()
        except Exception:
            ps_ok = False

    status_table = Table(show_header=False, box=None)
    status_table.add_row(
        "[bold]Illustrator:[/bold]",
        f"[green]연결됨 (v{ai_bridge.version})[/green]" if ai_ok else "[yellow]미연결 / 미실행[/yellow]"
    )
    status_table.add_row(
        "[bold]Photoshop:[/bold]",
        f"[green]연결됨 (v{ps_bridge.version})[/green]" if ps_ok else "[dim]미설치 / 미실행[/dim]"
    )
    
    llm_status = f"[green]Google OAuth (Gemini: {os.getenv('GEMINI_MODEL', 'gemini-3.7-flash')})[/green]"
    if llm.provider == "gemini_oauth" and not oauth_mgr.is_logged_in():
        llm_status += " [yellow](로그인 필요: /login)[/yellow]"
    
    status_table.add_row("[bold]AI Co-Pilot:[/bold]", llm_status)
    status_table.add_row("[bold]모드:[/bold]", "[cyan]스마트 자동 판단 (구체적 지시: 즉시실행 / 포괄적 지시: 질문 & 옵션제안)[/cyan]")
    
    console.print(Panel(status_table, title="[bold]시스템 상태[/bold]", border_style="cyan"))

    current_target = "ai" if ai_ok else ("ps" if ps_ok else "ai")
    console.print(f"[bold green]기본 대상 프로그램: [cyan]{'Illustrator' if current_target == 'ai' else 'Photoshop'}[/cyan][/bold green]\n")
    console.print("[dim]도움말: '/help' | 대화 초기화: '/reset' | 자연어로 자유롭게 지시하세요.[/dim]\n")

    while True:
        try:
            target_label = "Illustrator" if current_target == "ai" else "Photoshop"
            user_input = Prompt.ask(f"[bold magenta]{target_label} >[/bold magenta]").strip()
            
            if not user_input:
                continue

            # Command routing
            if user_input in ["/exit", "/quit", "exit", "quit"]:
                console.print("[bold yellow]프로그램을 종료합니다.[/bold yellow]")
                break
            
            elif user_input in ["/help", "help"]:
                show_help()
                continue

            elif user_input in ["/reset", "/clear"]:
                llm.clear_history()
                console.print("[bold green]✓ 대화 맥락 및 히스토리가 초기화되었습니다.[/bold green]")
                continue
            
            elif user_input == "/login":
                try:
                    with console.status("[bold cyan]브라우저에서 Google 로그인을 진행하세요...[/bold cyan]"):
                        oauth_mgr.get_valid_token()
                    console.print("[bold green]✓ Google OAuth 로그인이 완료되었습니다![/bold green]")
                except Exception as e:
                    console.print(f"[bold red]로그인 실패:[/bold red] {e}")
                continue

            elif user_input.startswith("/target"):
                parts = user_input.split()
                if len(parts) > 1 and parts[1].lower() in ["ai", "illustrator"]:
                    current_target = "ai"
                    console.print("[green]대상 프로그램이 [bold]Illustrator[/bold]로 변경되었습니다.[/green]")
                elif len(parts) > 1 and parts[1].lower() in ["ps", "photoshop"]:
                    current_target = "ps"
                    console.print("[green]대상 프로그램이 [bold]Photoshop[/bold]로 변경되었습니다.[/green]")
                else:
                    console.print("[red]사용법: /target ai  또는  /target ps[/red]")
                continue

            elif user_input in ["/status", "/info"]:
                bridge = ai_bridge if current_target == "ai" else ps_bridge
                doc_count = bridge.document_count if bridge.is_connected else 0
                console.print(f"[{target_label}] 열린 문서 수: [bold cyan]{doc_count}개[/bold cyan]")
                continue

            elif user_input == "/inspect":
                bridge = ai_bridge if current_target == "ai" else ps_bridge
                inspect_fn = DocumentInspector.inspect_illustrator if current_target == "ai" else DocumentInspector.inspect_photoshop
                with console.status("[bold cyan]문서 상태 분석 중...[/bold cyan]"):
                    state = inspect_fn(bridge)
                console.print_json(data=state)
                continue

            elif user_input.startswith("/new"):
                bridge = ai_bridge if current_target == "ai" else ps_bridge
                with console.status("[bold green]새 문서 생성 중...[/bold green]"):
                    res = bridge.create_document()
                console.print(f"[bold green]문서 생성 결과:[/bold green] {res}")
                continue

            # Natural Language Processing with Smart Decision
            active_bridge = ai_bridge if current_target == "ai" else ps_bridge
            inspect_fn = DocumentInspector.inspect_illustrator if current_target == "ai" else DocumentInspector.inspect_photoshop
            
            with console.status("[bold cyan]문서 상태 분석 및 의도 파악 중...[/bold cyan]"):
                doc_state = inspect_fn(active_bridge)
                decision_res = llm.process_prompt(
                    user_prompt=user_input,
                    doc_state=doc_state,
                    bridge=active_bridge,
                    target_app="illustrator" if current_target == "ai" else "photoshop"
                )

            # 1. AI decided to ask questions / suggest options
            if decision_res.get("action") == "ask":
                question_md = Markdown(decision_res.get("question", ""))
                console.print(Panel(
                    question_md,
                    title="[bold yellow]🎨 AI 디렉터의 제안 및 질문[/bold yellow]",
                    border_style="yellow"
                ))

            # 2. AI decided to execute code
            elif decision_res.get("action") == "execute":
                if decision_res.get("success"):
                    console.print(Panel(
                        f"[bold green]✓ 작업 완료 (시도 횟수: {decision_res.get('attempts')}회)[/bold green]\n"
                        f"[white]{decision_res.get('result') or '작업이 성공적으로 적용되었습니다.'}[/white]",
                        title="[bold green]디자인 반영 완료[/bold green]",
                        border_style="green"
                    ))
                    if decision_res.get("code"):
                        syntax = Syntax(decision_res["code"], "javascript", theme="monokai", line_numbers=True)
                        console.print(Panel(syntax, title="[dim]실행된 ExtendScript (JSX)[/dim]", expand=False))
                else:
                    console.print(Panel(
                        f"[bold red]✗ 실행 실패[/bold red]\n[yellow]오류: {decision_res.get('error')}[/yellow]",
                        title="[bold red]오류 발생[/bold red]",
                        border_style="red"
                    ))
                    if decision_res.get("last_code"):
                        syntax = Syntax(decision_res["last_code"], "javascript", theme="monokai", line_numbers=True)
                        console.print(Panel(syntax, title="[dim]실패한 코드[/dim]", expand=False))

        except KeyboardInterrupt:
            console.print("\n[bold yellow]작업이 취소되었습니다.[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]오류:[/bold red] {e}")


if __name__ == "__main__":
    main()
