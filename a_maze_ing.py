from mlx import Mlx


def on_key(keycode: int, data: object) -> None:
    print(f"Touche: {keycode}")
    if keycode == 65307:  # Escape
        m.mlx_loop_exit(mlx_ptr)


def on_close(data: object) -> None:
    m.mlx_loop_exit(mlx_ptr)


if __name__ == "__main__":
    # 1. Initialisation 1
    m: Mlx = Mlx()
    mlx_ptr = m.mlx_init()

    # 2. Créer la fenêtre
    win_ptr = m.mlx_new_window(mlx_ptr, 400, 300, "Hello MLX")

    # 3. Afficher du texte
    m.mlx_string_put(mlx_ptr, win_ptr, 20, 140, 0xFFFFFFFF, "Hello MLX!")

    m.mlx_key_hook(win_ptr, on_key, None)
    m.mlx_hook(win_ptr, 33, 0, on_close, None)

    # 5. Boucle (bloquant)
    m.mlx_loop(mlx_ptr)

    print("This is a maze generator and solver.")
