import PIL.Image
import wx
import cv2
import numpy as np
from wx.lib.masked import NumCtrl


def readimg(path):
    """读取图像并转换为OpenCV格式"""
    pil_img = PIL.Image.open(path)
    img_array = np.array(pil_img)
    image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    return image


class ScaledStaticBitmap(wx.Panel):
    """支持缩放的图像显示面板"""

    def __init__(self, parent):
        super(ScaledStaticBitmap, self).__init__(parent)
        self.bitmap = None
        self.original_image = None
        self.scale_factor = 1.0

        # 绑定绘制事件
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def set_image(self, cv2_image):
        """设置OpenCV图像"""
        if cv2_image is not None:
            self.original_image = cv2_image
            self.update_display()

    def update_display(self):
        """更新显示"""
        if self.original_image is not None:
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
                    self.bitmap = wx.Bitmap.FromBuffer(new_width, new_height, resized_image)
                    self.Refresh()  # 触发重绘

    def on_paint(self, event):
        """绘制图像"""
        dc = wx.PaintDC(self)
        if self.bitmap and self.bitmap.IsOk():
            # 清除背景
            dc.Clear()

            # 获取面板尺寸
            panel_width, panel_height = self.GetClientSize()
            bitmap_width = self.bitmap.GetWidth()
            bitmap_height = self.bitmap.GetHeight()

            # 计算居中位置
            x = (panel_width - bitmap_width) // 2
            y = (panel_height - bitmap_height) // 2

            # 绘制图像
            dc.DrawBitmap(self.bitmap, x, y, True)

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

        # 初始化UI
        self.init_ui()
        self.Centre()
        self.Show()

    def init_ui(self):
        # 创建主面板
        panel = wx.Panel(self)

        # 创建主水平布局 - 调整比例让图像区域更大
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 左侧图像显示区域 - 占据70%宽度
        left_panel = wx.Panel(panel, style = wx.BORDER_SUNKEN)
        left_sizer = wx.BoxSizer(wx.VERTICAL)

        # 使用自定义的缩放图像控件替代wx.StaticBitmap
        self.original_display = ScaledStaticBitmap(left_panel)
        left_sizer.Add(self.original_display, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)

        # 控制按钮
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.load_btn = wx.Button(left_panel, label = '加载图像')
        self.correct_btn = wx.Button(left_panel, label = '执行校正')
        self.save_btn = wx.Button(left_panel, label = '保存结果')

        button_sizer.Add(self.load_btn, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 5)
        button_sizer.Add(self.correct_btn, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 5)
        button_sizer.Add(self.save_btn, proportion = 1, flag = wx.EXPAND)

        left_sizer.Add(button_sizer, proportion = 0, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = 5)
        left_panel.SetSizer(left_sizer)

        # 右侧控制面板 - 占据30%宽度
        right_panel = wx.Panel(panel, style = wx.BORDER_SUNKEN)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # 校正结果显示
        self.corrected_display = ScaledStaticBitmap(right_panel)
        right_sizer.Add(self.corrected_display, proportion = 2, flag = wx.EXPAND | wx.ALL, border = 5)

        # 点坐标编辑区域
        points_box = wx.StaticBox(right_panel, label = '控制点坐标')
        points_sizer = wx.StaticBoxSizer(points_box, wx.VERTICAL)

        # 使用GridBagSizer以获得更好的布局控制
        grid_sizer = wx.GridBagSizer(5, 5)

        # 表头
        grid_sizer.Add(wx.StaticText(points_box, label = '点'), (0, 0), flag = wx.ALIGN_CENTER)
        grid_sizer.Add(wx.StaticText(points_box, label = 'X坐标'), (0, 1), flag = wx.ALIGN_CENTER)
        grid_sizer.Add(wx.StaticText(points_box, label = 'Y坐标'), (0, 2), flag = wx.ALIGN_CENTER)
        grid_sizer.Add(wx.StaticText(points_box, label = '操作'), (0, 3), flag = wx.ALIGN_CENTER)

        self.point_controls = []
        for i in range(4):
            # 点标签
            grid_sizer.Add(wx.StaticText(points_box, label = f'点 {i + 1}'), (i + 1,
                                                                              0), flag = wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

            # X坐标输入
            x_ctrl = NumCtrl(points_box, integerWidth = 4, fractionWidth = 0, size = (80, -1))
            grid_sizer.Add(x_ctrl, (i + 1, 1), flag = wx.EXPAND)

            # Y坐标输入
            y_ctrl = NumCtrl(points_box, integerWidth = 4, fractionWidth = 0, size = (80, -1))
            grid_sizer.Add(y_ctrl, (i + 1, 2), flag = wx.EXPAND)

            # 设置点按钮
            set_btn = wx.Button(points_box, label = f'设置')
            grid_sizer.Add(set_btn, (i + 1, 3), flag = wx.EXPAND)

            self.point_controls.append((x_ctrl, y_ctrl, set_btn))

            # 绑定按钮事件
            set_btn.Bind(wx.EVT_BUTTON, lambda event, idx = i: self.set_point_from_controls(idx))

        points_sizer.Add(grid_sizer, 1, flag = wx.EXPAND | wx.ALL, border = 5)
        right_sizer.Add(points_sizer, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)

        right_panel.SetSizer(right_sizer)

        # 设置主布局比例：左侧70%，右侧30%
        main_sizer.Add(left_panel, proportion = 7, flag = wx.EXPAND | wx.ALL, border = 5)
        main_sizer.Add(right_panel, proportion = 3, flag = wx.EXPAND | wx.ALL, border = 5)

        panel.SetSizer(main_sizer)

        # 绑定事件
        self.load_btn.Bind(wx.EVT_BUTTON, self.on_load_image)
        self.correct_btn.Bind(wx.EVT_BUTTON, self.on_correct)
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)

        # 绑定鼠标事件到图像显示面板
        self.original_display.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.original_display.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.original_display.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.original_display.Bind(wx.EVT_LEFT_DCLICK, self.on_double_click)

        # 初始状态禁用按钮
        self.correct_btn.Disable()
        self.save_btn.Disable()

    def on_load_image(self, event):
        with wx.FileDialog(self, "选择图像文件",
                wildcard = "图像文件 (*.jpg;*.png;*.bmp;*.jpeg)|*.jpg;*.png;*.bmp;*.jpeg") as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                filepath = dialog.GetPath()
                self.image = readimg(filepath)
                if self.image is not None:
                    self.original_display.set_image(self.image)
                    self.initialize_points()
                    self.correct_btn.Enable()
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
                cv2.circle(display_image, (x, y), self.point_radius, (0, 0, 255), -1)
                cv2.putText(display_image, str(i + 1), (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # 绘制连线
        if len(self.src_points) == 4:
            points = np.array(self.src_points, dtype = np.int32)
            cv2.polylines(display_image, [points], True, (0, 255, 0), 2)

        # 更新显示
        self.original_display.set_image(display_image)

    def initialize_points(self):
        """初始化四个控制点"""
        if self.image is None:
            return

        h, w = self.image.shape[:2]
        margin = min(w, h) * 0.1  # 10%边距

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
                self.src_points[point_index] = [x, y]
                self.display_original_image()

    # 其他方法（on_mouse_down, on_mouse_move, on_mouse_up, on_double_click,
    # on_correct, display_corrected_image, on_save）保持不变...
    # 这里省略了其他方法的实现以保持简洁，您原有的这些方法可以保留

    def on_mouse_down(self, event):
        """鼠标按下事件"""
        if self.image is None:
            return

        x, y = event.GetPosition()
        bitmap = self.original_bitmap.GetBitmap()
        if not bitmap.IsOk():
            return

        # 转换为图像坐标
        img_width = self.image.shape[1]
        img_height = self.image.shape[0]

        bitmap_width = bitmap.GetWidth()
        bitmap_height = bitmap.GetHeight()

        scale_x = img_width / bitmap_width
        scale_y = img_height / bitmap_height

        img_x = int(x * scale_x)
        img_y = int(y * scale_y)

        # 检查是否点击了控制点
        for i, point in enumerate(self.src_points):
            if len(point) == 2:
                px, py = point
                distance = np.sqrt((px - img_x) ** 2 + (py - img_y) ** 2)
                if distance < self.point_radius * 2:  # 扩大点击区域
                    self.dragging_point = i
                    break

    def on_mouse_move(self, event):
        """鼠标移动事件"""
        if self.dragging_point is not None and event.Dragging() and event.LeftIsDown():
            x, y = event.GetPosition()
            bitmap = self.original_bitmap.GetBitmap()

            if bitmap.IsOk():
                img_width = self.image.shape[1]
                img_height = self.image.shape[0]

                bitmap_width = bitmap.GetWidth()
                bitmap_height = bitmap.GetHeight()

                scale_x = img_width / bitmap_width
                scale_y = img_height / bitmap_height

                img_x = max(0, min(img_width - 1, int(x * scale_x)))
                img_y = max(0, min(img_height - 1, int(y * scale_y)))

                # 更新点坐标
                self.src_points[self.dragging_point] = [img_x, img_y]

                # 更新控件显示
                if self.dragging_point < len(self.point_controls):
                    x_ctrl, y_ctrl, btn = self.point_controls[self.dragging_point]
                    x_ctrl.SetValue(img_x)
                    y_ctrl.SetValue(img_y)

                self.display_original_image()

    def on_mouse_up(self, event):
        """鼠标释放事件"""
        self.dragging_point = None

    def on_double_click(self, event):
        """双击添加/移动点"""
        if self.image is None:
            return

        x, y = event.GetPosition()
        bitmap = self.original_bitmap.GetBitmap()

        img_width = self.image.shape[1]
        img_height = self.image.shape[0]

        bitmap_width = bitmap.GetWidth()
        bitmap_height = bitmap.GetHeight()

        scale_x = img_width / bitmap_width
        scale_y = img_height / bitmap_height

        img_x = int(x * scale_x)
        img_y = int(y * scale_y)

        # 找到最近的点并移动它
        if len(self.src_points) > 0:
            distances = [np.sqrt((p[0] - img_x) ** 2 + (p[1] - img_y) ** 2) for p in self.src_points]
            min_index = np.argmin(distances)
            if distances[min_index] < 100:  # 最大移动距离
                self.src_points[min_index] = [img_x, img_y]
                self.update_point_controls()
                self.display_original_image()

    def on_correct(self, event):
        """执行透视校正"""
        if self.image is None or len(self.src_points) != 4:
            wx.MessageBox('请确保已加载图像并设置了4个控制点！', '提示', wx.OK | wx.ICON_INFORMATION)
            return

        try:
            # 定义源点和目标点[1,2](@ref)
            src_pts = np.float32(self.src_points)

            # 计算目标点（基于源点的边界框）
            x_coords = [p[0] for p in self.src_points]
            y_coords = [p[1] for p in self.src_points]

            width = int(max(x_coords) - min(x_coords))
            height = int(max(y_coords) - min(y_coords))

            dst_pts = np.float32([
                [0, 0],
                [width, 0],
                [width, height],
                [0, height]
            ])

            # 计算透视变换矩阵[1,5](@ref)
            M = cv2.getPerspectiveTransform(src_pts, dst_pts)

            # 执行透视变换[2,3](@ref)
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

        display_image = cv2.cvtColor(self.corrected_image, cv2.COLOR_BGR2RGB)
        h, w = display_image.shape[:2]

        wx_image = wx.Bitmap.FromBuffer(w, h, display_image)
        self.corrected_bitmap.SetBitmap(wx_image)
        self.corrected_bitmap.Refresh()

    def on_save(self, event):
        """保存校正结果"""
        if self.corrected_image is None:
            return

        with wx.FileDialog(self, "保存校正后的图像",
                wildcard = "JPEG文件 (*.jpg)|*.jpg|PNG文件 (*.png)|*.png",
                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dialog:

            if dialog.ShowModal() == wx.ID_OK:
                filepath = dialog.GetPath()
                success = cv2.imwrite(filepath, self.corrected_image)
                if success:
                    wx.MessageBox('图像保存成功！', '提示', wx.OK | wx.ICON_INFORMATION)
                else:
                    wx.MessageBox('图像保存失败！', '错误', wx.OK | wx.ICON_ERROR)



class PerspectiveCorrectorApp(wx.App):
    def OnInit(self):
        frame = PerspectiveCorrectorFrame(None, title = '手动透视校正工具')
        return True


def main():
    app = PerspectiveCorrectorApp()
    app.MainLoop()


if __name__ == '__main__':
    main()


