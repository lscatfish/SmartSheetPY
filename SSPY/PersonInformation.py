from dataclasses import dataclass


@dataclass
class Person:
	"""表示一个人的结构体类，包含基本个人信息"""
	name: str  # 姓名
	age: int  # 年龄
	gender: str  # 性别
	height: float  # 身高(米)
	weight: float  # 体重(千克)


# 使用示例
if __name__ == "__main__":
	# 创建Person实例
	person1 = Person("张三", 30, "男", 1.75, 70.5)
	person2 = Person("李四", 25, "女", 1.62, 52.3)
	# 访问属性
	print(f"{person1.name}的年龄是{person1.age}岁")
	print(f"{person2.name}的身高是{person2.height}米")

	# 打印整个对象（dataclass自动生成了__repr__方法）
	print(person1)
	print(person2)
	del person1
