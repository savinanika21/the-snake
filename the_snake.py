from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """
    Базовый класс для всех игровых объектов.
    Хранит общие атрибуты: позицию и цвет объекта.
    Предоставляет заглушку для метода отрисовки, который должен
    быть переопределен в дочерних классах.
    """

    position = (0, 0)
    body_color = (0, 255, 0)

    def __init__(self, position, body_color=None):
        """
        Инициализирует игровой объект.
        Аргументы:
        position - начальная позиция объекта (x, y).
        body_color - цвет объекта. Если не указан,
        используется цвет по умолчанию.
        """
        self.position = position
        if body_color:
            self.body_color = body_color
        else:
            self.body_color = self.body_color

    def draw(self):
        """
        Метод отрисовки объекта.
        В базовом классе не выполняет действий, реализация
        зависит от конкретного типа объекта (яблоко, змейка).
        """
        pass


class Apple(GameObject):
    """Игровой объект: яблоко. Отвечает за позицию и отрисовку."""

    def __init__(self, position):
        """Задает цвет яблока."""
        super().__init__(position, APPLE_COLOR)

    def randomize_position(self):
        """Генерирует случайную позицию по сетке клеток."""
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)
        return self.position

    # Метод draw класса Apple - забрала из шаблона в конце файла
    def draw(self):
        """Отрисовывает яблоко как квадрат с обводкой."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Игровой объект: змейка. Управляет движением,
    ростом и отрисовкой сегментов.
    """

    def __init__(self, position):
        """Задаёт стартовую позицию, направление и список сегментов."""
        super().__init__(position, SNAKE_COLOR)
        self.positions = [position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает текущие координаты головы змейки."""
        return self.positions[0]

    def move(self, is_apple_eaten=False):
        """
        Обновляет позицию змейки.
        Вычисляет новую голову с учётом
        направления и телепортации через границы поля.
        Если яблоко не съедено, удаляет хвост и сохраняет
        его координаты в last.
        """
        current_head = self.get_head_position()
        new_head_x = (
            (current_head[0] + self.direction[0] * GRID_SIZE)
            % SCREEN_WIDTH
        )
        new_head_y = (
            (current_head[1] + self.direction[1] * GRID_SIZE)
            % SCREEN_HEIGHT
        )
        new_head = (new_head_x, new_head_y)
        self.positions.insert(0, new_head)
        # Съели яблоко или нет и в зависимости от этого действия
        if not is_apple_eaten:
            self.last = self.positions[-1]
            self.positions.pop()
        else:
            self.last = None

    # Метод обновления направления после
    # нажатия на кнопку - из шаблона в конце файла
    def update_direction(self):
        """Применяет запланированное направление движения
        (next_direction) к текущему.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    # Метод draw класса Snake- из шаблона,
    # который был в конце файла,
    # чуть поменяла местами блоки
    def draw(self):
        """
        Отрисовывает змейку.
        Сначала стирает старый хвост (если есть), затем рисует все сегменты.
        """
        # Затирание последнего сегмента и обнуление last
        # (чтобы не стирать дважды)
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
            self.last = None

        # Тело рисуется без головы
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения."""
        start_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [start_position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.position = start_position


# Функция обработки действий пользователя - из шаблона в конце файла
def handle_keys(game_object):
    """
    Обрабатывает события ввода (нажатия клавиш и закрытие окна).
    Записывает новое направление в next_direction объекта.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Главный игровой цикл.
    Инициализирует объекты, запускает бесконечный цикл:
    1. Обработка ввода.
    2. Обновление логики (направление, движение, столкновения).
    3. Отрисовка объектов.
    4. Контроль FPS.
    """
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    start_position = (100, 100)
    snake = Snake(start_position)

    apple = Apple((0, 0))
    apple.randomize_position()

    while True:
        clock.tick(SPEED)
        # Обработка событий
        handle_keys(snake)
        # Новое направление змейки
        snake.update_direction()
        # Проверка, съели ли яблоко
        is_apple_eaten = False
        if snake.get_head_position() == apple.position:
            is_apple_eaten = True
            apple.randomize_position()
        # Змейка двигается
        snake.move(is_apple_eaten)
        # Столкновение змейки с самой собой
        head = snake.get_head_position()
        if head in snake.positions[1:]:
            print("Игра окончена! Змейка врезалась сама в себя.")
            # Сбрасываем змейку в начальное состояние,
            # яблоко рандомно перемещается
            snake.reset()
            apple.randomize_position()
        # Очистка экрана
        # Примечание: Использую полную очистку экрана,
        # чтобы гарантировать отсутствие следов
        # и корректную очистку поля после сброса игры (reset).
        # Логика частичного стирания хвоста в
        # snake.draw() остаётся из-за шаблона,
        # но она становится избыточной благодаря этой строке.
        screen.fill(BOARD_BACKGROUND_COLOR)
        # Отрисовка змейки и яблока
        snake.draw()
        apple.draw()
        # Обновление окна
        pygame.display.update()

        
if __name__ == '__main__':
    main()
