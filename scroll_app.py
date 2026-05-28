import tkinter as tk
from tkinter import ttk
import time

class ScrollAlgorithmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("スクロールアルゴリズム比較アプリ")
        self.root.geometry("600x500")

        # テスト用データ（1万件のアイテム）
        self.data = [f"アイテム 行番号: {i:05d}" for i in range(10000)]
        
        # 仮想スクロール用の設定
        self.item_height = 25  # 1行の高さ(ピクセル)
        self.visible_count = 15 # 画面に表示する行数
        self.canvas_height = self.item_height * self.visible_count

        self.setup_ui()

    def setup_ui(self):
        # --- コントロールパネル ---
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)

        self.algo_var = tk.StringVar(value="virtual")
        
        rb_virtual = ttk.Radiobutton(control_frame, text="仮想スクロール (高速・省メモリ)", 
                                     variable=self.algo_var, value="virtual", command=self.switch_algorithm)
        rb_virtual.pack(side=tk.LEFT, padx=10)

        rb_normal = ttk.Radiobutton(control_frame, text="通常スクロール (データ量が多いと重い)", 
                                    variable=self.algo_var, value="normal", command=self.switch_algorithm)
        rb_normal.pack(side=tk.LEFT, padx=10)

        # ステータス表示（描画時間など）
        self.status_label = ttk.Label(control_frame, text="モードを選択してください", font=("Helvetica", 10, "bold"))
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # --- メインコンテンツエリア ---
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 初期状態は仮想スクロールで起動
        self.init_virtual_scroll()

    def clear_main_frame(self):
        """画面をクリアする"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def switch_algorithm(self):
        """アルゴリズムの切り替え"""
        algo = self.algo_var.get()
        self.clear_main_frame()
        
        if algo == "virtual":
            self.init_virtual_scroll()
        else:
            self.init_normal_scroll()

    # ==========================================
    # アルゴリズム1: 通常のスクロール (Naive Approach)
    # ==========================================
    def init_normal_scroll(self):
        start_time = time.time()
        
        # キャンバスとスクロールバーの配置
        canvas = tk.Canvas(self.main_frame, bg="white")
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 1万件のデータを「すべて」ラベルとして生成して配置する
        # ※ ここで大量のメモリと描画時間を消費します
        for item in self.data:
            lbl = tk.Label(scrollable_frame, text=item, bg="white", height=1, anchor="w")
            lbl.pack(fill=tk.X, padx=5)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        end_time = time.time()
        self.status_label.config(text=f"全件描画時間: {(end_time - start_time)*1000:.1f} ms", foreground="red")

    # ==========================================
    # アルゴリズム2: 仮想スクロール (Virtual Scroll)
    # ==========================================
    def init_virtual_scroll(self):
        start_time = time.time()

        # 表示用のキャンバス
        self.v_canvas = tk.Canvas(self.main_frame, bg="white", height=self.canvas_height)
        self.v_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 全体データ量に合わせたダミーのスクロールバー
        # 1万件分の高さがあるように見せかける
        self.v_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.on_virtual_scroll)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # スクロールバーの移動範囲を設定 (0.0 〜 1.0)
        self.v_scrollbar.set(0.0, float(self.visible_count) / len(self.data))
        
        # 現在のスクロール位置（インデックス）
        self.current_top_index = 0
        
        # マウスホイールイベントのバインド
        self.v_canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        # 初回描画（画面に見える分だけ）
        self.update_virtual_view()

        end_time = time.time()
        self.status_label.config(text=f"初回描画時間: {(end_time - start_time)*1000:.1f} ms", foreground="green")

    def update_virtual_view(self):
        """画面に見えている部分だけを再描画するコアアルゴリズム"""
        self.v_canvas.delete("all")
        
        # 描画する範囲のインデックスを計算
        start_idx = self.current_top_index
        end_idx = min(start_idx + self.visible_count, len(self.data))

        # 見えている数（最大15件）だけをループして描画
        for i in range(start_idx, end_idx):
            y_pos = (i - start_idx) * self.item_height
            # キャンバスにテキストとして描画（軽量）
            self.v_canvas.create_text(15, y_pos + self.item_height//2, 
                                      text=self.data[i], anchor="w", font=("Helvetica", 10))

    def on_virtual_scroll(self, action, fraction, unit=None):
        """スクロールバーが動かされた時の処理"""
        if action == "scroll":
            direction = int(fraction)
            self.current_top_index = max(0, min(self.current_top_index + direction, len(self.data) - self.visible_count))
        elif action == "moveto":
            pos = float(fraction)
            self.current_top_index = int(pos * (len(self.data) - self.visible_count))
        
        # スクロールバーの位置を更新
        start_ratio = self.current_top_index / len(self.data)
        end_ratio = (self.current_top_index + self.visible_count) / len(self.data)
        self.v_scrollbar.set(start_ratio, end_ratio)
        
        self.update_virtual_view()

    def on_mouse_wheel(self, event):
        """マウスホイールでのスクロール対応"""
        if event.delta > 0:
            direction = -1  # 上スクロール
        else:
            direction = 1   # 下スクロール
            
        self.current_top_index = max(0, min(self.current_top_index + direction, len(self.data) - self.visible_count))
        
        start_ratio = self.current_top_index / len(self.data)
        end_ratio = (self.current_top_index + self.visible_count) / len(self.data)
        self.v_scrollbar.set(start_ratio, end_ratio)
        
        self.update_virtual_view()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScrollAlgorithmApp(root)
    root.mainloop()
