import numpy as np
import matplotlib.pyplot as plt

# Создаём массив значений времени от 0 до 100
t = np.linspace(0, 100, 1000)

# Определяем функцию f(t) = sin(t)
y = np.sin(t/4)

# Строим график
plt.figure(figsize=(10, 5))
plt.plot(t, y, label='f(t) = sin(t)')
plt.xlabel('Время t')
plt.ylabel('f(t)')
plt.title('График функции f(t) = sin(t)')
plt.legend()
plt.grid(True)
plt.show()
