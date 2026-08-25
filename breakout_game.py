#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打砖块小游戏 (Breakout)
- 鼠标移动控制挡板，按住鼠标时球垂直弹出，松开则正常反弹
- 砖块定时生成，层数过高则游戏结束
- 球速、砖块生成速度、砖块生命值随游戏时间递增
- 分数 = 砖块生命值的平方
- 不同HP的砖块用不同颜色显示并标注数值
"""

import tkinter as tk
import time
import math
import random


class BreakoutGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("打砖块 - Breakout")
        self.root.resizable(False, False)

        # ==================== 画布 ====================
        self.CW = 800   # 画布宽度
        self.CH = 600   # 画布高度
        self.canvas = tk.Canvas(
            self.root, width=self.CW, height=self.CH,
            bg="#0d0d2b", highlightthickness=0
        )
        self.canvas.pack()

        # ==================== 常量 ====================
        self.PADDLE_W = 130          # 挡板宽度
        self.PADDLE_H = 14           # 挡板高度
        self.PADDLE_Y = self.CH - 55 # 挡板 Y 坐标
        self.BALL_R = 10             # 球半径
        self.BW = 68                 # 砖块宽度
        self.BH = 24                 # 砖块高度
        self.BGAP = 4                # 砖块间距
        self.BTOP = 35               # 砖块区域顶部 Y
        self.MAX_ROWS = 16           # 砖块到达此行 → 游戏结束

        # ==================== 挡板 ====================
        self.px = self.CW // 2       # 挡板中心 X
        self.py = self.PADDLE_Y

        # ==================== 球 ====================
        self.bx = self.px
        self.by = self.py - self.BALL_R - self.PADDLE_H // 2
        self.bdx = 0.0
        self.bdy = 0.0
        self.base_speed = 4.5        # 初始球速
        self.speed = self.base_speed
        self.attached = True         # 球是否吸附在挡板上

        # ==================== 输入状态 ====================
        self.mouse_down = False

        # ==================== 游戏状态 ====================
        self.score = 0
        self.game_over_flag = False
        self.start_time: float | None = None

        # ==================== 砖块数据 ====================
        # canvas_id → {"row": int, "col": int, "hp": int, "max_hp": int, "text_id": int, "x": float, "y": float}
        self.bricks: dict[int, dict] = {}

        # ==================== 难度参数 ====================
        self.gen_interval = 5.5       # 初始砖块生成间隔（秒）
        self.last_gen_time = 0.0

        # ==================== Canvas 对象 ID ====================
        self.paddle_id: int = None
        self.ball_id: int = None
        self.score_text_id: int = None
        self.info_text_id: int = None
        self.game_over_text_id: int = None

        # ==================== 初始化界面 ====================
        self._create_objects()
        self._bind_events()

        # ==================== 启动游戏循环 ====================
        self.root.after(80, self._game_loop)
        self.root.mainloop()

    # ---------- 创建画布元素 ----------
    def _create_objects(self):
        """创建挡板、球和分数显示"""
        self.paddle_id = self.canvas.create_rectangle(
            self.px - self.PADDLE_W // 2, self.py - self.PADDLE_H // 2,
            self.px + self.PADDLE_W // 2, self.py + self.PADDLE_H // 2,
            fill="#00ddff", outline="#00aacc", width=2
        )
        self.ball_id = self.canvas.create_oval(
            self.bx - self.BALL_R, self.by - self.BALL_R,
            self.bx + self.BALL_R, self.by + self.BALL_R,
            fill="#ffffff", outline="#cccccc", width=1
        )
        self._draw_ui()

    def _draw_ui(self):
        """绘制分数和信息面板"""
        if self.score_text_id:
            self.canvas.delete(self.score_text_id)
        if self.info_text_id:
            self.canvas.delete(self.info_text_id)

        self.score_text_id = self.canvas.create_text(
            12, 10, anchor="nw", fill="#ffffff",
            text=f"★ 分数: {self.score}",
            font=("Consolas", 18, "bold")
        )

        elapsed = self._elapsed()
        spd_str = f"{self.speed:.1f}" if not self.attached else "吸附中"
        hp = self._current_max_hp()
        interval = max(1.0, 5.5 - elapsed / 35.0)
        self.info_text_id = self.canvas.create_text(
            self.CW - 12, 10, anchor="ne", fill="#aaaaaa",
            text=f"球速: {spd_str}  |  砖块HP: {hp}  |  生成间隔: {interval:.1f}s  |  时间: {elapsed:.0f}s",
            font=("Microsoft YaHei", 11)
        )

    # ---------- 事件绑定 ----------
    def _bind_events(self):
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<space>", self._on_space)

    # ---------- 鼠标事件 ----------
    def _on_mouse_move(self, event):
        if self.game_over_flag:
            return
        self.px = max(self.PADDLE_W // 2, min(self.CW - self.PADDLE_W // 2, event.x))
        self.canvas.coords(
            self.paddle_id,
            self.px - self.PADDLE_W // 2, self.py - self.PADDLE_H // 2,
            self.px + self.PADDLE_W // 2, self.py + self.PADDLE_H // 2,
        )
        if self.attached:
            self.bx = self.px
            self.by = self.py - self.BALL_R - self.PADDLE_H // 2
            self.canvas.coords(
                self.ball_id,
                self.bx - self.BALL_R, self.by - self.BALL_R,
                self.bx + self.BALL_R, self.by + self.BALL_R,
            )

    def _on_mouse_down(self, event):
        if self.game_over_flag:
            self._restart()
            return
        self.mouse_down = True
        if self.attached:
            self._launch_ball()

    def _on_mouse_up(self, event):
        self.mouse_down = False

    def _on_space(self, event):
        """空格键也可以发射球 / 重新开始"""
        if self.game_over_flag:
            self._restart()
        elif self.attached:
            self._launch_ball()

    def _launch_ball(self):
        """发射球 - 垂直向上"""
        self.attached = False
        self.bdx = 0.0
        self.bdy = -self.speed
        if self.start_time is None:
            self.start_time = time.time()
            self.last_gen_time = self.start_time

    # ---------- 难度计算 ----------
    def _elapsed(self) -> float:
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def _current_max_hp(self) -> int:
        """当前新生成砖块的基础 HP"""
        t = self._elapsed()
        return 1 + int(t / 18.0)

    def _current_speed(self) -> float:
        """当前球速"""
        t = self._elapsed()
        return self.base_speed + t / 15.0

    def _current_gen_interval(self) -> float:
        """当前砖块生成间隔"""
        t = self._elapsed()
        return max(1.0, 5.5 - t / 35.0)

    # ---------- 砖块颜色 ----------
    @staticmethod
    def _brick_fill(hp: int, max_hp: int) -> str:
        """根据剩余 HP 返回砖块颜色"""
        ratio = hp / max(max_hp, 1)
        if hp >= 6:
            return "#7B1FA2"  # 紫色
        elif hp >= 5:
            return "#D32F2F"  # 深红
        elif hp == 4:
            return "#F44336"  # 红色
        elif hp == 3:
            return "#FF9800"  # 橙色
        elif hp == 2:
            return "#FFEB3B"  # 黄色
        else:
            # HP=1, 根据原始 max_hp 显示不同深浅绿
            if max_hp >= 4:
                return "#81C784"
            return "#4CAF50"  # 绿色

    @staticmethod
    def _brick_text_color(hp: int) -> str:
        """深色背景白字，浅色背景黑字"""
        if hp <= 2:
            return "#1a1a1a"
        return "#ffffff"

    # ---------- 砖块生成 ----------
    def _generate_brick_row(self):
        """在顶部生成一行新砖块，已有砖块整体下移"""
        # 1) 将所有已有砖块向下移一行
        shift = self.BH + self.BGAP
        for brick in self.bricks.values():
            brick["row"] += 1
            brick["y"] = self.BTOP + brick["row"] * shift
            self.canvas.move(brick["id"], 0, shift)
            self.canvas.move(brick["text_id"], 0, shift)
            # 检查游戏结束
            if brick["row"] >= self.MAX_ROWS:
                self._end_game(f"砖块堆积过多！\n最终分数: {self.score}")
                return

        # 2) 在 row=0 处生成新砖块
        cols = (self.CW - self.BGAP) // (self.BW + self.BGAP)
        start_x = (self.CW - (cols * (self.BW + self.BGAP) - self.BGAP)) // 2
        max_hp = self._current_max_hp()

        y = self.BTOP  # row 0

        for col in range(cols):
            # 随机留空，保持趣味性
            if random.random() < 0.25:
                continue

            x = start_x + col * (self.BW + self.BGAP)

            # HP 在 max_hp 基础上有 ±1 浮动
            hp = max_hp + random.randint(-1, 1)
            hp = max(1, hp)

            brick_id = self.canvas.create_rectangle(
                x, y, x + self.BW, y + self.BH,
                fill=self._brick_fill(hp, max_hp),
                outline="#1a1a3a", width=1,
            )
            text_id = self.canvas.create_text(
                x + self.BW // 2, y + self.BH // 2,
                text=str(hp),
                fill=self._brick_text_color(hp),
                font=("Consolas", 11, "bold"),
            )

            self.bricks[brick_id] = {
                "id": brick_id,
                "row": 0,
                "col": col,
                "hp": hp,
                "max_hp": max_hp,
                "text_id": text_id,
                "x": float(x),
                "y": float(y),
            }

    # ---------- 碰撞检测 ----------
    def _check_brick_collision(self):
        """检测球与砖块的碰撞，处理反弹和扣分"""
        ball_left = self.bx - self.BALL_R
        ball_right = self.bx + self.BALL_R
        ball_top = self.by - self.BALL_R
        ball_bottom = self.by + self.BALL_R

        # 球心，用于方向判断
        ball_cx = self.bx
        ball_cy = self.by

        hit_brick_id = None
        hit_brick = None

        # 找到第一个碰撞的砖块
        for brick_id, brick in self.bricks.items():
            bx1 = brick["x"]
            by1 = brick["y"]
            bx2 = bx1 + self.BW
            by2 = by1 + self.BH

            if ball_right > bx1 and ball_left < bx2 and ball_bottom > by1 and ball_top < by2:
                hit_brick_id = brick_id
                hit_brick = brick
                break

        if hit_brick is None:
            return

        # 减少砖块 HP
        hit_brick["hp"] -= 1

        if hit_brick["hp"] <= 0:
            # 砖块被摧毁
            self.canvas.delete(hit_brick_id)
            self.canvas.delete(hit_brick["text_id"])
            max_hp = hit_brick["max_hp"]
            self.score += max_hp * max_hp  # 分数 = 原始HP的平方
            del self.bricks[hit_brick_id]
        else:
            # 更新砖块外观
            self.canvas.itemconfig(
                hit_brick_id,
                fill=self._brick_fill(hit_brick["hp"], hit_brick["max_hp"]),
            )
            self.canvas.itemconfig(
                hit_brick["text_id"],
                text=str(hit_brick["hp"]),
                fill=self._brick_text_color(hit_brick["hp"]),
            )

        # 计算碰撞方向并反弹
        bx1 = hit_brick["x"]
        by1 = hit_brick["y"]
        bx2 = bx1 + self.BW
        by2 = by1 + self.BH

        # 找出球是从哪边进入砖块的：计算各方向重叠量
        overlap_left = ball_right - bx1
        overlap_right = bx2 - ball_left
        overlap_top = ball_bottom - by1
        overlap_bottom = by2 - ball_top

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if min_overlap == overlap_left:
            self.bdx = -abs(self.bdx)
            self.bx = bx1 - self.BALL_R
        elif min_overlap == overlap_right:
            self.bdx = abs(self.bdx)
            self.bx = bx2 + self.BALL_R
        elif min_overlap == overlap_top:
            self.bdy = -abs(self.bdy)
            self.by = by1 - self.BALL_R
        else:  # overlap_bottom
            self.bdy = abs(self.bdy)
            self.by = by2 + self.BALL_R

    # ---------- 游戏循环 ----------
    def _game_loop(self):
        if self.game_over_flag:
            return

        elapsed = self._elapsed()

        # ---- 更新难度 ----
        if elapsed > 0:
            self.speed = self._current_speed()
            self.gen_interval = self._current_gen_interval()

        # ---- 生成砖块 ----
        if elapsed > 0 and time.time() - self.last_gen_time >= self.gen_interval:
            self._generate_brick_row()
            self.last_gen_time = time.time()

        # ---- 移动球 ----
        if not self.attached:
            # 归一化速度方向
            current_spd = math.hypot(self.bdx, self.bdy)
            if current_spd > 0:
                self.bdx = self.bdx / current_spd * self.speed
                self.bdy = self.bdy / current_spd * self.speed

            self.bx += self.bdx
            self.by += self.bdy

            # 左右墙反弹
            if self.bx - self.BALL_R <= 0:
                self.bx = self.BALL_R
                self.bdx = abs(self.bdx)
            if self.bx + self.BALL_R >= self.CW:
                self.bx = self.CW - self.BALL_R
                self.bdx = -abs(self.bdx)

            # 顶部反弹
            if self.by - self.BALL_R <= 0:
                self.by = self.BALL_R
                self.bdy = abs(self.bdy)

            # 底部 - 球掉落 → 游戏结束
            if self.by + self.BALL_R >= self.CH:
                self._end_game(f"球掉落了！\n最终分数: {self.score}")
                return

            # 挡板碰撞
            if (
                self.bdy > 0
                and self.by + self.BALL_R >= self.py - self.PADDLE_H // 2
                and self.by - self.BALL_R <= self.py + self.PADDLE_H // 2
                and self.bx + self.BALL_R >= self.px - self.PADDLE_W // 2
                and self.bx - self.BALL_R <= self.px + self.PADDLE_W // 2
            ):
                if self.mouse_down:
                    # 鼠标按住 → 垂直于挡板弹出
                    self.bdx = 0.0
                    self.bdy = -self.speed
                else:
                    # 正常反弹：根据撞击位置改变角度
                    rel_x = (self.bx - self.px) / (self.PADDLE_W / 2)  # [-1, 1]
                    rel_x = max(-1.0, min(1.0, rel_x))
                    angle_deg = rel_x * 60.0  # 最大偏转 60°
                    angle_rad = math.radians(angle_deg)
                    self.bdx = self.speed * math.sin(angle_rad)
                    self.bdy = -self.speed * math.cos(angle_rad)

                # 将球移到挡板上方，防止卡入
                self.by = self.py - self.PADDLE_H // 2 - self.BALL_R

            # 砖块碰撞
            self._check_brick_collision()

            # 更新球在画布上的位置
            self.canvas.coords(
                self.ball_id,
                self.bx - self.BALL_R, self.by - self.BALL_R,
                self.bx + self.BALL_R, self.by + self.BALL_R,
            )

        # ---- 刷新 UI ----
        self._draw_ui()

        # ---- 下一帧 ----
        self.root.after(16, self._game_loop)  # ~60 FPS

    # ---------- 游戏结束 ----------
    def _end_game(self, message: str):
        self.game_over_flag = True
        self.attached = True
        self.bdx = 0.0
        self.bdy = 0.0

        # 半透明遮罩
        self.canvas.create_rectangle(
            0, 0, self.CW, self.CH,
            fill="#000000", stipple="gray50", tags="overlay",
        )
        self.game_over_text_id = self.canvas.create_text(
            self.CW // 2, self.CH // 2 - 20,
            text=message,
            fill="#ffffff",
            font=("Microsoft YaHei", 28, "bold"),
            justify="center",
            tags="overlay",
        )
        self.canvas.create_text(
            self.CW // 2, self.CH // 2 + 40,
            text="点击鼠标 或 按空格键 重新开始",
            fill="#aaaaaa",
            font=("Microsoft YaHei", 16),
            tags="overlay",
        )

    def _restart(self):
        """重新开始游戏"""
        # 清除遮罩
        self.canvas.delete("overlay")
        self.game_over_text_id = None

        # 清除所有砖块
        for brick_id in list(self.bricks.keys()):
            self.canvas.delete(brick_id)
            self.canvas.delete(self.bricks[brick_id]["text_id"])
        self.bricks.clear()

        # 重置状态
        self.score = 0
        self.game_over_flag = False
        self.start_time = None
        self.attached = True
        self.mouse_down = False
        self.speed = self.base_speed
        self.bdx = 0.0
        self.bdy = 0.0
        self.px = self.CW // 2
        self.bx = self.px
        self.by = self.py - self.BALL_R - self.PADDLE_H // 2
        self.last_gen_time = 0.0

        # 重置画布元素
        self.canvas.coords(
            self.paddle_id,
            self.px - self.PADDLE_W // 2, self.py - self.PADDLE_H // 2,
            self.px + self.PADDLE_W // 2, self.py + self.PADDLE_H // 2,
        )
        self.canvas.coords(
            self.ball_id,
            self.bx - self.BALL_R, self.by - self.BALL_R,
            self.bx + self.BALL_R, self.by + self.BALL_R,
        )
        self._draw_ui()

        # 重新启动循环
        self.root.after(16, self._game_loop)


if __name__ == "__main__":
    BreakoutGame()
