from day9_Multi_User_Memory.memory_manager import delete_memory, save_memory, get_memory

#1.准备两个不同的用户
user_a="user_001"
user_b="user_002"

#2.清理本次实验可能遗留的数据
delete_memory(user_a,"primary_language")
delete_memory(user_b,"primary_language")

#3.分别保存用户的长期记忆
save_memory(user_a,"primary_language","Python")
save_memory(user_b,"primary_language","Java")

#4.分别读取两个用户的记忆
memory_a=get_memory(user_a)
memory_b=get_memory(user_b)

#5.输出结果
print("用户A的长期记忆：",memory_a)
print("用户B的长期记忆：",memory_b)

#6.验证数据隔离
assert memory_a["primary_language"]=="Python"
assert memory_b["primary_language"]=="Java"
assert memory_a!=memory_b

print("测试通过：不同用户的长期记忆相互隔离。")