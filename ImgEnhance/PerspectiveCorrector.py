import wx
import cv2
import numpy as np

from ImgEnhance.iofunc import read_img, write_img


class ScaledStaticBitmap(wx.Panel):
    """支持缩放的图像显示面板，解决黑色背景和频闪问题"""

    def __init__(self, parent, default_bg_color = (240, 240, 240)):
        super(ScaledStaticBitmap, self).__init__(parent)
        self.bitmap = None
        self.original_image = None
        self.scale_factor = 1.0
        self.default_bg_color = default_bg_color
        self.has_image = False

        # 设置面板背景色
        self.SetBackgroundColour(wx.Colour(self.default_bg_color))

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)

    def on_erase_background(self, event):
        """空的事件处理器，阻止背景擦除导致的闪烁"""
        pass

    def set_image(self, cv2_image):
        """设置OpenCV图像"""
        if cv2_image is not None:
            self.original_image = cv2_image
            self.has_image = True
            self.update_display()
        else:
            self.has_image = False
            self.bitmap = None
            self.Refresh()

    def update_display(self):
        """更新显示"""
        if self.has_image and self.original_image is not None:
            # 转换颜色空间
            display_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            h, w = display_image.shape[:2]

            # 获取面板尺寸
            panel_width, panel_height = self.GetClientSize()

            if panel_width > 0 and panel_height > 0:
                # 计算保持宽高比的缩放比例
                scale_x = panel_width / w
                scale_y = panel_height / h
                self.scale_factor = min(scale_x, scale_y)

                # 计算缩放后的尺寸
                new_width = int(w * self.scale_factor)
                new_height = int(h * self.scale_factor)

                # 缩放图像
                if new_width > 0 and new_height > 0:
                    resized_image = cv2.resize(display_image, (new_width, new_height))

                    # 转换为wxPython位图
                    height, width = resized_image.shape[:2]
                    self.bitmap = wx.Bitmap.FromBuffer(width, height, resized_image)
                    self.Refresh()
        else:
            self.Refresh()

    def on_paint(self, event):
        """绘制图像 - 使用双缓冲技术避免闪烁"""
        dc = wx.BufferedPaintDC(self)

        # 获取面板尺寸
        panel_width, panel_height = self.GetClientSize()

        # 绘制默认背景
        dc.SetBackground(wx.Brush(wx.Colour(self.default_bg_color)))
        dc.Clear()

        if self.bitmap and self.bitmap.IsOk() and self.has_image:
            # 绘制图像（居中显示）
            bitmap_width = self.bitmap.GetWidth()
            bitmap_height = self.bitmap.GetHeight()

            x = (panel_width - bitmap_width) // 2
            y = (panel_height - bitmap_height) // 2

            dc.DrawBitmap(self.bitmap, x, y, True)
        else:
            # 没有图片时显示提示文本
            dc.SetTextForeground(wx.Colour(100, 100, 100))
            font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            dc.SetFont(font)

            text = "请加载图像"
            text_width, text_height = dc.GetTextExtent(text)

            x = (panel_width - text_width) // 2
            y = (panel_height - text_height) // 2

            dc.DrawText(text, x, y)

    def on_size(self, event):
        """处理尺寸变化"""
        self.update_display()
        event.Skip()


class PerspectiveCorrectorFrame(wx.Frame):
    def __init__(self, parent, title):
        super(PerspectiveCorrectorFrame, self).__init__(parent, title = title, size = (1400, 800))

        self.image = None
        self.corrected_image = None
        self.src_points = []  # 原始图像中的四个点
        self.dragging_point = None
        self.point_radius = 8
        self.image_width = 0  # 图像宽度
        self.image_height = 0  # 图像高度

        # 初始化UI
        self.init_ui()
        self.Centre()
        self.Show()

    def init_ui(self):
        # 创建主面板
        panel = wx.Panel(self)

        # 创建主水平布局
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 左侧图像显示区域 - 占据70%宽度
        left_panel = wx.Panel(panel, style = wx.BORDER_SUNKEN)
        left_panel.SetBackgroundColour(wx.Colour(240, 240, 240))
        left_sizer = wx.BoxSizer(wx.VERTICAL)

        # 原始图像显示区域
        self.original_display = ScaledStaticBitmap(left_panel)
        left_sizer.Add(self.original_display, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)

        # 控制按钮
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.load_btn = wx.Button(left_panel, label = '加载图像')
        self.correct_btn = wx.Button(left_panel, label = '执行校正')
        self.save_btn = wx.Button(left_panel, label = '保存结果')
        self.reset_btn = wx.Button(left_panel, label = '重置点')

        button_sizer.Add(self.load_btn, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 5)
        button_sizer.Add(self.correct_btn, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 5)
        button_sizer.Add(self.save_btn, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 5)
        button_sizer.Add(self.reset_btn, proportion = 1, flag = wx.EXPAND)

        left_sizer.Add(button_sizer, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 5)
        left_panel.SetSizer(left_sizer)

        # 右侧控制面板 - 占据30%宽度
        right_panel = wx.Panel(panel, style = wx.BORDER_SUNKEN)
        right_panel.SetBackgroundColour(wx.Colour(240, 240, 240))
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # 校正结果显示
        self.corrected_display = ScaledStaticBitmap(right_panel)
        right_sizer.Add(self.corrected_display, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)

        # 点坐标编辑区域
        points_box = wx.StaticBox(right_panel, label = '控制点坐标 (左上->右上->右下->左下)')
        points_sizer = wx.StaticBoxSizer(points_box, wx.VERTICAL)

        # 创建网格布局
        grid_sizer = wx.FlexGridSizer(rows = 5, cols = 4, vgap = 5, hgap = 5)

        # 表头
        grid_sizer.Add(wx.StaticText(points_box, label = '点'), 0, wx.ALIGN_CENTER)
        grid_sizer.Add(wx.StaticText(points_box, label = 'X坐标'), 0, wx.ALIGN_CENTER)
        grid_sizer.Add(wx.StaticText(points_box, label = 'Y坐标'), 0, wx.ALIGN_CENTER)
        grid_sizer.Add(wx.StaticText(points_box, label = '操作'), 0, wx.ALIGN_CENTER)

        self.point_controls = []
        for i in range(4):
            # 点标签
            grid_sizer.Add(wx.StaticText(points_box, label = f'点 {i + 1}'), 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

            # X坐标输入 - 使用wx.SpinCtrl，带上下调整按钮
            # 初始范围设为0-1000，加载图像后会根据实际尺寸调整
            x_ctrl = wx.SpinCtrl(points_box, min = 0, max = 1000, initial = 0)
            x_ctrl.SetMinSize((80, -1))

            # Y坐标输入 - 使用wx.SpinCtrl，带上下调整按钮
            y_ctrl = wx.SpinCtrl(points_box, min = 0, max = 1000, initial = 0)
            y_ctrl.SetMinSize((80, -1))

            # 设置点按钮
            set_btn = wx.Button(points_box, label = '设置')
            set_btn.SetMinSize((60, -1))

            grid_sizer.Add(x_ctrl, 0, wx.EXPAND)
            grid_sizer.Add(y_ctrl, 0, wx.EXPAND)
            grid_sizer.Add(set_btn, 0, wx.EXPAND)

            self.point_controls.append((x_ctrl, y_ctrl, set_btn))

            # 绑定按钮事件
            set_btn.Bind(wx.EVT_BUTTON, lambda event, idx = i: self.set_point_from_controls(idx))

            # 绑定SpinCtrl变化事件，实现实时更新
            x_ctrl.Bind(wx.EVT_SPINCTRL, lambda event, idx = i: self.on_spin_change(idx))
            y_ctrl.Bind(wx.EVT_SPINCTRL, lambda event, idx = i: self.on_spin_change(idx))

            # 绑定文本输入事件（当用户直接输入数字时）
            x_ctrl.Bind(wx.EVT_TEXT, lambda event, idx = i: self.on_spin_text_change(idx))
            y_ctrl.Bind(wx.EVT_TEXT, lambda event, idx = i: self.on_spin_text_change(idx))

        points_sizer.Add(grid_sizer, 1, flag = wx.EXPAND | wx.ALL, border = 5)
        right_sizer.Add(points_sizer, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 5)

        right_panel.SetSizer(right_sizer)

        # 设置主布局比例：左侧70%，右侧30%
        main_sizer.Add(left_panel, proportion = 7, flag = wx.EXPAND | wx.ALL, border = 5)
        main_sizer.Add(right_panel, proportion = 3, flag = wx.EXPAND | wx.ALL, border = 5)

        panel.SetSizer(main_sizer)

        # 绑定事件
        self.load_btn.Bind(wx.EVT_BUTTON, self.on_load_image)
        self.correct_btn.Bind(wx.EVT_BUTTON, self.on_correct)
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        self.reset_btn.Bind(wx.EVT_BUTTON, self.on_reset_points)

        # 绑定鼠标事件到图像显示面板
        self.original_display.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.original_display.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.original_display.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.original_display.Bind(wx.EVT_LEFT_DCLICK, self.on_double_click)

        # 初始状态禁用按钮
        self.correct_btn.Disable()
        self.save_btn.Disable()
        self.reset_btn.Disable()

    def update_spin_ctrl_ranges(self):
        """根据图像尺寸更新SpinCtrl的最大值范围"""
        if self.image is not None:
            h, w = self.image.shape[:2]
            self.image_width = w
            self.image_height = h

            # 更新所有SpinCtrl的范围
            for x_ctrl, y_ctrl, btn in self.point_controls:
                x_ctrl.SetRange(0, w - 1)  # X坐标范围：0到图像宽度-1
                y_ctrl.SetRange(0, h - 1)  # Y坐标范围：0到图像高度-1

    def on_load_image(self, event):
        """加载图像"""
        with wx.FileDialog(self, "选择图像文件",
                wildcard = "图像文件 (*.jpg;*.png;*.bmp;*.jpeg)|*.jpg;*.png;*.bmp;*.jpeg") as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                filepath = dialog.GetPath()
                self.image = read_img(filepath)
                if self.image is not None:
                    self.original_display.set_image(self.image)
                    # 更新SpinCtrl的范围限制
                    self.update_spin_ctrl_ranges()
                    self.initialize_points()
                    self.correct_btn.Enable()
                    self.reset_btn.Enable()
                else:
                    wx.MessageBox('无法加载图像文件！', '错误', wx.OK | wx.ICON_ERROR)

    def display_original_image(self):
        """显示原始图像并绘制控制点"""
        if self.image is None:
            return

        display_image = self.image.copy()
        h, w = display_image.shape[:2]

        # 绘制控制点和连线
        for i, point in enumerate(self.src_points):
            if len(point) == 2:
                x, y = int(point[0]), int(point[1])
                # 确保点在图像范围内
                x = max(0, min(w - 1, x))
                y = max(0, min(h - 1, y))

                cv2.circle(display_image, (x, y), self.point_radius, (0, 0, 255), -1)
                cv2.putText(display_image, str(i + 1), (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # 绘制连线
        if len(self.src_points) == 4:
            points = []
            for point in self.src_points:
                if len(point) == 2:
                    x, y = int(point[0]), int(point[1])
                    x = max(0, min(w - 1, x))
                    y = max(0, min(h - 1, y))
                    points.append([x, y])

            if len(points) == 4:
                points = np.array(points, dtype = np.int32)
                cv2.polylines(display_image, [points], True, (0, 255, 0), 2)

        # 更新显示
        self.original_display.set_image(display_image)

    def initialize_points(self):
        """初始化四个控制点"""
        if self.image is None:
            return

        h, w = self.image.shape[:2]
        margin = min(w, h) * 0.05  # 5%边距

        self.src_points = [
            [margin, margin],  # 左上
            [w - margin, margin],  # 右上
            [w - margin, h - margin],  # 右下
            [margin, h - margin]  # 左下
        ]

        self.update_point_controls()
        self.display_original_image()

    def update_point_controls(self):
        """更新点坐标控件"""
        for i, (x_ctrl, y_ctrl, btn) in enumerate(self.point_controls):
            if i < len(self.src_points):
                x_ctrl.SetValue(int(self.src_points[i][0]))
                y_ctrl.SetValue(int(self.src_points[i][1]))

    def set_point_from_controls(self, point_index):
        """从控件设置点坐标"""
        if point_index < len(self.point_controls):
            x_ctrl, y_ctrl, btn = self.point_controls[point_index]
            x = x_ctrl.GetValue()
            y = y_ctrl.GetValue()

            if point_index < len(self.src_points):
                # 由于SpinCtrl已经设置了范围，这里不需要再手动调整范围
                self.src_points[point_index] = [x, y]
                self.display_original_image()
                wx.CallAfter(self.on_correct, None)

    def on_spin_change(self, point_index):
        """当使用上下按钮调整数值时的处理"""
        self.set_point_from_controls(point_index)

    def on_spin_text_change(self, point_index):
        """当在文本框中直接输入数值时的处理"""
        # 添加延迟处理，避免频繁更新
        if hasattr(self, '_text_timer'):
            self._text_timer.Stop()

        self._text_timer = wx.CallLater(500, self.set_point_from_controls, point_index)

    def on_mouse_down(self, event):
        """鼠标按下事件"""
        if self.image is None:
            return

        # 获取鼠标位置
        x, y = event.GetPosition()

        # 转换为图像坐标
        img_x, img_y = self.screen_to_image_coords(x, y)
        if img_x is None or img_y is None:
            return

        # 检查是否点击了控制点
        for i, point in enumerate(self.src_points):
            if len(point) == 2:
                px, py = point
                distance = np.sqrt((px - img_x) ** 2 + (py - img_y) ** 2)
                if distance < self.point_radius * 3:  # 扩大点击区域
                    self.dragging_point = i
                    break

    def on_mouse_move(self, event):
        """鼠标移动事件"""
        if self.dragging_point is not None and event.Dragging() and event.LeftIsDown():
            x, y = event.GetPosition()

            # 转换为图像坐标
            img_x, img_y = self.screen_to_image_coords(x, y)
            if img_x is None or img_y is None:
                return

            # 确保坐标在图像范围内
            if self.image is not None:
                h, w = self.image.shape[:2]
                img_x = max(0, min(w - 1, img_x))
                img_y = max(0, min(h - 1, img_y))

            # 更新点坐标
            self.src_points[self.dragging_point] = [img_x, img_y]

            # 更新控件显示
            if self.dragging_point < len(self.point_controls):
                x_ctrl, y_ctrl, btn = self.point_controls[self.dragging_point]
                x_ctrl.SetValue(int(img_x))
                y_ctrl.SetValue(int(img_y))

            self.display_original_image()

    def on_mouse_up(self, event):
        """鼠标释放事件"""
        self.dragging_point = None

    def on_double_click(self, event):
        """双击添加/移动点"""
        if self.image is None:
            return

        x, y = event.GetPosition()

        # 转换为图像坐标
        img_x, img_y = self.screen_to_image_coords(x, y)
        if img_x is None or img_y is None:
            return

        # 找到最近的点并移动它
        if len(self.src_points) > 0:
            distances = []
            for point in self.src_points:
                if len(point) == 2:
                    px, py = point
                    distance = np.sqrt((px - img_x) ** 2 + (py - img_y) ** 2)
                    distances.append(distance)
                else:
                    distances.append(float('inf'))

            if distances:
                min_index = np.argmin(distances)
                if distances[min_index] < 100:  # 最大移动距离
                    # 确保坐标在图像范围内
                    h, w = self.image.shape[:2]
                    img_x = max(0, min(w - 1, img_x))
                    img_y = max(0, min(h - 1, img_y))

                    self.src_points[min_index] = [img_x, img_y]
                    self.update_point_controls()
                    self.display_original_image()

    def screen_to_image_coords(self, screen_x, screen_y):
        """将屏幕坐标转换为图像坐标"""
        if self.image is None or self.original_display.bitmap is None:
            return None, None

        # 获取显示面板和位图尺寸
        panel_width, panel_height = self.original_display.GetClientSize()
        bitmap_width = self.original_display.bitmap.GetWidth() if self.original_display.bitmap else 0
        bitmap_height = self.original_display.bitmap.GetHeight() if self.original_display.bitmap else 0

        if bitmap_width == 0 or bitmap_height == 0:
            return None, None

        # 计算位图在面板中的偏移（居中显示）
        offset_x = (panel_width - bitmap_width) // 2
        offset_y = (panel_height - bitmap_height) // 2

        # 检查点击是否在图像范围内
        if (offset_x <= screen_x < offset_x + bitmap_width and
                offset_y <= screen_y < offset_y + bitmap_height):
            # 计算在位图中的相对位置
            bitmap_x = screen_x - offset_x
            bitmap_y = screen_y - offset_y

            # 计算缩放比例
            img_height, img_width = self.image.shape[:2]
            scale_x = img_width / bitmap_width
            scale_y = img_height / bitmap_height

            # 转换为原始图像坐标
            img_x = bitmap_x * scale_x
            img_y = bitmap_y * scale_y

            return img_x, img_y

        return None, None

    def on_correct(self, event):
        """执行透视校正"""
        if self.image is None or len(self.src_points) != 4:
            wx.MessageBox('请确保已加载图像并设置了4个控制点！', '提示', wx.OK | wx.ICON_INFORMATION)
            return

        try:
            # 检查所有点是否有效
            valid_points = True
            for point in self.src_points:
                if len(point) != 2:
                    valid_points = False
                    break

            if not valid_points:
                wx.MessageBox('控制点设置不完整！', '错误', wx.OK | wx.ICON_ERROR)
                return

            # 定义源点和目标点
            src_pts = np.float32(self.src_points)

            # 计算目标点（基于源点的边界框）
            x_coords = [p[0] for p in self.src_points]
            y_coords = [p[1] for p in self.src_points]

            width = int(max(x_coords) - min(x_coords))
            height = int(max(y_coords) - min(y_coords))

            # 设置目标点（A4比例）
            a4_ratio = 297.0 / 210.0  # A4纸高宽比
            if width > 0:
                current_ratio = height / width
                if current_ratio > a4_ratio:
                    # 以高度为准调整宽度
                    width = int(height / a4_ratio)
                else:
                    # 以宽度为准调整高度
                    height = int(width * a4_ratio)

            dst_pts = np.float32([
                [0, 0],
                [width, 0],
                [width, height],
                [0, height]
            ])

            # 计算透视变换矩阵
            M = cv2.getPerspectiveTransform(src_pts, dst_pts)

            # 执行透视变换
            self.corrected_image = cv2.warpPerspective(self.image, M, (width, height))

            # 显示校正结果
            self.display_corrected_image()
            self.save_btn.Enable()

        except Exception as e:
            wx.MessageBox(f'透视校正失败：{str(e)}', '错误', wx.OK | wx.ICON_ERROR)

    def display_corrected_image(self):
        """显示校正后的图像"""
        if self.corrected_image is None:
            return

        self.corrected_display.set_image(self.corrected_image)

    def on_save(self, event):
        """保存校正结果"""
        if self.corrected_image is None:
            return

        with wx.FileDialog(self, "保存校正后的图像",
                wildcard = "JPEG文件 (*.jpg)|*.jpg|PNG文件 (*.png)|*.png",
                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dialog:

            if dialog.ShowModal() == wx.ID_OK:
                filepath = dialog.GetPath()
                # 确保文件扩展名正确
                if not filepath.lower().endswith(('.jpg', '.jpeg', '.png')):
                    if dialog.GetFilterIndex() == 0:  # JPEG
                        filepath += '.jpg'
                    else:  # PNG
                        filepath += '.png'

                success = write_img(self.corrected_image, filepath)
                if success:
                    wx.MessageBox(f'图像保存成功！\n保存路径: {filepath}', '提示', wx.OK | wx.ICON_INFORMATION)
                else:
                    wx.MessageBox('图像保存失败！', '错误', wx.OK | wx.ICON_ERROR)

    def on_reset_points(self, event):
        """重置控制点"""
        if self.image is not None:
            self.initialize_points()


class PerspectiveCorrectorApp(wx.App):
    def OnInit(self):
        frame = PerspectiveCorrectorFrame(None, title = '手动透视校正工具')
        frame.Show()
        return True


def main():
    app = PerspectiveCorrectorApp()
    app.MainLoop()


if __name__ == '__main__':
    main()
