"""
Main entry point for the Schwarzschild black-hole simulation.

This module:

1. Runs the complete physical validation suite.
2. Traces null geodesics backwards from a static camera.
3. Displays or saves the gravitationally lensed celestial sky.

The physical model itself is implemented in the physics/
and simulation/ packages.

The renderer is responsible only for visualization.
"""

import argparse
import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Valida a física e renderiza o buraco negro de Schwarzschild."
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="Salva a imagem sem abrir uma janela (automático sem display).",
    )
    parser.add_argument(
        "--output", type=Path,
        help="Destino da imagem; padrão: outputs/blackhole.png no projeto.",
    )
    parser.add_argument(
        "--validate-only", action="store_true", help="Executa apenas a validação física.",
    )
    parser.add_argument(
        "--mode", choices=("raytrace", "geometry"), default="raytrace",
        help="Ray tracing (padrão) ou diagrama geométrico anterior.",
    )
    parser.add_argument("--width", type=int, default=640, help="Largura da imagem em pixels.")
    parser.add_argument("--height", type=int, default=400, help="Altura da imagem em pixels.")
    parser.add_argument("--fov", type=float, default=45.0, help="Campo de visão vertical, graus.")
    parser.add_argument("--distance", type=float, default=30.0, help="Distância da câmera em M.")
    return parser.parse_args(argv)


def run_validation():
    """Run all seven physical checks, importing their dependencies on demand."""
    from validation.newtonian_limit import test_flat_space, test_newtonian_limit
    from validation.schwarzschild_radius import test_event_horizon
    from validation.photon_sphere import test_photon_sphere
    from validation.circular_orbits import test_stable_circular_orbit, test_isco
    from validation.precession import test_perihelion_precession

    print("=== Validação física ===")
    results = {
        "flat_space": test_flat_space(),
        "newtonian_limit": test_newtonian_limit(),
        "event_horizon": test_event_horizon(),
        "photon_sphere": test_photon_sphere(),
        "circular_orbit": test_stable_circular_orbit(),
        "isco": test_isco(),
        "precession": test_perihelion_precession(),
    }
    print("\n=== Resumo ===")
    for name, ok in results.items():
        print(f"{name}: {'OK' if ok else 'FALHOU'}")
    return results


def run_renderer(headless=False, output=None, mode="raytrace", width=640,
                 height=400, fov=45.0, distance=30.0):
    """Render numerical rays by default; keep the geometry diagram optional."""
    cache = PROJECT_ROOT / "outputs" / ".cache" / "matplotlib"
    if "MPLCONFIGDIR" not in os.environ:
        cache.mkdir(parents=True, exist_ok=True)
        os.environ["MPLCONFIGDIR"] = str(cache)

    import matplotlib

    no_display = sys.platform.startswith("linux") and not (
        os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    )
    if headless or no_display:
        matplotlib.use("Agg")
    backend = matplotlib.get_backend().lower()
    noninteractive = backend in {"agg", "pdf", "svg", "ps", "cairo", "template", "pgf"}

    import matplotlib.pyplot as plt

    if mode == "raytrace":
        from raytracing import Camera, render

        camera = Camera(width=width, height=height, fov=fov, distance=distance)
        print(f"\n=== Ray tracing: {width} x {height} raios ===", flush=True)
        image, result = render(camera)
        print(
            f"[OK] Capturados: {result.captured.sum()}; "
            f"escaparam: {result.escaped.sum()}; "
            f"não resolvidos: {result.unresolved.sum()}; "
            f"erro relativo máx. de E²: {result.energy_error.max():.2e}",
            flush=True,
        )
        fig, ax = plt.subplots()
        ax.imshow(image)
        ax.set_axis_off()
        fig.tight_layout(pad=0)
    else:
        from renderer import Renderer2D

        print("\n=== Renderer geométrico 2D ===")
        renderer = Renderer2D(M=1.0)
        renderer.draw_scene(title="Schwarzschild Black Hole")
        fig = renderer.fig
    try:
        if output is not None or headless or no_display or noninteractive:
            destination = output if output is not None else PROJECT_ROOT / "outputs" / "blackhole.png"
            destination = Path(destination).resolve()
            destination.parent.mkdir(parents=True, exist_ok=True)
            if mode == "raytrace":
                plt.imsave(destination, image)
            else:
                fig.savefig(destination)
            print(f"[OK] Imagem salva em: {destination}")
        if not (headless or no_display or noninteractive):
            plt.show()
    finally:
        plt.close(fig)


def main(argv=None):
    args = parse_args(argv)
    try:
        results = run_validation()
        if not results or not all(results.values()):
            print("[ERRO] Validação física falhou; renderer não será executado.", file=sys.stderr)
            return 1
        print("\n[OK] Todos os testes físicos passaram.")
        if not args.validate_only:
            run_renderer(
                headless=args.headless, output=args.output, mode=args.mode,
                width=args.width, height=args.height, fov=args.fov, distance=args.distance,
            )
    except ModuleNotFoundError as exc:
        print(
            f"[ERRO] Dependência ausente: {exc.name}. Instale com:\n"
            f'  "{sys.executable}" -m pip install -r "{PROJECT_ROOT / "requirements.txt"}"',
            file=sys.stderr,
        )
        return 1
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    # Reuse the prepared local environment even when invoked with system Python.
    venv_root = PROJECT_ROOT / ".venv"
    venv_python = venv_root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if venv_python.is_file() and Path(sys.prefix).resolve() != venv_root.resolve():
        os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]])
    raise SystemExit(main())
