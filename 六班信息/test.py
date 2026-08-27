import tkinter as tk
import random

# 游戏配置
CELL_SIZE = 20          # 每个格子的大小（像素）
GRID_WIDTH = 30         # 网格宽度（格子数）
GRID_HEIGHT = 20        # 网格高度（格子数）
INITIAL_SPEED = 150     # 初始速度（毫秒），越小越快
SPEED_INCREMENT = 3     # 每吃一个食物加速的毫秒数
MIN_SPEED = 60          # 最低速度限制


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🐍 贪吃蛇")
        self.root.resizable(False, False)

        # 分数
        self.score = 0
        self.best_score = 0

        # ----- 顶部信息栏 -----
        self.info_frame = tk.Frame(root)
        self.info_frame.pack(pady=(10, 5))

        tk.Label(self.info_frame, text="分数:", font=("微软雅黑", 14)).pack(side=tk.LEFT)
        self.score_label = tk.Label(self.info_frame, text="0", font=("微软雅黑", 14, "bold"),
                                    fg="#2196F3", width=5)
        self.score_label.pack(side=tk.LEFT)

        tk.Label(self.info_frame, text="  最高分:", font=("微软雅黑", 14)).pack(side=tk.LEFT)
        self.best_label = tk.Label(self.info_frame, text="0", font=("微软雅黑", 14, "bold"),
                                   fg="#FF5722", width=5)
        self.best_label.pack(side=tk.LEFT)

        # ----- 游戏画布 -----
        self.canvas_width = GRID_WIDTH * CELL_SIZE
        self.canvas_height = GRID_HEIGHT * CELL_SIZE
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height,
                                bg="#2d2d2d", highlightthickness=0)
        self.canvas.pack(padx=20, pady=(5, 10))

        # ----- 底部按钮 -----
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=(0, 15))

        self.restart_btn = tk.Button(self.btn_frame, text="🔄 重新开始",
                                     font=("微软雅黑", 12), command=self.restart,
                                     bg="#4CAF50", fg="white", padx=20, pady=5,
                                     activebackground="#45a049")
        self.restart_btn.pack(side=tk.LEFT, padx=10)

        self.pause_btn = tk.Button(self.btn_frame, text="⏸ 暂停",
                                   font=("微软雅黑", 12), command=self.toggle_pause,
                                   bg="#FF9800", fg="white", padx=20, pady=5,
                                   activebackground="#e68900")
        self.pause_btn.pack(side=tk.LEFT, padx=10)

        # 键盘绑定
        self.root.bind("<Up>", lambda e: self.change_direction("up"))
        self.root.bind("<Down>", lambda e: self.change_direction("down"))
        self.root.bind("<Left>", lambda e: self.change_direction("left"))
        self.root.bind("<Right>", lambda e: self.change_direction("right"))
        self.root.bind("<w>", lambda e: self.change_direction("up"))
        self.root.bind("<s>", lambda e: self.change_direction("down"))
        self.root.bind("<a>", lambda e: self.change_direction("left"))
        self.root.bind("<d>", lambda e: self.change_direction("right"))
        self.root.bind("<space>", lambda e: self.toggle_pause())
        self.root.bind("<r>", lambda e: self.restart())

        # 开始游戏
        self.init_game()
        self.root.after(INITIAL_SPEED, self.game_loop)
        self.root.mainloop()

    def init_game(self):
        """初始化游戏状态"""
        self.snake = [
            (GRID_WIDTH // 2, GRID_HEIGHT // 2),      # 蛇头
            (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),  # 身体
            (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2),  # 尾巴
        ]
        self.direction = "right"    # 当前方向
        self.next_direction = "right"
        self.food = None
        self.speed = INITIAL_SPEED
        self.score = 0
        self.game_over = False
        self.paused = False

        self.place_food()
        self.update_score_display()
        self.draw()

    def place_food(self):
        """在空白位置随机放置食物"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break

    def draw(self):
        """绘制整个游戏画面"""
        self.canvas.delete("all")

        # 绘制网格线（可选）
        for x in range(GRID_WIDTH):
            self.canvas.create_line(x * CELL_SIZE, 0,
                                    x * CELL_SIZE, self.canvas_height,
                                    fill="#3a3a3a", dash=(1, 4))
        for y in range(GRID_HEIGHT):
            self.canvas.create_line(0, y * CELL_SIZE,
                                    self.canvas_width, y * CELL_SIZE,
                                    fill="#3a3a3a", dash=(1, 4))

        # 绘制食物
        if self.food:
            fx, fy = self.food
            x1 = fx * CELL_SIZE + 2
            y1 = fy * CELL_SIZE + 2
            x2 = x1 + CELL_SIZE - 4
            y2 = y1 + CELL_SIZE - 4
            self.canvas.create_oval(x1, y1, x2, y2,
                                    fill="#FF5252", outline="#FF1744", width=2)

        # 绘制蛇
        for i, (sx, sy) in enumerate(self.snake):
            x1 = sx * CELL_SIZE + 1
            y1 = sy * CELL_SIZE + 1
            x2 = x1 + CELL_SIZE - 2
            y2 = y1 + CELL_SIZE - 2

            if i == 0:
                # 蛇头：不同颜色
                color = "#4CAF50"
                outline = "#388E3C"
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=color, outline=outline, width=2)
                # 画眼睛
                eye_r = 3
                if self.direction in ("right", ""):
                    cx1, cy1 = x1 + CELL_SIZE - 8, y1 + 7
                    cx2, cy2 = x1 + CELL_SIZE - 8, y1 + CELL_SIZE - 9
                elif self.direction == "left":
                    cx1, cy1 = x1 + 8, y1 + 7
                    cx2, cy2 = x1 + 8, y1 + CELL_SIZE - 9
                elif self.direction == "up":
                    cx1, cy1 = x1 + 7, y1 + 8
                    cx2, cy2 = x1 + CELL_SIZE - 9, y1 + 8
                else:  # down
                    cx1, cy1 = x1 + 7, y1 + CELL_SIZE - 8
                    cx2, cy2 = x1 + CELL_SIZE - 9, y1 + CELL_SIZE - 8
                self.canvas.create_oval(cx1 - eye_r, cy1 - eye_r,
                                        cx1 + eye_r, cy1 + eye_r,
                                        fill="white", outline="")
                self.canvas.create_oval(cx2 - eye_r, cy2 - eye_r,
                                        cx2 + eye_r, cy2 + eye_r,
                                        fill="white", outline="")
            else:
                # 蛇身：渐变颜色
                ratio = i / len(self.snake)
                r = int(76 + (139 - 76) * ratio)
                g = int(175 + (195 - 175) * ratio)
                b = int(80 + (40 - 80) * ratio)
                color = f"#{r:02X}{g:02X}{b:02X}"
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=color, outline="#1B5E20", width=1)

        # 游戏结束遮罩
        if self.game_over:
            self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height,
                                         fill="black", stipple="gray50")
            self.canvas.create_text(self.canvas_width // 2, self.canvas_height // 2 - 20,
                                    text="游戏结束", font=("微软雅黑", 28, "bold"),
                                    fill="#FF5252")
            self.canvas.create_text(self.canvas_width // 2, self.canvas_height // 2 + 25,
                                    text=f"得分: {self.score}  按 R 重新开始",
                                    font=("微软雅黑", 16), fill="white")

        # 暂停提示
        elif self.paused:
            self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height,
                                         fill="black", stipple="gray25")
            self.canvas.create_text(self.canvas_width // 2, self.canvas_height // 2,
                                    text="⏸ 已暂停", font=("微软雅黑", 28, "bold"),
                                    fill="#FFC107")
            self.canvas.create_text(self.canvas_width // 2, self.canvas_height // 2 + 35,
                                    text="按 空格键 继续", font=("微软雅黑", 14),
                                    fill="white")

    def change_direction(self, new_dir):
        """改变蛇的方向（不允许直接掉头）"""
        opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
        if new_dir != opposites.get(self.direction, ""):
            self.next_direction = new_dir

    def game_loop(self):
        """游戏主循环"""
        if not self.game_over and not self.paused:
            self.move_snake()

        next_delay = self.speed
        if self.game_over:
            next_delay = 200
        elif self.paused:
            next_delay = 100

        self.root.after(next_delay, self.game_loop)

    def move_snake(self):
        """移动蛇"""
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]

        # 计算新头部位置
        if self.direction == "right":
            new_head = (head_x + 1, head_y)
        elif self.direction == "left":
            new_head = (head_x - 1, head_y)
        elif self.direction == "down":
            new_head = (head_x, head_y + 1)
        elif self.direction == "up":
            new_head = (head_x, head_y - 1)
        else:
            return

        # 检测碰撞：撞墙
        nx, ny = new_head
        if nx < 0 or nx >= GRID_WIDTH or ny < 0 or ny >= GRID_HEIGHT:
            self.end_game()
            return

        # 检测碰撞：撞自己（新头部与身体碰撞，排除尾巴尖因为尾巴马上会移走）
        if new_head in self.snake[:-1]:
            self.end_game()
            return

        # 蛇向前移动
        self.snake.insert(0, new_head)

        # 判断是否吃到食物
        if new_head == self.food:
            self.score += 10
            self.update_score_display()
            self.place_food()
            # 加速
            self.speed = max(MIN_SPEED, self.speed - SPEED_INCREMENT)
        else:
            # 没吃到食物，移除尾巴
            self.snake.pop()

        self.draw()

    def end_game(self):
        """游戏结束"""
        self.game_over = True
        if self.score > self.best_score:
            self.best_score = self.score
            self.best_label.config(text=str(self.best_score))
        self.draw()

    def restart(self):
        """重新开始游戏"""
        if self.score > self.best_score:
            self.best_score = self.score
        self.init_game()

    def toggle_pause(self):
        """暂停/继续"""
        if self.game_over:
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="▶ 继续")
        else:
            self.pause_btn.config(text="⏸ 暂停")
        self.draw()

    def update_score_display(self):
        """更新分数显示"""
        self.score_label.config(text=str(self.score))
        if self.score > self.best_score:
            self.best_label.config(text=str(self.score))


if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
