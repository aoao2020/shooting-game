import tkinter as tk
import random
import time
import math

class ShootingGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Blue Shooter")
        self.master.geometry("800x600")
        
        # ブルートーンカラーの定義
        self.colors = {
            'bg': '#000030',  # ダークネイビー
            'player': '#00BFFF',  # ディープスカイブルー
            'bullet': '#87CEFA',  # ライトスカイブルー
            'enemy': '#4169E1',  # ロイヤルブルー
            'text': '#ADD8E6',  # ライトブルー
            'effect': '#00FFFF'  # シアン
        }
        
        # キャンバスの作成
        self.canvas = tk.Canvas(self.master, width=800, height=600, bg=self.colors['bg'])
        self.canvas.pack()
        
        # ゲーム変数の初期化
        self.score = 0
        self.game_over = False
        self.enemies = []
        self.bullets = []
        self.player_size = 30
        
        # プレイヤーの初期位置
        self.player_x = 400
        self.player_y = 550
        
        # プレイヤーの描画（銃の形）
        self.player = self.create_gun(self.player_x, self.player_y)
        
        # スコア表示
        self.score_text = self.canvas.create_text(
            50, 30, 
            text=f"SCORE: {self.score}", 
            fill=self.colors['text'], 
            font=("Arial", 16, "bold")
        )
        
        # キーバインディング
        self.master.bind("<Left>", self.move_left)
        self.master.bind("<Right>", self.move_right)
        self.master.bind("<space>", self.shoot)
        
        # 背景の星を作成
        self.create_stars()
        
        # ゲームループの開始
        self.spawn_enemy()
        self.update()
    
    def create_gun(self, x, y):
        # 銃の形状を定義
        gun_shape = [
            x - 15, y + 10,  # 左下
            x - 15, y - 5,   # 左上
            x - 5, y - 5,    # 銃身開始
            x - 5, y - 15,   # 銃身上部
            x + 5, y - 15,   # 銃身上部右
            x + 5, y - 5,    # 銃身終了
            x + 15, y - 5,   # 右上
            x + 15, y + 10,  # 右下
        ]
        return self.canvas.create_polygon(gun_shape, fill=self.colors['player'], outline='#00FFFF')

    def create_stars(self):
        # 背景に星を描く
        for _ in range(50):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            size = random.randint(1, 3)
            color = random.choice(['#4169E1', '#87CEFA', '#B0E2FF'])  # 青系の星
            self.canvas.create_text(x, y, text='✦', fill=color, font=('Arial', size*4))
    
    def move_left(self, event):
        if not self.game_over and self.player_x > 40:
            self.player_x -= 20
            self.canvas.move(self.player, -20, 0)
    
    def move_right(self, event):
        if not self.game_over and self.player_x < 760:
            self.player_x += 20
            self.canvas.move(self.player, 20, 0)
    
    def shoot(self, event):
        if not self.game_over:
            # レーザービーム風の弾を作成
            bullet = self.canvas.create_rectangle(
                self.player_x - 2,
                self.player_y - 20,
                self.player_x + 2,
                self.player_y - 30,
                fill=self.colors['bullet'],
                outline=self.colors['effect']
            )
            self.bullets.append(bullet)
            # 発射エフェクト
            self.create_muzzle_flash(self.player_x, self.player_y - 15)
    
    def create_muzzle_flash(self, x, y):
        # 銃口フラッシュエフェクト
        flash = self.canvas.create_oval(
            x - 5, y - 5,
            x + 5, y + 5,
            fill=self.colors['effect'],
            outline=''
        )
        self.master.after(50, lambda: self.canvas.delete(flash))
    
    def spawn_enemy(self):
        if not self.game_over:
            x = random.randint(50, 750)
            # 敵の作成（六角形）
            enemy_points = self.create_hexagon_points(x, 0, 15)
            enemy = self.canvas.create_polygon(
                enemy_points,
                fill=self.colors['enemy'],
                outline=self.colors['effect']
            )
            self.enemies.append(enemy)
            self.master.after(2000, self.spawn_enemy)
    
    def create_hexagon_points(self, x, y, size):
        points = []
        for i in range(6):
            angle = i * 60
            rad = math.radians(angle)
            points.extend([
                x + size * math.cos(rad),
                y + size * math.sin(rad)
            ])
        return points

    def update(self):
        if not self.game_over:
            # 弾の移動
            for bullet in self.bullets[:]:
                self.canvas.move(bullet, 0, -10)
                bullet_pos = self.canvas.coords(bullet)
                if not bullet_pos or bullet_pos[1] < 0:
                    self.canvas.delete(bullet)
                    self.bullets.remove(bullet)
                else:
                    # 弾と敵の衝突判定
                    for enemy in self.enemies[:]:
                        enemy_pos = self.canvas.bbox(enemy)
                        if enemy_pos and self.check_collision(bullet_pos, enemy_pos):
                            # 爆発エフェクト
                            self.create_explosion(enemy_pos[0], enemy_pos[1])
                            self.canvas.delete(bullet)
                            self.canvas.delete(enemy)
                            self.bullets.remove(bullet)
                            self.enemies.remove(enemy)
                            self.score += 10
                            self.canvas.itemconfig(
                                self.score_text,
                                text=f"SCORE: {self.score}"
                            )
                            break
            
            # 敵の移動
            for enemy in self.enemies[:]:
                self.canvas.move(enemy, 0, 3)
                enemy_pos = self.canvas.bbox(enemy)
                if enemy_pos and enemy_pos[3] > 600:
                    self.canvas.delete(enemy)
                    self.enemies.remove(enemy)
                elif enemy_pos:
                    # プレイヤーと敵の衝突判定
                    player_pos = self.canvas.bbox(self.player)
                    if player_pos and self.check_collision(player_pos, enemy_pos):
                        self.game_over = True
                        self.show_game_over()
                        return
            
            self.master.after(16, self.update)

    def create_explosion(self, x, y):
        # 爆発エフェクト
        colors = ['#00FFFF', '#87CEFA', '#1E90FF']
        for i in range(8):
            angle = i * 45
            rad = math.radians(angle)
            line = self.canvas.create_line(
                x, y,
                x + 20 * math.cos(rad),
                y + 20 * math.sin(rad),
                fill=random.choice(colors),
                width=2
            )
            self.master.after(200, lambda l=line: self.canvas.delete(l))
    
    def check_collision(self, pos1, pos2):
        return not (pos1[2] < pos2[0] or
                   pos1[0] > pos2[2] or
                   pos1[3] < pos2[1] or
                   pos1[1] > pos2[3])
    
    def show_game_over(self):
        self.canvas.create_text(
            400, 300,
            text=f"GAME OVER\n\nSCORE: {self.score}\n\nPRESS SPACE TO RESTART",
            fill=self.colors['text'],
            font=("Arial", 24, "bold"),
            justify="center"
        )
        self.master.bind("<space>", self.restart_game)
    
    def restart_game(self, event):
        self.master.destroy()
        start_game()

def start_game():
    root = tk.Tk()
    game = ShootingGame(root)
    root.mainloop()

if __name__ == "__main__":
    start_game() 