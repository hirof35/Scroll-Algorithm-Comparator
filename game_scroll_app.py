import tkinter as tk
from tkinter import ttk

class GameScrollApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ゲームスクロール・アルゴリズム比較")
        self.root.geometry("800x500")

        # ゲーム世界のデータ（横に長いステージ：0 〜 3000ピクセル）
        self.world_width = 3000
        self.screen_width = 800
        self.screen_height = 350

        # プレイヤーの初期ステータス
        self.player_x = 150
        self.player_y = 250
        self.player_size = 30
        self.player_speed = 15

        # カメラの初期位置
        self.camera_x = 0

        # キー入力の状態
        self.keys = {"Left": False, "Right": False}

        self.setup_ui()
        
        # ゲームループの開始
        self.root.bind("<KeyPress>", self.press_key)
        self.root.bind("<KeyRelease>", self.release_key)
        self.game_loop()

    def setup_ui(self):
        # --- コントロールパネル ---
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)

        self.algo_var = tk.StringVar(value="player_centered")
        
        rb1 = ttk.Radiobutton(control_frame, text="① プレイヤー追従 (常に中央)", 
                              variable=self.algo_var, value="player_centered")
        rb1.pack(side=tk.LEFT, padx=10)

        rb2 = ttk.Radiobutton(control_frame, text="② スクロールロック (端まで動ける)", 
                              variable=self.algo_var, value="scroll_lock")
        rb2.pack(side=tk.LEFT, padx=10)

        rb3 = ttk.Radiobutton(control_frame, text="③ 視差効果 (パララックス：遠景・近景)", 
                              variable=self.algo_var, value="parallax")
        rb3.pack(side=tk.LEFT, padx=10)

        # 操作説明
        lbl_info = ttk.Label(self.root, text="【操作方法】 左右の矢印キー (← / →) で赤いプレイヤーを移動", font=("Helvetica", 10))
        lbl_info.pack(pady=5)

        # --- ゲーム画面 (キャンバス) ---
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, bg="#1a1a2e")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def press_key(self, event):
        if event.keysym in self.keys:
            self.keys[event.keysym] = True

    def release_key(self, event):
        if event.keysym in self.keys:
            self.keys[event.keysym] = False

    def update_physics(self):
        # プレイヤーの移動処理（ステージの端を越えないように制限）
        if self.keys["Left"]:
            self.player_x = max(0, self.player_x - self.player_speed)
        if self.keys["Right"]:
            self.player_x = min(self.world_width - self.player_size, self.player_x + self.player_speed)

        # --- スクロールアルゴリズムの切り替え ---
        algo = self.algo_var.get()

        if algo == "player_centered":
            # ① プレイヤーが常に画面の中央にくるようにカメラを動かす
            self.camera_x = self.player_x - (self.screen_width / 2)
            # ステージの端に達したらカメラを止める（一般的なゲームの挙動）
            self.camera_x = max(0, min(self.camera_x, self.world_width - self.screen_width))

        elif algo == "scroll_lock":
            # ② 画面の「左右30%」の境界線（デッドゾーン）を超えたらスクロールする
            left_buffer = self.screen_width * 0.3
            right_buffer = self.screen_width * 0.7
            
            # プレイヤーの画面上での相対位置
            player_screen_x = self.player_x - self.camera_x

            if player_screen_x > right_buffer:
                self.camera_x = self.player_x - right_buffer
            elif player_screen_x < left_buffer:
                self.camera_x = self.player_x - left_buffer
                
            self.camera_x = max(0, min(self.camera_x, self.world_width - self.screen_width))

        elif algo == "parallax":
            # ③ パララックス（視差）用のカメラ位置（基本は中央追従）
            self.camera_x = self.player_x - (self.screen_width / 2)
            self.camera_x = max(0, min(self.camera_x, self.world_width - self.screen_width))

    def draw_game(self):
        self.canvas.delete("all")
        algo = self.algo_var.get()

        if algo == "parallax":
            # --- パララックススクロール (視差効果) ---
            # 遠景（星空や遠くの山）：カメラの動きの「0.2倍」だけ動かす（ゆっくり動く＝遠くに見える）
            star_camera_x = self.camera_x * 0.2
            for i in range(0, self.world_width, 200):
                xpos = i - star_camera_x
                if -50 < xpos < self.screen_width + 50:
                    self.canvas.create_oval(xpos, 50, xpos+10, 60, fill="#ffffff")
                    self.canvas.create_oval(xpos+80, 120, xpos+95, 135, fill="#53354a")

            # 中景（ビルや木）：カメラの動きの「0.5倍」だけ動かす
            bg_camera_x = self.camera_x * 0.5
            for i in range(0, self.world_width, 150):
                xpos = i - bg_camera_x
                if -100 < xpos < self.screen_width + 100:
                    self.canvas.create_rectangle(xpos, 180, xpos+100, self.screen_height, fill="#0f3460", outline="")

        else:
            # --- 通常の背景描画 (目印用のグリッド線や障害物) ---
            for i in range(0, self.world_width, 200):
                xpos = i - self.camera_x
                if -20 < xpos < self.screen_width + 20:
                    self.canvas.create_line(xpos, 0, xpos, self.screen_height, fill="#2e2e4f")
                    self.canvas.create_text(xpos + 10, 20, text=f"{i}m", fill="#4e4e7f", anchor="nw")

        # 地面の描画
        self.canvas.create_rectangle(0, self.screen_height - 20, self.screen_width, self.screen_height, fill="#e94560")

        # プレイヤーの描画（世界座標からカメラ座標に変換）
        screen_player_x = self.player_x - self.camera_x
        self.canvas.create_rectangle(
            screen_player_x, self.player_y, 
            screen_player_x + self.player_size, self.player_y + self.player_size, 
            fill="#ff0055", outline="#ffffff", width=2
        )

        # デッドゾーンの視覚化（スクロールロック選択時のみガイド線を表示）
        if algo == "scroll_lock":
            self.canvas.create_line(self.screen_width * 0.3, 0, self.screen_width * 0.3, self.screen_height, fill="yellow", dash=(4,4))
            self.canvas.create_line(self.screen_width * 0.7, 0, self.screen_width * 0.7, self.screen_height, fill="yellow", dash=(4,4))

    def game_loop(self):
        self.update_physics()
        self.draw_game()
        # 約60FPS (16ミリ秒ごとに更新)
        self.root.after(16, self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = GameScrollApp(root)
    root.mainloop()
